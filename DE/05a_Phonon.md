# Phonon

## Was ist ein Phonon?

Ein `Phonon` ist ein *Klangpartikel* — die kleinste beschreib- und reduzierbare Einheit von Klang. Der Komplexität sind dabei keine Grenzen gesetzt.

Ein `Phonon` erweitert das `TemporalObject` um musikalisches Vokabular: Tonhöhen in verschiedenen Einheiten, Lautstärke, Akkord- und Sequenzstrukturen. Die musikalischen Informationen werden intern verarbeitet und erst beim Export über `unfold()` in konkrete `TemporalObject`-Blätter aufgelöst.


## Ein Phonon erzeugen

### Sekunden oder Beats

Ein `Phonon` muss wie ein `TemporalObject` immer mit einer Startzeit und einer Dauer initialisiert werden. Im musikalischen Kontext kann die Zeit entweder in `'seconds'` / `'s'` (Standard) oder `'beats'` / `'b'` angegeben werden:

```python
from GreasyPidgin.Phonon import Phonon

ps = Phonon(1, 10, timeUnit='s')
pb = Phonon(1, 10, timeUnit='b', bpm=161)

print(ps)
print(pb)

##########  OUTPUT  ############################################################
# Phonon(
#    id           : 0
#    start        : 1.000s  (1.000 beats)
#    duration     : 10.000s  (10.000 beats)
#    bpm          : 60.0
#    chordOrSeq   : seq
#    allPitches   : [0.0]
#    lowest       : [0.0]
#    highest      : [0.0]
#    voices       : 1
#    envelopes    : ['dynamic']
#    children     : 0
# )

# Phonon(
#    id           : 1
#    start        : 0.373s  (1.000 beats)
#    duration     : 3.727s  (10.000 beats)
#    bpm          : 161
#    ...
# )
```


### Tonhöhe

Die wesentliche Erweiterung gegenüber dem `TemporalObject` ist, dass Tonhöhen in verschiedenen Einheiten angegeben werden können: `'midi'` (Standard), `'hz'` oder `'spn'`[^1].

```python
from GreasyPidgin.Phonon import Phonon

pMidi      = Phonon(1, 1, pitch=68)
pMidiMicro = Phonon(1, 1, pitch=68.45)      # Mikrotöne als Nachkommastellen
pSPN       = Phonon(1, 4, 'af4', pitchUnit='spn')
pHz        = Phonon(1, 2, 440,   pitchUnit='hz')

print("MIDI-Wert für pSPN:", pSPN.allPitches[0])
print("MIDI-Wert für pHz:", pHz.allPitches[0])

##########  OUTPUT  ############################################################
# MIDI-Wert für pSPN: 68.0
# MIDI-Wert für pHz:  69.0
```


### Lautstärke

`dynamic` kann entweder ein einzelner Wert oder zeitlich variierend sein:

```python
from GreasyPidgin.Phonon import Phonon
from GreasyPidgin.Envelope import Envelope

# Einzelwert — wird als Velocity beim Export genutzt (dynamicUnit='midi' oder 'dB')
pFlat  = Phonon(0, 4, 60, dynamic=80,            dynamicUnit='midi')
pFlat2 = Phonon(0, 4, 60, dynamic=90.0,          dynamicUnit='dB')

# Liste — gleichmäßig über die Dauer verteilt (Crescendo)
pCresc = Phonon(0, 4, 60, dynamic=[20, 60, 127], dynamicUnit='midi')

# Envelope — volle Kontrolle über die zeitliche Form
env    = Envelope([(0, 20), (2, 127), (4, 60)])
pEnv   = Phonon(0, 4, 60, dynamic=env)
```

:::{note}
Ist `dynamic` eine Liste oder `Envelope`, wird die Hüllkurve als `envelopes['aftertouch']` gespeichert und beim MIDI-Export als Channel-Aftertouch exportiert. Ein einzelner Wert wird als `data['dynamicdB']` gespeichert und als Velocity der Note verwendet.
:::


## Tonhöhenstruktur

Ein `Phonon` kennt drei Tonhöhenstrukturen, gesteuert über `chordOrSeq`:

### `'seq'` / `'s'` — Monophones Sequenz (Standard)

Eine Abfolge von Tonhöhen, gleichmäßig über die Dauer verteilt. Sonderfall Länge 1 = eine einzige gehaltene Note.

```python
from GreasyPidgin.Phonon import Phonon

pSingle = Phonon(1, 1, 'af4', pitchUnit='spn')
pList   = Phonon(1, 1, ['af4'], pitchUnit='spn')
print(pSingle.allPitches == pList.allPitches,
      "— beide sind eine einelementige 'seq'")

pSeq = Phonon(1, 1, ['af4', 'b4', 'bf4', 'b4'], pitchUnit='spn')
print(pSeq)

##########  OUTPUT  ############################################################
# True — beide sind eine einelementige 'seq'
# Phonon(
#    id           : 2
#    allPitches   : [68.0, 70.0, 71.0]
#    lowest       : [68.0]
#    highest      : [71.0]
#    voices       : 1
#    ...
# )
```


### `'chord'` / `'c'` — Akkord

Alle Töne klingen gleichzeitig für die gesamte Dauer. Geeignet für Akkorde und Spektren.

```python
from GreasyPidgin.Phonon import Phonon

pChladni = Phonon(
    2, 10,
    [320, 630, 733, 854, 1370, 1650, 1850, 3159],
    pitchUnit='hz',
    chordOrSeq='chord',
)
print(pChladni)

##########  OUTPUT  ############################################################
# Phonon(
#    id           : 0
#    allPitches   : [63.49, 75.21, 77.84, 80.48, 88.66, 91.88, 93.86, 103.13]
#    lowest       : [63.49]
#    highest      : [103.13]
#    voices       : 8
#    ...
# )
```

:::{figure}
Beispiel-Spektrum aus Chladni-Platten-Resonanzen.
:::


### `'chordSeq'` / `'cs'` — Akkordsequenz

Eine Folge von Akkorden, gleichmäßig über die Dauer verteilt. Die Anzahl der Stimmen darf zwischen den Akkorden variieren. Standardmäßig werden die Töne innerhalb jedes Akkords von unten nach oben sortiert (`autoSortChords=True`).

```python
from random import randint
from numpy import clip
from GreasyPidgin.Phonon import Phonon
from GreasyPidgin.Pitch import spntof

# Zufällige Frequenzverläufe — wie das THX-Logo-Thema
stages = [[randint(200, 400) for _ in range(30)]]
for _ in range(8):
    newStage = [int(clip(f + randint(-20, 20), 200, 400)) for f in stages[-1]]
    stages.append(newStage)

finalChordSPN = [
    'd1','d1','d2','d2','d3','d3','d3',
    'a2','a2',
    'd4','d4','dtf4','dts4','d5','d5','dtf5','dts5','d6','d6','dtf6','dts6',
    'a4','atf4','ats4','a5','atf5','ats5',
    'fs5','fstf5','fsts5',
]
stages.append([spntof(f) for f in finalChordSPN])

thx = Phonon(0, 29, stages, pitchUnit='hz', chordOrSeq='chordSeq')
print(thx)
```

```{image} IMG/moorer_thx.png
:alt: Original-Handschrift von James A. Moorer für das "THX LOGO THEME"
:width: 650px
:align: center
```


## Glissando

Ein Glissando wird als *analytische / deskriptive* Hüllkurve gespeichert — es beeinflusst den MIDI-Export nicht direkt, steht aber für Score-Rendering, Analyse oder eigene Exporter zur Verfügung.

```python
from GreasyPidgin.Phonon import Phonon

p = Phonon(0, 4, 'c4', pitchUnit='spn')
p.glissando('c4', 'e4')   # Glissando von C4 nach E4 über 4 Sekunden

print(p.envelopes['glissando'])  # Envelope mit MIDI-Werten 60.0 → 64.0
```


## unfold() — Tonhöhen auflösen

Bevor ein `Phonon` exportiert werden kann, müssen seine Tonhöhen in konkrete `TemporalObject`-Blätter aufgelöst werden. Das geschieht automatisch beim Aufruf einer Export-Methode, kann aber auch manuell ausgelöst werden:

```python
p = Phonon(0, 10, ['c4', 'e4', 'g4'], pitchUnit='spn', chordOrSeq='seq')
p.unfold(noteSelectKey='lowest')

for child in p.children:
    print(child)
```

`unfold()` ist rekursiv — enthält ein `Phonon` weitere `Phonon`-Objekte als `children`, werden diese zuerst aufgelöst.


### Optionen für `noteSelectKey`

| Key | Bedeutung |
|---|---|
| `'lowest'` | Tiefste Note aus allen MIDI-Werten (Standard) |
| `'highest'` | Höchste Note |
| `'mostCommon'` | Häufigste Note |
| `'leastCommon'` | Seltenste Note |
| `'all'` | Alle Noten als Blockakkord, inkl. Dopplungen |
| `'chord'` / `'allSet'` | Alle Noten als Blockakkord, ohne Dopplungen |
| `'seq'` | Eine Note pro Zeitslot (aus der ersten Pitch-Envelope) |
| `'chordSeq'` | Alle Stimmen aller Akkord-Zeitslots |


## Export

### MIDI

```python
from GreasyPidgin.Phonon import Phonon

p = Phonon(0, 10, [['af4','a4'],['af4','gqs4'],['af4','a4']],
           chordOrSeq='cs', pitchUnit='spn')

# Standard: tiefste Note
p.toMidi('/tmp/lowest.mid')

# Alle Akkorde auf separaten Tracks
p.toMidi('/tmp/chordSeq.mid', noteSelectKey='chordSeq', perNoteTracks=True)
```

### Alle Formate

```python
p.toMidi('/tmp/out.mid',  noteSelectKey='chordSeq', perNoteTracks=True)
p.toXml( '/tmp/out.xml',  noteSelectKey='lowest')
p.toCsv( '/tmp/out.csv',  noteSelectKey='all')
p.toJson('/tmp/out.json', noteSelectKey='chord')
```

### Beispiele für alle noteSelectKey-Optionen

Sequenz:

```python
from GreasyPidgin.Phonon import Phonon

p = Phonon(0, 10,
    ['af4','a4','a4','gqs4','af4','a4'],
    chordOrSeq='s', pitchUnit='spn')

for key in ['seq','chordSeq','lowest','highest','mostCommon','leastCommon','allSet','chord']:
    p.toMidi(f'/tmp/seq_{key}.mid', noteSelectKey=key)
```

Akkordsequenz:

```python
from GreasyPidgin.Phonon import Phonon

p = Phonon(0, 10,
    [['af4','a4'],['a4','gqs4'],['af4','a4']],
    chordOrSeq='cs', pitchUnit='spn')

for key in ['seq','chordSeq','lowest','highest','mostCommon','leastCommon','allSet','chord']:
    p.toMidi(f'/tmp/cs_{key}.mid', noteSelectKey=key)
```

Akkord:

```python
from GreasyPidgin.Phonon import Phonon

p = Phonon(0, 10,
    ['af4','a4','a4','gqs4','af4','a4'],
    chordOrSeq='c', pitchUnit='spn')

for key in ['seq','chordSeq','lowest','highest','mostCommon','leastCommon','allSet','chord']:
    p.toMidi(f'/tmp/chord_{key}.mid', noteSelectKey=key)
```


[^1]: *Scientific Pitch Notation*, siehe `Pitch.py`, `02_Pitch.md` oder **Kapitel 2: Pitch**.
