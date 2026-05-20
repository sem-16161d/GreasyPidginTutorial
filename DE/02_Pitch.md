# Pitch
Eine Python-Adaption von Michael Edwards' ```Pitch.lsp``` aus seiner Kompositionsumgebung ```slippery chicken```[^1]. ```Pitch.py``` enthält dabei keine eigenständige Klasse, sondern ist lediglich eine Sammlung von Funktionen. Das System basiert auf der *Scientific Pitch Notation (SPN)*[^2]. 

### Aufbau

#### Oktavlagen

In diesem System ist der tiefste Ton als ```c0``` = *16.3516 Hz* definiert, bei einem Kammerton von ```a4``` = *440 Hz*. Die Basis bilden die englischen Notennamen: ```A,B,C,D,E,F,G``` gefolgt von der Oktavlage von ```0-9```.

| SPN | DE | MIDI | Hz (*a=440*)| Hz (*a = 442*)|
| --- | --- | --- | --- | --- |
| ```c0``` | Subkontra C| 12 | 16.35    | 16.42     |
| ```c1``` | Kontra C   | 24 | 32.70    | 32.85     |
| ```c2``` | großes C   | 36 | 65.4     | 65.70     |
| ```c3``` | kleines c  | 48 | 130.81   | 131.4     |
| ```c4``` | c'         | 60 | 261.626  | 262.81    |
| ```c5``` | c''        | 72 | 523.25   | 525.63    |
| ```c6``` | c'''        | 84 | 1046.5   | 1051.26   |
| ```c7``` | c''''        | 96 | 2093     | 2102.52   |
| ```c8``` | c'''''        | 108| 4186     | 4205      |

#### Versetzungszeichen

Vorzeichen / Versetzungszeichen werden mittels Suffix indiziert: ```f``` für *flat* und ```s``` für *sharp*.

| SPN | DE | MIDI | Hz (*a=440*)| Hz (*a = 442*)|
| --- | --- | --- | --- | --- |
| ```af4``` |  as'| 68 | 415.3    | 417.19     |
| ```cs3``` | kleines cis   | 49 | 138.59    | 139.22     |

Das gleiche gilt für Mikrotonalität[^3]:

| Suffix | EN | DE| CENT |
| --- | --- | --- | --- |
|```qf```| quarter tone flat | Viertelton tief | -50 |
|```qs```| quarter tone sharp | Viertelton hoch | +50 |
|```sf```| sixth tone flat | Sechstelton tief | -33 |
|```ss```| sixth tone sharp | Sechstelton hoch | +33 |
|```tf```| twelfth tone flat | Zwölftelton tief | -17 |
|```ts```| twelfth tone sharp | Zwölftelton hoch | +17 |

### Umrechnungen

Um zwischen den verschiedenen Tonhöhendarstellungen zu wechseln sind die Funktionen nach ihrer Entsprechungen in ```PureData``` und ```MAX/MSP``` benannt. Die Umrechnung Frequenz zu MIDI (*ftom*) folgt der Formel[^4]:

```{math}
:enumerated: false
f(a_{ref}, MIDI) = a_{ref} * 2^{(MIDI - 69)/12}
```

Und umgekehrt MIDI zu Frequenz (*mtof*):
```{math}
:enumerated: false

MIDI(a_{ref}, f) = 69 + 12 * log_2(f / a_{ref})

```

Der default-Wert für den Referenz-Kammerton {math}`a_{ref}` ist 440 Hz, lässt sich aber via ```referenceA4``` auf eine beliebige Frequenz ändern. ```spntom``` und ```spntof``` sind die Equivalente um *SPN* in MIDI und Frequenz umzurechnen. Eine direkte Umwandlung von ```MIDI``` oder *Frequenz* in *SPN* ist zur Zeit noch nicht implementiert, da dieses die Bestimmung von Stimmungssystemen vorausssetzt. Eine solche Umwandlung muss über ```PitchGrid``` erfolgen.


```python
from GreasyPidgin.Pitch import mtof,ftom, spntom, spntof
pitch = 'c4'
midi = spntom(pitch)
freqDirect = spntof(pitch, referenceA4=440)
freqViaMtof = mtof(midi)
back2Midi = ftom(freqDirect)

print(
    " pitch           : ", pitch, '\n',
    "midi            : ", midi, '\n',
    "freq            : ", freqDirect, '\n',
    "freq(from Midi) : ", freqViaMtof, '\n',
    "freq to midi    : ", back2Midi, '\n',
)

##########  OUTPUT  ############################################################
#>  pitch           :  c4 
#>  midi            :  60.0 
#>  freq            :  261.6255653005986 
#>  freq(from Midi) :  261.6255653005986 
#>  freq to midi    :  60.0 
```



[^1]: https://michael-edwards.org/sc/
[^2]: wiki: https://en.wikipedia.org/wiki/Scientific_pitch_notation
[^3]: Edwards' Original nimmt EDO-72 als Standard an. Auch für den Gebrauch in einem Just-Intonation-System lassen sich die ersten 16 Partialtöne hinreichend genau mit diesem System beschreiben.
[^4]: Eine gute Herleitung und Zusammenfassung findet sich hier: https://newt.phys.unsw.edu.au/jw/notes.html 