# Cover Image Generation Prompts v1.0

> 문서 버전: v1.0 · 작성일: 2026-05-27
> 사용처: README, PPT 표지, GitHub OG image, 소셜 미디어 카드
> 도구: Midjourney v6+, DALL-E 3, Stable Diffusion XL, Imagen 3, Recraft 3

---

## 1. 공통 비주얼 아이덴티티

| 항목 | 값 |
|---|---|
| 배경 | dark navy `#0E1525` with subtle starfield/grid texture |
| 주 색상 | cyan `#22D3EE` (highlights, energy) |
| 보조 색상 | lime `#A3E635` (success, action) |
| 텍스트 색상 | white `#F8FAFC` |
| 경고 색상 (선택) | amber `#FBBF24` |
| 스타일 | minimal flat illustration + isometric perspective + soft glow |
| 분위기 | premium tech keynote, research, autonomous, calm-confident |
| 금기 | photorealistic faces, advertising look, busy/cluttered, neon arcade |

---

## 2. 메인 커버 (16:9, README + PPT 표지)

### 한국어 컨셉
이소메트릭 시점의 떠 있는 칸반 보드(8 카드 chain 진행), 그 위로 6명의 추상 페르소나(철학자/과학자 실루엣) 아이콘이 hexagonal 배치, 보드 아래로는 무한 사이클 루프(∞)가 빛으로 흐름. 우측 하단에 작은 인간 손이 하나의 카드(DECIDE 표시)에 손가락 터치. 다크 네이비 배경 + 시안/라임 글로우.

### 메인 프롬프트 (Midjourney v6+ / SDXL 호환)

```
A premium isometric tech illustration of a self-improving AI research workflow.
Central focus: a floating translucent kanban board with 8 task cards arranged
in a flowing chain from left to right, cards glowing soft cyan (#22D3EE),
last card highlighted golden (DECIDE gate) with a delicate human fingertip
gently touching it from the lower right.
Above the board: 6 hexagonal portrait tiles of abstract philosopher/scientist
silhouettes (Aristotle, Tukey, Spearman, Gauss, Ada Lovelace, Turing) arranged
in a soft halo, each with thin cyan border.
Below the board: a luminous infinity loop (∞) made of lime (#A3E635) light
trails representing cycles repeating.
Background: deep dark navy (#0E1525) with subtle starfield texture and
faint diagonal grid lines, very subtle. Volumetric soft glow.
Style: minimal flat vector illustration, isometric perspective,
premium keynote aesthetic, no photorealism, no advertising look,
no busy details, calm and confident.
Aspect ratio: 16:9 --ar 16:9 --style raw --v 6
```

### DALL-E 3 / GPT Image 호환 변형

```
A premium 16:9 isometric illustration in flat vector style for a tech keynote
cover. Show a floating translucent kanban board with 8 glowing cyan task cards
flowing left to right in a dependency chain, the last card highlighted in gold
with a small human finger touching it. Above, 6 hexagonal portraits of
philosopher and scientist silhouettes form a halo. Below, a glowing lime green
infinity loop suggests repeating cycles. Background: deep navy #0E1525 with
subtle starfield. Color palette: dark navy, cyan #22D3EE, lime #A3E635, white
#F8FAFC. Mood: minimal, premium, autonomous, research-grade. Avoid: photo-
realistic faces, advertising look, cluttered detail.
```

---

## 3. README 헤더 (16:9, 슬림 변형)

좌측 텍스트 공간 확보용. 보드+사이클은 우측 2/3에, 좌측 1/3은 단색.

```
A premium minimal isometric illustration in 16:9 wide format. Right two-thirds
of the canvas: a small floating translucent kanban board with a flowing chain
of 8 cyan task cards, last card glowing gold, with a luminous lime infinity
loop swirling beneath it. Left one-third: clean negative space of deep navy
#0E1525, suitable for overlaying a title and badges. Subtle starfield in the
background. Style: flat vector, calm and confident, no photorealism.
Color palette: navy #0E1525, cyan #22D3EE, lime #A3E635.
--ar 16:9 --style raw --v 6
```

---

## 4. GitHub OG Image (1.91:1, 소셜 카드)

링크 미리보기용 압축형. 핵심 1개 요소만.

```
A premium minimal isometric vector illustration. Centered composition:
a single elegant kanban board with 8 cyan glowing cards arranged in a forward
chain, with a small lime infinity loop wrapping below it. No text in image.
Background: deep navy #0E1525 with faint starfield. Style: minimal flat,
premium keynote. Avoid clutter, avoid faces, avoid photorealism.
--ar 1.91:1 --style raw --v 6
```

---

## 5. 소셜 미디어 정사각 (1:1, Instagram/Threads)

```
A premium minimal isometric vector illustration in 1:1 square format.
Central focus: a glowing cyan kanban board with 8 task cards arranged in
a tight vertical chain, with a lime infinity loop circling the entire board.
6 small hexagonal philosopher silhouette icons orbit the board like satellites.
Background: deep navy #0E1525 with subtle starfield. Style: minimal flat vector,
calm premium tech aesthetic. Color palette: navy #0E1525, cyan #22D3EE,
lime #A3E635, white #F8FAFC. Avoid: photorealism, advertising look, clutter.
--ar 1:1 --style raw --v 6
```

---

## 6. PPT 마지막 슬라이드 (Q&A, 16:9 미니멀)

```
A premium minimal 16:9 closing slide background. A single softly glowing
infinity loop (∞) of lime #A3E635 light trails on a deep navy #0E1525 backdrop
with subtle starfield. The loop is centered but small enough to leave generous
negative space for "감사합니다" text overlay. Style: minimal vector, ambient,
calm. No other elements. --ar 16:9 --style raw --v 6
```

---

## 7. 대안 컨셉 3종 (선택용)

### 7.1 "지도교수와 박사과정생 6명" (humanizing)

```
A premium isometric illustration showing a research lab metaphor.
Center: a single floating advisor figure (silhouette only, no facial detail)
gently pointing at one card in a flowing kanban chain. Around the chain:
6 small workspace pods, each occupied by an abstract philosopher/scientist
silhouette working at their own station. Each pod glows with soft cyan light.
Background: deep navy #0E1525, subtle starfield. Mood: collaborative, calm,
autonomous. Style: minimal flat vector, no photorealism.
--ar 16:9 --style raw --v 6
```

### 7.2 "24시간 시계 + 사이클" (operational metaphor)

```
A premium isometric illustration of a 24-hour clock face merged with a flowing
kanban chain. The clock has only 2 small human-finger marks at 9am and 6pm
(representing daily human decisions), all other hours show small gear icons
in cyan. A lime infinity loop wraps around the clock perimeter representing
cycle repetition. Background: deep navy #0E1525. Style: minimal flat vector,
informational, calm. --ar 16:9 --style raw --v 6
```

### 7.3 "한국어 채점 도메인 hint" (domain-aware)

```
A premium minimal isometric illustration. Foreground: a stylized open
notebook with abstract Hangul-like script marks (no real characters, only
suggestive curves) and a soft red pen ticking gentle marks. Behind the
notebook: a translucent kanban board with cyan task cards flowing in a chain,
and a lime infinity loop suggesting autonomous cycles. Background: deep navy
#0E1525 with subtle starfield. Style: minimal flat vector, scholarly and
autonomous. --ar 16:9 --style raw --v 6
```

---

## 8. 부정 프롬프트 (모든 변형 공통)

```
no photorealism, no real human faces, no advertising look, no neon arcade,
no busy cluttered details, no excessive text overlays in image, no AI-generated
text artifacts, no random Korean characters, no logos of existing companies,
no anime style, no 3D rendering, no chromatic aberration, no lens flare
```

도구별 부정 프롬프트 적용:
- Midjourney v6: `--no photorealism, faces, advertising, neon, clutter`
- SDXL: negative prompt 필드에 위 문장 그대로
- DALL-E 3: 본문 마지막에 "Avoid: ..." 형태로

---

## 9. 도구별 호환성 표

| 도구 | 강점 | 권장 변형 | 주의 |
|---|---|---|---|
| **Midjourney v6+** | isometric + lighting 우수 | 메인 + 부정 명령 활용 | `--style raw` 필수 |
| **DALL-E 3** | 명확한 instruction following | DALL-E 3 변형 사용 | 색상 hex code 인식 잘됨 |
| **Stable Diffusion XL** | 비용 효율 + 후처리 가능 | 메인 + negative prompt | LoRA 사용 시 "flat vector" weight 1.2 |
| **Imagen 3 (Google)** | 한국어 명확 | DALL-E 3 변형 | 페르소나 silhouette 표현 일관 |
| **Recraft 3** | vector 직접 출력 | 메인 (vector 강조) | SVG export 가능 |
| **Adobe Firefly** | enterprise 안전 | DALL-E 3 변형 | royalty-free 출처 보장 |

---

## 10. 사용 가이드

### Step 1: 도구 선택
- 빠른 prototype → DALL-E 3
- 최종 quality → Midjourney v6 + 후처리 (Figma)
- Vector export → Recraft 3
- 무료 → SDXL local

### Step 2: 프롬프트 사용
- 메인 (§2) 먼저 생성 → 만족 못 하면 대안 (§7) 시도
- 색상은 hex code 그대로 유지 (테마 일관성)
- aspect ratio는 용도에 맞춰 §3-§6 중 선택

### Step 3: 후처리 (Figma/Photoshop)
- 텍스트 오버레이 (제목 / 배지 / 부제)
- 색상 미세 조정 (실제 출력 확인)
- 경계 crop (필요 시)

### Step 4: 적용
- README 상단: §3 (헤더형, 좌측 텍스트 공간)
- GitHub OG: §4 (1.91:1)
- PPT Slide 1 표지: §2 (16:9 메인)
- PPT Slide 마지막: §6 (Q&A 미니멀)
- Social preview: §5 (1:1)

---

## 11. 본 프로젝트 정체성 keyword (이미지 검토 시)

생성 이미지가 다음 5 keyword를 시각화하는지 확인:

1. **자가발전 (self-improving)** — 무한 루프, 사이클, 반복
2. **장기 자율 (long-running autonomous)** — 시간/지속의 표현
3. **인간 게이트 (human gate)** — 인간 손 또는 단일 결정 포인트
4. **다중 에이전트 (multi-agent)** — 6 profile, hexagonal
5. **연구/검증 (research/validation)** — 과학적, 학술적 분위기

3개 이상 표현되면 채택, 2개 이하면 재생성.

---

## 12. 라이선스 / 출처

- 본 프롬프트는 본 프로젝트 비주얼 아이덴티티 정의용
- 생성 이미지는 사용 도구의 라이선스 정책 준수
- 외부 공개 시 출처 명시: "Hermes Kanban 자가발전 워크플로우 검증, 2026"
