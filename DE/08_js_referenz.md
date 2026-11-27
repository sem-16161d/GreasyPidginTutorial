---
exports:
  - format: typst
    template: plain_typst_book
    output: exports/js-referenz.pdf
---

(js-referenz)=
# JavaScript-Referenz (Max 9 / `[v8]`)

Diese Referenz beschreibt die JavaScript-Version von GreasyPidgin im Ordner `js/`. Sie ist eine Portierung der Python-Bibliothek und läuft in Max 9 im Objekt `[v8]` bzw. `[v8.codebox]` sowie in Node.js. Jedes Python-Modul hat ein gleichnamiges JavaScript-Modul; Begriffe, Einheiten und Ergebnisse sind dieselben.

:::{note}
Das ältere Max-Objekt `[js]` kann GreasyPidgin nicht ausführen, da es keine modernen JavaScript-Sprachmittel (Klassen, `const`, Pfeilfunktionen) versteht. Verwendet wird immer `[v8]` oder `[v8.codebox]`.
:::

## Einrichtung und Laden

1. In Max **Options ▸ File Preferences** öffnen.
2. Den Ordner `GreasyPidgin` hinzufügen und **Subfolders** aktivieren.
3. Die Max-Konsole öffnen (**Window ▸ Max Console**). Alle Ausgaben von `post()` und alle Fehlermeldungen erscheinen dort.

Ein Modul wird mit `require()` und seinem Namen geladen. Die geschweiften Klammern holen einzelne Klassen oder Funktionen aus dem Modul heraus:

```js
const { Envelope } = require("Envelope");
const { TimeGrid, RQQ, R } = require("TimeGrid");
const { mtof, spntom } = require("Pitch");
```

Ohne Klammern liefert `require()` das ganze Modulobjekt:

```js
const Pitch = require("Pitch");
Pitch.mtof(69);   // 440
```

In Node.js wird mit relativem Pfad geladen: `require("./js/Envelope")`.

## Konventionen

### Optionsobjekte statt Schlüsselwortargumenten

Wo Python Schlüsselwortargumente verwendet, nimmt die JavaScript-Version ein **Optionsobjekt** als letztes Argument. Die Namen der Optionen sind dieselben wie in Python.

```python
# Python
Envelope.periodic(3, 16, shape="saw", jitter=0.1)
```

```js
// JavaScript
Envelope.periodic(3, 16, { shape: "saw", jitter: 0.1 });
```

### Einheiten

| Größe | Einheit | Beispiel |
|---|---|---|
| Tonhöhe | MIDI-Float | `60` = C4, `60.5` = C4 einen Viertelton höher |
| Notenname | Scientific Pitch Notation (SPN) | `"c4"`, `"cs4"`, `"bf3"`, `"cqs4"` |
| Zeit | Sekunden (Standard) oder Schläge mit `timeUnit: "beats"` | `1.5` |
| Dynamik | MIDI-Velocity 1–127, Markierung oder Gabel | `80`, `"mf"`, `"pp-f"` |
| Tempo | Schläge pro Minute | `bpm: 120` |

Max rechnet in Millisekunden, GreasyPidgin in Sekunden. Beim Ausgeben wird daher mit 1000 multipliziert: `Math.round(e.startSec * 1000)`.

### Kopie oder Original

Methoden mit dem Präfix `with…` sowie `reverse()` und `inverse()` geben eine **neue** Envelope zurück und lassen das Original unverändert. Mit `{ overwriteOriginal: true }` wird stattdessen das Original verändert.

```js
let env = new Envelope([0, 1, 0.5]);
env = env.withJitter(0.1);   // Ergebnis wieder in die Variable schreiben
```

### Unterschiede zur Python-Version

- Keine Dateiexporte (MIDI, MusicXML, JSON, CSV) und kein MIDI-Import. Stattdessen liefert `toEvents()` die spielbaren Noten als Liste von Objekten (siehe {ref}`js-events`).
- Kein `OSCBridge`; in Max übernehmen `[udpsend]` und `[udpreceive]` diese Aufgabe.
- `display()` (matplotlib) fehlt; `Envelope.displayAscii()` und `Turtle.toSvg()` ersetzen es.
- Zufallszahlen mit `seed` sind innerhalb von JavaScript reproduzierbar, ergeben aber andere Werte als numpy in Python.

(js-events)=
### Das Event-Objekt

`Phonon`, `Gesture`, `Phrase`, `TimeGrid` und `PitchGrid` besitzen eine Methode `toEvents()`. Sie liefert ein nach Startzeit sortiertes Array von Objekten mit folgenden Feldern:

| Feld | Bedeutung |
|---|---|
| `startSec` | Startzeit in Sekunden, absolut |
| `durationSec` | Dauer in Sekunden |
| `pitch` | ganzzahlige MIDI-Note |
| `bend` | `[start, ende]` in Halbtönen: Abweichung von `pitch` (Mikrotöne, Glissandi) |
| `velocity` | MIDI-Velocity 1–127 |
| `aftertouch` | Envelope in Velocity-Einheiten bei Gabeln, sonst `null` |
| `lyric` | Liedtext-Silbe oder `null` |
| `dynamicMarking` | Dynamikbezeichnung (`"mf"`, `"pp-f"`) oder `null` |

`TimeGrid.toEvents()` und `PitchGrid.toEvents()` liefern nur `startSec`, `durationSec`, `pitch` und `bend`.

Ein typischer Abspielweg in Max:

```js
// jede Note als "pitch velocity dauerMs verzögerungMs" an [pipe 0 0 0 0] -> [makenote] -> [noteout]
function play(events) {
    for (const e of events) {
        outlet(0, e.pitch, e.velocity, Math.round(e.durationSec * 1000), Math.round(e.startSec * 1000));
    }
}
```

Für Mikrotöne wird die exakte Tonhöhe `e.pitch + e.bend[0]` verwendet, z. B. über `[mtof]` an einen Oszillator.

## Grundlagen

(js-pitch)=
### Pitch

Umrechnung zwischen Notennamen, MIDI-Floats und Frequenzen, nach `Pitch.lsp` aus Michael Edwards' *slippery chicken*.

```js
const { spntom, mtospn, mtof, ftom, spntof, forceIntoRangeMidi } = require("Pitch");
```

| Funktion | Beschreibung |
|---|---|
| `spntom(spn)` | Notenname → MIDI-Float. `spntom("cqs4")` → `60.5` |
| `mtospn(midi)` | MIDI-Float → Notenname. `mtospn(61)` → `"cs4"`, `mtospn(60.5)` → `"cqs4"`. Werte zwischen den unterstützten Mikrotönen werden gerundet. |
| `mtof(midi, referenceA4 = 440)` | MIDI-Float → Hz |
| `ftom(freq, referenceA4 = 440)` | Hz → MIDI-Float |
| `spntof(spn, referenceA4 = 440)` | Notenname → Hz. `spntof("a4", 443)` → `443` |
| `forceIntoRangeMidi(value, lo, hi, maxIter = 10)` | verschiebt einen Wert oktavweise in den Bereich `[lo, hi]`. `forceIntoRangeMidi(30, 48, 72)` → `54` |

Notennamen bestehen aus Tonbuchstabe, Vorzeichen und Oktave. Die Oktave 4 beginnt mit dem mittleren C (`c4` = 60).

| Vorzeichen | Bedeutung | Abweichung |
|---|---|---|
| `s` / `f` | Kreuz / B | ±1 |
| `qs` / `qf` | Viertelton hoch / tief | ±0.5 |
| `ss` / `sf` | Sechstelton hoch / tief | ±1/3 |
| `ts` / `tf` | Zwölftelton hoch / tief | ±1/6 |
| `sqs`, `fqf`, … | Kombinationen | z. B. +1.5 |

(js-normalisation)=
### Normalisation

Skalieren und Normalisieren von Zahlen.

```js
const { scale, scaleValues, normaliseIntoRange, normaliseValuesIntoRange, normaliseValues } = require("Normalisation");
```

| Funktion | Beschreibung |
|---|---|
| `scale(value, inLo, inHi, outLo, outHi, exponent = 1, clipToRange = false)` | bildet `value` von `[inLo, inHi]` auf `[outLo, outHi]` ab, wie Max' `[scale]`. Ein umgekehrter Eingangsbereich kehrt die Abbildung um; `exponent ≠ 1` krümmt sie. |
| `scaleValues(values, …)` | dasselbe für ein Array; begrenzt standardmäßig auf den Zielbereich |
| `normaliseIntoRange(value, lo, hi, clipToRange = true)` | Wert aus `[lo, hi]` nach `[0, 1]`; warnt bei Werten außerhalb |
| `normaliseValuesIntoRange(values, lo, hi, clipToRange = true)` | dasselbe für ein Array |
| `normaliseValues(values)` | normalisiert ein Array nach seinem eigenen Minimum und Maximum: `[2, 4, 6]` → `[0, 0.5, 1]` |

(js-iterable)=
### IterableOperations

| Funktion | Beschreibung |
|---|---|
| `flatten(x)` | beliebig verschachtelte Arrays als flaches Array; Strings bleiben ganz. `flatten([1, [2, [3, "ab"]]])` → `[1, 2, 3, "ab"]` |
| `isNested(it)` | `true` für ein nicht leeres Array oder Set, dessen Elemente alle Arrays sind |
| `ensureList(value)` | packt einen Einzelwert in ein Array; ein Set wird zum Array |

(js-dynamics)=
### Dynamics

Dynamikbezeichnungen und Gabeln als MIDI-Velocity.

```js
const { DYNAMIC_MARKINGS, dynamicMarkingToVelocity, parseDynamicMarking, splitHairpin, isDynamicMarkingText } = require("Dynamics");
```

| Bezeichnung | `pppp` | `ppp` | `pp` | `p` | `mp` | `mf` | `f` | `ff` | `fff` | `ffff` |
|---|---|---|---|---|---|---|---|---|---|---|
| Velocity | 8 | 16 | 33 | 49 | 64 | 80 | 96 | 112 | 120 | 127 |

| Funktion | Beschreibung |
|---|---|
| `dynamicMarkingToVelocity(marking)` | `"mf"` → `80` |
| `parseDynamicMarking(text)` | Einzelbezeichnung → Velocity; Gabel → `[start, ende]`. `"pp-f"` → `[33, 96]` |
| `splitHairpin(text)` | `"ff>mp"` → `["ff", "mp"]`; `null` bei einer einfachen Bezeichnung |
| `isDynamicMarkingText(text)` | `true`, wenn der Text eine Bezeichnung oder Gabel ist |

Eine Gabel wird immer von links nach rechts gelesen. Das Trennzeichen (`-`, `<`, `>`, `~`) ist nur Schreibweise: `"pp<f"` und `"pp-f"` bedeuten dasselbe.

(js-envelope)=
## Envelope

Jede zweidimensionale Abfolge – Melodiekontur, Crescendo, Dichteverlauf, Hüllkurve – ist in GreasyPidgin eine `Envelope`. Eine Envelope besteht aus Stützpunkten (*breakpoints*) mit einer Kurvenform pro Segment. Intern werden die Punkte auf `x` und `y` im Bereich 0..1 normalisiert; die ursprünglichen Bereiche stehen in `x_range` und `y_range`.

```js
const { Envelope } = require("Envelope");
```

### Konstruktor

```text
new Envelope(data, options)
```

`data` ist entweder eine Liste von Einzelwerten (gleichmäßig über `x` verteilt) oder eine Liste von Wertepaaren `[x, y]` bzw. Tripeln `[x, y, kurve]`.

```js
const a = new Envelope([0, 2, 1, 3]);                      // x = 0, 1, 2, 3
const b = new Envelope([[0, 0], [1, 10], [3, 2]]);         // Wertepaare
const c = new Envelope([[0, 0, "exp"], [1, 10], [3, 2]]);  // Kurve pro Segment
a.getValue(1.5);   // 1.5
```

| Option | Standard | Bedeutung |
|---|---|---|
| `autosort` | `true` | Wertepaare nach `x` sortieren |
| `curves` | `null` | eine Kurve pro Segment (alternativ zu Tripeln) |
| `polyFit` | `false` | Polynome Grad 1–5 sofort anpassen (siehe `recalculatePolynomials()`) |
| `minEnv`, `maxEnv` | `null` | bewegliche Unter-/Obergrenze (siehe `withBounds()`) |
| `boundsNormalizedX`, `boundsSubdivisions` | `true`, `null` | Optionen für `withBounds()` |
| `jitter`, `jitterMode`, `jitterClip`, `jitterNormalizedX`, `seed` | – | Optionen für `withJitter()` |

### Kurvenformen

Eine Kurve gehört zu dem Segment, das an ihrem Stützpunkt **beginnt**. Eine Envelope mit *n* Punkten hat *n* − 1 Segmente.

| Kurve | Verlauf |
|---|---|
| `"linear"` | gerade Linie (Standard, auch `null` oder `0`) |
| `"step"` / `"hold"` | bleibt auf dem Startwert bis zum nächsten Punkt |
| `"exp"` | langsamer Beginn, schnelles Ende (konvex) |
| `"log"` | schneller Beginn, langsames Ende (konkav) |
| `"easeIn"` / `"easeOut"` | quadratisch: langsamer Beginn / langsames Ende |
| `"easeInOut"` | *smoothstep*: langsamer Beginn und langsames Ende |
| `"smooth"` / `"sine"` | Kosinus-Übergang |
| Zahl | Krümmung wie `Env` in SuperCollider: > 0 langsamer Beginn, < 0 schneller Beginn |

### Weitere Konstruktoren

| Methode | Beschreibung |
|---|---|
| `Envelope.from_pairs(pairs, options)` | aus Wertepaaren oder Tripeln |
| `Envelope.from_values(values, options)` | aus Einzelwerten |
| `Envelope.periodic(periods = 1, resolution = 16, options)` | aus einer periodischen Funktion |

`periodic` erzeugt `resolution` Stützpunkte pro Periode; `periods` darf gebrochen sein (`7.3`).

| Option | Standard | Bedeutung |
|---|---|---|
| `shape` | `"sine"` | `"sine"`, `"cosine"`, `"triangle"`, `"saw"`, `"saw_down"`, `"square"` oder eine Funktion `phase → [-1, 1]` |
| `phase` | `0` | Phasenverschiebung in Perioden |
| `xRange`, `yRange` | `[0, 1]` | Wertebereich des Ergebnisses |
| `includeEnd` | `true` | letzten Punkt genau ans Ende der letzten (Teil-)Periode setzen |

```js
const lfo = Envelope.periodic(3, 16, { shape: "triangle", yRange: [48, 72] });
```

### Werte lesen

```text
env.getValue(xPos, normalizedX = false, normalizedY = false, interpolateOutsideOfRange = true, polyDegree = 0)
```

| Argument | Bedeutung |
|---|---|
| `xPos` | Position auf der x-Achse |
| `normalizedX` | `true`: `xPos` ist 0..1; `false`: in den Einheiten von `x_range` |
| `normalizedY` | `true`: Ergebnis 0..1; `false`: in den Einheiten von `y_range` |
| `interpolateOutsideOfRange` | außerhalb des Bereichs weiterführen (`true`) oder den Randwert halten |
| `polyDegree` | > 0: Wert des angepassten Polynoms dieses Grades statt der Stützpunkte |

```js
const contour = new Envelope([60, 72, 64]);
const values = [];
for (let i = 0; i < 8; i++) {
    values.push(contour.getValue(i / 7, true, false));   // 8 Werte zwischen 60 und 72
}
```

### Kurven ändern

| Methode | Beschreibung |
|---|---|
| `setCurves(curves)` | alle Segmentkurven ersetzen (genau eine pro Segment); `null` = linear |
| `setCurve(segmentIndex, curve)` | eine Segmentkurve setzen (0 = zwischen den ersten beiden Punkten) |
| `getCurves()` | Liste der Segmentkurven |
| `hasCurves()` | `true`, wenn mindestens ein Segment nicht linear ist |
| `withCurves(curves, { overwriteOriginal })` | Kopie mit neuen Kurven |

`withCurves` verlangt genau eine Kurve pro Segment, sonst erscheint `Envelope: expected 64 curves (one per segment), got 2`.

### Umformungen

| Methode | Beschreibung |
|---|---|
| `rescale(newXRange = null, newYRange = null, inplace = false)` | neue Bereiche für `x` und `y`, Form bleibt gleich |
| `withBounds(minEnv, maxEnv, { normalizedX, subdivisions, overwriteOriginal })` | Unter- und Obergrenze selbst als Envelope (oder Zahl, Array, `null`). Ergebnis: `unten(x) + form(x) · (oben(x) − unten(x))`. Das Ergebnis hat lineare Segmente. |
| `withJitter(jitter, { mode, clip, normalizedX, seed, overwriteOriginal })` | zufällige Abweichung der Stützpunkte um einen Anteil (`0.1` = bis ±10 %). `mode: "value"` bezogen auf den Punktwert, `"range"` auf den ganzen Bereich. `jitter` kann selbst eine Envelope sein. |
| `reverse({ overwriteOriginal })` | Krebs: zeitlich gespiegelt |
| `inverse(axis = null, { overwriteOriginal })` | Umkehrung: jeder Wert gespiegelt, `y' = 2 · axis − y` |

#### Reihentechnik: `reverse` und `inverse`

`reverse()` spiegelt die Envelope in der Zeit. Die Bereiche bleiben gleich; die Kurven werden mitgespiegelt (`easeIn` ↔ `easeOut`, `exp` ↔ `log`, Zahl `c` → `−c`), sodass jedes Segment seine Form behält. `"step"` bleibt `"step"`: Eine Stufenreihe `[a, b, c, d]` wird zu `[d, c, b, a]`.

`inverse(axis)` spiegelt jeden Wert. Die Kurven bleiben unverändert.

| `axis` | Spiegelachse | Ergebnis |
|---|---|---|
| `null` (Standard) | erster Wert | serielle Umkehrung: der erste Ton bleibt, jedes Intervall kehrt sich um |
| `"center"` | Mitte des y-Bereichs | Bereich bleibt gleich |
| Zahl | dieser Wert | z. B. `inverse(60)` spiegelt um das mittlere C |

```js
const row = new Envelope([60, 62, 61, 65, 64]);
row.reverse();             // Krebs:            64 65 61 62 60
row.inverse();             // Umkehrung:        60 58 59 55 56
row.reverse().inverse();   // Krebsumkehrung:   64 63 67 66 68
```

### Analyse

| Methode | Beschreibung |
|---|---|
| `recalculatePolynomials()` | passt Polynome vom Grad 1–5 an die Stützpunkte an (für `getValue(…, polyDegree)`) |
| `reduceEnvPoints(numMinima = 3, numMaxima = 3, resolution = 20)` | vereinfachte Envelope aus Endpunkten, den tiefsten lokalen Minima und höchsten lokalen Maxima; auch in `env.reducedEnv` |
| `mapToGrid(xGrid, yGrid)` | quantisiert die Envelope auf zwei Grids; liefert `[x, y]`-Paare an jeder Stelle, an der sich der quantisierte Wert ändert |
| `mean_y(normalized = false)` | Mittelwert der Stützpunkte |
| `median_y(normalized = false)` | Median |
| `std_y(normalized = false, ddof = 0)` | Standardabweichung |
| `most_common_y(…)`, `least_common_y(…)` | häufigster / seltenster Wert |
| `histogram(normalized = false, rounding = 6, sortBy = "value")` | `Map` Wert → Anzahl; `sortBy: "count"` sortiert nach Häufigkeit |
| `displayAscii(maxWidth = 60, maxHeight = 20, useNormalized = false)` | zeichnet die Envelope als Text in die Max-Konsole |

### Eigenschaften

| Eigenschaft | Inhalt |
|---|---|
| `points` | normalisierte Stützpunkte `[[x, y], …]` |
| `x_range`, `y_range` | ursprüngliche Bereiche `[min, max]` |
| `curves` | Segmentkurven |
| `poly_fits`, `coefficients` | angepasste Polynome |
| `reducedEnv` | Ergebnis von `reduceEnvPoints()` |


## Grids

Ein Grid ist eine Menge von Zahlen, auf die andere Werte eingerastet (quantisiert) werden. `Grid` ist die Grundklasse; `TimeGrid`, `PitchGrid` und `DynamicGrid` sind Grids für Zeitpunkte, Tonhöhen und Lautstärken.

(js-grid)=
### Grid

`Grid` erweitert das eingebaute `Set`: Doppelte Werte fallen weg, alle `Set`-Methoden (`has`, `add`, `size`, `for … of`) funktionieren.

```js
const { Grid } = require("Grid");
const g = new Grid([3, 7, 10, 15]);
g.quantise(8.5);        // 7  (bei Gleichstand gewinnt der tiefere Wert)
g.quantise([1, 12]);    // [3, 10]
g.sorted();             // [3, 7, 10, 15]
```

#### Konstruktoren

| Methode | Beschreibung |
|---|---|
| `new Grid(values)` | aus einem Array oder Set |
| `Grid.series(start, step, size)` | arithmetische Reihe: `series(0, 0.5, 4)` → `0, 0.5, 1, 1.5` |
| `Grid.geom(start, ratio, size, { decimals })` | geometrische Reihe: `geom(1, 2, 5)` → `1, 2, 4, 8, 16` |
| `Grid.linearInterpolation(start, end, size, { decimals, includeEnd })` | `size` gleichmäßig verteilte Werte |
| `Grid.fib(size, a = 0, b = 1)` | Fibonacci-Reihe; doppelte Werte fallen weg |
| `Grid.rand(size, low = 0, high = 1, { integer })` | Zufallswerte; mit `integer: true` verschiedene ganze Zahlen |
| `Grid.fill(size, funcOrValue)` | `funcOrValue(i)` für i = 0 … size−1, oder ein fester Wert |

#### Methoden

| Methode | Beschreibung |
|---|---|
| `sorted()` | Werte aufsteigend als Array |
| `quantise(value)` | rastet eine Zahl (oder jede Zahl eines Arrays / Sets) auf den nächsten Grid-Wert ein |
| `sieve(stepSize = 1, offsetIndex = 0, { discardOffset, inverse, reverse, rotation })` | Sieb nach Xenakis: jeder `stepSize`-te Wert ab `offsetIndex`. Ergebnis als neues Grid, auch in `this.sieved` |
| `sample(numElements)` | `numElements` verschiedene Zufallswerte als Array, auch in `this.sampled` |
| `differentiate(copyFirst = false)` | Abstände zwischen den sortierten Werten: `[3, 7, 10, 15]` → `[0, 4, 3, 5]` |

Optionen von `sieve`:

| Option | Standard | Bedeutung |
|---|---|---|
| `discardOffset` | `true` | Werte vor `offsetIndex` verwerfen |
| `inverse` | `false` | die Werte behalten, die das Sieb verwerfen würde |
| `reverse` | `false` | vom höchsten Wert abwärts sieben |
| `rotation` | `0` | Phase des Siebs um so viele Positionen verschieben |

(js-timegrid)=
### TimeGrid

Ein Grid aus Zeitpunkten in Sekunden, mit Tempo und Zeitspanne. Dazu gehören die Rhythmusnotation `RQQ`, die Pause `Rest` und Hilfsfunktionen.

```js
const { TimeGrid, RQQ, Rest, R, beatToSec, secToBeat, bjorklund } = require("TimeGrid");
```

#### Konstruktor

```text
new TimeGrid(values, { startTimeSec = 0, endTimeSec = null, bpm = 60, ticksPerBeat = 480 })
```

`values` sind Zeitpunkte in Sekunden. Ohne `endTimeSec` endet das Grid einen Abstand nach dem letzten Wert.

#### Eigenschaften

| Eigenschaft | Inhalt |
|---|---|
| `startTimeSec`, `endTimeSec`, `durationSec` | Zeitspanne in Sekunden |
| `startTimeBeats`, `endTimeBeats`, `durationBeats` | dieselbe Spanne in Schlägen |
| `bpm`, `ticksPerBeat` | Tempo und MIDI-Auflösung |
| `layers` | Teilraster, z. B. bei `fromSubdivisions` (`layers["/ 3"]`) |

#### Rhythmen erzeugen

| Methode | Beschreibung |
|---|---|
| `TimeGrid.series(startTimeSec, stepSec, size, { bpm, ticksPerBeat })` | gleichmäßiger Puls |
| `TimeGrid.linearInterpolation(startTimeSec, endTimeSec, size, { bpm, decimals, includeEnd })` | `size` gleichmäßig verteilte Zeitpunkte |
| `TimeGrid.fromSubdivisions(subdivisions, { bpm, startTimeBeats, durationBeats })` | gleichzeitige Unterteilungen des Schlags, z. B. `[1, 2, 3]` |
| `TimeGrid.fromRQQ(rqq, { startTimeSec, bpm })` | Einsätze einer RQQ (siehe unten) |
| `TimeGrid.RQQfromLSystem(rqqs, productionRules, numIterations = 5, { axiom, bpm, durationsCutoffBeats, cutoffMode })` | ein L-System über eine Palette von RQQs |
| `TimeGrid.fromEuclidean(pulses, steps, rotation = 0, { durationBeats, durationSec, startTimeSec, bpm })` | euklidischer Rhythmus: `pulses` Einsätze gleichmäßig auf `steps` Schritte verteilt |
| `TimeGrid.fromPulsesEuclidean(pulses, subdivisions = [1, 2, 4], rotation = 0, { … })` | euklidischer Rhythmus auf der Vereinigung mehrerer Unterteilungen |
| `TimeGrid.fromDensityEuclidean(densityHz = 4, subdivisions, rotation = 0, { … })` | wie oben, mit `pulses = densityHz · Dauer` |
| `TimeGrid.fromDensity(startTimeSec = 0, durationSec = 4, densityHz = 5, leaning = 0, subdivisions = null, { leaningIntensity, … })` | zufällige Einsätze mit erwarteter Dichte `densityHz` (Einsätze pro Sekunde) |

```js
TimeGrid.fromEuclidean(5, 8, 0, { durationBeats: 4, bpm: 120 }).sorted();   // [0, 0.5, 0.75, 1.25, 1.5]  x.xx.xx.
TimeGrid.fromDensity(0, 4, 4, 1);    // etwa 16 Einsätze in 4 s, zum Ende hin dichter
```

Bei `fromDensity` steuert `leaning` die Verteilung: −1 = dicht am Anfang, 0 = gleichmäßig, 1 = dicht am Ende. Ohne `subdivisions` liegen die Einsätze auf beliebigen Millisekunden; mit z. B. `[1, 2, 4]` auf Vierteln, Achteln und Sechzehnteln.

:::{tip}
Auf einem groben Raster und mit starkem `leaning` entstehen weniger Einsätze als erwartet, weil der dichte Teil keine freien Plätze mehr hat.
:::

#### RQQ und Rest

`RQQ` (*Rhythm Quantisation Quotient*) teilt eine Dauer in Schlägen in **Proportionen**. Die Zahlen sind Gewichte, keine Dauern: `new RQQ(4, [1, 1, 2])` teilt 4 Schläge im Verhältnis 1 : 1 : 2, also Viertel, Viertel, Halbe. Eine verschachtelte RQQ unterteilt ihren eigenen Anteil. `R(1)` (gleichbedeutend mit `new Rest(1)`) ist eine Pause mit Gewicht 1: Sie nimmt Zeit ein, erzeugt aber keinen Einsatz.

```js
const bar = new RQQ(4, [1, new RQQ(1, [1, 1]), R(1), new RQQ(1, [1, 1, 1])]);
TimeGrid.fromRQQ(bar, { bpm: 60 }).sorted();   // Viertel, zwei Achtel, Viertelpause, Triole
```

```text
new RQQ(durationBeats, ratios, { bpm = 60, startOffsetBeats = 0 })
```

#### Methoden

| Methode | Beschreibung |
|---|---|
| `toEvents(pitch = 60)` | die Einsätze als Noten (siehe {ref}`js-events`); Dauer = kleinster Abstand |
| `toRelativeTimes(unit = "seconds")` | Abstände zwischen den Einsätzen, in `"seconds"` oder `"beats"` |
| `sample(numElements)` | zufällige Auswahl als neues TimeGrid mit gleicher Spanne |
| `leaningSample(densityHz = 5, leaning = 0, { … })` | zufällige Auswahl wie bei `fromDensity` |
| `getDensityCurve(lookbackInterval = 1, lookBackFrame = 1, { lookBackUnit })` | Dichteverlauf: `{ density, minDensityHz, maxDensityHz, relativeMaxPosition, meanDensityHz }` |
| `getSelfSimilarity(maxVal = 1, maxLength = 8)` | Anteil der Abstandsmuster (Länge 2 … `maxLength`), die mehr als einmal vorkommen |
| `analyseExternalStartTimesSec(starts)` | Dichte (Einsätze pro Schlag) und `leaning` fremder Zeitpunkte auf diesem Grid |

#### Hilfsfunktionen

| Funktion | Beschreibung |
|---|---|
| `beatToSec(beat, bpm = 60)` | Schläge → Sekunden |
| `secToBeat(sec, bpm = 60)` | Sekunden → Schläge |
| `bjorklund(pulses, steps)` | euklidisches Muster als 0/1-Array: `bjorklund(3, 8)` → `[1, 0, 0, 1, 0, 0, 1, 0]` |

(js-tuningsystem)=
### TuningSystem und ScaleMask

Ein `TuningSystem` ist ein Tonraum aus Abständen (in MIDI-Halbtönen) zum Grundton 0, der sich in einem Intervall wiederholt (12 = Oktave, ≈ 19.02 = Duodezime bei Bohlen-Pierce) oder sich gar nicht wiederholt. Eine `ScaleMask` wählt daraus Stufen aus: Modi, Skalen, Maqamat.

```js
const { TuningSystem, ScaleMask, TUNING_SYSTEMS, toMidi } = require("TuningSystem");
```

#### Vordefinierte Stimmungen

`TUNING_SYSTEMS` enthält:

| Name | Stufen | Wiederholung | Masken |
|---|---|---|---|
| `edo12` | 12 | Oktave | 31 (siehe unten) |
| `edo24`, `edo31`, `edo53`, `edo72` | 24, 31, 53, 72 | Oktave | `chromatic` |
| `werckmeister1` … `werckmeister4`, `kirnberger2`, `kirnberger3`, `meantoneQC`, `pythagorean`, `zeta12` | 12 | Oktave | 31 |
| `JI_5limit_major`, `JI_7limit` | 7 | Oktave | `chromatic` |
| `harmonicSeries8_16` | 8 | Oktave | `chromatic` |
| `maqamRast`, `maqamBayati`, `maqamHijaz` | 7 | Oktave | `chromatic` |
| `slendro_approx`, `pelog_approx` | 5, 7 | Oktave | `chromatic` |
| `AstridsBontempi` | 24 | Oktave | `chromatic` |
| `bohlenPierce` | 13 | Duodezime (≈ 19.02) | `chromatic`, `lambda`, `walker` |
| `studieII` | 5 | keine | `chromatic` |
| `stria` | 1 | keine | `chromatic` |

Die 12-stufigen Stimmungen haben 31 Masken: `ionian`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`, `harmonicMinor`, `locrianSharp6`, `ionianSharp5`, `dorianSharp4`, `phrygianDominant`, `lydianSharp2`, `ultraLocrian`, `melodicMinor`, `dorianFlat2`, `lydianAugmented`, `lydianDominant`, `mixolydianFlat6`, `locrianSharp2`, `altered`, `wholeTone`, `halfWholeDim`, `messiaen3` … `messiaen7`, `majorPentatonic`, `minorPentatonic`, `chromatic`.

`chromatic` (jede Stufe) gibt es in jeder Stimmung.

#### Eigene Stimmungen

| Methode | Beschreibung |
|---|---|
| `new TuningSystem(name, pitchClasses, { repeatIntervalSemitones = 12, scaleMasks, metadata, stepSemitones })` | aus Abständen in Halbtönen |
| `TuningSystem.fromEDO(n, { name })` | *n* gleiche Teile der Oktave |
| `TuningSystem.fromRatio(name, stepRatio, stepsPerGroup, { groupRatio, repeatInterval })` | gleichstufig aus einem Frequenzverhältnis pro Stufe; `repeatInterval: false` = ohne Wiederholung |
| `TuningSystem.fromSemitones(name, semitones, { repeatInterval })` | explizite Abstände (reine Stimmung, historische Temperaturen); ein letzter Wert ≥ 12 gilt als Wiederholungsintervall |
| `TuningSystem.fromHz(name, frequencies, referenceHz, { repeatIntervalHz })` | gemessene Frequenzen (Gamelan, Instrumente) |

```js
const edo19 = TuningSystem.fromEDO(19);
const bp = TuningSystem.fromRatio("bp", Math.pow(3, 1 / 13), 13);   // wiederholt sich nach ≈ 19.02 Halbtönen
```

#### Methoden

| Methode | Beschreibung |
|---|---|
| `generatePitches(lowestPitch, highestPitch, { tuningSystemRoot, scaleRoot, mask, useAscending, referenceAHz })` | alle Tonhöhen im Bereich als MIDI-Floats |
| `addMask(mask)`, `addMasks(masks)` | eigene `ScaleMask` hinzufügen |
| `pitchClassOf(midi)` | Tonklasse innerhalb des Wiederholungsintervalls; `null` ohne Wiederholung |
| `midiToHz(midi, referenceAHz)`, `hzToMidi(hz, referenceAHz)` | Umrechnung |

`tuningSystemRoot` legt fest, auf welchem Ton die Stufe 0 liegt (Standard: C, genauer MIDI 0). Bei Stimmungen ohne Oktavwiederholung (Bohlen-Pierce, Studie II) sollte er gesetzt werden, sonst liegt das Gitter von MIDI 0 aus und trifft z. B. C4 nicht.

#### ScaleMask

```text
new ScaleMask(name, indices, { description = "", ascending = null })
```

`indices` sind Stufennummern (ab 0) der Stimmung. `ascending` ist eine optionale eigene Aufwärtsform (melodisch Moll, Maqamat, Ragas). `mask.pitchClasses(ts)` liefert die Abstände in Halbtönen.

```js
const ts = TUNING_SYSTEMS.edo12;
ts.addMask(new ScaleMask("myScale", [0, 1, 4, 5, 7, 8, 11]));
```

`toMidi(value, referenceAHz = 440, pitchUnit = "midi")` wandelt eine Tonhöhe in einen MIDI-Float um: Strings sind immer Notennamen, Zahlen werden bei `pitchUnit: "hz"` als Hz gelesen.

(js-pitchgrid)=
### PitchGrid

Ein Grid aus MIDI-Floats, erzeugt aus einer Stimmung und einer Maske in einem Register.

```js
const { PitchGrid } = require("PitchGrid");
const pg = PitchGrid.fromMask("edo12", "dorian", "d4", "d5");
pg.sorted();         // [62, 64, 65, 67, 69, 71, 72, 74]
pg.quantise(66.2);   // 67
```

#### Konstruktoren

| Methode | Beschreibung |
|---|---|
| `new PitchGrid(values, { referenceAHz })` | aus MIDI-Floats oder Notennamen |
| `PitchGrid.fromTuningSystem(ts, lowestPitch = 48, highestPitch = 84, tuningSystemRoot = null, { pitchUnit, referenceAHz })` | alle Stufen einer Stimmung im Bereich |
| `PitchGrid.fromMask(ts, maskName, lowestPitch = 48, highestPitch = 84, tuningSystemRoot = null, scaleRoot = null, { pitchUnit, referenceAHz, useAscending })` | Stufen einer Maske im Bereich |
| `PitchGrid.fromCorrelation(targetPitch, lowestPitch = 48, highestPitch = 84, { possibleSystems, possibleMasks, possibleScaleRoots, applyMask })` | sucht Stimmung und Maske, die am besten zu gegebenen Tönen passen |

`ts` ist ein Name aus `TUNING_SYSTEMS` oder ein `TuningSystem`-Objekt. Ohne `scaleRoot` beginnt die Maske auf dem tiefsten Ton des Bereichs: `fromMask("edo12", "dorian", "d4", "d5")` ist D-dorisch.

```js
// E-dorisch in Werckmeister I, Stimmung auf B gegründet, a' = 419 Hz
const pg = PitchGrid.fromMask("werckmeister1", "dorian", "e4", "e5", "bf3", "e4", { referenceAHz: 419 });
```

#### Methoden

| Methode | Beschreibung |
|---|---|
| `quantise(value)` | auf den nächsten Ton einrasten (von `Grid`) |
| `melodicContourFromEnvelope(env = null, numNotes = 16)` | `numNotes` Töne entlang einer Envelope; ohne Envelope bei jedem Aufruf eine neue zufällige Kontur |
| `makeChordFromTopNote(topNote, { primaryIntervals, numPrimaryNotes, numMaxNotes, clusterChance, minPitch, clusterIntervals })` | Akkord von `topNote` abwärts, mit diesem Grid als Sieb |
| `constrainToRange(lowestPitch = 48, highestPitch = 84)` | neues PitchGrid, alle Töne oktavweise in den Bereich gefaltet (Bereich ≥ 1 Oktave) |
| `findClosestTuningSystem(possibleSystems)` | `[[fehler, name], …]`, beste Stimmung zuerst |
| `findClosestMask(tuningSystemName = "edo12", possibleMasks)` | `[[fehler, name], …]`, beste Maske zuerst |
| `toMidiList()`, `toHzList()` | Töne als Array in MIDI oder Hz |
| `toEvents(noteDurationSec = 2)` | die Töne aufsteigend als Noten (siehe {ref}`js-events`) |

#### Eigenschaften

`lowestPitch`, `highestPitch`, `referenceAHz`, `tuningSystemName`, `maskName`, `tuningSystemRoot`, `scaleRoot`.

(js-dynamicgrid)=
### DynamicGrid

Ein Grid aus Pegeln in dB, ein Pegel pro Dynamikbezeichnung (`ppppp` … `fffff`), mit zugehöriger MIDI-Velocity.

```js
const { DynamicGrid } = require("DynamicGrid");
const dg = new DynamicGrid();                  // 3 dB Abstand, lautester Pegel 100 dB
dg.dynamicMapping.mf;                          // { velMidi: 75, db: 85 }
```

```text
new DynamicGrid(dynamicStepdB = 3, maxdB = 100, possibleDynamicsString = null, minVelMidi = 20, maxVelMidi = 120)
```

| Eigenschaft | Inhalt |
|---|---|
| `dynamicMapping` | `{ bezeichnung: { velMidi, db } }` |
| `possibleDynamicsString` | die Bezeichnungen von leise nach laut |
| `dynamicStepdB`, `maxdB`, `mindB` | Pegelraster |
| `minVelMidi`, `maxVelMidi` | Velocity-Bereich |

:::{note}
`Dynamics` (Abschnitt {ref}`js-dynamics`) und `DynamicGrid` verwenden zwei verschiedene Skalen: `pppp` … `ffff` mit festen Velocities bzw. `ppppp` … `fffff` mit Velocities aus dem dB-Raster.
:::


## Zeitobjekte

Alles, was in der Zeit stattfindet – eine Note, eine Geste, eine Phrase, ein ganzes Stück –, ist ein `TemporalObject`. Zeitobjekte bilden einen Baum: Ein Objekt kann Kinder enthalten, deren Zeiten **relativ** zum Elternobjekt angegeben sind.

```
TemporalObject
├── Phonon        eine Note, ein Akkord oder eine kurze Tonfolge
├── Gesture       eine Folge von Phonons
├── Phrase        mehrstimmige Struktur aus einer Palette von Elementen
└── GreasyPidgin  das Stück: Besetzung und Grids
```

(js-temporalobject)=
### TemporalObject

```js
const { TemporalObject } = require("TemporalObject");
```

```text
new TemporalObject(startTimeSec = 0, durationSec = 0, children = null, { envelopes, annotations, data })
```

| Eigenschaft | Inhalt |
|---|---|
| `startTimeSec`, `durationSec`, `endTimeSec` | Zeit in Sekunden, relativ zum Elternobjekt |
| `children` | Kinder (Zeiten relativ zu diesem Objekt) |
| `envelopes` | `{ name: Envelope }` – zeitlich veränderliche Werte, z. B. `dynamic` |
| `annotations` | `[[offsetSec, text], …]` – Textmarken |
| `data` | alles Weitere, z. B. `pitchMidi`, `bpm` |
| `id` | eindeutige Nummer |

Ohne Dauer erhält ein Container die Dauer seiner Kinder:

```js
const g = new TemporalObject(10, 0, [new TemporalObject(0, 1), new TemporalObject(1, 1)]);
g.durationSec;                          // 2
g.flatten().map(t => t.startTimeSec);   // [10, 11]  (absolute Zeiten)
```

| Methode | Beschreibung |
|---|---|
| `addChild(child)` | hängt eine **Kopie** von `child` an |
| `clone()` | tiefe Kopie mit neuen ids |
| `isContainer()` | `true`, wenn Kinder vorhanden sind |
| `setDuration(durationSec)` | Dauer setzen |
| `shiftTime(deltaSec)` | Start und Ende verschieben; Kinder wandern mit |
| `stretchTime(factor)` | Dauer strecken; Starts und Dauern der Kinder strecken sich mit |
| `sortChildren()` | Kinder nach Startzeit sortieren |
| `overlaps(other)` | `true`, wenn sich zwei Objekte zeitlich überschneiden |
| `resolveChildOverlaps(minDurationSec = 0)` | überlappende Nachbarn kürzen |
| `removeShortChildren(thresholdSec = 0.01)` | Kinder mit Dauer ≤ Schwelle entfernen |
| `clear()` | alle Kinder entfernen |
| `quantiseTime(grid, parentalStartSec = 0)` | absolute Start- und Endzeiten aller Blätter auf ein Grid einrasten |
| `flatten(parentalStartSec = 0)` | Kopien aller Blätter mit absoluten Zeiten; nichts wird verändert |
| `export(exporter)` | an ein Objekt mit Methode `export(temporalObject)` übergeben |

(js-phonon)=
### Phonon

Ein Phonon ist ein Notenereignis: Zeit, Tonhöhe(n), Dynamik. Mehrere Tonhöhen klingen entweder nacheinander (`"seq"`), gleichzeitig (`"chord"`) oder als Folge von Akkorden (`"chordSeq"`).

```js
const { Phonon, noteEvents, velocityOf } = require("Phonon");
```

```text
new Phonon(startTime = 0, duration = 0, pitch = 0, dynamic = 64, bpm = 60, options)
```

| Argument | Bedeutung |
|---|---|
| `startTime`, `duration` | in Sekunden, mit `timeUnit: "beats"` in Schlägen |
| `pitch` | Zahl, Notenname oder Array davon; bei `"chordSeq"` ein Array von Akkorden |
| `dynamic` | Velocity, Markierung (`"mf"`), Gabel (`"pp-f"`), Array oder Envelope |
| `bpm` | Tempo |

| Option | Standard | Bedeutung |
|---|---|---|
| `timeUnit` | `"seconds"` | `"seconds"` / `"s"` oder `"beats"` / `"b"` |
| `pitchUnit` | `"midi"` | `"midi"`, `"hz"` oder `"spn"`; Strings sind immer Notennamen |
| `dynamicUnit` | `"midi"` | `"midi"` (Velocity) oder `"dB"` |
| `chordOrSeq` | `"seq"` | `"seq"` / `"s"`, `"chord"` / `"c"`, `"chordSeq"` / `"cs"` |
| `autoSortChords` | `true` | Akkordtöne aufsteigend sortieren |
| `envelopes` | `null` | zusätzliche Envelopes |
| `referenceA` | `440` | Kammerton für Hz |
| `lyric` | `null` | Liedtext-Silbe |
| `ticksPerBeat` | `480` | MIDI-Auflösung |

Die Tonhöhen werden gleichmäßig über die Dauer verteilt:

```js
new Phonon(0, 1.5, [60, 64, 67], "mp");                               // C E G nacheinander, je 0.5 s
new Phonon(0, 2, ["c4", "e4", "g4"], "pp", 60, { chordOrSeq: "chord" });  // Akkord, 2 s
new Phonon(0, 3, [[60, 64, 67], [], [62, 65]], "mf", 60, { chordOrSeq: "cs" });   // Akkord, Pause, Akkord
new Phonon(1, 2, 60, 80, 120, { timeUnit: "beats" });                  // Start 0.5 s, Dauer 1 s
```

Dynamik als Zahl setzt die Anschlagstärke. Eine Gabel, ein Array oder eine Envelope erzeugt zusätzlich einen Verlauf (`aftertouch` im Event), die Anschlagstärke ist der erste Wert.

| Methode | Beschreibung |
|---|---|
| `toEvents(noteSelectKey = null)` | die spielbaren Noten (siehe {ref}`js-events`) |
| `unfold(noteSelectKey = null)` | Tonhöhen und Dynamik in Blatt-Kinder auflösen (macht `toEvents` automatisch) |
| `calculatePitch(key = "all")` | `"all"`, `"lowest"`, `"highest"`, `"mostCommon"`, `"leastCommon"`, `"chord"` |
| `glissando(startPitch, endPitch, pitchUnit)` | Glissando: Ausgangsnote plus Pitchbend-Verlauf |
| `setDynamicMarking(text)`, `getDynamicMarking()` | Dynamik neu setzen / lesen |
| `setLyric(text, offsetSec = 0)`, `getLyric()` | Liedtext setzen / lesen |
| `quantiseTime(grid, parentalStartSec = 0)` | Start und Ende als ein Ereignis auf ein Grid einrasten |

`noteSelectKey` wählt beim Auflösen: `null` folgt `chordOrSeq`; `"seq"` = eine Note pro Slot (tiefste Stimme); `"chordSeq"` = jede Tonhöhe jedes Slots; ein `calculatePitch`-Schlüssel = diese Tonhöhen über die ganze Dauer.

```js
const p = new Phonon(0, 2, 60, 80);
p.glissando(60, 67);
p.toEvents();   // [{ pitch: 60, bend: [0, 7], … }]
```

Mikrotöne stehen im Feld `bend`: `"eqf4"` (63.5) ergibt `pitch: 64, bend: [-0.5, -0.5]`.

Außerdem exportiert das Modul zwei Funktionen:

| Funktion | Beschreibung |
|---|---|
| `noteEvents(to)` | die Noten eines beliebigen TemporalObject-Baums als Event-Liste |
| `velocityOf(leaf)` | MIDI-Velocity eines Blatts |

:::{note}
Eine Gabel auf einem `"seq"`-Phonon ändert die Velocities der einzelnen Töne nicht. Für ein Crescendo über mehrere Töne eignet sich eine `Gesture` mit einer Liste von Dynamiken.
:::

(js-gesture)=
### Gesture

Eine Gesture ist eine Folge von Phonons (oder anderen Gestures) mit Zeiten relativ zum Start der Gesture.

```js
const { Gesture } = require("Gesture");
```

```text
new Gesture(startTimeSec = 0, phonons = null, durationSec = 0, { bpm = 60, ticksPerBeat = 480 })
```

#### `Gesture.fromRhythm`

Baut eine Gesture aus Notenwerten, die nacheinander klingen. Jeder Wert ist die Länge einer Note (in Schlägen); ein negativer Wert ist eine Pause. Tonhöhen und Dynamiken laufen zyklisch über die klingenden Noten und dürfen beliebig lang sein.

```text
Gesture.fromRhythm(rhythm, options)
```

```js
const g = Gesture.fromRhythm([1, 0.5, 0.5, -1, 1], {
    pitches: [60, 62, 64],    // [64, 67] im Array = Akkord
    dynamics: ["p", "f"],
    bpm: 120,
});
// Viertel C, Achtel D, Achtel E, Viertelpause, Viertel C
```

| Option | Standard | Bedeutung |
|---|---|---|
| `pitches` | `[60]` | Tonhöhen, zyklisch; ein Array darin ist ein Akkord |
| `dynamics` | `64` | Velocity, Markierung oder Envelope, zyklisch |
| `legato` | `1` | klingender Anteil des Notenwerts (`0.5` = staccato) |
| `repeats` | `1` | Rhythmus mehrmals hintereinander |
| `startOffset` | `0` | Start der Gesture |
| `timeUnit` | `"beats"` | `"beats"` oder `"seconds"` |
| `bpm` | `60` | Tempo |
| `pitchUnit`, `dynamicUnit`, `chordOrSeq`, `autoSortChords`, `ticksPerBeat`, `referenceA` | – | wie bei `Phonon` |

Die Dauer der Gesture umfasst auch Pausen am Ende.

#### `Gesture.fromLists`

Baut eine Gesture aus parallelen Listen, jede zyklisch wiederholt: Abstände zwischen den Einsätzen und Notenlängen getrennt. Geeignet, wenn Einsätze und Längen unabhängig voneinander laufen sollen.

```text
Gesture.fromLists(size, { startDeltas = 0.5, durations = 1, pitches = [0], dynamics = 64, startOffset = 0, timeUnit = "seconds", … })
```

```js
Gesture.fromLists(8, { startDeltas: [0.5, 0.25], durations: 0.4, pitches: [60, 62, [64, 67]], dynamics: ["p", "mf-ff"] });
```

Note 0 beginnt immer bei 0; Note *i* beginnt `startDeltas[i]` nach Note *i*−1. Der erste Wert von `startDeltas` wird daher im ersten Durchlauf übersprungen.

#### Methoden

| Methode | Beschreibung |
|---|---|
| `toEvents(noteSelectKey = null)` | alle Noten (siehe {ref}`js-events`) |
| `quantiseTime(grid, parentalStartSec = 0, durationThresholdSec = 0.001)` | Notenzeiten auf ein Grid einrasten, zu kurze Noten entfernen |
| `setDynamicMarkings(markings)`, `getDynamicMarkings()` | eine Dynamik pro Phonon, der Reihe nach |
| `setLyrics(lyrics, { offsetSec })`, `getLyrics()` | eine Silbe pro Phonon, der Reihe nach |
| Methoden von `TemporalObject` | `shiftTime`, `stretchTime`, `flatten`, … |

```js
const { TimeGrid } = require("TimeGrid");
g.quantiseTime(TimeGrid.series(0, 0.25, 16));   // auf Sechzehntel (bei 60 bpm) einrasten
```

(js-phrase)=
### Phrase

Eine Phrase setzt mehrere Stimmen aus einer Palette von Elementen zusammen. Jede Stimme ist eine Stufen-Envelope aus Paaren `(Zeit, Elementnummer)`.

```js
const { Phrase } = require("Phrase");
```

```text
new Phrase(startTimeSec = 0, elements = null, voices = null, { bpm = 60, timeUnit = "seconds", ticksPerBeat = 480 })
```

| Argument | Bedeutung |
|---|---|
| `elements` | `{ nummer: TemporalObject \| null }`; Nummer 0 ist immer eine Pause |
| `voices` | `{ name: Envelope }`; x = Zeit (in `timeUnit`, relativ zum Start), y = Elementnummer |

Jedes Element dauert bis zum nächsten Stützpunkt der Stimme; das letzte so lang wie das Element selbst. Eine Gesture wird auf ihren Platz gestreckt.

```js
const elements = { 0: null, 1: new Phonon(0, 1, "c4"), 2: new Phonon(0, 1, "e4") };
const voices = { soprano: new Envelope([[0, 1], [1, 2], [2, 0], [3, 1]]) };
const ph = new Phrase(0, elements, voices);
ph.toEvents();   // C bei 0 s, E bei 1 s, Pause, C bei 3 s
```

| Methode | Beschreibung |
|---|---|
| `toEvents(noteSelectKey = null)` | alle Noten aller Stimmen (siehe {ref}`js-events`) |


## Besetzung

(js-instrument)=
### Instrument

Ein Instrument mit Umfang, Transposition, fehlenden Tönen, Mikrotonfähigkeit, Schlüsseln und Dynamikumfang, nach `Instrument.lsp` aus *slippery chicken*. Umfang und fehlende Töne sind **notiert** angegeben; klingend = notiert + `transposition_semitones`.

```js
const { Instrument } = require("Instrument");
const cl = new Instrument({ name: "b-flat-clarinet", rangeMidi: [50, 91], transposition_semitones: -2 });
cl.in_range(49);         // [false, 0]   zu tief
cl.force_in_range(40);   // 52           oktavweise in den Umfang geschoben
```

| Option | Standard | Bedeutung |
|---|---|---|
| `name` | `"dummy"` | Name |
| `rangeMidi` | `[0, 127]` | notierter Umfang |
| `transposition_semitones` | `0` | klingend − notiert (B-Klarinette: −2) |
| `missing_notes` | `null` | notierte Töne, die das Instrument nicht spielen kann |
| `microTones` | `true` | kann Mikrotöne spielen |
| `chordsPossible` | `true` | kann Akkorde spielen |
| `numSystems`, `initClefs`, `possibleClefs` | – | Notation |
| `writtenDynamicRange` | `["ppppp", "fffff"]` | notierbarer Dynamikumfang |
| `physicalDynamicRangedB` | `[60, 100]` | tatsächlicher Pegelumfang |
| `midi_program` | `1` | General-MIDI-Programm |

| Methode | Beschreibung |
|---|---|
| `in_range(midi, { sounding, allow_microtones, allow_missing_notes })` | `[imUmfang, info]`: `info` 0 = zu tief, 1 = zu hoch, `null` = im Umfang oder wegen Mikroton / fehlendem Ton abgelehnt |
| `force_in_range(midi, { … })` | schiebt eine Tonhöhe oktavweise in den Umfang; rundet vorher auf Halbtöne, wenn Mikrotöne nicht erlaubt sind |

`sounding: true` liest `midi` als klingende Tonhöhe.

(js-instruments)=
### Instruments

Die Standardpalette mit 63 Instrumenten.

```js
const { STANDARD_INSTRUMENTS, get_standard_instrument } = require("Instruments");
STANDARD_INSTRUMENTS.flute.rangeMidi;   // [60, 98]
get_standard_instrument("violin");
```

`piccolo`, `flute`, `altoFlute`, `bassFlute`, `sopranino-recorder`, `soprano-recorder`, `alto-recorder`, `tenor-recorder`, `consort-tenor-recorder`, `bass-recorder`, `oboe`, `corAnglais`, `oboe-d-amore`, `EbClarinet`, `BbClarinet`, `AClarinet`, `bassClarinet`, `sopraninoSaxophone`, `sopranoSaxophone`, `altoSaxophone`, `tenorSaxophone`, `baritoneSaxophone`, `bassoon`, `contrabassoon`, `frenchHorn`, `frenchHornHi`, `frenchHornLo`, `CTrumpet`, `BbTrumpet`, `tenorTrombone`, `bassTrombone`, `tuba`, `marimba`, `vibraphone`, `accordion`, `glockenspiel`, `xylophone`, `celesta`, `crotales`, `piano`, `piano-lh`, `harpsichord`, `harp`, `organ`, `organ-pedals`, `percussion`, `tambourine`, `guitar`, `mandolin`, `soprano`, `mezzo`, `alto-voice`, `countertenor`, `tenor-voice`, `baritone-voice`, `bass-voice`, `violin`, `viola`, `viola-d-amore`, `cello`, `doubleBass`, `bass-guitar`, `computer`.

Namen mit Bindestrich werden mit eckigen Klammern gelesen: `STANDARD_INSTRUMENTS["alto-recorder"]`.

(js-player)=
### Player

Eine Spielerin oder ein Spieler mit einem oder mehreren Instrumenten aus einer Palette. Ohne Namen wird der Player nach seinen Instrumenten benannt.

```text
new Player(instruments = [], name = "", { instrumentPalette = STANDARD_INSTRUMENTS })
```

```js
const { Player } = require("Player");
new Player(["flute", "piccolo"]).name;   // "flute_piccolo"
```

Eigenschaften: `name`, `instruments`, `instrumentPalette`, `temporalObjects`.

(js-ensemble)=
### Ensemble

Eine `Map` von Playern nach Namen. Einträge können `Player`-Objekte, Instrumentennamen oder einfache Namen sein. Ein doppelter Name erhält eine Nummer.

```js
const { Ensemble } = require("Ensemble");
const e = new Ensemble(["flute", "flute", "violin"]);
e.players;               // ["flute", "flute_2", "violin"]
e.getPlayer("flute_2");  // Player
```

| Methode / Eigenschaft | Beschreibung |
|---|---|
| `players` | Namen in der Reihenfolge des Hinzufügens |
| `getPlayer(name)` | Player oder `null` |
| Methoden von `Map` | `get`, `has`, `size`, `for … of` |

(js-greasypidgin)=
### GreasyPidgin

Das Stück als Ganzes: ein `TemporalObject` mit Besetzung und den drei Grids.

```js
const { GreasyPidgin } = require("GreasyPidgin");
const gp = new GreasyPidgin("piece", { ensemble: ["flute", "violin"], pitchGrid: [60, 62, 63, 65, 67] });
```

| Option | Standard | Bedeutung |
|---|---|---|
| `ensemble` | leeres Ensemble | `Ensemble` oder Liste für `new Ensemble(…)` |
| `timeGrid` | leeres TimeGrid | `TimeGrid` oder Zeitpunkte |
| `pitchGrid` | leeres PitchGrid | `PitchGrid` oder Tonhöhen |
| `dynamicGrid` | `new DynamicGrid()` | muss ein `DynamicGrid` sein |
| `temporalObjects` | `null` | Kinder |
| `startTimeSec`, `durationSec` | `0` | Zeit |

Eigenschaften: `name`, `ensemble`, `timeGrid`, `pitchGrid`, `dynamicGrid` sowie alles von `TemporalObject`.

## Generatoren

(js-markov)=
### MarkovChains

Markow-Ketten beliebiger Ordnung. Ein Zustand ist ein Array der letzten `order` Symbole. Symbole dürfen Zahlen, Strings, `null` (z. B. eine Pause) oder andere JSON-darstellbare Werte sein.

```js
const { MarkovChain, MarkovRule, MarkovRules } = require("MarkovChains");
const chain = new MarkovChain();
chain.generateRulesFromList([60, 62, 64, 62, 60, 67, 64, 62], { order: 2 });
chain.getNElements({ seed: [60, 62], n: 16 });   // 2 + 16 Töne
```

#### MarkovChain

```text
new MarkovChain({ rules = null, seed = null, order = 1, n = 0 })
```

| Methode | Beschreibung |
|---|---|
| `generateRulesFromList(list, { order = 1, wrap = true })` | lernt Übergänge aus einer Folge; `wrap` verbindet das Ende mit dem Anfang |
| `getNElements({ seed, n, order })` | die `seed`-Symbole plus `n` neue; bricht früh ab, wenn ein Zustand keinen Nachfolger hat (Meldung `chain broken`) |
| `nextElement(state)` | ein Nachfolger für einen Zustand, `undefined` ohne Regel |

Bei `order: 2` braucht `seed` zwei Symbole.

#### MarkovRule und MarkovRules

Regeln können auch von Hand gebaut werden. Die Gewichte werden normalisiert.

```js
const rules = new MarkovRules([
    new MarkovRule([60], [62, 64], [3, 1]),   // nach 60: 62 (75 %) oder 64 (25 %)
    new MarkovRule([62], [60], [1]),
    new MarkovRule([64], [60], [1]),
]);
new MarkovChain({ rules }).getNElements({ seed: [60], n: 8 });
```

`MarkovRules` prüft, dass alle Regeln dieselbe Ordnung haben und jeder erreichbare Zustand eine Regel besitzt. Methoden: `has(state)`, `get(state)`, `size`. `MarkovRule.sample()` zieht einen Nachfolger.

(js-ca)=
### CellularAutomata

Elementare zelluläre Automaten nach Wolfram: eindimensional, zwei Zustände, Nachbarschaft aus drei Zellen, die Ränder sind verbunden.

```js
const { CellularAutomaton, CellularRules, intToBinary, binaryToInt } = require("CellularAutomata");
const ca = new CellularAutomaton({ rules: CellularRules.elementaryWolfram(30) });
ca.gen0fromSingleCell(32);
ca.iterate(20);
ca.printGenerations();
```

| Methode | Beschreibung |
|---|---|
| `CellularRules.elementaryWolfram(ruleNumber)` | Regel 0 … 255 |
| `rules.apply("010")` | nächster Zustand für eine Nachbarschaft |
| `gen0fromSingleCell(size = 32, position = null)` | eine aktive Zelle (Standard: in der Mitte) |
| `gen0fromInteger(n, maxNumCells = -1)` | Startgeneration aus den Binärziffern von `n` |
| `iterate(numIterations, { startIndex })` | so viele Schritte; mit `startIndex` von einer früheren Generation aus (spätere werden neu berechnet) |
| `elementaryWolframStep(fromKey)` | ein Schritt von Generation `fromKey` |
| `generationsAsArray()` | alle Generationen als Array von Zeilen (0/1) |
| `concatenateGenerations()` | alle Generationen als ein flaches Array |
| `generationsToEnvelope()` | Envelope: x = Generation, y = Zeile als Binärzahl |
| `printGenerations(on = "█", off = "·")` | als Text in die Konsole |

Hilfsfunktionen: `intToBinary(5, 4)` → `[0, 1, 0, 1]`, `binaryToInt([1, 0, 1])` → `5`.

(js-lsystem)=
### LSystem

Lindenmayer-Systeme: Ersetzungsregeln, die aus einem Axiom Generation für Generation neue Symbolfolgen erzeugen. Die `Turtle` übersetzt eine Generation in Liniensegmente.

```js
const { LSystem, Turtle, ProductionRule, ProductionRules } = require("LSystem");
const ls = LSystem.fromStrings("A", { A: "AB", B: "A" });
ls.iterate(4);
ls.currentGeneration().join("");   // "ABAABABA"
ls.lengths();                      // { 0: 1, 1: 2, 2: 3, 3: 5, 4: 8 }
```

| Methode | Beschreibung |
|---|---|
| `LSystem.fromStrings(axiom, rules)` | ein Zeichen pro Symbol; Leerzeichen werden ignoriert |
| `new LSystem(axiom, productionRules)` | mit beliebigen Symbolen (Zahlen, Strings, Objekte) |
| `step()` | ein Ersetzungsschritt |
| `iterate(numIterations, { fromStart })` | so viele Schritte; gibt die letzte Generation zurück |
| `currentGeneration()`, `generationAt(index)` | Generation als Array |
| `lengths()` | Länge jeder Generation |
| `reset()` | zurück zum Axiom |
| `interpret(turtleOrOptions, generation)` | Generation mit einer Turtle zeichnen |

`new ProductionRule(predecessor, successor)` und `new ProductionRules([…])` bauen Regeln von Hand; Symbole ohne eigene Regel bleiben unverändert. `ProductionRules.fromStrings({ F: "F-F++F-F" })` liest Regeln aus Strings.

#### Turtle

```js
const k = LSystem.fromStrings("F++F++F", { F: "F-F++F-F" });   // Koch-Schneeflocke
k.iterate(2);
const svg = Turtle.toSvg(k.interpret({ angle: 60 }));
```

| Symbol | Standardaktion |
|---|---|
| `F` | vorwärts zeichnen |
| `f` | vorwärts bewegen |
| `+` / `-` | links / rechts drehen um `angle` |
| `\|` | umdrehen |
| `[` / `]` | Position speichern / zurückholen |
| `>` / `<` | Schrittlänge mal / durch `lengthScale` |

Optionen: `angle = 90`, `stepLength = 1`, `lengthScale = 1`, `startPosition = [0, 0]`, `startHeading = 90` sowie für jede Aktion eine Liste von Symbolen (`draw: ["F", "A"]`). `turtle.run(symbols)` liefert `{ segments, bounds, maxDepth }`; `Turtle.toSvg(result, { size, margin, stroke, strokeWidth, background })` einen SVG-String.

(js-attractors)=
### StrangeAttractors

Seltsame Attraktoren als Bewegungsgleichungen; `buildTrajectory` integriert sie mit dem Runge-Kutta-Verfahren 4. Ordnung.

```js
const SA = require("StrangeAttractors");
const path = SA.buildTrajectory(SA.lorenz, [0.1, 0, 0], 0.01, 1000);   // 1000 Punkte [x, y, z]
```

| Funktion | Beschreibung |
|---|---|
| `lorenz`, `rossler`, `thomas`, `halvorsen` | Position `[x, y, z]` → Geschwindigkeit `[dx, dy, dz]` |
| `buildTrajectory(equations, start, dt = 0.01, steps = 80000)` | `steps` Positionen ab `start` |
| `rk4Step(equations, position, dt)` | ein Integrationsschritt |

(js-perceptron)=
### Perceptron

Ein einzelnes Neuron mit Gewichten und Bias, Beispiel für Beispiel trainiert.

```js
const { Perceptron } = require("Perceptron");
const p = new Perceptron({ learning_rate: 0.05, n_iterations: 2000 });
p.fit([[1], [2]], [2, 4]);
p.predict([3]);           // ≈ 6
p.predict([[1], [3]]);    // ≈ [2, 6]
```

| Option | Standard | Bedeutung |
|---|---|---|
| `learning_rate` | `0.01` | Lernrate |
| `n_iterations` | `1000` | Trainingsdurchläufe |
| `activationFunction` | `"identity"` | `"identity"` (lineare Regression), `"binary"`, `"tanh"`, `"ReLu"` |
| `verbose` | `false` | Fortschritt ausgeben |

`fit(features, targets)`: `features` ist ein Array von Beispielen (je ein Array von Zahlen), `targets` eine Zahl pro Beispiel. `predict` nimmt ein Beispiel oder mehrere.

## Max-Besonderheiten

### `require()` in Max

Max lädt ein Modul bei jedem `require()` neu und gibt bei fehlender Datei keinen Fehler aus, sondern `could not find file …` und ein leeres Objekt. GreasyPidgin lädt seine Module deshalb zuerst über den Namen (Suchpfad) und prüft das Ergebnis.

Weil dieselbe Klasse dadurch mehrfach existieren kann, prüft `instanceof` bei GreasyPidgin-Klassen zusätzlich eine gemeinsame Kennung. `phonon instanceof Phonon` funktioniert also auch, wenn das Phonon aus einer anderen Kopie des Moduls stammt.

### Häufige Fehlermeldungen

| Meldung | Ursache | Lösung |
|---|---|---|
| `Cannot find module` / `could not find file` | Ordner nicht im Suchpfad oder Subfolders aus | Einrichtung prüfen |
| `X is not a constructor` / `X is not a function` | geschweifte Klammern beim `require` fehlen | `const { Grid } = require("Grid");` |
| `expected 2 curves (one per segment), got 1` | Anzahl der Kurven ≠ Anzahl der Segmente | Punkte − 1 Kurven angeben |
| `mask 'dorian' not in 'edo24'. Available: [...]` | Maske gibt es in dieser Stimmung nicht | eine Maske aus der Liste wählen |
| `chain broken at state [...]` | Markow-Zustand ohne Nachfolger | längere Lernfolge oder `order: 1` |
| Noten erklingen gleichzeitig | Verzögerung fehlt | `[pipe]` verwenden, Verzögerung als letzte Zahl |
| Zeiten 1000-mal zu kurz oder zu lang | Sekunden statt Millisekunden | beim Ausgeben mit 1000 multiplizieren |
