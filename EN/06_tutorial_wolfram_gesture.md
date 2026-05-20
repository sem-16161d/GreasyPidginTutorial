# Composing with Cellular Automata

A beginner-friendly guide to generating music from a Wolfram elementary cellular automaton using GreasyPidgin.

By the end of this tutorial you will have a MIDI file containing a melody whose **pitches** come from the evolving state of a cellular automaton, and whose **rhythmic pattern** is determined by the binary cells of that automaton.

---

## What is a Cellular Automaton?

A cellular automaton (CA) is a grid of cells, each either **on** (1) or **off** (0). At every step, each cell looks at its neighbours and updates its state according to a fixed rule. Running many steps produces surprisingly complex, often musical patterns from very simple starting conditions.

We use a **Wolfram elementary CA**: one row of cells, each looking at its left neighbour, itself, and its right neighbour — three cells, eight possible combinations. The rule number (0–255) defines what happens in each case.

```{figure} https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/CA_rule30s.png/400px-CA_rule30s.png
:alt: Wolfram Rule 30
Wolfram Rule 30 — complex behaviour from a simple rule
```

---

## Step 1 — Imports

```python
from GreasyPidgin.TimeGrid import TimeGrid, beatToSec
from GreasyPidgin.Normalisation import scale
from GreasyPidgin import spntom
from GreasyPidgin.PitchGrid import PitchGrid
from GreasyPidgin.Gesture import Gesture
from GreasyPidgin.CellularAutomata import CellularAutomaton, CellularRules, intToBinary
```

Each import brings in one tool:

| Import | What it does |
|---|---|
| `TimeGrid` | A set of time positions in seconds |
| `beatToSec` | Converts a beat number to seconds at a given BPM |
| `scale` | Maps a value from one range to another |
| `spntom` | Converts a note name like `'e2'` to a MIDI number |
| `PitchGrid` | A set of pitches in a chosen tuning and scale |
| `Gesture` | A musical gesture — a sequence of Phonons (notes) |
| `CellularAutomaton` | Runs the CA forward in time |
| `CellularRules` | Defines the CA rule table |
| `intToBinary` | Converts an integer to a list of 0s and 1s |

---

## Step 2 — Basic Parameters

```python
path             = "/Users/sraw/Documents/GreasyPidgin/MIDI/"
lowestPitchMidi  = spntom('e2')   # E2  = MIDI 40
highestPitchMidi = spntom('e6')   # E6  = MIDI 88
bpm              = 161
stepSizeBeats    = 0.5            # each CA cell = half a beat
```

`spntom` (Scientific Pitch Notation to MIDI) converts note names to MIDI numbers. `'e2'` is the lowest note and `'e6'` is the highest — these define the pitch range the melody will use.

`stepSizeBeats = 0.5` means each cell in the CA grid corresponds to half a beat (an eighth note at the given BPM).

---

## Step 3 — Building the Pitch Grid

```python
pitchGrid = PitchGrid.fromMask(
    'edo12', 'lydianSharp2',
    lowestPitchMidi, highestPitchMidi,
    lowestPitchMidi, lowestPitchMidi
)
```

A `PitchGrid` is a set of allowed MIDI pitches — a kind of musical sieve. Instead of allowing every semitone, we restrict pitches to a specific **scale within a tuning system**.

- `'edo12'` — standard 12-tone equal temperament
- `'lydianSharp2'` — a mode from the harmonic minor family: like Lydian but with a raised 2nd degree, giving an exotic, bright quality
- The register runs from `lowestPitchMidi` to `highestPitchMidi`

Later, when the CA generates raw numbers, we snap them to this grid — so every pitch in the output is a valid scale degree.

:::{note}
`PitchGrid.fromMask` takes: tuning system, mask name, lowest pitch, highest pitch, tuning system root, scale root. Passing `lowestPitchMidi` for both roots anchors the scale on E.
:::

---

:::{important}
**Binary and integers are two views of the same number.**

Every row of cells in the CA is secretly an integer. Reading the cells
left to right as a binary number — `0 0 1 1 0 0 1 0` — gives you 50.
Going the other way, `intToBinary(50, 8)` gives back `[0, 0, 1, 1, 0, 0, 1, 0]`.

This is why the starting state `gen0Int = 50` and the pitch curve from
`generationsToEnvelope()` are related: the envelope reads each generation's
row as an integer, and those integers trace the melody. The binary list drives
the rhythm. Same data, two readings.
:::

## Step 4 — Setting Up the Cellular Automaton

```python
numGenerations = 40
gen0Int        = 50
gen0           = intToBinary(gen0Int, 16)
```

`gen0` is the initial state — a row of 16 cells. We start from the integer 50, which in binary is `0000000000110010`. This gives us a specific starting pattern rather than a random one — using an integer makes it easy to reproduce and document.

```python
ruleNumber = 140
filename   = f"wolfram_{ruleNumber}_gen0_{gen0Int}_numGenerations{numGenerations}.mid"

wolfram = CellularRules.elementaryWolfram(ruleNumber)
ca      = CellularAutomaton(rules=wolfram, gen0=gen0)
ca.iterate(numGenerations)
```

`CellularRules.elementaryWolfram(140)` builds the lookup table for Wolfram rule 140. `ca.iterate(40)` runs the automaton forward 40 generations, storing every generation in `ca.generations`.

The filename encodes the rule number and starting conditions — essential for reproducibility.

```python
env        = ca.generationsToEnvelope()
binaryList = ca.concatenateGenerations()
```

Two different views of the CA output:

- `generationsToEnvelope()` — converts each generation's binary cells into a single integer (reading the row as a binary number), then wraps those integers as an `Envelope` (a breakpoint function over time). This gives a smooth curve we can use for pitch mapping.
- `concatenateGenerations()` — flattens all 40 generations into one long list of 0s and 1s (`40 × 16 = 640 values`). This is the raw rhythm data.

---

## Step 5 — Mapping the CA to Pitches

```python
pitchSeq = []
for i in range(numGenerations):
    y            = env.getValue(i / numGenerations, True, True)
    rawMidi      = scale(y, 0, 1, lowestPitchMidi, highestPitchMidi)
    quantisedMidi = pitchGrid.quantise(rawMidi)
    pitchSeq.append(quantisedMidi)
```

For each of the 40 generations we:

1. **Read the envelope** at a normalised time position `i / numGenerations` (0.0 → 1.0). The `True, True` arguments enable normalisation so the output is in `[0, 1]`.
2. **Scale** that 0–1 value into the MIDI pitch range with `scale()`.
3. **Quantise** to the nearest allowed pitch in the `pitchGrid` — snapping to the LydianSharp2 scale.

The result is a list of 40 MIDI pitches, one per generation, following the CA's evolving integer values.

---

## Step 6 — Mapping the CA to Rhythms

```python
startTimesSec = []

for i, bin in enumerate(binaryList):
    startTimeBeats = i * stepSizeBeats
    if bin == 1:
        startTimeSec = beatToSec(startTimeBeats, bpm)
        startTimesSec.append(startTimeSec)
```

`binaryList` has 640 values (0 or 1). Each position represents one half-beat step. When a cell is **1**, a note onset is placed there; when it is **0**, silence. `beatToSec` converts the beat position to seconds using the BPM.

The result is a list of onset times in seconds — only the positions where the CA has a `1`.

```python
tg      = TimeGrid(startTimesSec, bpm=161)
deltaTs = tg.differentiate()
```

`TimeGrid` wraps the onset times into a musical time structure. `differentiate()` converts the absolute times into **inter-onset intervals** (the time between consecutive onsets) — the format `Gesture.fromLists` needs.

:::{note}
`differentiate()` follows the SuperCollider convention: the first value is always 0 (the delta of the first element with itself), and each subsequent value is the gap to the next onset.
:::

---

## Step 7 — Building the Gesture

```python
g = Gesture.fromLists(
    numGenerations, 0,
    deltaTs, 0.125, pitchSeq, 100,
    bpm=bpm
)
g.toMidi(path + filename)
```

`Gesture.fromLists` assembles everything into a musical gesture:

| Argument | Value | Meaning |
|---|---|---|
| `size` | `numGenerations` (40) | Number of notes |
| `startOffset` | `0` | Start at time zero |
| `startDeltas` | `deltaTs` | Inter-onset intervals in seconds |
| `durations` | `0.125` | Fixed note duration (eighth note) |
| `pitches` | `pitchSeq` | The 40 MIDI pitches from the CA |
| `dynamics` | `100` | Fixed velocity |
| `bpm` | `161` | Tempo for MIDI export |

Finally, `g.toMidi(...)` writes the MIDI file. The filename encodes the rule number and initial conditions so you can always recreate the exact same output.

---

## Putting It All Together

The full data flow:

```{mermaid}
graph LR
    A["Integer 50\n(gen0)"] --> B["CellularAutomaton\nRule 140, 40 generations"]
    B --> C["generationsToEnvelope\n→ pitch curve"]
    B --> D["concatenateGenerations\n→ binary rhythm"]
    C --> E["scale + quantise\n→ pitchSeq (40 notes)"]
    D --> F["TimeGrid\n→ onset times"]
    F --> G["differentiate\n→ deltaTs"]
    E --> H["Gesture.fromLists"]
    G --> H
    H --> I["MIDI file"]
```

The cellular automaton generates **both** the melody and the rhythm from a single source — just read two different ways. This is what makes the technique musically coherent: pitch and rhythm share the same underlying structure.

---

## Experiments to Try

**Change the rule number:**
```python
ruleNumber = 30   # chaotic
ruleNumber = 110  # complex, Turing-complete
ruleNumber = 90   # Sierpinski triangle
```

**Change the starting pattern:**
```python
gen0Int = 1       # single active cell in the middle
gen0Int = 255     # all cells on
gen0Int = 42      # arbitrary — document and listen
```

**Change the scale:**
```python
pitchGrid = PitchGrid.fromMask('edo12', 'phrygian', ...)
pitchGrid = PitchGrid.fromMask('werckmeister1', 'dorian', ...)
```

**Change the step size:**
```python
stepSizeBeats = 0.25   # sixteenth notes — denser rhythms
stepSizeBeats = 1.0    # quarter notes — sparser
```

Each combination of rule / starting pattern / scale is a unique composition. The filename convention (`wolfram_140_gen0_50_numGenerations40.mid`) makes it easy to catalogue your explorations.
