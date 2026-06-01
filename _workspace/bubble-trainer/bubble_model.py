#!/usr/bin/env python3
"""
말풍선 배치 학습 모델 (Bubble Placement Model) — 순수 Python, 의존성 0
=====================================================================
"얼굴 근처가 좋다"는 단 하나의 근거로 일단 배치 → 사람이 베스트 위치로 교정 →
그 교정값(label)을 정답으로 작은 신경망(MLP)이 학습 → 연습이 쌓이면 모델이
직접 베스트 위치를 예측한다.

torch / numpy / 인터넷 / CDN 전혀 필요 없음. 표준 라이브러리만 사용 →
샌드박스에서 그대로 `python3 bubble_model.py ...` 로 실행/검증 가능.

서브커맨드:
    selftest                       합성 데이터로 "샘플 늘수록 오차 감소" 검증(입력 불필요)
    train   --data D --out M       dataset.json 으로 학습 → model.json 저장
    eval    --data D --model M      검증셋 MSE 출력
    predict --panels P --model M [--panel-id 5.1]
                                   패널 메타로 말풍선 위치 예측(+ heuristic 비교)
    features --panels P --panel-id 5.1
                                   피처 벡터 출력(라벨러 JS와 인코딩 일치 확인용)

데이터 포맷은 references/storyboard-data-spec.md 참조.
"""

import os
import sys
import json
import math
import random
import argparse

GRID = 4
TYPES = ["speech", "thought", "narration", "screen", "sfx"]
# 피처 길이: face4 + torso4 + bubble2 + type5 + aspect1 + occGrid16 = 32
FEATLEN = 4 + 4 + 2 + 5 + 1 + GRID * GRID


# ─────────────────────────────────────────────────────────────
# 피처 추출 (storyboard-data-spec §3 의 기하 핵심 — 이미지 디코딩 불필요)
# ─────────────────────────────────────────────────────────────
def _clamp(v, a, b):
    return max(a, min(b, v))


def _box_rect(b):
    return (b["x"] - b["w"] / 2, b["y"] - b["h"] / 2,
            b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)


def _cell_rect(i):
    r, c, s = i // GRID, i % GRID, 1.0 / GRID
    return (c * s, r * s, c * s + s, r * s + s)


def _inter_area(a, b):
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return w * h


def speaker_char(panel, bubble):
    for c in panel["characters"]:
        if c.get("name") == bubble.get("speaker"):
            return c
    return panel["characters"][0]


def occ_grid(panel, bubble):
    """타 인물(화자 제외) face+torso 박스가 각 격자 칸을 덮는 면적비 (0~1)."""
    g = [0.0] * (GRID * GRID)
    others = [c for c in panel["characters"] if c.get("name") != bubble.get("speaker")]
    cell_area = (1.0 / GRID) ** 2
    for i in range(len(g)):
        cr = _cell_rect(i)
        cov = 0.0
        for c in others:
            if c.get("face"):
                cov += _inter_area(cr, _box_rect(c["face"]))
            if c.get("torso"):
                cov += _inter_area(cr, _box_rect(c["torso"]))
        g[i] = _clamp(cov / cell_area, 0.0, 1.0)
    return g


def extract_features(panel, bubble):
    sp = speaker_char(panel, bubble)
    f = sp.get("face") or {"x": 0.5, "y": 0.5, "w": 0.0, "h": 0.0}
    t = sp.get("torso") or {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0}
    type_oh = [0.0] * 5
    ti = TYPES.index(bubble["type"]) if bubble.get("type") in TYPES else 0
    type_oh[ti] = 1.0
    ar = (panel.get("imageW") or 1) / (panel.get("imageH") or 1)
    aspect = ar / (ar + 1)
    v = [f["x"], f["y"], f["w"], f["h"],
         t["x"], t["y"], t["w"], t["h"],
         bubble.get("w", 0.2), bubble.get("h", 0.1)]
    v += type_oh
    v.append(aspect)
    v += occ_grid(panel, bubble)
    assert len(v) == FEATLEN, f"feature length {len(v)} != {FEATLEN}"
    return v


# ─────────────────────────────────────────────────────────────
# 휴리스틱 (유일한 근거: 얼굴 근처 + 가장 빈 칸 방향)
# ─────────────────────────────────────────────────────────────
def heuristic_place(panel, bubble):
    sp = speaker_char(panel, bubble)
    f = sp.get("face") or {"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.1}
    occ = occ_grid(panel, bubble)
    bw, bh = bubble.get("w", 0.2), bubble.get("h", 0.1)
    best, best_cost = None, 1e9
    for deg in (-90, -60, -120, -30, -150, 0, 180):
        rad = math.radians(deg)
        x = _clamp(f["x"] + math.cos(rad) * (f["w"] / 2 + bw / 2 + 0.02), bw / 2, 1 - bw / 2)
        y = _clamp(f["y"] + math.sin(rad) * (f["h"] / 2 + bh / 2 + 0.02), bh / 2, 1 - bh / 2)
        ci = _clamp(int(y * GRID), 0, GRID - 1) * GRID + _clamp(int(x * GRID), 0, GRID - 1)
        face_ov = _inter_area((x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2), _box_rect(f))
        cost = occ[ci] + face_ov * 40 + y * 0.15  # 위쪽 선호
        if cost < best_cost:
            best_cost, best = cost, {"x": x, "y": y}
    return best


# ─────────────────────────────────────────────────────────────
# MLP (순수 Python, Adam) — 회귀: 피처 → (x, y)
# ─────────────────────────────────────────────────────────────
def _relu(z):
    return z if z > 0 else 0.0


def _sigmoid(z):
    if z < -60:
        return 0.0
    if z > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


class MLP:
    def __init__(self, sizes=(FEATLEN, 32, 16, 2), seed=0):
        rng = random.Random(seed)
        self.sizes = list(sizes)
        self.W, self.b = [], []
        for i in range(len(sizes) - 1):
            nin, nout = sizes[i], sizes[i + 1]
            scale = math.sqrt(2.0 / nin)  # He init
            self.W.append([[rng.gauss(0, scale) for _ in range(nin)] for _ in range(nout)])
            self.b.append([0.0] * nout)
        # Adam 상태
        self.mW = [[[0.0] * len(r) for r in layer] for layer in self.W]
        self.vW = [[[0.0] * len(r) for r in layer] for layer in self.W]
        self.mb = [[0.0] * len(layer) for layer in self.b]
        self.vb = [[0.0] * len(layer) for layer in self.b]
        self.t = 0

    def forward(self, x):
        acts = [x]
        zs = []
        a = x
        for li in range(len(self.W)):
            W, b = self.W[li], self.b[li]
            z = [sum(W[o][i] * a[i] for i in range(len(a))) + b[o] for o in range(len(b))]
            zs.append(z)
            last = (li == len(self.W) - 1)
            a = [(_sigmoid(v) if last else _relu(v)) for v in z]
            acts.append(a)
        return acts, zs

    def predict(self, x):
        acts, _ = self.forward(x)
        return acts[-1]

    def _grads(self, x, y):
        acts, zs = self.forward(x)
        gW = [[[0.0] * len(r) for r in layer] for layer in self.W]
        gb = [[0.0] * len(layer) for layer in self.b]
        L = len(self.W)
        # 출력층 delta (sigmoid + MSE)
        out = acts[-1]
        n_out = len(out)
        delta = [2.0 * (out[o] - y[o]) / n_out * out[o] * (1 - out[o]) for o in range(n_out)]
        for li in reversed(range(L)):
            a_prev = acts[li]
            for o in range(len(self.b[li])):
                gb[li][o] = delta[o]
                row = gW[li][o]
                d = delta[o]
                for i in range(len(a_prev)):
                    row[i] = d * a_prev[i]
            if li > 0:
                z_prev = zs[li - 1]
                new_delta = [0.0] * len(a_prev)
                for i in range(len(a_prev)):
                    s = sum(self.W[li][o][i] * delta[o] for o in range(len(delta)))
                    new_delta[i] = s * (1.0 if z_prev[i] > 0 else 0.0)  # relu'
                delta = new_delta
        return gW, gb

    def fit(self, X, Y, epochs=400, lr=0.01, verbose=False):
        b1, b2, eps = 0.9, 0.999, 1e-8
        n = len(X)
        for ep in range(epochs):
            # 풀배치 누적 평균 그래디언트
            aW = [[[0.0] * len(r) for r in layer] for layer in self.W]
            ab = [[0.0] * len(layer) for layer in self.b]
            for x, y in zip(X, Y):
                gW, gb = self._grads(x, y)
                for li in range(len(self.W)):
                    for o in range(len(self.b[li])):
                        ab[li][o] += gb[li][o]
                        arow, grow = aW[li][o], gW[li][o]
                        for i in range(len(grow)):
                            arow[i] += grow[i]
            self.t += 1
            for li in range(len(self.W)):
                for o in range(len(self.b[li])):
                    # bias
                    g = ab[li][o] / n
                    self.mb[li][o] = b1 * self.mb[li][o] + (1 - b1) * g
                    self.vb[li][o] = b2 * self.vb[li][o] + (1 - b2) * g * g
                    mh = self.mb[li][o] / (1 - b1 ** self.t)
                    vh = self.vb[li][o] / (1 - b2 ** self.t)
                    self.b[li][o] -= lr * mh / (math.sqrt(vh) + eps)
                    # weights
                    Wrow, mrow, vrow, arow = self.W[li][o], self.mW[li][o], self.vW[li][o], aW[li][o]
                    for i in range(len(Wrow)):
                        g = arow[i] / n
                        mrow[i] = b1 * mrow[i] + (1 - b1) * g
                        vrow[i] = b2 * vrow[i] + (1 - b2) * g * g
                        mh = mrow[i] / (1 - b1 ** self.t)
                        vh = vrow[i] / (1 - b2 ** self.t)
                        Wrow[i] -= lr * mh / (math.sqrt(vh) + eps)
            if verbose and (ep + 1) % max(1, epochs // 5) == 0:
                print(f"  epoch {ep+1}/{epochs}  loss={mse(self, X, Y):.5f}")

    def to_dict(self):
        return {"sizes": self.sizes, "W": self.W, "b": self.b}

    @classmethod
    def from_dict(cls, d):
        m = cls(sizes=d["sizes"])
        m.W = d["W"]
        m.b = d["b"]
        return m


def mse(model, X, Y):
    tot = 0.0
    for x, y in zip(X, Y):
        p = model.predict(x)
        tot += sum((p[o] - y[o]) ** 2 for o in range(len(y))) / len(y)
    return tot / len(X)


# ─────────────────────────────────────────────────────────────
# 합성 데이터 (self-test) — 알려진 정답 함수: 빈 쪽 위로
# ─────────────────────────────────────────────────────────────
def synth_sample(rng):
    fx = 0.2 + rng.random() * 0.6
    fy = 0.3 + rng.random() * 0.5
    fw = 0.08 + rng.random() * 0.18
    fh = fw * 1.2
    chars = [{"name": "S", "face": {"x": fx, "y": fy, "w": fw, "h": fh},
              "torso": {"x": fx, "y": _clamp(fy + 0.4, 0, 1), "w": fw * 2, "h": 0.4}}]
    # 타 인물 0~2명 무작위 → occGrid 채움
    for k in range(rng.randint(0, 2)):
        ox = rng.random()
        chars.append({"name": f"O{k}", "face": {"x": ox, "y": rng.random(), "w": 0.12, "h": 0.15},
                      "torso": {"x": ox, "y": _clamp(rng.random() + 0.3, 0, 1), "w": 0.2, "h": 0.4}})
    panel = {"imageW": 1024, "imageH": 1024, "characters": chars}
    bubble = {"speaker": "S", "type": "speech", "w": 0.18, "h": 0.1}
    feats = extract_features(panel, bubble)
    occ = occ_grid(panel, bubble)
    left = sum(occ[i] for i in range(16) if i % 4 < 2)
    right = sum(occ[i] for i in range(16) if i % 4 >= 2)
    lx = _clamp(fx + (-0.16 if left > right else 0.16), 0.1, 0.9)
    ly = _clamp(fy - 0.22, 0.1, 0.9)
    return feats, [lx, ly]


def cmd_selftest(args):
    rng = random.Random(42)
    val = [synth_sample(rng) for _ in range(40)]
    vX, vY = [s[0] for s in val], [s[1] for s in val]
    sizes = [int(n) for n in args.sizes.split(",")]
    results = []
    for n in sizes:
        rng2 = random.Random(100 + n)
        tr = [synth_sample(rng2) for _ in range(n)]
        m = MLP()
        m.fit([s[0] for s in tr], [s[1] for s in tr], epochs=args.epochs, lr=args.lr)
        e = mse(m, vX, vY)
        results.append((n, e))
        print(f"샘플 {n:4d} → val MSE {e:.5f}")
    dropped = results[0][1] > results[-1][1]
    print(f"\n결과: 샘플 늘수록 MSE {'감소 ✅ (학습 동작)' if dropped else '미감소 ⚠'}")
    print(f"최종 MSE {results[-1][1]:.5f} (<0.02 면 신호 학습 성공)")
    return 0 if (dropped and results[-1][1] < 0.02) else 1


# ─────────────────────────────────────────────────────────────
# 데이터/패널 입출력
# ─────────────────────────────────────────────────────────────
def load_dataset(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    X = [d["features"] for d in data]
    Y = [[d["label"]["x"], d["label"]["y"]] for d in data]
    return X, Y, data


def load_panels(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    panels = j["panels"] if isinstance(j, dict) and "panels" in j else j
    return {p["panelId"]: p for p in panels}


def cmd_train(args):
    X, Y, data = load_dataset(args.data)
    if len(X) < 2:
        print("⚠ 샘플 2개 미만 — 더 라벨링 필요")
        return 1
    nv = max(1, len(X) // 5) if len(X) >= 8 else 0
    tX, tY = X[nv:], Y[nv:]
    m = MLP()
    print(f"학습 시작 · 샘플 {len(tX)} (val {nv}) · epochs {args.epochs}")
    m.fit(tX, tY, epochs=args.epochs, lr=args.lr, verbose=True)
    print(f"train MSE {mse(m, tX, tY):.5f}")
    if nv:
        print(f"val   MSE {mse(m, X[:nv], Y[:nv]):.5f}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(m.to_dict(), f)
    print(f"모델 저장 → {args.out}")
    return 0


def cmd_eval(args):
    X, Y, _ = load_dataset(args.data)
    with open(args.model, encoding="utf-8") as f:
        m = MLP.from_dict(json.load(f))
    print(f"MSE {mse(m, X, Y):.5f} · 샘플 {len(X)}")
    return 0


def cmd_predict(args):
    panels = load_panels(args.panels)
    with open(args.model, encoding="utf-8") as f:
        m = MLP.from_dict(json.load(f))
    ids = [args.panel_id] if args.panel_id else list(panels.keys())
    out = {}
    for pid in ids:
        panel = panels[pid]
        out[pid] = []
        for b in panel.get("bubbles", []):
            feats = extract_features(panel, b)
            p = m.predict(feats)
            p = {"x": _clamp(p[0], b["w"] / 2, 1 - b["w"] / 2),
                 "y": _clamp(p[1], b["h"] / 2, 1 - b["h"] / 2)}
            h = heuristic_place(panel, b)
            out[pid].append({"bubbleId": b["id"], "model": p, "heuristic": h})
            print(f"{pid} {b['id']:<8} model=({p['x']:.3f},{p['y']:.3f})  heuristic=({h['x']:.3f},{h['y']:.3f})")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"예측 저장 → {args.out}")
    return 0


def cmd_features(args):
    panels = load_panels(args.panels)
    panel = panels[args.panel_id]
    for b in panel.get("bubbles", []):
        v = extract_features(panel, b)
        print(f"{args.panel_id} {b['id']} len={len(v)} {['%.3f' % x for x in v]}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="말풍선 배치 학습 모델 (순수 Python)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("selftest")
    s.add_argument("--sizes", default="10,30,80")
    s.add_argument("--epochs", type=int, default=400)
    s.add_argument("--lr", type=float, default=0.01)
    s.set_defaults(fn=cmd_selftest)

    s = sub.add_parser("train")
    s.add_argument("--data", required=True)
    s.add_argument("--out", default="model.json")
    s.add_argument("--epochs", type=int, default=600)
    s.add_argument("--lr", type=float, default=0.01)
    s.set_defaults(fn=cmd_train)

    s = sub.add_parser("eval")
    s.add_argument("--data", required=True)
    s.add_argument("--model", required=True)
    s.set_defaults(fn=cmd_eval)

    s = sub.add_parser("predict")
    s.add_argument("--panels", required=True)
    s.add_argument("--model", required=True)
    s.add_argument("--panel-id", default=None)
    s.add_argument("--out", default=None)
    s.set_defaults(fn=cmd_predict)

    s = sub.add_parser("features")
    s.add_argument("--panels", required=True)
    s.add_argument("--panel-id", required=True)
    s.set_defaults(fn=cmd_features)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
