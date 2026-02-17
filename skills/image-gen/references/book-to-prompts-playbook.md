# Book-to-Prompts: Turning Literature into Image Generation
## A playbook for extracting visual prompts from any book, with Simak's City as the worked example

This document is a method. The examples come from *City* by Clifford D. Simak, but each step is written so you can apply it to any novel, story cycle, or narrative text.

## Step 1: Extract Visual Scenes from Prose

### What makes a scene prompt-worthy
A scene is prompt-worthy when it gives you enough visual signal to generate a coherent image without inventing half the frame from scratch.

Use these four criteria:
- Visual density: concrete objects, surfaces, weather, movement, and spatial cues in the same passage.
- Emotional weight: grief, awe, dread, tenderness, or revelation that can be felt visually.
- Narrative pivot: a turning point where the world, stakes, or character state changes.
- Setting transition: movement into a new environment, season, time-of-day, or visual regime.

### How to scan a book systematically
Do not cherry-pick from memory. Build a scene candidate pass from beginning to end.

Use this process:
1. Read in order and mark every passage with explicit visual action.
2. Tag each candidate by chapter/tale, location, time-of-day, and emotional tone.
3. Score each candidate (1-5) on density, emotional weight, and uniqueness.
4. Keep top scenes per section so the image set covers the whole narrative arc.

### What to capture for each scene
For each candidate, capture:
- Visual elements: subjects, objects, textures, weather, architecture, motion.
- Mood: contemplative, ominous, ecstatic, ritual, intimate, etc.
- Palette: dominant colors and accent colors.
- Lighting: source, direction, contrast, and time-of-day.

### Worked example: Scene 1 (Autonomous Mower)
In *City*, the opening mower scene is a strong seed because it combines domestic calm with technical unease. The old man in the chair, warm sunlight, and neat lawn patterns create stability; the snap-open machine panel and grasping crane arm create disruption. That visual contradiction gives the image model a clear emotional target.

Extraction notes:
- Subject: autonomous mower in operation, old man observing.
- Setting: suburban lawn in soft sunlight.
- Palette: warm greens, faded yellows, washed blue sky.
- Lighting: broad daylight with low-contrast warmth.
- Narrative function: first signal that machines are becoming active agents.

### Worked example: Scene 10 (First Steps on Jupiter)
This scene is a different extraction problem: alien beauty with minimal Earth analogs. The passage succeeds because it still provides concrete anchors: purple mist, crystalline cliff, and a many-band rainbow from ammonia spray. For your book, do the same in unfamiliar settings: find specific physical anchors and avoid abstract-only wording.

Extraction notes:
- Subject: transformed beings moving through a newly perceived world.
- Setting: Jovian landscape with extreme atmospheric effects.
- Palette: purple mist, red-violet ground, white crystalline faces, hyper-spectral rainbow.
- Lighting: charged sky with luminous atmospheric flares.
- Narrative function: perceptual rebirth and tonal expansion of the book's world.

### Practical "what to look for" checklist
- A passage where you can identify foreground, midground, and background in one read.
- A scene with at least one distinctive material cue (moss-softened granite, polished metal, drifting ash, etc.).
- A scene where weather or light changes the meaning of the action.
- A scene that advances the visual arc of the book, not just the plot.

## Step 2: Build a Visual Style Guide

### Why this comes before prompt writing
Without a style guide, each prompt drifts toward model defaults. With a style guide, your outputs stay in one visual world even as scenes change.

You need the guide to control:
- Consistency across a series.
- Mood continuity.
- Palette discipline.
- Character recognizability across time jumps.

### How to identify a book's visual DNA
Before writing prompts, extract five system-level patterns from the text:
- Dominant palette: what colors define the baseline world.
- Recurring motifs: repeated objects/spaces that carry thematic weight.
- Technology level: what tools/materials are visible at each stage of the story.
- Atmosphere progression: how emotional weather changes across the book.
- Character visual language: repeatable silhouettes, textures, posture cues.

### Worked example: City visual DNA
In *City*, we see:
- Earth tones dissolving into alien chromatics.
- Fireplace light as a recurring interior anchor.
- Empty streets as a repeated image of post-human transition.
- Wind treated as an active atmospheric force.

For your book, build equivalent anchors and reuse them deliberately.

### Palette progression (City example)
Track palette as a timeline:
1. Warm mid-century Americana: dust, rust, weed-green, autumn gold.
2. Jupiter phase: purple mist, red-violet ground, crystalline white, hyper-chromatic rainbow bands.
3. Late-world austerity: black-grey winter, silver moonlight, muted earth with isolated bright accents.

For your book, define 2-4 palette phases tied to narrative eras.

### Style guide template
Create a one-page guide with:
- Palette: base colors, accents, forbidden out-of-world colors.
- Motifs: 3-6 recurring objects/locations to thread through the series.
- Atmosphere keywords: 8-12 words you reuse in prompts.
- Technology progression: how machinery/material culture changes over time.
- Character visual language: silhouette, scale, texture, and motion traits per major character.

## Step 3: Translate Literary Descriptions into Image Prompts

### The bridge from prose to prompting
Literary text is expressive; prompts must be operational. Translation means preserving mood while converting language into renderable instructions.

Break each scene into:
- Subject
- Setting
- Lighting
- Mood
- Composition
- Style keywords

### Prompt structure that works
Use this order for most image models:
1. Primary subject and action.
2. Environment and spatial context.
3. Lighting and atmosphere.
4. Materials/textures and key props.
5. Composition cues (framing, lens feel, distance).
6. Style and quality keywords.

Put the highest-priority details first. If the model misses something repeatedly, move that element earlier and make it more concrete.

### Worked translation: Scene 4 (Drizzle Funeral at the Webster Crypt)
Literary description -> extracted elements -> assembled prompt.

Extracted elements:
- Weather and sky: cold drizzle, leaden skies.
- Vegetation frame: bare branches, hedges blurred by rain haze, pines around crypt.
- Subjects: silver-gleaming robot bodies in rigid formation carrying a casket.
- Architecture/materials: moss-softened granite statue, age-greened crypt door, bronze and marble crypt interior.
- Mood: solemn, ceremonial, restrained.

Assembled prompt:
```text
A funeral procession in cold drizzle beneath leaden skies, bare branches and rain-softened hedges framing a family crypt among pines, silver-gleaming robot bodies in rigid bowed formation carrying a casket, moss-softened granite statue above an age-greened crypt door, bronze and marble interior visible inside the crypt, muted grey palette, cinematic realism, solemn ceremonial mood, medium-wide composition.
```

### Worked translation: Scene 19 (Jenkins Returns in the Gift Body)
Extracted elements:
- Subject: monumental polished robot with a fire-like sheen.
- Secondary subject: raccoon perched on the robot's shoulder.
- Motion: cat-soft movement despite massive scale.
- Composition: doorway framing, darkness behind, warmth ahead.
- Mood: awe, continuity, protective gentleness.

Assembled prompt:
```text
Nighttime doorway reveal of a monumental polished robot glowing with a slow fire-like sheen, a small raccoon perched on its shoulder for dramatic scale contrast, the giant machine moving with cat-soft precision despite immense weight, darkness behind the figure and warm interior light ahead, reflective metal textures, quiet mythic tone, high-detail cinematic composition.
```

### What models respond to well vs what gets lost
Models respond well to:
- Specific materials and surfaces.
- Clear lighting direction and time-of-day.
- Distinct scale contrasts.
- Concrete weather effects.

Models often lose:
- Abstract philosophy with no visual anchor.
- Crowded prompts with too many equal-priority subjects.
- Conflicting style cues (for example: "minimal flat design" plus "photoreal cinematic grit").

### Common failure modes
- Too abstract: mood words with no scene geometry.
- Too many subjects: focal point collapse.
- Conflicting cues: mixed eras, mixed rendering styles, mixed lighting logic.

## Step 4: Maintain Visual Consistency Across a Series

### The core problem
Twenty images from one book should read like one body of work, not twenty unrelated generations.

### Use the style guide as the anchor
For every prompt, explicitly carry forward:
- Palette phase
- Motif references
- Atmosphere keywords
- Character visual signatures

### Recurring elements as visual threads
In *City*, the Webster House appears across multiple eras and emotional states. That repetition binds the series. For your book, choose equivalent recurring anchors (a street, a room, a threshold, a vehicle, a tree line) and revisit them with controlled variation.

### Palette discipline
When scenes shift dramatically, keep them inside the book's color world. In *City*, even extreme Jupiter scenes still connect to the larger arc because palette progression is planned rather than random.

### Character consistency across time
Jenkins spans roughly ten thousand years. Consistency comes from invariant cues:
- Reflective metal presence near hearth or threshold spaces.
- Formal service posture and controlled movement.
- Later monumental scale while retaining gentleness.

For your book, define invariant character markers before generating.

### Atmosphere keywords that unify a series
Keep a small reusable vocabulary (for example in *City*: contemplative, wind-worn, elegiac, ritual, moonlit, subdued, uncanny). Reuse these across prompts to stabilize tonal identity.

### Practical technique: visual constants checklist
Before each generation session, confirm:
- Palette phase matches narrative point.
- At least one recurring motif is present when appropriate.
- Character silhouette and scale cues match prior scenes.
- Atmosphere keywords match the series tone.
- Lighting logic is consistent with time/place in the story.

## Step 5: The Review Loop

### Check outputs against source and series
Review each image on three axes:
- Prompt adherence: did the model render the required elements?
- Series consistency: does it belong with the other images?
- Mood fidelity: does it feel emotionally correct for the passage?

### What to evaluate
- Subject accuracy
- Environment accuracy
- Lighting and palette control
- Material/detail fidelity
- Composition clarity

### Regenerate vs accept (80% rule)
If an image lands around 80% of target and preserves the scene's core meaning, keep it. Regenerate when misses are structural (wrong subject, wrong mood, wrong palette phase, broken continuity). Perfection-seeking across all frames usually reduces throughput and coherence.

### How to refine prompts after misses
When the model misunderstands:
1. Move critical details to the first sentence.
2. Replace abstract adjectives with physical descriptors.
3. Reduce competing secondary subjects.
4. Reassert palette and atmosphere keywords from the style guide.

### Example correction (Jupiter too dark/threatening)
If Jupiter outputs look hostile instead of ecstatic/sublime:
- Add explicit mood language: "ecstatic, transcendent, contemplative awe."
- Increase luminous terms: "painted sky," "radiant mist," "crystalline highlights."
- Remove horror-coded language: "ominous," "menacing," "storm terror."
- Emphasize joy of movement and sensory beauty in the main clause.

## Appendix: City Scene Prompts (The Complete Set)

Each entry below shows the method in action. Here is what the extracted prompt looks like for this scene.

### 1) Autonomous Mower on Suburban Lawn
**Tale 1, "City"**

Here is what the extracted prompt looks like for this scene:

A warm, soft-sunlight suburban lawn where an old man dozes in a chair while a self-directed mower patrols in neat swaths. The mower suddenly opens a side panel, extends a crane arm with grasping steel fingers, plucks a stone from the grass, drops it in a container, and purrs onward. A helicopter skims a sun-washed sky above. The mood is pastel domesticity invaded by twitchy machine intelligence - the first hint of a world outgrowing its human operators.

- Warm sunshine, bulging clipping bag, neat swath lines
- Snap-open panel, articulated crane arm, steel fingers
- Old man with unnecessary cane in lawn chair
- Sun-washed sky, distant helicopter silhouette

### 2) Rusted Automobile on Overgrown Streets
**Tale 1, "City"**

Here is what the extracted prompt looks like for this scene:

A battered, dilapidated automobile rounds a corner on a street swallowed by weeds and grass. Steam hisses from an overheated radiator, blue smoke trails from a muffler-less exhaust. The driver squints through the windshield, dodging invisible ruts beneath the overgrowth. The palette is rust, dry green, and oily blue haze - a fossil-fuel relic navigating streets that nature has already reclaimed.

- Rusty machine, rocking and chugging
- Grass and weeds burying the road surface
- Steam plume and blue exhaust smoke
- Driver squinting stolidly behind the wheel

### 3) Dust Street and the Ruined Adams House
**Tale 1, "City"**

Here is what the extracted prompt looks like for this scene:

A former residential street reduced to a dusty footpath. Across it stands a once-proud house: grey fieldstone front now green with moss, picture windows broken and gaping, stoop consumed by weeds, an elm pressing its branches against the gable. A memory-overlay haunts the scene: children on tricycles, smoke from chimneys, a shirtless man planting the elm with burlap-wrapped roots. Present decay haunted by intact mid-century suburbia.

- Pale dust with every footstep
- Moss-green fieldstone, broken windows, weed-choked lawn
- Elm branch against gable
- Ghostly overlay of former domestic life

### 4) Drizzle Funeral at the Webster Crypt
**Tale 2, "Huddling Place"**

Here is what the extracted prompt looks like for this scene:

Cold drizzle falls from leaden skies, drifting like smoke through bare branches and softening hedges into grey blur. Rain flashes on the metallic bodies of rigid, bowed robots forming an honor line. A black-clad minister reads from a cupped book. Above the crypt door, a moss-mellowed granite figure strains upward in frozen yearning. Six robots carry a casket into a bronze-and-marble resting place and seal it behind a small door and nameplate. Pines frame the scene.

- Lead-grey rain haze, bare trees, blurred hedges
- Silver-gleaming robot bodies in formation
- Moss-softened granite statue over age-greened crypt door
- Bronze and marble interior glimpsed through crypt

### 5) Telepresence Mountain Vista
**Tale 2, "Huddling Place"**

Here is what the extracted prompt looks like for this scene:

A study dissolves: walls melt away, leaving only chair and desk suspended in a vast alien landscape. Golden grass covers a hillside above a lake gripped by purple mountain spurs striped with blue-green pine, rising to jagged snow peaks tinged blue. Wind tears through long grass and twisted trees while late sunlight ignites the far summits crimson. In the foreground, a soft-eyed furry Martian crouches on an elaborate pedestal amid indistinct alien furnishings, gesturing toward the peaks with a furry hand.

- Study-to-panorama dissolution effect
- Gold grass, twisted trees, mountain lake
- Purple/blue-green/snow-blue mountain layering
- Furry Martian on crouching pedestal
- Crimson sunset pooling behind stone peaks

### 6) Webster Trapped in the Closing Room
**Tale 2, "Huddling Place"**

Here is what the extracted prompt looks like for this scene:

A man stands in his study surrounded by memory-objects: dual-world chronometer, dead wife's photo, school trophy, framed Mars memento. Early spring dusk deepens. Pussy-willow scent drifts through a window. Hearth flicker competes with failing resolve. Jenkins appears at the doorway with firelight dancing on his shining metal hide. Then the walls close in - hands grope for the desk edge, the body collapses into the chair, the room becomes a trap that will never release him.

- Memory-laden study at dusk
- Dusty travel bag from high shelf
- Firelight flickering on polished robot metal in doorway
- Constricting-room sensation, hands gripping desk

### 7) Firelit Debate in the Webster House
**Tale 3, "Census"**

Here is what the extracted prompt looks like for this scene:

Two men sit near a hearth while leaping firelight carves hard planes into one man's face, making it almost surrealistic. Long fingers with bone-hard, merciless knuckles extend toward the heat. The room is dark enough that fire and shadow do all the sculpting: glasses lifted against flame, brandy glinting, smoke-crackle between long silences. Outside, autumn wind whispers and a raccoon cries from river bottoms, pressing wilderness against the warm interior.

- Hearth fire as sole light source
- Flame-carved facial planes, surrealistic shadows
- Long-fingered hands with severe knuckles
- Wind and animal cries beyond the walls

### 8) Ant Industry in the Wild Glen
**Tale 3, "Census"**

Here is what the extracted prompt looks like for this scene:

In a remote glen of boulders, oak clumps, and meadow patches, an ant hill bristles with activity. Tiny harnessed ants pull carts along roadways into root-level tunnels - loaded carts inbound, empty carts outbound. Miniature chimneys protrude from the mound belching acrid smoke, implying metallurgy at insect scale. A broken glassite dome still covers parts of the nest, decayed like an abandoned experiment. The surrounding landscape is wild, hushed, untouched.

- Harnessed ants pulling micro-carts on roadways
- Smoking chimneys on the mound
- Broken glassite dome in disrepair
- Wild glen: bluffs, boulders, oak clumps, meadow scraps

### 9) Joe the Mutant in High Grass
**Tale 3, "Census"**

Here is what the extracted prompt looks like for this scene:

In high grass behind a man, a figure materializes: tall and gangling, stoop-shouldered, with hands almost hamlike but fingers tapered white and smooth. His eyes glitter in sunlight. He holds a faint private amusement behind still lips. He hunkers by the ant hill, then rocks with knobby knees hugged to his chest - a feral, elongated silhouette against the broad river valley and open hills. A solitary anomaly in pastoral landscape.

- Gangling frame, stooped shoulders
- Contradictory hands: brutal palms, delicate white fingertips
- Glittering eyes, suppressed amusement
- Rocking posture with hugged knees against open sky

### 10) First Steps on Jupiter
**Tale 4, "Desertion"**

Here is what the extracted prompt looks like for this scene:

The expected toxic deluge resolves into drifting purple mist sliding like fleeing shadows over a red-and-purple sward. Snaking lightning becomes flares of pure ecstasy across a painted sky. A new body feels sleek and powerful as two-hundred-mile-per-hour wind registers as gentle fingers. Two transformed beings run with sheer joy across the vivid ground toward a crystalline cliff. An ammonia waterfall feathers down the shining white face of solid oxygen, breaking into a rainbow of many hundreds of distinct colors - not blended human spectra but hyper-differentiated bands. Music beats through the landscape.

- Purple mist over red/purple ground
- Painted sky with ecstatic lightning flares
- Sleek, powerful alien body forms in motion
- White crystalline cliff of solid oxygen
- Multi-hundred-color ammonia-fall rainbow
- Tiny black dome on the distant horizon

### 11) Empty Geneva Boulevard
**Tale 6, "Hobbies"**

Here is what the extracted prompt looks like for this scene:

A broad marble stoop overlooks a tree-lined boulevard with flowerbeds, polished walks, and nodding tulips in a tiny breeze - all maintained by robots, but almost devoid of people. Birdsong fills bright daylight over what feels like a museum come to life. Inside, the room is cathedral-like: stained-glass windows, soft carpets, aged wood sheen, glinting silver and brass, and a large muted painting of the Webster House above the fireplace.

- Robot-maintained boulevard with tulips and symmetry
- Depopulated "last city" street composition
- Stained-glass interior, patina-rich wood and metal
- Large painting of hilltop house under storm sky

### 12) The Artificial Seashore Room
**Tale 6, "Hobbies"**

Here is what the extracted prompt looks like for this scene:

A door opens into simulated surf: blazing sun over a white straight beach stretching to both horizons, blue ocean with whitecaps. Palm trees shade bright canvas chairs and a pastel jug. Salt tang and wind effects complete the illusion. Behind the scene: mirrors, fans, pumps, synthetic sun-and-moon controls. Tide pools sparkle in residual light. Pure engineered escapism in a dying human city.

- Indoor horizon illusion stretching both ways
- Sun-washed blue sea, foaming wave tips
- Bright chairs, pastel jug, palm shade
- Exposed machinery of manufactured paradise

### 13) Wolf Offers Rabbit to Dog on Forest Trail
**Tale 6, "Hobbies"**

Here is what the extracted prompt looks like for this scene:

A little black dog skids to a stop on a spring forest trail. In the path stands a wolf with a rabbit's bloody body hanging from its jaws. The dog pants, red tongue lolling. A pint-size robot slides in alongside. The wolf's yellow feral stare slowly cools. Step by cautious step, the wolf advances, then carefully lays the rabbit on the ground. Dog and wolf nearly touch noses. Then the wolf reclaims the rabbit in gaping jaws, tail moving in an almost-wag, and vanishes as a grey blur through trees.

- Little black dog mid-skid, red tongue out
- Wolf with prey in jaws, yellow wildness in eyes
- Two-foot standoff, nose-to-nose contact
- Grey blur disappearing through spring forest

### 14) Webster House Seen from Below
**Tale 6, "Hobbies"**

Here is what the extracted prompt looks like for this scene:

The forest thins into gnarled, scattered oaks like hobbling old men climbing a hill. At the top sits a huddled house that has taken root and crouched close to the earth. So old it shares the color of grass, flowers, trees, sky, and weather. Built by men who loved it, died in by a legendary family. Wind sucks along the eaves on stormy nights. Cowbells tinkle and pups bark, bringing in cows for evening milking - pastoral rhythm around an ancient structure.

- Gnarled oaks ascending the slope
- Crouched, earth-hugging house profile
- Weather-faded camouflage coloring (grass/sky/earth tones)
- Pastoral dusk: cowbells, barking pups, evening milking

### 15) Grey Shadow on the Rocky Ledge
**Tale 7, "Aesop"**

Here is what the extracted prompt looks like for this scene:

A grey shadow glides along a rocky ledge in slanting early-afternoon light. Its face and body are indistinct and murky, like morning mist rising from a gully. The ledge dead-ends before a den that no longer exists. The creature crouches against stone. Tufted tentacles rise from its ears and search the air. The world below hums with dense life across marching hills. A swallow's nest is plastered on the cliff where none had been before. Everything is familiar yet wrong - this is a different world.

- Grey, mist-like creature silhouette on cliff
- Tufted ear-tentacles, crouched predatory posture
- Swallow nest on rocky wall
- River shifted closer to bluffs
- Valley of marching hills dense with life

### 16) Robin Shot Under Blue Noon
**Tale 7, "Aesop"**

Here is what the extracted prompt looks like for this scene:

Under trees, a man whittles a smooth wand while a wolf with a neatly wrapped bushy tail and a squirrel perched on his shoulder watch. He bends a hickory shaft into an arc with cord tension and launches. The projectile whistles. The robin falls in a burst of flying feathers, lands on its back with clenched claws pointing up, blood staining a leaf beneath. Noon-blue sky and suddenly frozen leaves. The clouds float but everything alive has stopped. First killing in five thousand years.

- Knife-worked bow, hickory arc and cord
- Robin strike: feather burst, blood on leaf, limp claws up
- Blue noon sky, unstirring leaves, floating clouds
- Wolf and squirrel as stunned witnesses

### 17) Mutant Castle - Door to a Desert World
**Tale 7, "Aesop"**

Here is what the extracted prompt looks like for this scene:

A black castle shimmers in moonlight: windowless, unlit, no bell or knocker, reached by broad stone steps. Inside: an old hollow room saturated with dust and silence, dust-covered furniture, tools, gadgets, and books. One interior door opens not to another chamber but to a blast of heat and a gold-yellow desert under a blazing blue sun. A green-purple lizard-like thing skitters across sand at the threshold between worlds.

- Black shimmering fortress exterior in moonlight
- Dust-thick abandoned interior with massive bookcase
- Portal threshold: one foot in dust, one in alien desert
- Blazing blue sun, gold sand, green-purple lizard creature

### 18) Archie the Raccoon Facing the Building
**Tale 8, "The Simple Way"**

Here is what the extracted prompt looks like for this scene:

A small renegade raccoon crouches on an autumn hillside, batting at tiny scurrying black things in the grass. His fur ruffles in cold wind, tail tucked around his feet, bright beady eyes scanning the slopes. Across the river valley, the Building rises as a dark smudge above the far hills - once the size of a house, now a township, still growing. A cloudy terror for the little forest folk. In the night, its menace becomes pulsing otherness singing between worlds.

- Raccoon silhouette in autumn wind, tucked tail
- Tiny ticking ant-things swarming in grass
- Dark megastructure smudge on far horizon
- Cloud of ominous growth, sprawling and towering

### 19) Jenkins Returns in the Gift Body
**Tale 8, "The Simple Way"**

Here is what the extracted prompt looks like for this scene:

At night, a door opens on a robot larger than any the dog has seen: gleaming, huge, massive, polished, glowing like slow fire in darkness. A raccoon rides perched on its shoulder - stark scale contrast. Despite immense weight the robot moves cat-soft, projecting metal gentleness and armored strength. Seven thousand years of service in a body built to last another seven thousand.

- Monumental polished robot with fire-like sheen
- Shoulder-perched raccoon, tiny against gleaming chassis
- Cat-soft movement despite massive weight
- Doorway framing, darkness behind, warmth ahead

### 20) Winter Hilltop - The Simple Way
**Tale 8, "The Simple Way"**

Here is what the extracted prompt looks like for this scene:

Jenkins stands on a hilltop in the first rough wind of winter. Below, the river slope is etched in black and grey by leafless tree skeletons. To the northeast rises the Building - shadow-shape, cloud of evil omen, spawned in the mind of ants. He knows the human way to deal with ants: poison. But the Dogs know no chemistry, and there has been no killing for five thousand years. He turns slowly and goes down the hill. The final image of the book: a lone robot descending into a world that has outgrown the answer he carries.

- Black-grey winter palette, bare-tree linework
- Wind-scoured hilltop vantage point
- Distant ant megastructure as dark cloud on horizon
- Lone robot figure descending the slope
