# Episode 01 — Character Prompts

## Style Prefix (모든 프롬프트 공통)
`Korean webtoon style, cell-shaded, vivid color, soft lineart, clean modern composition`

## Negative Prompt (모든 프롬프트 공통)
`extra fingers, deformed face, asymmetric eyes, blurry, low quality, watermark, text, signature, distorted hands, missing limbs`

## Character Signatures (이번 화 등장 인물 — character-bible.md 참조)

### 강민호 (Kang Minho)
`Korean man late-30s, short black hair with slight gray streaks at temples, faint thin mustache, lean 178cm build, plain black crew-neck tee, dark indigo raw denim jeans, mechanical wristwatch with worn leather strap, calm steady gaze`
- Voice cue (시각 무게): 차분한 시선, 표정 변화 거의 없음, 커피 머그 자주

### 한재민 (Han Jaemin)
`Korean man mid-30s, neat side-parted black hair styled with wax, light gray button-up shirt tucked into slate slacks, brown leather belt, 175cm average athletic build, confident upright posture, smartwatch on left wrist`
- Voice cue (시각 무게): 손짓 많음, 눈빛 자신감, 항상 정면 카메라 자세

### 최태규 (Choi Taegyu, 사장)
`Korean man early-50s, balding crown with short trimmed side hair, no glasses, slightly round build 170cm, white dress shirt with top button open no tie, gray dress slacks, tired but sharp eyes, coffee mug in hand`
- Voice cue (시각 무게): 천천히 움직임, 안경은 없지만 멀리 보는 눈빛

### 윤소율 (Yoon Soyul)
`Korean woman age 30, shoulder-length wavy light-brown hair, large round clear-frame glasses, slim 165cm, oversized cream knit sweater, wide-leg slate slacks, iPad and stylus in hand, small silver hoop earrings`
- Voice cue (시각 무게): 표정 풍부, 손에 항상 아이패드

### 박지호 (Park Jiho)
`Korean man late-20s, messy short black hair slightly tousled, round black-rim glasses, slim 168cm build, oversized black hoodie over white tee, dark slacks, laptop bag strap diagonal across chest, slightly slouched posture`
- Voice cue (시각 무게): 자세 약간 구부정, 시선 자주 회피, 손이 노트북에 자주

## Scene Prompts

### Scene 1 — 강민호의 출근 (아침 카페 → 회사 로비)
- 등장: 강민호 (단독)
- **Prompt 1.A (카페)**: `{style prefix}, {강민호 signature}, sitting at small wooden cafe table near window, laptop open showing email interface, mug of black coffee beside, morning soft warm light streaming from window, urban cafe interior background blurred, medium close-up from slight side angle, calm contemplative expression`
- **Prompt 1.B (회사 로비)**: `{style prefix}, {강민호 signature}, walking through modern minimalist office lobby, laptop bag over shoulder, large glass windows behind showing city skyline, cool morning light, wide shot full-body, neutral expression, slightly elongated vertical composition for webtoon scroll`
- Negative: `{공통 negative} + crowded background, multiple people, dramatic shadows`

### Scene 2 — 회의실 입장 (회의실, 9:55, 5인 모임)
- 등장: 5인 모두 (강민호 가장 늦게)
- **Prompt 2.A (실내 와이드)**: `{style prefix}, modern bright meeting room with large white table and ergonomic chairs, projector screen at front, large windows with city view, cool fluorescent + natural light mix, wide establishing shot from doorway angle, 16:9 horizontal but composed for vertical scroll, no people yet`
- **Prompt 2.B (4인 먼저 있는 상태)**: `{style prefix}, meeting room interior, {최태규 signature} seated at head of table holding coffee mug, {윤소율 signature} seated mid-table holding iPad, {박지호 signature} seated at far end looking slightly nervous, {한재민 signature} standing at projector setting up laptop with confident posture, morning meeting atmosphere, soft cool lighting, wide shot capturing all four, slight diagonal angle showing seat hierarchy`
- **Prompt 2.C (강민호 입장 컷)**: `{style prefix}, {강민호 signature} entering through meeting room doorway with quiet calm presence, viewed from behind/over-shoulder of the four already seated, slight back-light from corridor outside, medium shot, neutral expression`
- Negative: `{공통 negative} + cluttered room, distracting decorations`

### Scene 3 — 한재민의 시연 시작 (회의실, 10:05)
- 등장: 한재민 (중심), 4인 (관찰자)
- **Prompt 3.A (시연 클로즈업)**: `{style prefix}, {한재민 signature} standing beside projector screen, gesturing at displayed code editor and browser preview window, slight smug confident smile, dynamic standing pose with one hand pointing, screen showing colorful marketing dashboard mockup with charts, low-angle shot emphasizing presenter dominance, warm bright lighting on him`
- **Prompt 3.B (회의실 술렁임 와이드)**: `{style prefix}, meeting room wide shot, {한재민 signature} at front gesturing at screen with dashboard, {최태규 signature} leaning forward intrigued, {윤소율 signature} sitting up straighter with iPad ready, {박지호 signature} eyes wide behind glasses, {강민호 signature} expression unchanged sipping coffee, atmospheric murmur energy, medium-wide angle, cool office lighting with warm screen glow`
- Negative: `{공통 negative} + chaotic background, too many UI details on screen`

### Scene 4 — 최태규의 첫 반응 (회의실, 10:10)
- 등장: 최태규 (중심), 박지호 (반응 cut)
- **Prompt 4.A (최태규 클로즈업)**: `{style prefix}, {최태규 signature} close-up portrait, slowly setting down coffee mug on table, mouth slightly open as if mid-sentence trailing off, calculating expression behind tired eyes, slightly furrowed brow, depth of field with blurred background, dramatic but subtle composition, warm afternoon-ish window light from side`
- **Prompt 4.B (박지호 반응 컷)**: `{style prefix}, {박지호 signature} reaction shot, back slightly stiffening, faint sweat on temple, eyes widening behind round glasses, mouth pressed thin, profile to three-quarter view, sharp focus on face, slightly desaturated to convey unease`
- Negative: `{공통 negative} + exaggerated cartoon sweat drops, melodramatic expression`

### Scene 5 — 윤소율의 권한 회복 흥분 (회의실, 10:12)
- 등장: 윤소율 (중심), 한재민 (반응)
- **Prompt 5.A (윤소율 흥분)**: `{style prefix}, {윤소율 signature} leaning forward in chair holding iPad up showing design mockups, animated excited expression with raised eyebrows and slight open smile, hand gesture mid-air emphasizing point, glasses catching light, warm bright illumination, medium close-up three-quarter angle, energetic body language`
- **Prompt 5.B (한재민 맞장구)**: `{style prefix}, {한재민 signature} half-turned toward Yoon Soyul, enthusiastic agreement expression, both hands open in welcoming gesture, "yes exactly" body language, warm collaborative atmosphere, two-shot with Yoon partially visible at edge of frame, dynamic composition`
- Negative: `{공통 negative} + overly dramatic emotion, theatrical poses`

### Scene 6 — 박지호의 자기부정 흥분 (회의실, 10:15)
- 등장: 박지호 (중심), 한재민 (가벼운 위로)
- **Prompt 6.A (박지호 어색한 웃음)**: `{style prefix}, {박지호 signature} forcing awkward small smile that doesn't reach the eyes, one hand scratching back of neck nervously, looking at screen then away, slightly hunched posture, conflicted micro-expression, medium close-up from slight low angle making him look smaller, cool clinical lighting that flattens face`
- **Prompt 6.B (한재민 가벼운 위로)**: `{style prefix}, {한재민 signature} casual reassuring gesture with one hand toward Park Jiho, friendly but slightly dismissive smile, body language of "no big deal", over-shoulder shot from Jiho's perspective showing both characters, contrast between Jiho's slumped pose and Han's confident upright pose`
- Negative: `{공통 negative} + exaggerated comic distress, oversized emotions`

### Scene 7 — 강민호의 침묵 (회의실, 10:18)
- 등장: 강민호 (중심), 4인 (시선만)
- **Prompt 7.A (강민호 노트북 조작)**: `{style prefix}, {강민호 signature} seated calmly with own laptop open in front, screen reflected faintly in his calm eyes, fingers typing then pausing, completely neutral expression, sipping black coffee, depth of field background showing blurred meeting room with other four watching him, close-up three-quarter angle, balanced soft lighting`
- **Prompt 7.B (회의실 정적 와이드)**: `{style prefix}, meeting room wide shot, all five characters visible, {강민호 signature} center focus quietly working at laptop with coffee mug, {한재민 signature} at projector with awkward expression of waiting, {최태규 signature} watching Kang intently, {윤소율 signature} and {박지호 signature} also turned toward Kang, silence atmosphere, slightly cooler color grading, wide angle showing tense quiet, vertical composition friendly`
- **Prompt 7.C (강민호 깨진 화면 자세히)**: `{style prefix}, close-up on laptop screen showing the demo dashboard with one chart broken or showing error after Kang's input test, hands of Kang visible at keyboard, screen glow on his expressionless face partially visible at edge, sharp focus on screen with subtle glitch artifact`
- Negative: `{공통 negative} + dramatic camera angle, theatrical staging`

### Scene 8 — 강민호의 두 질문 (회의실, 10:22) ⚡ 절정
- 등장: 강민호 (중심), 한재민 (받는 사람), 다른 3인 (시선)
- **Prompt 8.A (강민호 노트북 닫는 손)**: `{style prefix}, close-up of {강민호 signature} hand slowly closing laptop lid, mechanical wristwatch visible, deliberate calm motion, table surface and coffee mug in frame, soft cinematic lighting, shallow depth of field`
- **Prompt 8.B (강민호 첫 질문 컷)**: `{style prefix}, {강민호 signature} medium close-up, looking directly at Han Jaemin off-screen, mouth opening to speak with utter calm, eyes steady not threatening but undeniable, slight side lighting creating subtle shadow on half of face, vertical composition for webtoon scroll`
- **Prompt 8.C (한재민 입 흐림)**: `{style prefix}, {한재민 signature} reaction shot, confident smile faltering, mouth slightly open mid-word that trailed off, hand frozen mid-gesture, eyes searching for answer, soft sweat sheen on forehead, medium close-up, lighting suddenly flat unflattering`
- **Prompt 8.D (강민호 두 번째 질문 — 시리즈 시그니처 컷)**: `{style prefix}, {강민호 signature} full medium shot from slight low angle making him quietly authoritative, laptop closed in front, coffee mug to side, calm direct gaze, mouth in mid-question, the whole meeting room background blurred but visible (four other characters all turned to him in silence), pivotal cinematic composition, this is the most important panel of the episode`
- **Prompt 8.E (정적 와이드 — 회의실 freeze)**: `{style prefix}, full meeting room overhead wide shot, all five characters frozen in their positions, complete silence atmosphere, light from windows creating long shadows on table, no movement, like a painting, slightly desaturated, hold-the-breath moment`
- Negative: `{공통 negative} + sweat drops, comic motion lines, exaggeration`

### Scene 9 — 회의 종료 (회의실 → 복도, 10:30)
- 등장: 5인 모두 분산
- **Prompt 9.A (최태규 일어남)**: `{style prefix}, {최태규 signature} standing up from chair gathering papers, neutral business-as-usual expression, no longer looking at screen, casual concluding gesture, medium shot, normal office lighting restored`
- **Prompt 9.B (윤소율-한재민 복도 대화)**: `{style prefix}, {윤소율 signature} and {한재민 signature} walking together in modern office corridor, animated conversation with hand gestures, both excited and energized, glass walls and indoor plants visible, two-shot medium walking pose, warm corridor lighting, ignoring others`
- **Prompt 9.C (박지호 책상 멍)**: `{style prefix}, {박지호 signature} seated alone at his desk in open office, monitor turned off, hands in lap, staring blankly into middle distance, surrounded by other people working in background blurred, isolated despite the crowd, medium shot showing loneliness in workplace, slightly cool lighting`
- **Prompt 9.D (강민호 자기 자리)**: `{style prefix}, {강민호 signature} seated at his desk in quiet corner, opening laptop calmly, coffee mug placed beside, no expression change from earlier, just back to work, medium shot from across the room showing context`
- Negative: `{공통 negative} + overly dramatic isolation, sad music visual cues`

### Scene 10 — 그날 밤, 박지호의 자취방 (밤 11시) ⚡ 후크
- 등장: 박지호 (단독)
- **Prompt 10.A (자취방 와이드)**: `{style prefix}, small modest Korean studio apartment interior at night, single bed with rumpled covers, low desk with laptop open, small fridge, instant noodle empty cup, posters of code conferences on wall, only desk lamp providing warm yellow light, rest of room in shadow, establishing shot wide angle from upper corner`
- **Prompt 10.B (박지호 노트북 앞)**: `{style prefix}, {박지호 signature} seated cross-legged on floor at low desk, no longer wearing hoodie hood, glasses reflecting laptop screen light, intense focused expression typing prompt, half-eaten convenience store dinner beside him, warm desk lamp lighting only, deep shadows around, close-up medium shot showing isolation and focus`
- **Prompt 10.C (생성된 앱 화면 클로즈업)**: `{style prefix}, close-up of laptop screen showing newly generated marketing dashboard application running, Park Jiho's blurred reflection in screen showing slack-jawed expression, hands on keyboard, dim apartment background visible past screen edge, the screen glow lighting his face from below`
- **Prompt 10.D (강민호 질문 머릿속 — 회상 인서트)**: `{style prefix}, ghostly visual of {강민호 signature} from the meeting earlier, semi-transparent overlay style, his calm face superimposed lightly on Park Jiho's current view, suggesting the question haunting him, vertical composition with Jiho below and Kang above as memory, monochromatic blue tint for memory layer`
- **Prompt 10.E (검색창 + 블로그 제목 — 후크 마지막 컷)**: `{style prefix}, extreme close-up on laptop screen showing Korean search engine results page, search query "운영 사고 새벽" typed in search bar, top result blog title clearly visible: "당신의 서비스, 새벽 3시에 누가 받습니까?", cursor hovering over the link, soft focus suggesting the moment of decision, dramatic chiaroscuro lighting with screen as only light source, Park Jiho's face barely visible at edge of frame`
- Negative: `{공통 negative} + cluttered apartment, unrealistic interior, English text dominant`

## 시그니처 컷 후보 (이번 화의 명장면 — 이미지로 가장 공들일 것)
1. **8.D**: 강민호의 두 번째 질문 — Part 1 도입의 무게중심 컷
2. **8.E**: 회의실 freeze — 침묵의 절정
3. **10.E**: 박지호 검색창 + 블로그 제목 — 다음 화로 끌고 가는 후크 마지막 컷
4. **2.C**: 강민호 회의실 입장 — 그의 첫 등장, 시리즈 무게중심 인물 인트로
