# Markov-Melodie mit Markov-Rhythmus

Eine Einführung in die gleichzeitige Verwendung von zwei unabhängigen Markov-Ketten: eine für **Tonhöhen** (über Intervalle), eine für **Rhythmus** (über Notenwerte).

Dies ist die Zusammenführung der beiden vorherigen Tutorials. Zwei unabhängige stochastische Prozesse erzeugen je eine eigene Dimension der Musik — und werden am Ende in einer einzigen Geste kombiniert.

---

## Zwei Ketten, eine Musik

Das Entscheidende an diesem Ansatz: Tonhöhe und Rhythmus sind **entkoppelt**. Jede Dimension hat ihre eigene Markov-Logik, ihre eigene Entwicklung. Beide sind durch Übergangswahrscheinlichkeiten gestaltet — aber sie kennen einander nicht.

Das erzeugt eine charakteristische Textur: rhythmische Muster und melodische Gesten entwickeln sich unabhängig voneinander, überlagern sich zufällig und erzeugen dabei eine Komplexität, die mit rein manueller Komposition schwer zu erreichen wäre.

## Gesamtüberblick

```
Intervall-Markov-Kette               Rhythmus-Markov-Kette
    ↓                                     ↓
Intervallsequenz                      Notenwerte (Brüche)
    ↓                                     ↓
Integration + Oktavkorrektur          Skalierung (* 4)
    ↓                                     ↓
pitchListMidi                         rhtmsMatched
          ↘                         ↙
                Gesture.fromLists()
                       ↓
                  MIDI-Datei
```

---

## Schritt 1 — Importe

```python
from GreasyPidgin.Pitch import forceIntoRangeMidi
from GreasyPidgin.Gesture import Gesture
from random import choices
from GreasyPidgin.MarkovChains import MarkovChain, MarkovRule, MarkovRules
```

---

## Schritt 2 — Intervall-Kette (Tonhöhen)

```python
rule5Down  = MarkovRule(-7, [0,  5,  1],       [2, 1, 1])
ruleM3Down = MarkovRule(-3, [0,  5, -7],       [4, 2, 1])
ruleM2Down = MarkovRule(-1, [1, -7],           [1, 1])
rule1      = MarkovRule( 0, [0, -1, 1, 5, -7], [1, 2, 2, 2, 1])
ruleM2Up   = MarkovRule( 1, [0, -1,  3],       [2, 1, 1])
ruleM3Up   = MarkovRule( 3, [1, -3,  3],       [4, 1, 4])
rule4Up    = MarkovRule( 5, [-1,  1],          [1, 1])

seed = 1
numElements = 200

mr = MarkovRules([rule1, rule5Down, ruleM3Down, ruleM2Down, ruleM2Up, ruleM3Up, rule4Up])
mc = MarkovChain(rules=mr, seed=seed)

intervalListMidi = mc.getNElements(n=numElements)

pitchListMidi = [57]
for intrvl in intervalListMidi:
    candidate = pitchListMidi[-1] + intrvl
    pitchMidi = forceIntoRangeMidi(candidate, 48, 90)
    pitchListMidi.append(pitchMidi)
```

Identisch mit dem Intervall-Tutorial. Die Kette erzeugt 200 Intervalle, die dann zu absoluten Tonhöhen integriert werden. Startnote: A3 (MIDI 57), Register: A2–F♯6.

---

## Schritt 3 — Rhythmus-Kette

```python
ruleHalbe  = MarkovRule(1/2,  [1/2, 1/4, 1/16], [1, 1, 0.5])
rule4tel   = MarkovRule(1/4,  [1/2, 1/8],        [1, 1])
rule8tel   = MarkovRule(1/8,  [1/16, 1/8],       [1, 4])
rule16tel  = MarkovRule(1/16, [1/16, 1/2],       [8, 1])

seedRhthm = 1/2

mrRhthm = MarkovRules([ruleHalbe, rule4tel, rule8tel, rule16tel])
mcRhthm = MarkovChain(rules=mrRhthm, seed=seedRhthm)

rhthmsRaw = mcRhthm.getNElements(n=numElements)
rhtmsMatched = [r * 4 for r in rhthmsRaw]
```

Identisch mit dem Rhythmus-Tutorial. Die Kette erzeugt 200 Notenwerte als Taktbrüche, die dann in Taktschläge skaliert werden.

:::{note}
Beide Ketten erzeugen `numElements = 200` Elemente. Die Listen `pitchListMidi` und `rhtmsMatched` haben also dieselbe Länge — Voraussetzung dafür, dass `Gesture.fromLists` sie paarweise zuordnet.

Der Seed von `pitchListMidi` ergibt technisch 201 Elemente (`[57] + 200 generierte`). Das erste Element ist der Startnoten-Seed und wird durch `size = numElements` automatisch auf die ersten 200 Elemente begrenzt.
:::

---

## Schritt 4 — Beide Ketten kombinieren

```python
Gesture.fromLists(numElements, 0, rhtmsMatched, rhtmsMatched, pitchListMidi, bpm=161, timeUnit='beats').toMidi()
```

Die Kombinationslogik ist einfach: `Gesture.fromLists` nimmt die Listen als parallele Streams entgegen. Element `i` von `pitchListMidi` wird mit Element `i` von `rhtmsMatched` kombiniert — erste Note mit erster Notendauer, zweite Note mit zweiter Notendauer usw.

Die Unabhängigkeit der beiden Ketten bedeutet: ein langer Ton (Halbe) kann genausogut auf einem Ton landen, der einem langen Sprung folgte, wie auf einem, der einem Sekundschritt folgte. Diese zufällige Überlagerung erzeugt den charakteristischen Klang des Stücks.

:::{tip}
**Kompositorische Kontrolle durch Gewichtung**

Auch wenn die beiden Ketten unabhängig sind, lässt sich ihr Zusammenspiel indirekt steuern:

- Hohe Wiederholungsgewichtung in der Intervall-Kette → statischere Melodie → rhythmisches Muster tritt stärker hervor
- Viele Sechzehntel in der Rhythmus-Kette → schnelle Läufe, bei denen melodische Sprünge besonders auffallen
- Lange Töne (Halbe, Ganze) in der Rhythmus-Kette → einzelne Intervallbewegungen bekommen mehr Gewicht

:::

---

## Experimente

**Rhythmisch dichtere Version:**
```python
rule16tel = MarkovRule(1/16, [1/16, 1/2], [16, 1])   # Sechzehntel-Läufe dominieren
```

**Melodisch ruhigere Version:**
```python
rule1 = MarkovRule(0, [0, -1, 1, 5, -7], [8, 2, 2, 1, 1])   # mehr Wiederholungen
```

**Andere Startsituation:**
```python
seed      = -3     # beginnt mit kleiner Terz abwärts
seedRhthm = 1/16   # beginnt mit Sechzehntel-Lauf
```

**Ungleiche Elementzahlen** — Rhythmus als Schleife über die Melodie:
```python
numRhythm  = 50
rhthmsRaw = mcRhthm.getNElements(n=numRhythm)
rhtmsMatched = [r * 4 for r in rhthmsRaw]
# fromLists wiederholt rhtmsMatched zyklisch über 200 Noten
Gesture.fromLists(numElements, 0, rhtmsMatched, rhtmsMatched, pitchListMidi, bpm=161, timeUnit='beats').toMidi()
```

Durch unterschiedliche Längen entstehen **Polyrhythmen zwischen Melodie und Rhythmik** — das rhythmische Pattern wiederholt sich alle 50 Noten, die melodische Bewegung alle 200.
