# Markov-Intervalle

Eine Einführung in die Erzeugung von Melodien über **Intervall-Markov-Ketten** mit GreasyPidgin.

Im Unterschied zur direkten Tonhöhen-Markov-Kette werden hier nicht die absoluten Tonhöhen als Zustände verwendet, sondern **Intervalle** — die Abstände zwischen aufeinanderfolgenden Tönen in Halbtönen. Das Ergebnis ist eine Melodie, deren Bewegungscharakter (Sprünge, Schritte, Wiederholungen) durch das Modell gelernt wurde — unabhängig von der Ausgangstonhöhe.

---

## Intervalle statt Tonhöhen

Der entscheidende Unterschied zur Melodie-Variante:

| Ansatz | Zustand | Modelliert |
|---|---|---|
| Tonhöhen-Markov | MIDI-Nummer (60, 63, ...) | Welcher Ton folgt |
| **Intervall-Markov** | Halbton-Abstand (-7, -3, 0, ...) | Welche **Bewegung** folgt |

Die Intervall-Variante ist **transponierfähig**: dasselbe Modell klingt in jeder Tonart gleich, weil es die melodische Geste beschreibt, nicht die absoluten Töne.

## Gesamtüberblick

```
Markov-Regeln (Intervalle + Gewichte)
    ↓
MarkovChain.getNElements()
    ↓
Liste von Intervallen (Halbtöne)
    ↓
Integration: Startnote + kumulative Summe der Intervalle
    ↓
forceIntoRangeMidi: Oktavkorrektur
    ↓
Gesture.fromLists()
    ↓
MIDI-Datei
```

---

## Schritt 1 — Importe

```python
from GreasyPidgin.Pitch import forceIntoRangeMidi
from GreasyPidgin.Gesture import Gesture
from GreasyPidgin.MarkovChains import MarkovChain, MarkovRule, MarkovRules
```

`forceIntoRangeMidi` ist neu gegenüber der Melodie-Variante: es verschiebt Töne, die außerhalb des gewünschten Registers liegen, um Oktaven nach oben oder unten — ohne die Tonhöhenklasse zu verändern.

---

## Schritt 2 — Intervall-Regeln definieren

```python
rule5Down  = MarkovRule(-7, [0,  5,  1],    [2, 1, 1])
ruleM3Down = MarkovRule(-3, [0,  5, -7],    [4, 2, 1])
ruleM2Down = MarkovRule(-1, [1, -7],        [1, 1])
rule1      = MarkovRule( 0, [0, -1, 1, 5, -7], [1, 2, 2, 2, 1])
ruleM2Up   = MarkovRule( 1, [0, -1,  3],    [2, 1, 1])
ruleM3Up   = MarkovRule( 3, [1, -3,  3],    [4, 1, 4])
rule4Up    = MarkovRule( 5, [-1,  1],       [1, 1])
```

Die Zustände sind Intervalle in Halbtönen:

| Zustand | Intervall |
|---|---|
| `-7` | Quinte abwärts |
| `-3` | Kleine Terz abwärts |
| `-1` | Kleiner Sekundschritt abwärts |
| `0` | Wiederholung (kein Sprung) |
| `1` | Kleiner Sekundschritt aufwärts |
| `3` | Kleine Terz aufwärts |
| `5` | Quarte aufwärts |

:::{note}
Das Modell beschreibt eine Melodik, die sich bevorzugt in kleinen Schritten bewegt, gelegentlich Terzen springt und selten große Sprünge macht.
:::

Die Übergangslogik beschreibt musikalisches Verhalten:

- Nach einer **Wiederholung** (`0`) folgen am häufigsten Sekundschritte in beide Richtungen oder eine Quarte aufwärts — die Melodie „entscheidet sich".
- Nach einer **kleinen Terz aufwärts** (`3`) folgt meist wieder eine kleine Terz oder ein Sekundschritt aufwärts — **sequenzartige Bewegungen** entstehen.
- Nach einer **Quinte abwärts** (`-7`) folgt oft eine Wiederholung — der Sprung landet auf einer wichtigen Note und bleibt dort kurz.

---

## Schritt 3 — Intervallsequenz generieren

```python
seed = 1
numElements = 200

mr = MarkovRules([rule1, rule5Down, ruleM3Down, ruleM2Down, ruleM2Up, ruleM3Up, rule4Up])
mc = MarkovChain(rules=mr, seed=seed)

intervalListMidi = mc.getNElements(n=numElements)
```

`seed = 1` bedeutet: die Kette beginnt mit einem Sekundschritt aufwärts. Die Ausgabe ist eine Liste von 200 Intervallen.

---

## Schritt 4 — Intervalle in Tonhöhen umrechnen

```python
pitchListMidi = [57]
for intrvl in intervalListMidi:
    candidate = pitchListMidi[-1] + intrvl
    pitchMidi = forceIntoRangeMidi(candidate, 48, 90)
    pitchListMidi.append(pitchMidi)
```

Der Starton ist MIDI 57 (A3). Jedes Intervall wird auf den letzten Ton addiert — das ist **Integration**: aus Differenzen werden absolute Werte.

`forceIntoRangeMidi(candidate, 48, 90)` stellt sicher, dass die Melodie im Register A2–Fs6 bleibt. Töne, die diesen Bereich nach oben oder unten verlassen würden, werden um eine Oktave verschoben.

:::{important}
**Integration — von Intervallen zu Tonhöhen**

Das Intervall-Modell lernt die **Bewegung** einer Melodie. Die Integration rekonstruiert daraus die absoluten Töne — beginnend von jedem beliebigen Startton.
:::

---

## Schritt 5 — Geste aufbauen und exportieren

```python
Gesture.fromLists(numElements, 0, 0.5, 0.5, pitchListMidi, bpm=161, timeUnit='beats').toMidi()
```

Identisch zur Melodie-Variante — der einzige Unterschied liegt in der Herkunft von `pitchListMidi`.

---

## Experimente

**Anderen Startnoten:**
```python
pitchListMidi = [60]   # C4
pitchListMidi = [69]   # A4
```

**Engeres Register — mehr Oktavkorrekturen:**
```python
pitchMidi = forceIntoRangeMidi(candidate, 55, 79)   # G3 bis G5
```

**Andere Sprunggewichtung — lyrischer:**
```python
ruleM3Up = MarkovRule(3, [1, 3], [3, 1])   # Terz führt meist zu Sekundschritt
rule5Down = MarkovRule(-7, [1, 0], [2, 1]) # Quintfall führt aufwärts
```

**Sequenzielle Muster verstärken:**
```python
ruleM3Up = MarkovRule(3, [1, -3, 3], [1, 1, 8])   # Terz-Sequenzen dominieren
```
