# 웹툰 자동 생성 스크립트

OpenAI gpt-image-1 API로 캐릭터 시트 + 67 패널 이미지 자동 생성.

## 셋업 (한 번만)

```bash
# 1. webtoon 디렉토리에서
cd C:\Users\ssarm\another-work\webtoon

# 2. Python 가상환경 (선택)
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
# 또는: .venv\Scripts\activate.bat  # Windows CMD

# 3. 의존성 설치
pip install -r scripts/requirements.txt

# 4. .env 파일 생성 (키는 직접 채워넣기)
copy scripts\.env.example scripts\.env
# 그 다음 scripts\.env 파일을 열어서 OPENAI_API_KEY=... 줄에 실제 키 붙여넣기
```

## 실행 순서

### Step 1: 캐릭터 시트 5장

```bash
python scripts/generate_character_sheets.py
```

출력: `_workspace/character-sheets/`
- 01_kang_minho.png (강민호)
- 02_han_jaemin.png (한재민)
- 03_choi_taegyu.png (최태규)
- 04_yoon_soyul.png (윤소율)
- 05_park_jiho.png (박지호)

각 시트는 (정면 + 3/4 뷰 + 표정 3가지)가 한 이미지에 들어있음.

비용: 약 $0.2~0.85 (5장 × $0.04~0.17 품질에 따라)

**마음에 안 드는 캐릭터**: 해당 .png 삭제 후 같은 스크립트 재실행 (기존 파일은 건너뜀)

### Step 2: 67 패널 (Step 1 완료 후)

```bash
python scripts/generate_panels.py
```

(아직 미작성 — Step 1 결과 확인 후 작성 예정)

출력: `episodes/episode-01/images/`
- page-01-1-1.png, page-01-1-2.png, ... page-22-22-1.png

각 패널은 해당 등장 인물의 character sheet를 reference로 사용 → 일관성 유지.

비용: 약 $2.7~11 (67장 × $0.04~0.17)

## 안전

- **`.env`는 .gitignore에 포함** — 커밋 안 됨
- **키를 절대 코드에 직접 쓰지 마세요** — 환경변수만 사용
- **키 노출 시**: https://platform.openai.com/api-keys 에서 즉시 revoke

## 트러블슈팅

- `OPENAI_API_KEY가 설정되지 않았습니다` → `.env` 파일 확인
- `Insufficient quota` → billing 페이지에서 충전
- `Rate limit` → `CONCURRENCY=1`로 .env 조정
