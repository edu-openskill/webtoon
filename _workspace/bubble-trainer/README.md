# 말풍선 배치 학습기 (Bubble Placement Trainer)

> "얼굴 근처가 좋다"는 단 하나의 근거로 일단 배치 → **사람이 드래그로 베스트 위치 교정**
> → 그 교정값을 정답으로 작은 신경망이 **학습** → 연습이 쌓이면 모델이 **직접 배치**.

이미지 생성(OpenAI)과 무관한 독립 도구다. **torch·numpy·인터넷·CDN 전부 불필요** —
모델은 순수 Python 표준 라이브러리로 샌드박스/로컬 CLI에서 바로 돈다.

## 구성

| 파일 | 역할 |
|------|------|
| `bubble_model.py` | **모델(CLI)** — 순수 Python MLP. train / predict / eval / selftest |
| `index.html` | **라벨러(오프라인 브라우저)** — 이미지+박스 위 말풍선 드래그 교정 → `dataset.json` |
| `panels.sample.json` | 시드 패널 메타데이터(얼굴/몸통 박스·말풍선). 03_panel_layout.md 기반 |
| `dataset.sample.json` | 데모/회귀용 시드 학습셋(사람 교정 시뮬레이션) |
| 스키마 | `.claude/skills/panel-layout-planning/references/storyboard-data-spec.md` |

`model.json` · `predictions.json` · `dataset.json` 은 실행 산출물(gitignore).

## 빠른 시작

### 1) 모델이 학습되는지부터 확인 (입력 불필요)
```bash
python3 bubble_model.py selftest
# 샘플 10→30→80 늘수록 val MSE 감소 = 학습 동작
```

### 2) 라벨링 (사람이 베스트 위치 교정)
```bash
npx http-server _workspace/bubble-trainer -p 8080   # 또는 그냥 index.html 열기
```
- 패널 선택 → "휴리스틱 배치" → 말풍선을 **드래그**해 베스트 위치로 → "교정 위치 저장"
- 샘플 사진(`샘플 1.png` / `샘플 22.jpg`) 또는 이미지 드롭으로 배경 교체, 박스는 그림에 맞게 보정
- "dataset.json 내보내기" → 이 폴더에 저장

### 3) 학습 → 예측
```bash
python3 bubble_model.py train  --data dataset.json --out model.json
python3 bubble_model.py predict --panels panels.sample.json --model model.json --out predictions.json
```

### 4) 루프 닫기 (active learning)
라벨러에서 "예측 불러오기"로 `predictions.json`을 띄워(노랑 테두리=모델) 어긋난 것만 다시
드래그 교정 → 저장 → 재학습. 연습할수록 예측이 교정 위치에 가까워진다.

## 피처 / 모델
- 입력 32차원(기하): 얼굴·몸통 박스, 말풍선 크기, 타입 one-hot, 종횡비, 타 인물 4×4 점유격자.
  인코딩은 `bubble_model.py`(Python)와 `index.html`(JS)가 **완전히 동일**(라벨러 export가 CLI에서 그대로 학습됨).
- 모델: MLP `[32→32→16→2]`, relu/sigmoid, MSE + Adam. 라벨=말풍선 중심 `(x,y)`.
- 이미지 혼잡도(빈 배경) 피처는 선택 확장 — 스펙 §3 참조.

## 검증
```bash
python3 bubble_model.py selftest                                  # 학습 동작(MSE 감소)
python3 bubble_model.py train --data dataset.sample.json --out model.json   # 실제 패널 학습
python3 bubble_model.py predict --panels panels.sample.json --model model.json
```
라벨러 오프라인 동작 + JS/Python 피처 일치는 `index.html`을 http-server로 띄워 확인.
