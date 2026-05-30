"""
캐릭터 시트 생성 스크립트
========================
1화에 등장하는 5명 메인 캐릭터의 reference sheet 5장을 생성한다.
이 시트들이 이후 67 패널 작업의 reference로 사용됨.

실행:
    cd webtoon
    pip install -r scripts/requirements.txt
    cp scripts/.env.example scripts/.env  # 그 다음 키 채워넣기
    python scripts/generate_character_sheets.py

출력:
    _workspace/character-sheets/{character_name}.png 5장
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64

# ───── Setup ─────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(SCRIPT_DIR / ".env")

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY or API_KEY.startswith("sk-proj-여기에"):
    sys.exit("❌ scripts/.env에 OPENAI_API_KEY가 설정되지 않았습니다.\n"
             "   .env.example을 복사해서 .env로 만들고 키를 채워넣으세요.")

MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1")
QUALITY = os.environ.get("QUALITY", "medium")
SHEETS_DIR = PROJECT_ROOT / os.environ.get("CHARACTER_SHEETS_DIR", "_workspace/character-sheets")
SHEETS_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=API_KEY)

# ───── Character signatures (character-bible.md 추출) ─────────
COMMON_STYLE = (
    "Korean webtoon style character reference sheet, cell-shaded, vivid color, "
    "soft lineart, clean modern composition. "
    "Sheet layout: three views in one image — "
    "(1) front-facing full body on left, "
    "(2) three-quarter angle medium shot in center, "
    "(3) close-up portrait with three expression variations (neutral, mid-emotion, signature emotion) on right. "
    "Plain off-white background, no other characters, no text labels, "
    "consistent lighting and proportions across all views."
)

CHARACTERS = {
    "01_kang_minho": {
        "name": "강민호",
        "role": "시니어 풀스택 리드, 38세",
        "signature": (
            "Korean man late-30s, lean 178cm build, short black hair with slight gray streaks at the temples, "
            "faint thin mustache, calm steady gaze. "
            "Outfit: plain black crew-neck tee, dark indigo raw denim jeans, mechanical wristwatch with worn leather strap. "
            "Holds a black coffee mug in one of the views. "
            "Expression variations: (a) neutral observant, (b) quiet contemplation while sipping coffee, (c) the signature look of asking a calm pivotal question."
        ),
    },
    "02_han_jaemin": {
        "name": "한재민",
        "role": "마케팅 팀장, 35세",
        "signature": (
            "Korean man mid-30s, 175cm average athletic build, neat side-parted black hair styled with wax. "
            "Outfit: light gray button-up shirt tucked into slate slacks, brown leather belt, smartwatch on left wrist. "
            "Confident upright posture, animated hand gestures in two of the views. "
            "Expression variations: (a) confident proud smile, (b) enthusiastic gesturing with both hands open, (c) faltering smile as confidence cracks (mid-sentence trailing off)."
        ),
    },
    "03_choi_taegyu": {
        "name": "최태규",
        "role": "회사 사장, 50대 초반",
        "signature": (
            "Korean man early-50s, slightly round build 170cm, balding crown with short trimmed side hair, no glasses. "
            "Outfit: white dress shirt with top button open no tie, gray dress slacks, dress shoes. "
            "Tired but sharp eyes, often holding a ceramic coffee mug. "
            "Expression variations: (a) neutral business observation, (b) calculating mid-thought with slight furrow of brow, (c) mouth half-open mid-sentence trailing off (the signature calculator-brain moment)."
        ),
    },
    "04_yoon_soyul": {
        "name": "윤소율",
        "role": "UX/UI 디자이너, 30세",
        "signature": (
            "Korean woman age 30, slim 165cm, shoulder-length wavy light-brown hair, large round clear-frame glasses, "
            "small silver hoop earrings. "
            "Outfit: oversized cream knit sweater, wide-leg slate slacks, holding an iPad with stylus in one hand. "
            "Expression variations: (a) soft thoughtful neutral, (b) animated excited expression with raised eyebrows and open smile, (c) corner of smile slightly stiffening (brief moment of doubt)."
        ),
    },
    "05_park_jiho": {
        "name": "박지호",
        "role": "주니어 백엔드 개발자, 27세",
        "signature": (
            "Korean man late-20s, slim 168cm build, messy short black hair slightly tousled, round black-rim glasses, "
            "slightly slouched posture, laptop bag strap diagonal across chest. "
            "Outfit: oversized black hoodie over white tee, dark slacks. "
            "Expression variations: (a) nervous tense neutral, (b) awkward forced smile that doesn't reach the eyes (his signature self-deprecating laugh), (c) slack-jawed expression of inner shock with slight sweat sheen."
        ),
    },
}

# ───── Generation function ───────────────────────────────────
def generate_character_sheet(key: str, character: dict) -> Path | None:
    """Generate one character reference sheet and save to disk."""
    out_path = SHEETS_DIR / f"{key}.png"
    if out_path.exists():
        print(f"⏭️  {key}.png 이미 존재. 건너뜀. (재생성하려면 파일 삭제)")
        return out_path

    prompt = f"{COMMON_STYLE}\n\nCharacter: {character['name']} ({character['role']}).\n{character['signature']}"

    print(f"🎨  {key} ({character['name']}) 생성 중...")
    t0 = time.time()
    try:
        result = client.images.generate(
            model=MODEL,
            prompt=prompt,
            size="1536x1024",  # wide for character sheet (3 views side by side)
            quality=QUALITY,
            n=1,
        )
        elapsed = time.time() - t0

        # gpt-image-1 returns b64_json
        b64 = result.data[0].b64_json
        out_path.write_bytes(base64.b64decode(b64))
        print(f"✅  {key}.png 저장 ({elapsed:.1f}s)")
        return out_path
    except Exception as e:
        print(f"❌  {key} 실패: {e}")
        return None


# ───── Main ──────────────────────────────────────────────────
def main():
    print(f"=== 캐릭터 시트 생성 ===")
    print(f"모델: {MODEL} | 품질: {QUALITY}")
    print(f"출력: {SHEETS_DIR}")
    print(f"대상: {len(CHARACTERS)}명\n")

    results = []
    for key, character in CHARACTERS.items():
        path = generate_character_sheet(key, character)
        results.append((key, character["name"], path))

    print(f"\n=== 완료 ===")
    success = sum(1 for _, _, p in results if p)
    print(f"성공: {success}/{len(results)}")
    for key, name, path in results:
        status = "✅" if path else "❌"
        print(f"  {status} {name} ({key}): {path or 'failed'}")

    if success == len(results):
        print("\n다음 단계:")
        print(f"  1. {SHEETS_DIR}/ 의 5장을 눈으로 확인")
        print("  2. 마음에 안 드는 캐릭터는 해당 .png 삭제 후 이 스크립트 재실행")
        print("  3. 5장 다 만족스러우면: python scripts/generate_panels.py")
    else:
        print("\n⚠️  일부 실패. 실패한 것만 재시도하려면 다시 실행하세요 (기존 파일은 건너뜀).")


if __name__ == "__main__":
    main()
