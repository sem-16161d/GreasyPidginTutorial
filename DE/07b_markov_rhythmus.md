# Markov-Rhythmus

Eine Einführung in die Erzeugung von Rhythmen mit Markov-Ketten und GreasyPidgin.

Am Ende dieses Tutorials hast du eine MIDI-Datei mit einem Rhythmusmuster, dessen **Notenwerte** durch ein Markov-Modell bestimmt werden — ein Modell, das lernt, wie Notenwerte in einer musikalischen Folge aufeinander folgen.

---

## Rhythmus als Markov-Kette

Rhythmus lässt sich als eine Folge von Notenwerten beschreiben: Viertel, Achtel, Sechzehntel, Halbe. Eine Markov-Kette kann lernen, welche Notenwerte in einer musikalischen Folge wahrscheinlich aufeinander folgen — zum Beispiel, dass auf eine Sechzehnte meist weitere Sechzehntel folgen, aber gelegentlich eine Halbe als Variation kommt.

## Gesamtüberblick

```
Markov-Regeln (Notenwerte + Gewichte)
    ↓
MarkovChain.getNElements()
    ↓
Liste von Notenwerten (als Beat-Brüche)
    ↓
Skalierung auf Taktschläge (* 4)
    ↓
Gesture.fromLists()
    ↓
MIDI-Datei
```

---

## Schritt 1 — Importe

```python
from GreasyPidgin.Gesture import Gesture
from random import choices
from GreasyPidgin.MarkovChains import MarkovChain, MarkovRule, MarkovRules
```

`choices` aus Pythons `random`-Modul wird hier für die zufällige Auswahl der Tonhöhen verwendet — ohne Markov-Logik, da der Fokus auf dem Rhythmus liegt.

---

## Schritt 2 — Rhythmische Übergangsregeln definieren

```python
ruleHalbe  = MarkovRule(1/2,  [1/2, 1/4, 1/16], [1, 1, 0.5])
rule4tel   = MarkovRule(1/4,  [1/2, 1/8],        [1, 1])
rule8tel   = MarkovRule(1/8,  [1/16, 1/8],       [1, 4])
rule16tel  = MarkovRule(1/16, [1/16, 1/2],       [8, 1])
```

Die Zustände sind hier keine Tonhöhen, sondern **Notenwerte als Brüche**:

| Zustand | Notenwert |
|---|---|
| `1/2` | Halbe Note |
| `1/4` | Viertelnote |
| `1/8` | Achtelnote |
| `1/16` | Sechzehntelnote |

Die Gewichte beschreiben musikalisches Verhalten:
- `rule8tel`: nach einer Achtelnote folgt viermal so häufig wieder eine Achtelnote wie eine Sechzehntelnote — **Läufe bleiben Läufe**.
- `rule16tel`: nach einer Sechzehntel folgt achtmal so häufig wieder eine Sechzehntel wie eine Halbe — **dichte Stellen bleiben dicht**, aber gelegentliche Pausen kommen vor.
- `ruleHalbe`: nach einer Halben ist eine weitere Halbe oder eine Viertel gleich wahrscheinlich — **Ruhepunkte führen zu weiteren Ruhepunkten**.

:::{note}
Die Notenwerte werden als Brüche einer ganzen Note angegeben. `1/4` bedeutet also nicht „eine Viertelsekunde", sondern eines 'Viertelnote' , also **einem Schlag**. Die spätere Skalierung (`* 4`) wandelt diese in Taktschläge -`beats`- um.
:::

---

## Schritt 3 — Sequenz generieren

```python
seed = 1/2
numElements = 200

mr = MarkovRules([ruleHalbe, rule4tel, rule8tel, rule16tel])
mc = MarkovChain(rules=mr, seed=seed)

rhthmsRaw = mc.getNElements(n=numElements)
```

Die Kette beginnt mit einer Halben (`seed = 1/2`) und erzeugt 200 Notenwerte nach den definierten Übergangswahrscheinlichkeiten.

---

## Schritt 4 — Skalierung auf Taktschläge

```python
rhtmsMatched = [r * 4 for r in rhthmsRaw]
```

`Gesture.fromLists` mit `timeUnit='beats'` erwartet Zeiten in Taktschlägen. Da unsere Notenwerte als **Brüche einer ganzen Note** definiert sind (ganze Note = 4 `beats`), multiplizieren wir mit 4:

| Rohwert | × 4 | Bedeutung |
|---|---|---|
| `1/2` | `2.0` | 2 `beats` = Halbe |
| `1/4` | `1.0` | 1 `beats` = Viertelnote |
| `1/8` | `0.5` | 0.5 `beats` = Achtelnote |
| `1/16` | `0.25` | 0.25 `beats` = Sechzehntelnote |

---

## Schritt 5 — Tonhöhen zufällig auswählen

```python
pitchListMidi = choices([48, 55, 60, 61], [4, 2, 4, 1], k=numElements)
```

Da hier der Rhythmus im Mittelpunkt steht, werden die Tonhöhen einfach zufällig aus einer kleinen Auswahl gezogen — ohne jede Markov-Logik. `choices` aus Pythons `random`-Modul funktioniert wie ein gewichtetes Lotto:

```python
pitchListMidi = choices([48, 55, 60, 61], [4, 2, 4, 1], k=numElements)
```

| Argument | Bedeutung |
|---|---|
| `[48, 55, 60, 61]` | Die möglichen Tonhöhen: C3, G3, C4, Df4 |
| `[4, 2, 4, 1]` | Relative Gewichte: C3 und C4 viermal so häufig wie Df4 |
| `k=numElements` | Anzahl der zu ziehenden Werte (200) |

Im Gegensatz zu einer Markov-Kette hat jede Ziehung **kein Gedächtnis** — die Wahrscheinlichkeiten ändern sich nie in Abhängigkeit vom vorherigen Ton. 

:::{note}
`choices` wählt **mit Zurücklegen** — dieselbe Tonhöhe kann beliebig oft hintereinander gezogen werden. 
:::
---

## Schritt 6 — Geste aufbauen und exportieren

```python
Gesture.fromLists(
    numElements, 0, 
    rhtmsMatched, rhtmsMatched, 
    pitchListMidi, bpm=161, 
    timeUnit='beats').toMidi()
```

Hier werden sowohl `startDeltas` als auch `durations` auf dieselbe Liste `rhtmsMatched` gesetzt — jede Note beginnt genau dann, wenn die vorherige endet (**legato**, kein Überlappen, keine Pause).

---

## Experimente

**Mehr Sechzehntel-Läufe:**
```python
rule16tel = MarkovRule(1/16, [1/16, 1/2], [16, 1])   # noch seltener unterbrochen
```

**Andere Startsituation:**
```python
seed = 1/16   # beginnt mit einem Sechzehntel-Lauf
seed = 1/4    # beginnt gemächlich
```

**Pausen einbauen** — indem du einen Zustand `0` (Pause) einführst:
```python
rulePause = MarkovRule(0, [1/4, 1/8], [1, 1])
ruleHalbe = MarkovRule(1/2, [1/2, 1/4, 0], [1, 1, 1])   # Halbe kann in Pause übergehen
```
