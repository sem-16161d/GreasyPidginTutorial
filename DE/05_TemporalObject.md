# TemporalObject

## Was ist ein TemporalObject?

Ein `TemporalObject` – kurz `TO` – ist die Superklasse für alle Objekte, die in der Zeit organisiert werden können. Das `TO` vererbt alle Eigenschaften an:

`Phonon`: Ein *Klangpartikel* — die kleinste reduzierbare Einheit von Klang.

`Gesture`: Eine *Klanggeste* — eine Kombination mehrerer `Phonon`-Objekte, die eine Sinneinheit bilden.

`GreasyPidgin`: *Toplevel-Struktur*, die eine algorithmische Generation und Analyse komplexer Strukturen aus `Phonon`, `Gesture`, `Phrase` und `Section` ermöglicht.

Weitere `TO`-Objekte befinden sich noch in der Entwicklungsphase. Zur Zeit geplant sind:

`Phrase`: Eine abgeschlossene *musikalische Mikrostruktur*, bestehend aus einem oder mehreren `Phonon`- und `Gesture`-Objekten.

`Section`: Eine abgeschlossene *musikalische Makrostruktur*, ein Abschnitt aus `Phonon`-, `Gesture`- und/oder `Phrase`-Objekten.

`Photon`: Lichtsteuerdaten (noch nicht implementiert).

`Graphon`: Videosteuerdaten (noch nicht implementiert).


## Aufbau

Ein `TemporalObject` besteht aus drei Bereichen:

**Zeit** — `startTimeSec`, `durationSec`, `endTimeSec`. Für Container wird die Dauer automatisch aus den `children` berechnet.

**Hüllkurven** — `envelopes: dict[str, Envelope]`. Zeitlich variierende Eigenschaften des Objekts selbst, unabhängig vom Inhalt. Beispiele: `'vibrato'`, `'tremolo'`, `'opacity'` für visuelle Objekte.

**Daten** — `data: dict`. Alle domänenspezifischen Informationen. Ein MIDI-Export liest z.B. `data['pitchMidi']`, `data['dynamicdB']` und `data['bpm']`. Ein Video-Export würde `data['file']` und `data['framerate']` lesen. Das `TO` selbst stellt keine Annahmen über den Inhalt von `data` an.


## Ein TemporalObject erzeugen

Ein `TO` wird immer mit Startzeit und Dauer initialisiert. Alle weiteren Parameter sind keyword-only:

```python
from GreasyPidgin.TemporalObject import TemporalObject
from GreasyPidgin.Envelope import Envelope

# Einfaches Blatt-Objekt mit Daten
leaf = TemporalObject(
    0.0, 10.0,
    data={
        "pitchMidi":    60.0,
        "dynamicdB":    80.0,
        "bpm":          120,
        "ticksPerBeat": 480,
    })

# Mit Hüllkurven
leaf2 = TemporalObject(
    1.0, 3.1415,
    envelopes={"vibrato": Envelope([0, 1, 0, 1, 0, 1, 0])},
    annotations=[("Hello World!", 0.0)],
    data={"pitchMidi": 64.0, "dynamicdB": 90.0, "bpm": 120},
)

# Container — Dauer wird automatisch aus children bestimmt
container = TemporalObject(
    0.0,
    children=[leaf, leaf2],
)

print(container)

##########  OUTPUT  ############################################################
#> TemporalObject(id=2, start=0.000, dur=4.142, end=4.142, children=2)
```

Wird ein `TO` mit `children` initialisiert, so werden Dauer und Endzeitpunkt automatisch anhand der Zeitwerte der `children` bestimmt. Die Zeiten der `children` sind immer *relativ* zur Startzeit des Containers.


## Ein TemporalObject exportieren

Export geschieht über separate Exporter-Klassen aus `Exporters.py`. Das `TO` selbst kennt keine Exportformate — es gibt sich nur an einen Exporter weiter:

```python
from GreasyPidgin.TemporalObject import TemporalObject
from GreasyPidgin.Exporters import MidiExporter, JsonExporter, CsvExporter

t1 = TemporalObject(0.0, 2.0, data={"pitchMidi": 60.0, "dynamicdB": 80.0, "bpm": 120})
t2 = TemporalObject(2.0, 2.0, data={"pitchMidi": 64.0, "dynamicdB": 75.0, "bpm": 120})
to = TemporalObject(0.0, children=[t1, t2])

# MIDI
to.export(MidiExporter("/tmp/out.mid"))

# JSON — komplette Baumstruktur
to.export(JsonExporter("/tmp/out.json"))

# CSV — Baumstruktur als id/parentId Tabelle
to.export(CsvExporter("/tmp/out.csv"))

##########  OUTPUT  ############################################################
#> MidiExporter: saved -> /tmp/out.mid
#> JsonExporter: saved -> /tmp/out.json
#> CsvExporter:  saved -> /tmp/out.csv
```

Oder alle auf einmal:

```python
for exporter in [
    MidiExporter("/tmp/out.mid"),
    JsonExporter("/tmp/out.json"),
    CsvExporter("/tmp/out.csv"),
]:
    to.export(exporter)
```


## MIDI-Export im Detail

Der `MidiExporter` liest folgende Schlüssel aus `leaf.data`:

| Key | Typ | Bedeutung | Default |
|---|---|---|---|
| `pitchMidi` | `float` | MIDI-Notenwert (Nachkommastellen = Mikrotöne) | `0.0` |
| `dynamicdB` | `float` | Lautstärke in dB | `100.0` |
| `bpm` | `float` | Tempo | `60.0` |
| `ticksPerBeat` | `int` | MIDI-Auflösung | `480` |
| `annotations` | `list` | `[(offsetSec, text), ...]` → Lyric-Events | `[]` |

Zusätzlich werden alle `leaf.envelopes` als MIDI-CC- bzw. Pitchwheel-Daten exportiert (sofern `parseEnvelopes=True`).


### Parameter des MidiExporters

```python
MidiExporter(
    path           = "/tmp/out.mid",
    trackName      = "track",
    parseEnvelopes = True,
    perNoteTracks  = False,  # True: überlappende Noten auf separate Tracks
    pitchBendRange = 4096,   # Ticks pro Halbton; 4096 × 2 = voller Wheel-Range
    channel        = 0,      # MIDI-Kanal (0-indiziert)
)
```

:::{danger}
Die `pitchBendRange` muss auf den Synthesizer abgestimmt sein! Die meisten Synthesizer haben entweder `2**10` oder `2**12` Auflösung.

| **Synth-Plugin (Ableton Live)** | **Pitch Bend Range** |
|---|---|
| Analog | `2**12` |
| Drift | `2**12` |
| Electric | `2**10` |
| Meld | `2**10` |
| Operator | `2**10` |
| Tension | `2**12` |
| Wavetable | `2**12` |

Kalibrierungsdateien erzeugen:

```python
from GreasyPidgin.TemporalObject import TemporalObject
from GreasyPidgin.Exporters import MidiExporter

container = TemporalObject(0.0)
for i in range(11):
    container.addChild(TemporalObject(
        i / 2, 0.5,
        data={"pitchMidi": 60 + (i / 10), "dynamicdB": 100.0, "bpm": 60},
    ))

for pbRange in [2**10, 2**12]:
    container.export(MidiExporter(
        f"/tmp/pitchBendConfig_{pbRange}.mid",
        pitchBendRange=pbRange,
    ))
```
:::


### Mikrotöne

```python
from GreasyPidgin.TemporalObject import TemporalObject
from GreasyPidgin.Exporters import MidiExporter

to = TemporalObject(0.0, 10.0, data={
    "pitchMidi": 60.5,   # Viertelton über c4
    "dynamicdB": 80.0,
    "bpm": 60,
})

to.export(MidiExporter("/tmp/quartertone.mid"))
```

Der `MidiExporter` berechnet automatisch den nächsten 12-EDO-Halbton als MIDI-Notenwert und schreibt die Differenz als Pitchwheel-Envelope.


### Polyphonie und perNoteTracks

Enthält ein `TO` gleichzeitige Ereignisse mit verschiedenen mikrotonalen Abweichungen, muss `perNoteTracks=True` gesetzt werden. Andernfalls überschreiben sich die Pitchwheel-Befehle gegenseitig.

```python
from GreasyPidgin.TemporalObject import TemporalObject
from GreasyPidgin.Exporters import MidiExporter

t1 = TemporalObject(0.0, 10.0, data={"pitchMidi": 60.0,   "dynamicdB": 80.0, "bpm": 60})
t2 = TemporalObject(1.0, 10.0, data={"pitchMidi": 69.69,  "dynamicdB": 80.0, "bpm": 60})
container = TemporalObject(0.0, children=[t1, t2])

# Pitchwheel-Konflikte möglich:
container.export(MidiExporter("/tmp/singleTrack.mid"))

# Separate Tracks pro Note — sicher:
container.export(MidiExporter("/tmp/perNoteTracks.mid", perNoteTracks=True))
```


## Baumstruktur

Ein `TO` kann beliebig tief verschachtelte `children` enthalten. Beim Exportieren wird der Baum automatisch zu einer flachen Liste von Blatt-Objekten mit absoluten Zeitwerten aufgefaltet (`flatten()`), ohne dass das Original verändert wird.

```python
from GreasyPidgin.TemporalObject import TemporalObject

t1 = TemporalObject(0.0,  10.0, data={"pitchMidi": 60.0, "bpm": 120})
t2 = TemporalObject(5.0,  10.0, data={"pitchMidi": 64.0, "bpm": 120})
t3 = TemporalObject(0.0,  children=[t1, t2])
t4 = TemporalObject(3.0,  children=[t1, t2, t3])
t5 = TemporalObject(5.0,  children=[t1, t2, t3, t4])

# Alle Blatt-Objekte mit absoluten Zeiten
for leaf in t5.flatten():
    print(leaf)
```

Die Zeiten der `children` sind immer relativ zum jeweiligen Container. `flatten()` addiert die Offsets rekursiv und gibt Kopien zurück — das Original bleibt unberührt.
