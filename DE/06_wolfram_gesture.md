# Zellulärer Automat à la Wolfram

Eine einführende Anleitung zur Musikgenerierung mit einem Wolfram-Elementarautomaten und GreasyPidgin.

Am Ende dieses Tutorials hast du eine MIDI-Datei mit einer Melodie, deren **Tonhöhen** aus dem sich entwickelnden Zustand eines zellulären Automaten stammen und deren **Rhythmik** durch die binären Zellen desselben Automaten bestimmt wird.

---

## Was ist ein Zellulärer Automat?

Ein zellulärer Automat (ZA) ist ein Gitter aus Zellen, die jeweils entweder **aktiv** (1) oder **inaktiv** (0) sind. In jedem Schritt schaut jede Zelle auf ihre Nachbarn und aktualisiert ihren Zustand nach einer festen Regel. Viele Schritte hintereinander erzeugen überraschend komplexe, oft musikalische Muster aus sehr einfachen Ausgangsbedingungen.

Wir verwenden einen **Wolfram-Elementarautomaten**: eine Zeile von Zellen, von denen jede auf ihren linken Nachbarn, sich selbst und ihren rechten Nachbarn schaut — drei Zellen, acht mögliche Kombinationen. Die Regelnummer (0–255) legt fest, was in jedem Fall passiert.

## Gesamtüberblick

Der vollständige Datenfluss:

```{image} IMG/flowchartWolfram.png

:align: center
```

Der zelluläre Automat erzeugt **sowohl** die Melodie als auch den Rhythmus aus einer einzigen Quelle — nur auf zwei verschiedene Arten gelesen. Genau das macht die Technik musikalisch kohärent: Tonhöhe und Rhythmus teilen dieselbe zugrundeliegende Struktur.

---
---

## Schritt 1 — Importe

```python
from GreasyPidgin.TimeGrid import TimeGrid, beatToSec
from GreasyPidgin.Normalisation import scale
from GreasyPidgin import spntom
from GreasyPidgin.PitchGrid import PitchGrid
from GreasyPidgin.Gesture import Gesture
from GreasyPidgin.CellularAutomata import CellularAutomaton, CellularRules, intToBinary, binaryToInt
```

Jeder Import stellt ein Werkzeug bereit:

| Import | Funktion |
|---|---|
| `TimeGrid` | Eine Menge von Zeitpositionen in Sekunden |
| `beatToSec` | Wandelt eine Taktposition in Sekunden bei gegebenem BPM um |
| `scale` | Bildet einen Wert von einem Wertebereich auf einen anderen ab |
| `spntom` | Wandelt einen Notennamen wie `'e2'` in eine MIDI-Nummer um |
| `PitchGrid` | Eine Menge von Tonhöhen in einem gewählten Stimmungssystem und einer Tonleiter |
| `Gesture` | Eine musikalische Geste — eine Folge von Phononen (Noten) |
| `CellularAutomaton` | Führt den ZA vorwärts in der Zeit aus |
| `CellularRules` | Definiert die Regeltabelle des ZA |
| `intToBinary` | Wandelt eine ganze Zahl in eine Liste aus 0en und 1en um |

---

## Schritt 2 — Grundlegende Parameter

```python
# erstelle im Vorfeld einen Projektordner, in dem du Midi-Dateien speichern kannst
path             = "MIDI/"
lowestPitchMidi  = spntom('e2')   # E2  = MIDI 40
highestPitchMidi = spntom('e6')   # E6  = MIDI 88
bpm              = 161
stepSizeBeats    = 0.5            # jede ZA-Zelle = eine Achtelnote
```

`spntom` (Scientific Pitch Notation to MIDI) wandelt Notennamen in MIDI-Nummern um. `'e2'` ist die tiefste Note und `'e6'` die höchste — sie legen den Tonhöhenbereich der Melodie fest.

`stepSizeBeats = 0.5` bedeutet, dass jede Zelle im ZA-Gitter einem halben Taktschlag entspricht (eine Achtelnote beim gegebenen Tempo).

---

## Schritt 3 — Das Tonhöhengitter aufbauen

```python
pitchGrid = PitchGrid.fromMask(
    'edo12', 'lydianSharp2',
    lowestPitchMidi, highestPitchMidi,
    lowestPitchMidi, lowestPitchMidi
)
```

Ein `PitchGrid` ist eine Menge erlaubter MIDI-Tonhöhen — eine Art musikalisches Sieb. Anstatt jeden Halbton zuzulassen, beschränken wir die Tonhöhen auf eine bestimmte **Tonleiter innerhalb eines Stimmungssystems**.

- `'edo12'` — gleichschwebende Stimmung mit 12 Tönen pro Oktave
- `'lydianSharp2'` — ein Modus aus der harmonisch-Moll-Familie: wie Lydisch, aber mit erhöhter zweiter Stufe.
- Der Register reicht von `lowestPitchMidi` bis `highestPitchMidi`

Wenn der ZA später "rohe" Midi-Werte erzeugt, rasten wir sie auf dieses Gitter ein — sodass jede Tonhöhe im Ergebnis ein gültiger Skalenton ist.

:::{note}
`PitchGrid.fromMask` erwartet: Stimmungssystem, Maskenname, tiefste Tonhöhe, höchste Tonhöhe, Stimmungssystem-Grundton, Skalengrundton. Durch Übergabe von `lowestPitchMidi` für beide Grundtöne wird die Skala auf E verankert.
:::

:::{important}
**Binär und Ganzzahl sind zwei Sichtweisen auf dieselbe Zahl.**

Jede Zellenzeile im ZA ist heimlich eine ganze Zahl. Die Zellen von links
nach rechts als Binärzahl gelesen — `0 0 1 1 0 0 1 0` — ergibt 50.
Umgekehrt liefert `intToBinary(50, 8)` wieder `[0, 0, 1, 1, 0, 0, 1, 0]`.

Deshalb hängen der Startzustand `gen0Int = 50` und die Tonhöhenkurve aus
`generationsToEnvelope()` zusammen: die Envelope liest jede Generationszeile
als ganze Zahl, und diese Zahlen bilden die Melodie. Die Binärliste steuert
den Rhythmus. Dieselben Daten, zwei Lesarten.
:::

---

## Schritt 4 — Den Zellulären Automaten einrichten

```python
numGenerations = 40
gen0Int        = 50
gen0           = intToBinary(gen0Int, 16)
```

`gen0` ist der Ausgangszustand — eine Zeile von 16 Zellen. Wir beginnen mit der ganzen Zahl 50, die in Binärdarstellung `0000000000110010` ergibt. Das liefert uns ein bestimmtes Startmuster statt eines zufälligen — die Verwendung einer ganzen Zahl macht es einfach, das Ergebnis zu reproduzieren und zu dokumentieren.

```python
ruleNumber = 121
filename   = f"wolfram_{ruleNumber}_gen0_{gen0Int}_numGenerations{numGenerations}.mid"

wolfram = CellularRules.elementaryWolfram(ruleNumber)
ca      = CellularAutomaton(rules=wolfram, gen0=gen0)
ca.iterate(numGenerations)
```

`CellularRules.elementaryWolfram(140)` erstellt die Nachschlagetabelle für Wolfram-Regel 140. `ca.iterate(40)` führt den Automaten 40 Generationen vorwärts und speichert jede Generation in `ca.generations`.

Der Dateiname kodiert die Regelnummer und die Startbedingungen — unverzichtbar für die Reproduzierbarkeit.

```python
env        = ca.generationsToEnvelope()
binaryList = ca.concatenateGenerations()
```

:::{note}
**Den Automaten in der Konsole beobachten**

Während der Entwicklung ist es hilfreich, die einzelnen Generationen direkt
auszugeben. Jede Generation ist eine Liste von 0en und 1en — die Binärdarstellung
einer ganzen Zahl. Diese sind intern in dem `dictionary` namens `.generations` abgespeichert. Mit `binaryToInt` lässt sich der Zustand jeder Zeile auf einen
einzigen Zahlenwert reduzieren, der den "Charakter" dieser Generation zusammenfasst:

```python
for key in ca.generations:
    gen     = ca.generations[key]
    intVal  = binaryToInt(gen)
    binStr  = "".join(str(b) for b in gen)   # lesbare Binärdarstellung
    print(f"Generation {key:>3} | {intVal:>6} | {binStr}")

# Eine typische Ausgabe könnte so aussehen:
# Generation   0 |     50 | 0000000000110010
# Generation   1 |  65465 | 1111111110111001
# Generation   2 |    237 | 0000000011101101
```

Die mittlere Spalte — der Ganzzahlwert — ist genau das, was `generationsToEnvelope()`
intern berechnet und als Kurve über die Zeit abbildet. Du kannst hier bereits erkennen,
ob der Automat in Richtung größerer oder kleinerer Zahlen driftet — und damit, ob die
Melodie eher nach oben oder unten tendiert.
:::

Zwei verschiedene Sichtweisen auf die ZA-Ausgabe:

- `generationsToEnvelope()` — wandelt die binären Zellen jeder Generation in eine einzelne ganze Zahl um (indem die Zeile als Binärzahl gelesen wird) und verpackt diese Zahlen als `Envelope`. Das ergibt eine glatte Kurve, die wir für die Tonhöhenzuordnung verwenden können.
- `concatenateGenerations()` — flacht alle 40 Generationen in eine lange Liste aus 0en und 1en ab (`40 × 16 = 640 Werte`). Das sind die rohen Rhythmusdaten.

---

## Schritt 5 — Den ZA auf Tonhöhen abbilden

```python
pitchSeq = []
for i in range(numGenerations):
    y             = env.getValue(i / numGenerations, True, True)
    rawMidi       = scale(y, 0, 1, lowestPitchMidi, highestPitchMidi)
    quantisedMidi = pitchGrid.quantise(rawMidi)
    pitchSeq.append(quantisedMidi)
```

Für jede der 40 Generationen:

1. **Envelope ablesen** an der normierten Zeitposition `i / numGenerations` (0.0 → 1.0). Die `True, True`-Argumente aktivieren die Normierung, sodass der Ausgabewert in `[0, 1]` liegt.
2. **Skalieren** dieses 0–1-Wertes in den MIDI-Tonhöhenbereich mit `scale()`.
3. **Quantisieren** auf die nächstliegende erlaubte Tonhöhe im `pitchGrid` — Einrasten auf die LydianSharp2-Skala.

Das Ergebnis ist eine Liste von 40 MIDI-Tonhöhen, eine pro Generation, die dem sich entwickelnden Ganzzahlverlauf des ZA folgt.

---

## Schritt 6 — Den ZA auf Rhythmen abbilden

```python
startTimesSec = []

for i, bin in enumerate(binaryList):
    startTimeBeats = i * stepSizeBeats
    if bin == 1:
        startTimeSec = beatToSec(startTimeBeats, bpm)
        startTimesSec.append(startTimeSec)
```

`binaryList` hat 640 Werte (0 oder 1). Jede Position entspricht einem halben Taktschlag. Wenn eine Zelle **1** ist, wird dort ein Notenanschlag gesetzt; bei **0** herrscht Stille. `beatToSec` wandelt die Taktposition mit dem BPM in Sekunden um.

Das Ergebnis ist eine Liste von Einsatzzeiten in Sekunden — nur die Positionen, an denen der ZA eine `1` hat.

```python
tg      = TimeGrid(startTimesSec, bpm=161)
deltaTs = tg.differentiate()
```

`TimeGrid` verpackt die Einsatzzeiten in eine musikalische Zeitstruktur. `differentiate()` wandelt die absoluten Zeiten in **Intereinsatzintervalle** um (die Zeit zwischen aufeinanderfolgenden Einsätzen) — das Format, das `Gesture.fromLists` benötigt.

:::{note}
`differentiate()` ist an die gleichnamige SuperCollider-Methode angelehnt, wobei in dieser Version standardmäßig der erste Wert als 0 angenommen wird - nicht als Differenz von 0.
:::

---

## Schritt 7 — Die Geste aufbauen

```python
g = Gesture.fromLists(
    numGenerations, 0,
    deltaTs, 0.125, pitchSeq, 100,
    bpm=bpm
)
g.toMidi(path + filename)
```

`Gesture.fromLists` fügt alles zu einer musikalischen Geste zusammen:

| Argument | Wert | Bedeutung |
|---|---|---|
| `size` | `numGenerations` (40) | Anzahl der Noten |
| `startOffset` | `0` | Beginn bei Zeit null |
| `startDeltas` | `deltaTs` | Intereinsatzintervalle in Sekunden |
| `durations` | `0.125` | Feste Notendauer (Achtelnote) |
| `pitches` | `pitchSeq` | Die 40 MIDI-Tonhöhen aus dem ZA |
| `dynamics` | `100` | Feste Anschlagstärke |
| `bpm` | `161` | Tempo für den MIDI-Export |

Schließlich schreibt `g.toMidi(...)` die MIDI-Datei. Der Dateiname kodiert die Regelnummer und die Anfangsbedingungen, sodass du exakt dasselbe Ergebnis jederzeit neu erzeugen kannst.

---



## Experimente

**Regelnummer ändern:**
```python
ruleNumber = 30   # chaotisch
ruleNumber = 110  # komplex, Turing-vollständig
ruleNumber = 90   # Sierpinski-Dreieck
```

**Startmuster ändern:**
```python
gen0Int = 1       # einzelne aktive Zelle in der Mitte
gen0Int = 255     # alle Zellen aktiv
gen0Int = 42      # beliebig — dokumentieren und anhören
```

**Tonleiter ändern:**
```python
pitchGrid = PitchGrid.fromMask('edo12', 'phrygian', ...)
pitchGrid = PitchGrid.fromMask('werckmeister1', 'dorian', ...)
```

**Schrittgröße ändern:**
```python
stepSizeBeats = 0.25   # Sechzehntelnoten — dichtere Rhythmen
stepSizeBeats = 1.0    # Viertelnoten — spärlicher
```

Jede Kombination aus Regel, Startmuster und Tonleiter ergibt eine einzigartige Komposition. Die Dateinamen-Konvention (`wolfram_140_gen0_50_numGenerations40.mid`) macht es leicht, deine Erkundungen zu katalogisieren.


## Ausblick: Die Stärke algorithmischer Generierung

Einer der größten Vorteile des algorithmischen Komponierens ist die Möglichkeit, **viele Varianten aus denselben Parametern** zu erzeugen — mit minimalem Aufwand. Statt eine Regel manuell zu wählen, können wir einfach einen ganzen Bereich von Regeln durchlaufen und für jede eine eigene MIDI-Datei erstellen.

Das folgende Beispiel zeigt außerdem eine weitere Möglichkeit, den Startzustand zu definieren: statt einer ganzen Zahl schreiben wir das Bitmuster **direkt als Liste** und berechnen den Ganzzahlwert nachträglich mit `binaryToInt`. Das macht die rhythmische Struktur des Startmusters unmittelbar lesbar:

```python
gen0 = [
    1,0,0,1,0,0,1,0,
    0,1,1,0,1,1,0,1]

gen0Int = binaryToInt(gen0)
```

Hier sieht man auf einen Blick: die erste Hälfte hat ein punktiertes Muster (`1 0 0 1 0 0 1 0`), die zweite eine dichtere Gegenbewegung (`0 1 1 0 1 1 0 1`). Diese Struktur wird als Ausgangszustand in den Automaten eingespeist — und jede Regel entwickelt sie auf ihre eigene Weise weiter.

Anstatt nun eine einzelne Regel auszuprobieren, iterieren wir über **50 aufeinanderfolgende Regeln** (100–149) und schreiben für jede eine eigene Datei:

```python
from GreasyPidgin.CellularAutomata import binaryToInt
from GreasyPidgin.TimeGrid import TimeGrid, beatToSec
from GreasyPidgin.Normalisation import scale
from GreasyPidgin import spntom
from GreasyPidgin.PitchGrid import PitchGrid
from GreasyPidgin.Gesture import Gesture
from GreasyPidgin.CellularAutomata import CellularAutomaton, CellularRules, intToBinary

path = "MIDI/"

lowestPitchMidi  = spntom('e2')
highestPitchMidi = spntom('e6')
bpm              = 161
stepSizeBeats    = 0.5

pitchGrid = PitchGrid.fromMask(
    'edo12', 'lydianSharp2',
    lowestPitchMidi, highestPitchMidi, lowestPitchMidi, lowestPitchMidi)

numGenerations = 40

gen0    = [1,0,0,1,0,0,1,0,
           0,1,1,0,1,1,0,1]
gen0Int = binaryToInt(gen0)

for ruleNumber in range(100, 150):
    filename = f"wolfram_{ruleNumber}_gen0_{gen0Int}_numGenerations{numGenerations}.mid"
    wolfram  = CellularRules.elementaryWolfram(ruleNumber)
    ca       = CellularAutomaton(rules=wolfram, gen0=gen0)
    ca.iterate(numGenerations)
    env        = ca.generationsToEnvelope()
    binaryList = ca.concatenateGenerations()

    pitchSeq = []
    for i in range(numGenerations):
        y             = env.getValue(i / numGenerations, True, True)
        rawMidi       = scale(y, 0, 1, lowestPitchMidi, highestPitchMidi)
        quantisedMidi = pitchGrid.quantise(rawMidi)
        pitchSeq.append(quantisedMidi)

    startTimesSec = []
    for i, bin in enumerate(binaryList):
        startTimeBeats = i * stepSizeBeats
        if bin == 1:
            startTimeSec = beatToSec(startTimeBeats, bpm)
            startTimesSec.append(startTimeSec)

    tg      = TimeGrid(startTimesSec, bpm=161)
    deltaTs = tg.differentiate()

    g = Gesture.fromLists(
        numGenerations, 0,
        deltaTs, 0.125, pitchSeq, 100, bpm=bpm
    )
    g.toMidi(path + filename)
```

Mit einem einzigen Skript entstehen so **50 MIDI-Dateien** — jede klingt anders, alle teilen dieselbe rhythmische DNA des Startmusters und dieselbe Tonleiter. In einer DAW kannst du diese Dateien nebeneinander laden und gezielt auswählen, welche Varianten sich für dein Stück eignen.

:::{tip}
**Kompositorischer Workflow**

Algorithmische Generierung ersetzt nicht die kompositorische Entscheidung — sie verlagert sie. Statt jede Note einzeln zu setzen, wählst du:

1. **Das Startmuster** (`gen0`) — die rhythmische DNA
2. **Die Regeln** — welche Automaten du als Kandidaten zulässt
3. **Die Tonleiter** — den harmonischen Raum
4. **Die Auswahl** — welche der generierten Varianten du verwendest

Das Stück entsteht im Dialog zwischen Algorithmus und Gehör.
:::

