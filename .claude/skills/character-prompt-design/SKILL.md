---
name: character-prompt-design
description: 웹툰 캐릭터의 비주얼 설정과 AI 이미지 생성용 프롬프트를 작성한다. 인물별 시그니처 디스크립터(불변 외형)와 씬별 가변 프롬프트(표정·포즈·조명)를 분리 관리. "캐릭터 프롬프트", "이미지 생성용 묘사", "인물 비주얼 설정", "이번 화 캐릭터 프롬프트" 요청에 트리거. 일러스트 그리기 자체가 아니라, Stable Diffusion/Midjourney 등에 투입할 텍스트 프롬프트를 만드는 작업.
---

# 캐릭터 프롬프트 설계 스킬

## 언제 사용

- 신규 에피소드의 씬별 이미지 생성 프롬프트를 작성할 때
- 새 인물 등장 시 시그니처 디스크립터를 character-bible.md에 추가할 때
- 사용자가 "스타일 바꿔줘", "더 어두운 톤으로" 같은 전역 변경 요청을 했을 때

## 핵심 분리 원칙

프롬프트는 **3개 블록의 합**이다:

1. **Style Prefix** (전 화 공통): 아트 스타일·렌더링 키워드
2. **Signature** (인물별 불변): 헤어컬러·눈동자·체형·시그니처 의상
3. **Scene-variable** (씬마다): 표정·포즈·조명·카메라·배경

**Why this matters:** 시그니처가 매 씬마다 흔들리면 같은 인물이 다른 사람처럼 보인다. 분리해 두면 일관성은 시그니처가, 다양성은 씬-가변 블록이 담당.

## 작업 순서

### 1. 컨텍스트 로딩
- `_workspace/style-guide.md`에서 아트 스타일 키워드 (예: "Korean webtoon style, cell-shaded, vivid color")
- `_workspace/character-bible.md`에서 기존 인물 시그니처
- `_workspace/episode-{NN}/01_story.md`에서 씬별 등장 인물·장소·감정

### 2. 신규 인물 처리
스토리에 character-bible에 없는 인물이 있으면:
- 시그니처 디스크립터 초안 작성 (사용자 외형 묘사가 있으면 반영, 없으면 합리적 추정)
- `character-bible.md`에 추가 제안 (실제 추가는 사용자 승인 후 또는 자동 — 컨벤션에 따름)

### 3. Negative Prompt 표준화
모든 프롬프트 공통 negative:
- 손가락/얼굴 깨짐: `extra fingers, deformed face, asymmetric eyes`
- 노이즈: `blurry, low quality, watermark, text, signature`

씬 특이값(예: 특정 사물이 배경에 절대 나오면 안 됨)은 씬별로 추가.

### 4. 씬별 프롬프트 작성
스토리의 모든 씬에 대해 1:1로 프롬프트 생성. 씬에 인물이 등장하지 않으면 (예: 배경만) 풍경 프롬프트로 작성.

각 프롬프트 형식:
```
{style prefix}, {signature 인물1}, {signature 인물2}, {장소}, {표정/감정}, {포즈}, {카메라 앵글}, {조명}
```

### 5. 산출

`_workspace/episode-{NN}/02_character_prompts.md`에 저장. 형식은 에이전트 정의의 출력 템플릿을 따른다.

## 하지 말 것

- **씬별 프롬프트에 시그니처 복붙 금지** → 시그니처는 별도 블록으로 두고, 씬별에는 "{signature 인물1}" 참조만 (가독성·유지보수)
- **부정 프롬프트 누락 금지** → 빈 negative는 거의 항상 손가락 사고로 이어짐
- **스토리·레이아웃 결정 금지** → 인물이 어디서 뭐 하는지는 스토리·레이아웃이 결정. 여기는 시각화만.

## 후속 작업

- `02_character_prompts.md` 존재 시: 변경된 씬만 재작성, 시그니처는 보존
- "스타일 바꿔줘" → style prefix만 갈아끼우고 씬별은 그대로
- character-bible.md 변경 시 → 모든 에피소드 프롬프트의 signature가 자동으로 최신 버전이어야 하므로, 본문에서 시그니처는 "참조" 형태로 작성
