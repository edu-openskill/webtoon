"""
67 패널 생성 스크립트
====================
1화 67 패널 이미지를 OpenAI gpt-image-1로 자동 생성.
_workspace/character-sheets/ 의 5장을 reference로 사용 → 캐릭터 일관성 유지.

실행:
    python scripts/generate_panels.py

옵션:
    python scripts/generate_panels.py --only 12.1,13.1,22.1    # 특정 패널만
    python scripts/generate_panels.py --skip-existing          # 기본 동작 (이미 있으면 건너뜀)
    python scripts/generate_panels.py --force                  # 모두 재생성

출력:
    episodes/episode-01/images/{panel_id}.png 67장
    storyboard.html 열면 자동으로 표시됨
"""

import os
import sys
import time
import base64
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ───── Setup ─────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(SCRIPT_DIR / ".env")

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY or "여기에" in API_KEY:
    sys.exit("❌ scripts/.env에 OPENAI_API_KEY 설정 필요")

MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1")
QUALITY = os.environ.get("QUALITY", "medium")
OUTPUT_DIR = PROJECT_ROOT / os.environ.get("OUTPUT_DIR", "episodes/episode-01/images")
SHEETS_DIR = PROJECT_ROOT / os.environ.get("CHARACTER_SHEETS_DIR", "_workspace/character-sheets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=API_KEY)

# ───── Character sheet mapping ───────────────────────────────
CHAR_SHEETS = {
    "강민호": SHEETS_DIR / "01_kang_minho.png",
    "한재민": SHEETS_DIR / "02_han_jaemin.png",
    "최태규": SHEETS_DIR / "03_choi_taegyu.png",
    "윤소율": SHEETS_DIR / "04_yoon_soyul.png",
    "박지호": SHEETS_DIR / "05_park_jiho.png",
}

# ───── Style + size mapping ──────────────────────────────────
STYLE = (
    "Korean webtoon style, cell-shaded, vivid color, soft lineart, "
    "clean modern composition, no text overlay, no watermark, no signature. "
    "Maintain exact character appearance from reference image(s). "
)

SIZE_MAP = {
    "wide": "1536x1024",
    "medium": "1024x1024",
    "close-up": "1024x1024",
    "full-bleed": "1024x1536",
}

# ───── Per-panel quality classification ─────────────────────
# LOW: 단순한 컷 — UI 화면, 손 close-up, silent atmospheric, 배경 establishing
# MEDIUM: 캐릭터 표정·연출이 중요한 컷 (기본 — .env의 QUALITY 사용)
# 시그니처 컷은 medium (필요시 --quality high로 override 가능)
LOW_QUALITY_PANELS = {
    # 도입 환경·UI
    "1.2",   # 노트북 화면 이메일
    "2.1",   # 강민호 뒷모습 로비 (silent)
    "2.2",   # 회의실 외부 복도 (빈 풍경)
    "4.2",   # 키보드 close-up
    # silent atmospheric close-ups
    "5.3",   # 강민호 커피 한 모금
    "6.1",   # 최태규 silent close-up
    "6.2",   # 커피 머그 내려놓는 손
    "6.4",   # 박지호 silent reaction
    "8.3",   # 박지호 시선 회피
    "9.2",   # 강민호 silent (10.2가 더 중요)
    "9.3",   # 강민호 손 + 화면 일부
    # UI·screen 컷
    "10.1",  # 깨진 화면
    "11.2",  # 노트북 닫는 손
    "14.2",  # 한재민 손
    # 잔여 reaction silent
    "15.1",  # 박지호 silent
    "15.2",  # 윤소율 silent
    "15.3",  # 최태규 silent
    "17.1",  # 박지호 멍 (회의 후)
    "17.2",  # 강민호 자리 (일상)
    "17.3",  # 강민호 silent (일상)
    # 자취방 UI·손
    "18.3",  # 프롬프트 입력 화면
    "19.1",  # 생성된 앱 화면
    "19.3",  # 손 close-up
    # 검색 UI
    "21.1",  # 검색창 타이핑
    "21.2",  # 자동완성
}

def get_quality_for_panel(panel_id, override=None):
    """Return quality tier for a panel. override > LOW classification > .env default."""
    if override:
        return override
    if panel_id in LOW_QUALITY_PANELS:
        return "low"
    return QUALITY  # .env default (medium)

# ───── Panel definitions (67 panels) ─────────────────────────
# Tuple: (id, characters_in_scene, scene_description, aspect)
PANELS = [
    # ─── Page 1 — 강민호 출근 ───
    ("1.1", ["강민호"], "Wide shot at a small wooden cafe table near window in the morning, this man sitting calmly with laptop open beside a black coffee mug, soft warm window light, urban cafe blurred", "wide"),
    ("1.2", [], "Extreme close-up on a laptop screen showing an email notification with Korean office announcement text, soft window light reflection, shallow focus", "close-up"),
    ("1.3", ["강민호"], "Medium close-up profile of this man with a faint quiet smile at corner of mouth, gaze drifting from laptop to window, morning warm light on his face", "medium"),
    # ─── Page 2 — 회의실 도착 ───
    ("2.1", ["강민호"], "Wide silent shot of this man from behind walking through a modern minimalist office lobby, laptop bag over shoulder, large glass windows with city skyline, cool morning light", "wide"),
    ("2.2", [], "Modern office corridor with a Meeting Room A sign on the door, wall clock showing 9:55, soft cool fluorescent light, empty corridor, slight perspective angle", "medium"),
    ("2.3", ["한재민", "최태규", "윤소율", "박지호"], "Wide shot of a modern meeting room interior. The balding 50s man holding coffee mug seated at head of table, the 30 year old woman with iPad mid-table, the late-20s man with messy hair and round glasses seated nervously at far end, the mid-30s man with side-parted hair standing at projector setting up laptop, morning meeting atmosphere, soft cool lighting", "wide"),
    # ─── Page 3 — 4인 소개 + 강민호 입장 ───
    ("3.1", ["최태규"], "Close-up of this man looking toward projector with neutral business interest, holding ceramic coffee mug, side window light", "close-up"),
    ("3.2", ["윤소율"], "Close-up of this woman holding iPad slightly raised, eager curious expression, glasses catching light", "close-up"),
    ("3.3", ["박지호"], "Close-up of this man seated at far end of table, shoulders slightly tense, eyes flickering nervously, glasses reflecting light", "close-up"),
    ("3.4", ["한재민"], "Medium shot of this man standing beside projector, confident posture, hands on laptop, slight smile of anticipation", "medium"),
    ("3.5", ["강민호"], "Over-shoulder view from behind four seated office workers, this man entering through doorway with quiet calm presence, slight back-light from corridor, medium shot, neutral expression", "medium"),
    # ─── Page 4 — 시연 시작 ───
    ("4.1", ["한재민"], "Wide shot of this man standing at front of meeting room gesturing both hands open, confident presenter pose, projector screen behind blank, four others visible at table seated", "wide"),
    ("4.2", [], "Close-up of hands typing on laptop keyboard, screen showing prompt input box with Korean text being entered", "close-up"),
    ("4.3", ["한재민"], "Medium shot of this man watching projector screen with proud anticipation, screen showing code generating in real-time with cascading lines, slight gleam in eyes", "medium"),
    ("4.4", [], "Full-bleed extreme view of a completed marketing dashboard on projector screen, colorful charts and Korean UI, professional clean design, slight glow effect", "full-bleed"),
    # ─── Page 5 — 술렁임 ───
    ("5.1", ["최태규", "윤소율", "박지호", "강민호"], "Wide meeting room shot, four characters reacting simultaneously: the balding 50s man mouth slightly open in surprise, the 30 year old woman with iPad sitting up straighter with raised eyebrows, the late-20s man with round glasses eyes wide jaw slack, the late-30s lean man calm coffee unchanged, atmospheric energy mixed with one stillness, cool office lighting with warm screen glow", "wide"),
    ("5.2", ["한재민"], "Medium shot of this man with satisfied smile, one hand gesturing at the dashboard on screen, confident posture, warm screen glow on his side", "medium"),
    ("5.3", ["강민호"], "Close-up profile of this man slowly sipping black coffee from mug, eyes on screen with utterly neutral focus, surrounding murmur shown by subtle motion blur of others in background", "close-up"),
    # ─── Page 6 — 최태규 반응 ───
    ("6.1", ["최태규"], "Close-up portrait of this man staring intently at projector screen, mind calculating behind tired sharp eyes, slight furrow of brow, warm window light from side", "close-up"),
    ("6.2", [], "Close-up of a man's hand slowly setting down a ceramic coffee mug on conference table, deliberate motion, mug surface details, shallow depth of field", "close-up"),
    ("6.3", ["최태규"], "Full-bleed close-up portrait of this man, mouth half-open mid-sentence trailing off, calculating expression visible, eyes elsewhere as if seeing budget numbers", "full-bleed"),
    ("6.4", ["박지호"], "Reaction shot of this man, back slightly stiffening, faint sweat at temple, eyes widening behind round glasses, mouth pressed thin, profile to three-quarter view, slightly desaturated tone", "close-up"),
    # ─── Page 7 — 윤소율-한재민 동맹 ───
    ("7.1", ["윤소율"], "Medium shot of this woman leaning forward in chair holding iPad up showing design mockups, animated excited expression with raised eyebrows, hand gesture mid-air, glasses catching light, warm energetic illumination", "medium"),
    ("7.2", ["윤소율", "한재민"], "Two-shot composition: the woman half-turned with eager expression, the man half-turned toward her with enthusiastic agreement, both hands open in welcoming gesture, warm collaborative atmosphere", "medium"),
    ("7.3", ["윤소율", "한재민", "박지호"], "Wide partial shot of meeting room. The woman and the mid-30s man in animated quick exchange foreground with hand gestures, the late-20s man with round glasses visible at edge with darkening expression slowly fading from frame focus", "wide"),
    # ─── Page 8 — 박지호 자기부정 ───
    ("8.1", ["박지호"], "Close-up of this man forcing an awkward small smile that doesn't reach his eyes, one hand scratching back of neck nervously, looking at screen then away, slightly hunched posture, conflicted micro-expression, cool clinical lighting", "close-up"),
    ("8.2", ["한재민"], "Medium shot of this man with casual reassuring gesture with one hand toward off-screen, friendly but slightly dismissive smile, no big deal body language", "medium"),
    ("8.3", ["박지호"], "Close-up of this man, corner of mouth twitching faintly, gaze escaping to laptop screen, slight isolation despite being in group, soft shadow on half of face", "close-up"),
    # ─── Page 9 — 강민호 침묵 시작 ───
    ("9.1", ["강민호", "한재민", "최태규", "윤소율", "박지호"], "Wide meeting room shot, four characters' gazes converging toward the late-30s lean man at one side of the table, who is still focused on his own laptop, quiet anticipation atmosphere, no movement", "wide"),
    ("9.2", ["강민호"], "Close-up of this man with own laptop open in front, screen reflected faintly in his calm eyes, completely neutral expression, sipping black coffee", "close-up"),
    ("9.3", [], "Close-up of hands on laptop keyboard with brief pause, partial view of laptop screen showing a number input field with absurdly long value entered, mechanical wristwatch visible", "close-up"),
    # ─── Page 10 — 침묵 절정 + 한재민 어색 ───
    ("10.1", [], "Close-up of a laptop or projector screen showing a marketing dashboard with one chart visibly broken or showing error message, subtle glitch artifact, sharp focus", "close-up"),
    ("10.2", ["강민호"], "Close-up of this man completely expressionless gazing at screen, calm steady eyes, hint of inner observation, perfectly still", "close-up"),
    ("10.3", ["한재민"], "Medium shot of this man with awkward forced smile, one hand adjusting collar of dress shirt nervously, smartwatch visible, confidence cracking subtly, slightly flatter lighting", "medium"),
    # ─── Page 11 — 정적 freeze ───
    ("11.1", ["강민호", "한재민", "최태규", "윤소율", "박지호"], "Wide meeting room shot, all five characters frozen in their positions, the lean man focused on laptop, others all watching him intently, complete silence atmosphere, long shadows from windows, slightly desaturated, hold-breath moment", "wide"),
    ("11.2", [], "Extreme close-up of a hand slowly closing a laptop lid, mechanical wristwatch with worn leather strap visible, deliberate calm motion, table surface and coffee mug at edge of frame, soft cinematic lighting", "close-up"),
    # ─── Page 12 ⚡ 강민호 첫 질문 ───
    ("12.1", ["강민호"], "Full-bleed medium close-up of this man looking directly at someone off-screen, mouth opening to speak with utter calm, eyes steady not threatening but undeniable, slight side lighting creating subtle shadow on half of face, vertical composition for webtoon scroll, pivotal cinematic panel", "full-bleed"),
    ("12.2", ["한재민"], "Reaction shot of this man, confident smile faltering, mouth slightly open mid-word that trailed off, hand frozen mid-gesture, eyes searching for answer, soft sweat sheen on forehead, lighting suddenly flat", "medium"),
    # ─── Page 13 ⚡⚡ 시리즈 시그니처 ───
    ("13.1", ["강민호", "한재민", "최태규", "윤소율", "박지호"], "Full-bleed medium shot of this lean late-30s man from slight low angle making him quietly authoritative, laptop closed in front, coffee mug to side, calm direct gaze, mouth in mid-question, the whole meeting room background blurred but visible with four other Korean office workers turned to him in silence, pivotal cinematic composition, this is the most important panel of the episode", "full-bleed"),
    # ─── Page 14 — overhead freeze ───
    ("14.1", ["강민호", "한재민", "최태규", "윤소율", "박지호"], "Full-bleed meeting room overhead wide shot from above, all five Korean office workers frozen in their positions, complete silence atmosphere, long shadows on table from windows, slightly desaturated color grading, like a painting, hold-the-breath moment", "full-bleed"),
    ("14.2", [], "Close-up of a hand frozen near a microphone or laser pointer on conference table, fingers slightly trembling, looking for an answer that won't come, sharp focus", "close-up"),
    # ─── Page 15 — 잔여 반응 ───
    ("15.1", ["박지호"], "Close-up of this man, eyes flickering between distant point and own hands, processing a question's weight, glasses subtly reflecting screen glow", "close-up"),
    ("15.2", ["윤소율"], "Close-up of this woman, the corner of her excited smile slightly stiffening, iPad still in hand but lower than before, brief moment of doubt crossing her face", "close-up"),
    ("15.3", ["최태규"], "Close-up of this man gazing steadily across the table, business mind weighing the question, no expression change but visible mental processing", "close-up"),
    # ─── Page 16 — 회의 종료 ───
    ("16.1", ["최태규"], "Medium shot of this man standing up from chair gathering papers, neutral business-as-usual expression, no longer looking at projector screen, casual concluding gesture, restored normal office lighting", "medium"),
    ("16.2", ["한재민", "윤소율", "박지호", "강민호"], "Wide shot of meeting room as people start to disperse: the mid-30s man closing laptop with hint of awkwardness, the 30 year old woman packing iPad, the late-20s man with round glasses still slow to move, the lean late-30s man already standing quietly", "wide"),
    ("16.3", ["윤소율", "한재민"], "Two-shot of this woman and this man walking together in modern office corridor with animated conversation, hand gestures, both still excited and energized, glass walls and indoor plants visible, warm corridor lighting", "wide"),
    # ─── Page 17 — 잔여 ───
    ("17.1", ["박지호"], "Medium shot of this man seated alone at his open-office desk, monitor turned off, hands in lap, staring blankly into middle distance, other employees blurred in background, isolation in workplace, slightly cool lighting", "medium"),
    ("17.2", ["강민호"], "Medium-wide shot of this man seated at his desk in quiet corner of office, opening laptop calmly, coffee mug placed beside, no expression change from meeting, back to work as usual", "wide"),
    ("17.3", ["강민호"], "Close-up of this man taking a sip of black coffee, eyes calm focused on his own work", "close-up"),
    # ─── Page 18 — 자취방 도입 ───
    ("18.1", [], "Wide silent establishing shot of a small modest Korean studio apartment interior at night, single bed with rumpled covers, low desk with laptop, small fridge, empty instant noodle cup, code conference posters on wall, only desk lamp providing warm yellow light, rest of room in deep shadow", "wide"),
    ("18.2", ["박지호"], "Medium shot of this man seated cross-legged on floor at low desk, no longer wearing hoodie hood, glasses reflecting laptop screen light, intense focused expression typing prompt, half-eaten convenience store dinner beside him, only warm desk lamp lighting", "medium"),
    ("18.3", [], "Close-up of a laptop screen showing a prompt being typed slowly in Korean about marketing dashboard, soft yellow lamp glow", "close-up"),
    # ─── Page 19 — 비슷한 앱 생성 ───
    ("19.1", [], "Close-up of laptop screen showing newly generated marketing dashboard application running successfully, similar to a corporate demo, charts and Korean UI, screen glow lighting an off-screen face from below", "close-up"),
    ("19.2", ["박지호"], "Close-up of this man, slack-jawed expression as he watches the screen, slight sweat sheen, warm lamp creating soft shadow on half his face, lonely contemplation", "close-up"),
    ("19.3", [], "Close-up of a fingertip on a computer mouse frozen in place, screen still showing the working dashboard in background, no celebration, just stillness", "close-up"),
    # ─── Page 20 — 강민호 회상 ───
    ("20.1", ["강민호"], "Ghostly memory flashback visual of this man from earlier, semi-transparent overlay in cool blue monochromatic tint, his calm face superimposed, suggesting a question haunting", "medium"),
    ("20.2", ["박지호"], "Close-up of this man, lips barely moving as he echoes a question to himself, eyes searching, the lamp glow now feeling cold despite its warmth, isolation deepening", "close-up"),
    # ─── Page 21 — 검색 ───
    ("21.1", [], "Close-up of a laptop screen showing a Korean search engine homepage, search query being typed slowly letter by letter into search bar, cursor still blinking", "close-up"),
    ("21.2", [], "Close-up of a search bar with autocomplete dropdown appearing, Korean search suggestions highlighted by cursor hover, multiple other suggestions visible below it", "close-up"),
    # ─── Page 22 ⚡⚡ 다음 화 훅 ───
    ("22.1", [], "Full-bleed extreme close-up on a laptop screen showing a Korean search engine results page, top result blog post title clearly visible in Korean Hangul characters reading 당신의 서비스 새벽 3시에 누가 받습니까, cursor hovering over the link, soft focus suggesting moment of decision, dramatic chiaroscuro lighting with screen as only light source", "full-bleed"),
]

# ───── Generation function ───────────────────────────────────
def generate_panel(panel, force=False, quality_override=None):
    panel_id, characters, scene, aspect = panel
    out_path = OUTPUT_DIR / f"{panel_id}.png"

    if out_path.exists() and not force:
        return "skip", None

    full_prompt = STYLE + scene
    size = SIZE_MAP.get(aspect, "1024x1024")
    quality = get_quality_for_panel(panel_id, override=quality_override)

    try:
        if characters:
            available = [CHAR_SHEETS[c] for c in characters if CHAR_SHEETS[c].exists()]
            if not available:
                # fallback to text-only
                result = client.images.generate(
                    model=MODEL, prompt=full_prompt, size=size, quality=quality, n=1
                )
            else:
                # gpt-image-1 supports multi-image reference via images.edit
                image_files = [open(p, "rb") for p in available]
                try:
                    result = client.images.edit(
                        model=MODEL,
                        image=image_files,
                        prompt=full_prompt,
                        size=size,
                        quality=quality,
                        n=1,
                    )
                finally:
                    for f in image_files:
                        f.close()
        else:
            result = client.images.generate(
                model=MODEL, prompt=full_prompt, size=size, quality=quality, n=1
            )

        b64 = result.data[0].b64_json
        out_path.write_bytes(base64.b64decode(b64))
        return "ok", quality
    except Exception as e:
        return f"error: {e}", quality


# ───── Main ──────────────────────────────────────────────────
def estimate_cost(targets, quality_override=None):
    """Rough cost estimate by quality tier (gpt-image-1 list price 기준)."""
    # 대략적 단가 (size별 가중치 평균 — 1024x1024 기준)
    PRICES = {"low": 0.011, "medium": 0.042, "high": 0.167}
    total = 0
    by_tier = {"low": 0, "medium": 0, "high": 0}
    for panel in targets:
        q = get_quality_for_panel(panel[0], override=quality_override)
        by_tier[q] = by_tier.get(q, 0) + 1
        total += PRICES.get(q, 0.042)
    return total, by_tier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="comma-separated panel ids (e.g., 12.1,13.1)")
    parser.add_argument("--force", action="store_true", help="regenerate even if exists")
    parser.add_argument("--quality", choices=["low", "medium", "high"],
                        help="모든 패널에 동일 품질 강제 (기본: low/medium 자동 분기)")
    args = parser.parse_args()

    targets = PANELS
    if args.only:
        ids = set(args.only.split(","))
        targets = [p for p in PANELS if p[0] in ids]
        if not targets:
            sys.exit(f"❌ --only로 지정한 패널 매칭 없음: {ids}")

    # check character sheets
    missing = [k for k, p in CHAR_SHEETS.items() if not p.exists()]
    if missing:
        sys.exit(f"❌ 캐릭터 시트 없음: {missing}\n   먼저 generate_character_sheets.py 실행")

    # 비용·품질 분포 사전 표시
    est_total, by_tier = estimate_cost(targets, quality_override=args.quality)
    print(f"=== 패널 생성 ({len(targets)}개) ===")
    print(f"모델: {MODEL}")
    if args.quality:
        print(f"품질: {args.quality} (강제 override)")
    else:
        print(f"품질 자동 분기: low={by_tier.get('low',0)}장 · medium={by_tier.get('medium',0)}장 · high={by_tier.get('high',0)}장")
    print(f"예상 비용: ~${est_total:.2f}")
    print(f"출력: {OUTPUT_DIR}\n")

    t0 = time.time()
    ok = skip = err = 0
    failures = []

    for i, panel in enumerate(targets, 1):
        panel_id = panel[0]
        chars = ", ".join(panel[1]) or "(no chars)"
        q = get_quality_for_panel(panel_id, override=args.quality)
        prefix = f"[{i:2d}/{len(targets)}] {panel_id:<6} [{q:<6}] ({chars[:30]:<30})"
        print(prefix, end=" ", flush=True)

        status, _ = generate_panel(panel, force=args.force, quality_override=args.quality)
        if status == "ok":
            print("✅")
            ok += 1
        elif status == "skip":
            print("⏭️")
            skip += 1
        else:
            print(f"❌  {status}")
            err += 1
            failures.append((panel_id, status))

    elapsed = time.time() - t0
    print(f"\n=== 완료 ({elapsed/60:.1f}분) ===")
    print(f"생성: {ok}  건너뜀: {skip}  실패: {err}")

    if failures:
        print(f"\n실패한 패널 ({len(failures)}개):")
        for pid, msg in failures:
            print(f"  - {pid}: {msg}")
        print(f"\n재시도: python scripts/generate_panels.py --only {','.join(p for p,_ in failures)}")

    if ok > 0:
        print(f"\n다음 단계:")
        print(f"  브라우저에서 열기: episodes/episode-01/storyboard.html")
        print(f"  생성된 이미지가 자동으로 표시됩니다.")


if __name__ == "__main__":
    main()
