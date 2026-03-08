# Video Prompting Masterclass

Universal video prompting techniques that work across all models.

## How Video Prompts Differ from Image Prompts

Image prompts describe a single frozen moment. Video prompts must describe **motion through time**:
- What changes between the first frame and the last?
- How does the camera behave?
- What sounds accompany the visuals?
- What is the temporal rhythm (slow, fast, building, resolving)?

A good image prompt describes a photograph. A good video prompt describes a scene from a film.

## The 8-Point Shot Grammar

Every production-quality video prompt should address these eight elements:

1. **Subject and Action** -- The "who" and physics-based behavior
2. **Emotional Energy** -- Micro-expressions, performance targets
3. **Camera Optics** -- Lens type (35mm anamorphic, 85mm prime), DoF, focus racks
4. **Motion** -- Camera moves (dolly-in, crane, parallax) and blocking
5. **Lighting Physics** -- Key/fill/rim, color temperature (3200K vs 5600K), volumetrics
6. **Style and Color Science** -- Film stock references (Kodak 2383), LUT references
7. **Audio Targets** -- Ambient bed, foley cues, beat synchronization
8. **Continuity Constraints** -- Wardrobe, props, time-of-day tokens

You don't need all 8 in every prompt. But the more you include, the more control you have.

## Universal Prompt Template

```
[Shot Type] of [Subject with specific visual details] [performing action with specifics]
in [environment with lighting description]. [Camera movement description].
[Style/aesthetic reference]. [Audio description if supported].
```

## Temporal Description Patterns

### Sequential Markers
- "Initially... Then... Finally..."
- "The scene begins with... transitions to... culminates in..."
- "The camera starts on... then moves to reveal..."

### Beat Structure (Sora's "shot stacks")
```
Beat 1 (0-2s): ENTER -- [establishing action]
Beat 2 (2-4s): REACT -- [response or development]
Beat 3 (4-6s): EXIT  -- [resolution or transition]
```

### Duration-Awareness
- 4s: Single action or establishing shot. One beat.
- 6s: Brief narrative arc. Two beats.
- 8s: Full micro-story. Three beats.
- 10s+: Extended sequence. Layer complexity carefully.

## Motion Description Language

### Weak vs. Strong Motion Verbs

| Weak | Strong |
|------|--------|
| "walks" | "takes deliberate steps, weight shifting" |
| "looks around" | "turns head thirty degrees left, eyes scanning" |
| "moves fast" | "sprints, arms pumping, coat flapping" |
| "sits down" | "lowers into the chair, settling back slowly" |
| "dances" | "spins on one foot, arms spiraling outward" |

### Subject Motion Templates
- `[Subject] [verb] [direction] [speed adverb]`
- "A woman strides forward purposefully through the crowded market"
- "The bird descends in a slow spiral toward the lake surface"

### Camera Motion Templates
- `Camera [movement type] [direction] [speed] [starting/ending position]`
- "Camera dollies in slowly from medium shot to close-up"
- "Steady tracking shot follows the subject at shoulder height"

### Combined Templates
- `As [subject action], the camera [camera motion], revealing [new element]`
- "As the door swings open, the camera pushes in past the threshold, revealing the sunlit room beyond"

## Camera Movement Integration

### When to Use Each Movement

| Camera Movement | Emotional Effect | Best For |
|----------------|-----------------|----------|
| Dolly in | Building intimacy/tension | Dialogue, revelation |
| Dolly out | Creating distance/context | Endings, establishing scale |
| Tracking | Engagement, journey | Following action |
| Crane up | Grandeur, liberation | Transitions, establishing |
| Crane down | Grounding, arrival | Introductions |
| Orbit | Energy, showcase | Product, character reveal |
| Static | Contemplation, weight | Emotional moments |
| Handheld | Urgency, realism | Action, documentary |
| Whip pan | Surprise, energy | Transitions, comedy |

### Camera Keywords That Work Across Models
- "Slow dolly forward", "gentle pan left", "crane shot descending"
- "Handheld tracking", "steady medium shot", "locked tripod"
- "Extreme close-up", "Dutch angle", "over-the-shoulder shot"
- "Establishing wide shot", "rack focus", "shallow depth of field"

## Scene Composition

### Depth Layering
Describe foreground, midground, and background separately:
```
Foreground: rain droplets on glass, slightly out of focus
Midground: the subject's face in sharp focus
Background: city lights, reduced to soft circular bokeh
```

### Visual Anchoring
Give the model concrete details to work with:
- Bad: "a beautiful woman"
- Good: "a woman in her thirties with auburn hair in a loose bun, wearing a charcoal peacoat and silver-rimmed glasses"

### Environment Detail
- Include 2-3 specific environmental objects
- Describe surfaces and materials: "worn wooden table", "polished marble floor"
- Include weather or atmospheric elements: "mist", "dust motes", "steam"

## Lighting and Mood

### Lighting Sets the Emotion

| Mood | Lighting Description |
|------|---------------------|
| Warmth/comfort | "Golden hour backlighting, warm amber tones" |
| Tension/drama | "Single harsh overhead light, deep shadows" |
| Mystery | "Volumetric fog, rim-lit silhouette" |
| Romance | "Soft candlelight, warm diffused glow" |
| Energy | "Neon signs, colored light bouncing off wet surfaces" |
| Melancholy | "Overcast grey, flat diffused light, desaturated" |

### Color Temperature Reference
- 3200K = warm tungsten indoor light
- 5600K = neutral daylight
- 7000K+ = cool shade / overcast

## Audio Cues in Prompts

For models that support audio (Veo, Kling, Sora, LTX):

### Sound Layering
1. **Ambient bed** (always): Room tone, wind, traffic, nature
2. **Foley** (when relevant): Footsteps, cloth, objects
3. **Dialogue** (when needed): In quotes, with speaker and tone
4. **Music** (sparingly): Only if part of the scene

### Dialogue Format (varies by model)

**Veo:** `[Character visual description] says: "Line here."`

**Kling:** `[Character Name, emotion]: "Line here."`

**Sora:** Dialogue block below visual description, speakers labeled

### Pro Tip
Add "no background music" when lip sync quality matters. Background music competes with dialogue processing.

## Multi-Subject Choreography

When multiple subjects appear:
1. Establish each subject's position in the frame
2. Describe their spatial relationship: "facing each other across the table"
3. Sequence their actions: "She speaks first, then he responds"
4. Keep it simple: 2 subjects max per clip for reliable results

## What Makes Prompts Fail

| Failure | Cause | Fix |
|---------|-------|-----|
| Generic/boring output | Vague prompt | Add specific details, textures, lighting |
| Wrong motion | Missing camera/subject motion | Explicitly describe both |
| Plastic/AI look | No physical imperfections | Add grain, dust, atmospheric haze |
| Incoherent scene | Too many elements | Simplify to one subject, one action |
| Static video | No motion described | Add camera movement AND subject movement |
| Inconsistent character | Vague character description | Use specific physical markers, reuse across prompts |
| Bad lip sync | Wrong dialogue format | Follow model-specific syntax exactly |
| Audio conflicts | Competing sound sources | Prioritize: dialogue > foley > ambient > music |

## 10+ Example Prompts with Annotations

### 1. Cinematic Landscape
```
A sweeping aerial drone shot over a volcanic coastline at dawn.
Black sand beaches meet turquoise waves under a sky streaked with
pink and gold. The drone pushes forward along the shoreline as mist
rises from geothermal vents. Jagged basalt columns cast long shadows.
Film grain, muted color grading with warm amber highlights.
```
**Why it works:** Clear camera (aerial drone), specific environment details (basalt, geothermal vents), temporal progression (dawn light), style anchor (film grain).

### 2. Character Close-Up
```
Close-up of an elderly woman's weathered hands shaping clay on a
spinning potter's wheel. Her fingers press into wet clay, creating
a smooth curve rising upward. Camera slowly tilts up to reveal her
focused expression, deep lines around eyes softened by warm afternoon
light. Rhythmic whir of the wheel fills the studio.
```
**Why it works:** Physical detail (weathered hands), specific motion (fingers pressing), camera movement (tilt up), audio (wheel whir).

### 3. Product Shot
```
A sleek matte black headphone case sits center-frame on a white
surface. Hands enter from below, pick up the case, open it in one
smooth motion revealing brushed aluminum headphones. Locked tripod,
slight slow-motion. Shallow depth of field, white bokeh. Satisfying
mechanical click of the case opening.
```
**Why it works:** Apple-demo clarity, specific product motion, controlled camera, satisfying audio cue.

### 4. Action Sequence
```
Medium tracking shot follows a parkour runner sprinting across
rain-slicked rooftops at twilight. Runner leaps across a gap between
buildings, legs extended mid-air, lands in a smooth roll. Camera
follows at shoulder height, handheld. Spray of water from each
footstrike. Rapid breathing and slap of shoes on wet concrete.
```
**Why it works:** Dynamic motion verbs (sprints, leaps, lands), specific camera style (handheld tracking), environmental detail (rain-slicked), foley (footstrike spray).

### 5. Dialogue Scene
```
Medium close-up of a man in his forties with salt-and-pepper beard,
worn leather jacket, sitting at a diner counter under warm tungsten
light. He stirs his coffee and says: "The thing about this town is,
nobody ever really leaves." Coffee shop murmur, spoon clinking,
distant jukebox. No background music.
```
**Why it works:** Specific character (age, beard, jacket), simple action (stirs), proper dialogue syntax, layered audio, "no background music" for lip sync quality.

### 6. Abstract / Artistic
```
Slow-motion macro of ink droplets falling into clear water, blooming
into fractal patterns of deep indigo and magenta. Tendrils of color
twist and intertwine, pulsing outward. Camera holds steady as new
drops disturb the surface. Low resonant hum accompanies the unfolding.
Dark background, shallow depth of field.
```
**Why it works:** Specific physics (ink in water), concrete colors, temporal progression (blooming, pulsing), audio harmony.

### 7. Nature Documentary
```
A snow leopard crouches on a rocky ledge in the Himalayas, eyes
locked on a herd of bharal far below. Camera holds a telephoto
close-up from 50 meters, compressing the landscape. Wind ruffles the
leopard's thick fur. It shifts weight to its haunches, muscles coiling.
Cold blue light, overcast sky, deep shadows in the rock crevices.
```
**Why it works:** Specific species and location, telephoto compression noted, anticipatory motion, environmental audio implied.

### 8. Music Video Aesthetic
```
A woman in a flowing red dress dances alone in an abandoned warehouse.
Shafts of dusty sunlight cut through broken windows. She spins, dress
fanning outward, caught in slow motion. Camera orbits around her at
waist height. High contrast, desaturated background with the red dress
as the only vivid color. Echo of her footsteps on concrete.
```
**Why it works:** Color isolation technique (red vs desaturated), specific camera (orbit), material physics (flowing dress), architectural setting.

### 9. Sci-Fi / Futuristic
```
A holographic city map flickers to life above a dark glass table in a
dimly lit control room. Camera pushes in from wide shot to close-up on
the map as data points pulse with cyan light. A hand reaches into frame
and rotates the projection. Volumetric light scatters through dust
particles. Subtle electronic hum, soft beeping of data feeds.
```
**Why it works:** Concrete sci-fi details (holographic, glass table), interaction (hand rotates), atmosphere (dust, dim light), appropriate audio.

### 10. Emotional / Intimate
```
A father and daughter sit on a park bench at golden hour. She leans
her head on his shoulder. He wraps his arm around her, and they watch
leaves drift from the oak tree in front of them. Camera holds a wide
profile shot from the side. Warm backlighting creates a golden rim
around their silhouettes. Birdsong, distant children playing.
```
**Why it works:** Specific relationship and gesture, static camera for emotional weight, backlighting for mood, peaceful ambient audio.

### 11. Horror / Tension
```
A long dark hallway in an old hospital. Single flickering fluorescent
light at the far end. Camera dollies in very slowly. A wheelchair sits
empty in the middle of the corridor, slightly askew. As the camera
reaches the wheelchair, it begins to rock gently on its own. Electrical
buzz of the failing light, distant drip of water. Cold blue-green
palette, high contrast, deep shadows.
```
**Why it works:** Environmental horror (no monsters needed), slow camera build, minimal but specific sound design, restrained motion that implies threat.
