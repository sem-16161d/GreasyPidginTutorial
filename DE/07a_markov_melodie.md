# Markov-Melodie

Eine Einführung in die Erzeugung von Melodien mit Markov-Ketten und GreasyPidgin.

Am Ende dieses Tutorials hast du eine MIDI-Datei mit einer Melodie, deren **Tonhöhen** durch ein Markov-Modell bestimmt werden — ein Modell, das lernt, welche Töne in einer musikalischen Folge aufeinander folgen.

---

## Was ist eine Markov-Kette?

Eine Markov-Kette ist ein stochastisches Modell, das beschreibt, wie ein System von einem Zustand in den nächsten übergeht. Die zentrale Eigenschaft: der nächste Zustand hängt **nur vom aktuellen Zustand** ab — nicht von der gesamten Vorgeschichte.

In der Musik bedeutet das: gegeben der aktuelle Ton, mit welcher Wahrscheinlichkeit folgt welcher nächste Ton? Diese Wahrscheinlichkeiten werden in **Übergangsregeln** kodiert.

## Gesamtüberblick

Der vollständige Datenfluss:

```
Markov-Regeln (Tonhöhen + Gewichte)
    ↓
MarkovChain.getNElements()
    ↓
Liste von MIDI-Tonhöhen
    ↓
Gesture.fromLists()
    ↓
MIDI-Datei
```

---

## Schritt 1 — Importe

```python
from GreasyPidgin.Gesture import Gesture
from GreasyPidgin.MarkovChains import MarkovChain, MarkovRule, MarkovRules
```

| Import | Funktion |
|---|---|
| `Gesture` | Eine musikalische Geste — eine Folge von Noten |
| `MarkovChain` | Erzeugt Sequenzen durch Markov-Übergänge |
| `MarkovRule` | Eine einzelne Übergangsregel: von einem Zustand zu möglichen Nachfolgern |
| `MarkovRules` | Eine validierte Sammlung von `MarkovRule`-Objekten |

---

## Schritt 2 — Übergangsregeln definieren

```python
rule60 = MarkovRule(60, [63, 64, 67, 68], [4,1,4,4])
rule63 = MarkovRule(63, [60,67,68],[1,2,1])
rule64 = MarkovRule(64, [60],[1])
rule67 = MarkovRule(67, [60,63,68],[1,1,2])
rule68 = MarkovRule(68, [60,67],[1,2])
```

Jede `MarkovRule` hat drei Argumente:

| Argument | Bedeutung |
|---|---|
| Erstes | Der aktuelle Zustand (MIDI-Tonhöhe) |
| Zweites | Liste möglicher Nachfolgetöne |
| Drittes | Relative Gewichte (höher = wahrscheinlicher) |

`rule60` bedeutet: wenn der aktuelle Ton MIDI 60 (C4) ist, folgt mit hoher Wahrscheinlichkeit MIDI 63 oder 68, seltener 64.

:::{note}
Die Gewichte werden automatisch normiert — es kommt nur auf ihre Verhältnisse zueinander an, nicht auf absolute Werte. `[4,1,4,4]` bedeutet, dass 63, 67 und 68 je viermal so wahrscheinlich sind wie 64.
:::

Die hier definierten Töne — 60, 63, 64, 67, 68 — entsprechen c4, ds4, e4, g4, Ab4

---

## Schritt 3 — Die Markov-Kette aufbauen

```python
seed = 60
numElements = 200

mr = MarkovRules([rule60,rule63,rule64,rule67,rule68])
mc = MarkovChain(rules=mr, seed=seed)
```

`MarkovRules` überprüft die Vollständigkeit der Regeln: jeder Ton, der als Nachfolger auftauchen kann, muss auch selbst eine Regel haben. Fehlt eine Regel, gibt es eine Warnung.

`seed = 60` setzt den Startzustand — die erste Tonhöhe der Sequenz.

---

## Schritt 4 — Sequenz generieren

```python
pitchListMidi = mc.getNElements(n=numElements)
```

`getNElements(n=200)` erzeugt 200 Töne durch sukzessive Anwendung der Übergangsregeln. Das Ergebnis ist eine Liste von MIDI-Tonhöhen — die Melodie.

:::{tip}
`getNElements` gibt auch den Startzustand zurück. Die Liste hat also `n + 1 = 201` Elemente: `[seed, t1, t2, ..., t200]`. Das `size`-Argument von `Gesture.fromLists` sollte daher ebenfalls `numElements + 1` oder `numElements` sein, je nachdem ob du den Seed mithörst oder nicht.
:::

---

## Schritt 5 — Geste aufbauen und exportieren

```python
Gesture.fromLists(numElements, 0, 0.5, 0.5, pitchListMidi, bpm=161, timeUnit='beats').toMidi()
```

| Argument | Wert | Bedeutung |
|---|---|---|
| `size` | `numElements` (200) | Anzahl der Noten |
| `startOffset` | `0` | Beginn bei Taktschlag 0 |
| `startDeltas` | `0.5` | Jede Note beginnt einen halben Beat nach der vorherigen |
| `durations` | `0.5` | Jede Note dauert einen halben Beat |
| `pitches` | `pitchListMidi` | Die 200 Markov-Tonhöhen |
| `bpm` | `161` | Tempo |
| `timeUnit` | `'beats'` | Zeiten in Taktschlägen angegeben |

---

## Experimente

**Andere Starttöne:**
```python
seed = 63   # beginnt auf D♯4
seed = 67   # beginnt auf G4
```

**Andere Gewichte — mehr Wiederholungen:**
```python
rule60 = MarkovRule(60, [60, 63, 67, 68], [8, 2, 2, 2])   # bleibt oft auf C4
```

**Längere Sequenz:**
```python
numElements = 500
```

**Andere Notendauern — 16tel statt 8tel:**
```python
Gesture.fromLists(numElements, 0, 0.25, 0.25, pitchListMidi, bpm=161, timeUnit='beats').toMidi()
```
