---
name: webtoon-episode-production
description: 웹툰 에피소드 한 화를 처음부터 끝까지 제작하는 오케스트레이터. 스토리·캐릭터 프롬프트·패널 레이아웃·대사 4개 에이전트를 팀으로 묶어 상호 리뷰하며 한 에피소드를 완성한다. "에피소드 X화 만들어줘", "새 화 기획", "이번 화 컨티", "에피소드 제작 시작" 같은 신규 요청은 물론, "에피소드 X화 스토리만 다시", "캐릭터 프롬프트 업데이트", "대사 톤 바꿔줘", "이전 결과 기반으로 수정" 같은 후속 요청도 이 스킬로 처리. 단순 용어 질문/조언은 직접 응답.
---

# 웹툰 에피소드 제작 오케스트레이터

스토리 → (캐릭터 + 레이아웃) → 대사 → 교차 리뷰 → 최종 통합의 5단계로 한 에피소드를 완성한다.

**실행 모드:** 에이전트 팀 (4명 + 오케스트레이터)
- 모든 Agent 호출 시 `model: "opus"` 필수

## 팀 구성

| 에이전트 | 역할 |
|---------|------|
| `story-writer` | 씬 비트, 감정 곡선, 다음 화 훅 |
| `character-prompt-designer` | 시그니처 + 씬별 이미지 프롬프트 |
| `panel-layout-planner` | 페이지·패널·앵글·말풍선 자리 |
| `dialogue-editor` | 패널별 대사·내레이션·효과음 |

## 데이터 전달

- **태스크 기반**: `TaskCreate`/`TaskUpdate`로 작업 진행 추적
- **메시지 기반**: `SendMessage`로 팀원 간 피드백·요청
- **파일 기반**: `_workspace/episode-{NN}/0X_*.md`에 산출물 저장 (보존 — 사후 검증용)
- **최종 산출**: `episodes/episode-{NN}/EPISODE.md`에 통합본 출력

## Phase 0: 컨텍스트 확인

워크플로우 시작 시 가장 먼저:

1. `_workspace/episode-{NN}/`가 이미 존재하는가?
2. 사용자 요청 유형 판별:
   - **초기 실행**: `_workspace/episode-{NN}/` 미존재 → 전체 워크플로우 (Phase 1~5)
   - **부분 재실행**: 존재 + 사용자가 "X만 다시" 명시 → 해당 에이전트만 호출, 영향 받는 다운스트림에 SendMessage로 알림
   - **새 실행 (재시작)**: 존재 + 사용자가 새 입력 제공/명시적 재시작 → 기존을 `_workspace/episode-{NN}_prev_{timestamp}/`로 이동 후 전체 워크플로우
3. `_workspace/style-guide.md`·`series-bible.md`·`character-bible.md` 존재 확인. 없는 핵심 파일이 있으면 사용자에게 생성 여부 확인 (기본값으로 진행도 가능).
4. 에피소드 번호 미지정 시: 가장 최근 에피소드 + 1을 제안.

## Phase 1: 팀 구성

```
TeamCreate(
  name: "episode-{NN}-team",
  members: [story-writer, character-prompt-designer, panel-layout-planner, dialogue-editor]
)
```

각 멤버에게 컨텍스트 (에피소드 번호, 의도, 시리즈 위치) 공유.

## Phase 2: 스토리 작성 (순차)

```
TaskCreate(assignee: story-writer, task: "Episode {NN} 씬 비트 작성")
```

- story-writer가 `_workspace/episode-{NN}/01_story.md` 작성
- 완료 후 `character-prompt-designer`와 `panel-layout-planner`에게 "신규 인물/장소" 알림 메시지 발신

## Phase 3: 캐릭터 프롬프트 + 패널 레이아웃 (병렬)

두 에이전트가 동시에 `01_story.md`를 기반으로 병렬 작업:

```
TaskCreate(assignee: character-prompt-designer, task: "씬별 이미지 프롬프트 작성", depends_on: [01_story])
TaskCreate(assignee: panel-layout-planner, task: "페이지·패널 레이아웃 작성", depends_on: [01_story])
```

산출물:
- `_workspace/episode-{NN}/02_character_prompts.md`
- `_workspace/episode-{NN}/03_panel_layout.md`

**상호 보완:** 두 에이전트는 작업 중 SendMessage로 협의:
- `panel-layout-planner` → `character-prompt-designer`: "Page 5 풀-블리드 컷에 인물 시그니처 디테일 추가 프롬프트 필요"
- `character-prompt-designer` → `panel-layout-planner`: "이 인물 빨간 머리는 시선 집중점 — 앵글에 반영"

레이아웃 추산이 평균 페이지 수의 130%를 넘으면 `panel-layout-planner`가 `story-writer`에게 씬 분량 조정 요청 → 필요 시 Phase 2 재실행.

## Phase 4: 대사 작성

```
TaskCreate(assignee: dialogue-editor, task: "패널별 대사 작성", depends_on: [01_story, 02_character_prompts, 03_panel_layout])
```

산출물: `_workspace/episode-{NN}/04_dialogue.md`

작업 중 발견 사항:
- 인물 보이스가 스토리 비트와 모순 → `story-writer`에게 SendMessage, 합의 후 스토리 또는 대사 수정
- 패널 글자 수 권장치 30%+ 초과 빈발 → `panel-layout-planner`에게 말풍선 자리 확장 요청

## Phase 5: 교차 피어 리뷰 라운드

4명 모두에게 동시 발신:

```
SendMessage(to: 모든 멤버, message: "최종 4개 파일에 대해 톤·스타일 일관성 리뷰. 자신의 영역이 아닌 다른 산출물에서 발견한 불일치를 1~3개 보고")
```

각 멤버는 다른 멤버의 산출물을 검수하여:
- `_workspace/episode-{NN}/05_review_{agent}.md`에 발견 사항 작성

오케스트레이터(나)가 5개 리뷰 파일을 모아:
- **합의된 수정 사항** (2명 이상이 같은 문제 지적) → 즉시 해당 에이전트에 수정 요청
- **이견이 있는 수정 사항** → 사용자에게 결정 요청
- **사소한 개별 의견** → 산출물에 코멘트 형태로 보존, 강제 수정 안 함

## Phase 6: 최종 통합

오케스트레이터가 직접:
- `_workspace/episode-{NN}/`의 4개 파일을 통합하여 `episodes/episode-{NN}/EPISODE.md` 생성
- 페이지 단위 뷰: 페이지마다 [레이아웃 + 패널별 (캐릭터 프롬프트 + 대사)] 결합
- `_workspace/`는 삭제하지 않고 보존 (감사 추적)

## Phase 7: 사용자 피드백

완료 후 사용자에게:
- 결과물 위치 안내
- "수정/개선할 부분 있나요?" 질문
- 피드백 있으면 → 변경 유형에 따라 적절한 Phase로 재진입

## 에러 핸들링

| 상황 | 대응 |
|------|------|
| 에이전트 1회 실패 | 동일 작업 1회 재시도, 재실패 시 해당 산출물 누락 명시 후 다음 Phase 진행 |
| 시리즈 바이블 모순 | 모순을 사용자에게 보고, 멋대로 수정하지 않음 |
| 상충하는 피어 리뷰 의견 | 두 의견 모두 보존, 사용자 결정 요청 |
| `_workspace/` 권한 에러 | 사용자에게 디렉토리 생성 권한 요청 |
| 평균 페이지 수 200% 초과 | 자동 진행 중단, 사용자에게 분량 확인 |

## 테스트 시나리오

### 정상 흐름
**입력:** "에피소드 3화 만들어줘. 주인공 A가 B의 정체를 알게 되는 전환점 화. 분위기는 미스터리 → 충격."
**기대:**
- Phase 0: `_workspace/episode-03/` 미존재 → 초기 실행
- Phase 2: 8~12씬, 마지막 씬에 다음 화 훅
- Phase 3: 02/03 산출, 페이지 수 22 내외
- Phase 4: 04 산출, 침묵 패널 포함
- Phase 5: 리뷰 4개 파일, 합의 사항 자동 수정
- Phase 6: `episodes/episode-03/EPISODE.md` 통합본

### 에러 흐름 (부분 재실행)
**입력:** "에피소드 3화 대사 톤만 더 캐주얼하게 바꿔줘"
**기대:**
- Phase 0: `_workspace/episode-03/` 존재 → 부분 재실행 모드
- character-bible.md voice cue 업데이트 제안 → 사용자 승인
- `dialogue-editor`만 호출하여 `04_dialogue.md` 재작성 (전 패널 재패스)
- Phase 5 (피어 리뷰) 축약 실행: 다른 3명이 보이스 변경의 영향 검수만
- Phase 6: 통합본 재생성

## 산출 체크리스트

- [ ] `_workspace/episode-{NN}/01_story.md`
- [ ] `_workspace/episode-{NN}/02_character_prompts.md`
- [ ] `_workspace/episode-{NN}/03_panel_layout.md`
- [ ] `_workspace/episode-{NN}/04_dialogue.md`
- [ ] `_workspace/episode-{NN}/05_review_*.md` (피어 리뷰 4개)
- [ ] `episodes/episode-{NN}/EPISODE.md` (통합본)
- [ ] `character-bible.md` 신규 인물 반영
