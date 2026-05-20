# PitchGrid

Ein weiteres spezialisiertes ```Grid``` ist das ```PitchGrid```. Es dient dazu Rohdaten in ein tonales System zu überführen oder generell ein harmonisches System zu erzeugen. Neben den vererbten Kontruktoren gibt es vor allem die Möglichkeit auf bestehende Intonations und Skalensyteme via ```.fromScaleMaskObj()``` zuzugreifen. Alternativ erlaubt der Konstruktor ```.fromCorrelation()``` aus aus einer Reihe von Möglichen Kandidaten das Stimmungssystem auszuwählen, das am besten auf die angegebenen Tonhöhen passt.

## Stimmungssysteme

In der Datei ```TuningSystemAndScaleMask.py``` findet sich eine Sammlung von Skalen und Masken, mit denen sich eine Vielzahl verschiedener hamonischer Systeme abbilden lässt.

### Oktavierende Stimmungssysteme

Die meisten musikalisch verwendeten Stimmungs- und Skalensystem bauen darauf auf, dass sie oktavtransponierend sind, das heißt, dass jede Tonhöhe potenziell eine beliebige Anzahl von Oktaven rauf und runter transponiert werden kann ohne den Charakter der Skala zu verändern.

#### Gleichschwebend

Als gleichschwebend bezeichnet man Stimmungssysteme in denen die Verhältnisse zwischen benachbarten Frequenzen immer die selben sind. Das in der westlichen Musik am weitesten verbreitete und standardisierte System ist die gleichschwebende Unterteilung der Oktave in 12 Schritte. Auf english: *12 Step Equal Distance Octave* oder kurz ```edo12```. Digital ist allerdings die Unterteilung der Oktave in eine beliebige Anzahl von Schritten möglich. ```GreasyPidgin``` bietet standardmäßig nicht nur ```edo12```, sondern zusätzlich ```edo7``` , ```edo11``` , ```edo53``` sowie ```edo72```.

#### Nicht gleichschwebend - aber 12-tönig

Historisch gesehen stellen gleichschwebende System allerdings eine Minderheit dar. Als Alternative zu ```edo12``` beinhaltet GreasyPidgin daher die Möglichkeit Skalen in der folgenden Stimmungssystemen zu erzeugen: ```werckmeister1```[^1] , ```werckmeister2```[^2] , ```werckmeister3```[^3], ```werckmeister4```[^4],```kirnberger2```[^5] , ```kirnberger3```[^6], ```meantoneQuarterComma```[^7] , ```pythagorean```[^8].

Aus dem Bereich der *Just Intonation*-Systeme ist bislang ausschließlich ```Zeta12```[^9] implementiert.

#### Weder gleichschwebend, noch 12-tönig

Neben diesen historischen europäischen Intonationssystemen ist mit ```shruti22``` auch die Grundlage für Skalen nach dem Vorbild von Ragas aus der karnatischen Tradition implementiert.[^10]

In Zukunft sollen auch noch weitere Systeme implementiert werden, wie zum Beispiel ```Pélog```, ```Slendro```, ```PartchJustIntonation``` und andere.[^11]

### Nicht-oktavierende Stimmungssysteme

z.B.: Bohlen-Pierce ; bisher nicht implementiert


## Skalen

```GreasyPidgin``` erlaubt dabei eine hohe theoretische Flexibilität. 
Die bisher implementierten Skalen sind:
### 12-Ton-Basis
#### Kirchentonarten
- ```ionian```, ```dorian```, ```phrygian```, ```lydian```, ```mixolydian```, ```aeolian```, ```locrian```
#### Kirchentonarten in harmonisch Moll
- ```harmonicMinor```, ```locrianSharp6```, ```ionianSharp5```, ```dorianSharp4```, ```phrygianDominant```, ```lydianSharp2```, ```ultraLocrian```
#### Kirchentonarten in melodisch Moll
- ```melodicMinor```, ```dorianFlat2```, ```lydianAugmented```, ```lydianDominant```, ```mixolydianFlat6```, ```locrianSharp2```, ```altered```
#### Modi mit begrenzten Transpositionsmöglichkeiten
- ```chromatic```, ```wholeTone```, ```halfToneWholeTone```, ```messiaen3```, ```messiaen4```, ```messiaen5```, ```messiaen6```, ```messiaen7```
#### Pentatoniken
- ```majorPentatonic```, ```minorPentatonic```, ```suspendedPentatonic```, ```bluesMinorPentatonic```, ```bluesMajorPentatonic```
### 22-Shruti-Basis
#### Skalen nach hindustanischem Vorbild[^13]
- ```abhogi```, ```mohanam```, ```hamsadhwani```, ```hindolam```, ```shuddhaSaveri```, ```madhyamavati```, ```khamas```, ```revati```, ```kalyani```, ```todi```, ```bhairavi```, ```shankarabharanam``` 
#### Skalen nach karnatischem Vorbild
- n.n.[^14]
### EDO53-Basis
#### Türkische Maqams
- n.n.
### EDO72-Basis[^15]
#### Iranische Dastgāhs und Āwāz
- n.n.


## Konstruktoren
### Skalenerzeugung
```.fromScaleInTUNING_SYSTEMS()``` bietet die Möglichkeit via Schlagwort eine Skala zu erzeugen. 
Der Parameter ```maskKey``` erwartet einen Skalennamen[^12], ```tuningSystemKey``` erwartet ein zum Skalennamen passendes Stimmungssystem. Mit den Parametern ```lowestPitchMidi``` und ```highestPitchMidi``` lässt sich der maximale Ambitus des ```PitchGrid``` bestimmen. 

```python
from GreasyPidgin.PitchGrid import PitchGrid

p = PitchGrid.fromScaleInTUNING_SYSTEMS(
    maskKey= 'chromatic',
    tuningSystemKey= "edo12",
    lowestPitchMidi=45,
    highestPitchMidi=55)
print(p)

##########  Output  ############################################################
#> PitchGrid
#>    size       : 11,
#>    range      : 45.0 to 55.0,
#>    tuning     : 'edo12',
#>    scale      : 'chromatic',
#>    pitchClass : [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
#>    preview    : [45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0 ...
```

Für alle Stimmungssysteme, die nicht ```edo12``` oder Vielfache dessen (```edo24```, ```edo72```, etc.) sind, ist es notwendig, den Startpunkt ```tuningSystemRoot``` für die Berechnung des Systems festzulegen.

```python
from GreasyPidgin.PitchGrid import PitchGrid

p60 = PitchGrid.fromScaleInTUNING_SYSTEMS(tuningSystemKey= "edo7",tuningSystemRootMidi = 60)
p59 = PitchGrid.fromScaleInTUNING_SYSTEMS(tuningSystemKey= "edo7",tuningSystemRootMidi = 59)
print(p60)
print(p59)
# p59.parseMidi("/tmp/root59_")
# p59.parseMidi("/tmp/root60_")

# same PitchClass (edo7) but different resulting pitches  due to different 
# calculation start. The default state for all systems is "chromatic" but only 
# edo12 produces a real chromatic scale. For all other tuning systems 
# "chromatic" tries to find the closest pitch in the system that resembles a 
# edo12 chromatic pitch. This doesn't work for shruti based systems!

##########  Output  ############################################################
# PitchGrid
#    size       : 8,
#    range      : 60.0 to 72.0,
#    tuning     : 'edo7',
#    scale      : 'chromatic',
#    pitchClass : [0.0, 1.71, 3.43, 5.14, 6.86, 8.57, 10.29],
#    preview    : [60.0, 61.71, 63.43, 65.14, 66.86, 68.57, 70.29, 72.0 

# PitchGrid
#    size       : 7,
#    range      : 60.71 to 71.0,
#    tuning     : 'edo7',
#    scale      : 'chromatic',
#    pitchClass : [0.0, 1.71, 3.43, 5.14, 6.86, 8.57, 10.29],
#    preview    : [60.71, 62.43, 64.14, 65.86, 67.57, 69.29, 71.0 

```

Noch deutlicher fällt dies bei historischen westlichen Stimmungen ins Gewicht. So lässt sich eine dorische Tonleiter in mitteltöniger Stimmung mit dem Grundton C sowohl in einem System konstruieren, das von C ausgehend konstruiert ist, oder zum Beispiel von Cis aus.

```python
from GreasyPidgin.PitchGrid import PitchGrid

pg60 = PitchGrid.fromScaleInTUNING_SYSTEMS(
    'dorian',
    tuningSystemKey='meantoneQC',
    tuningSystemRootMidi=60,
    scaleRootMidi=60,
    highestPitchMidi=73
)

pg61 = PitchGrid.fromScaleInTUNING_SYSTEMS(
    'dorian',
    tuningSystemKey='meantoneQC',
    tuningSystemRootMidi=61,
    scaleRootMidi=60,
    highestPitchMidi=73
)
print(pg60)
print(pg61)

##########  Output  ############################################################
#> PitchGrid
#>    size       : 8,
#>    range      : 60.0 to 72.0,
#>    tuning     : 'meantoneQC',
#>    scale      : 'dorian',
#>    pitchClass : [0.0, 1.93, 3.1, 5.03, 6.97, 8.9, 10.07],
#>    preview    : [60.0, 61.93, 63.1, 65.03, 66.97, 68.9, 70.07, 72.0 

# PitchGrid
#>    size       : 8,
#>    range      : 60.12 to 72.12,
#>    tuning     : 'meantoneQC',
#>    scale      : 'dorian',
#>    pitchClass : [0.12, 1.76, 2.93, 4.86, 6.79, 9.14, 9.9],
#>    preview    : [60.12, 61.76, 62.93, 64.86, 66.79, 69.14, 69.9, 72.12 
```



## Export

Um ein ```PitchGrid``` darzustellen, lässt es sich wie ein ```TimeGrid``` via ```.parseMidi()``` als MIDI-Datei exportieren[^16]. Für die Verwendung in DAWs werden die mikrotonalen Abweichungen in ```PitchBend```-Werte umgerechnet, für einen Notation werden sie als ```lyrics``` an den Noten annotiert.

```python
from GreasyPidgin.PitchGrid import PitchGrid

pg60 = PitchGrid.fromScaleInTUNING_SYSTEMS(
    'dorian',
    tuningSystemKey='meantoneQC',
    tuningSystemRootMidi=60,
    scaleRootMidi=60,
    highestPitchMidi=73
)
pg60.parseMidi("/tmp/mqc_dorian_tsRoot60") 


##########  Output  ############################################################
#> Midi file saved to:  /tmp/mqc_dorian_tsRoot60PitchGrid_meantoneQC_dorian.mid
```

```{image} IMG/PitchGrid_mqc_dorian_tsRoot60.png
:alt: Ein PitchGrid mit der Skala C Dorisch in mitteltöniger Stimmung. Unter den Notennamen sind die Mikrotonalen Abweichungen in der Abfolge: 0, -7, 10, 3, -3, -10, 7, 0
:width: 400px
:align: center
```


[^1]: Bezeichnet nach: http://www.groenewald-berlin.de/text/text_T016.html
[^2]: Bezeichnet nach: http://www.groenewald-berlin.de/text/text_T017.html
[^3]: Bezeichnet nach: http://www.groenewald-berlin.de/text/text_T018.html
[^4]: Bezeichnet nach: http://www.groenewald-berlin.de/text/text_T019.html
[^5]: nach https://www.lehrklaenge.de/PHP/Tonsystem/KirnbergerStimmung.php 
[^6]: ebenda
[^7]: https://de.wikipedia.org/wiki/Mittelt%C3%B6nige_Stimmung 
[^8]: https://de.wikipedia.org/wiki/Pythagoreische_Stimmung 
[^9]: Ratios von https://en.xen.wiki/w/Zeta12
[^10]: siehe: https://www.carnaticcorner.com/articles/sruthis.html alternativ ist eine Erweiterung möglich: https://en.xen.wiki/w/A_shruti_list 
[^11]: Bei Interesse zur eigenen Implementation und Mitwirkung bietet das XenharmonicWiki einen guten Recherche-Einstieg: https://en.xen.wiki/w/Gallery_of_12-tone_just_intonation_scales 
[^12]: Eine ```mask``` ist hier am besten mit den deutschen Wort *Schablone* zu übersetzen – ein Filter mittels welchem aus einem vollständigen chromatischen ```set``` nur die Töne ausgewählt werden, die für die Skala benötigt werden.
[^13]: Wichtige Anmerkung für alle Weißbrote: Es sind ausdrücklich Skalen nach dem *VORBILD* von Ragas, da der Begriff Raga mehr als nur eine Abfolge von Tonhöhen bezeichnet. Möchte man in diesem Klangraum arbeiten, empfehle ich Kontakt zu Musiker!nnen aufzunehmen, die sich in diesen Traditionen bewegen und mit denen man gemeinsam ein Verständnis für diese Klangsprache entwickelt. Das gleiche gilt auch für die weiteren Systeme von *Maqams* und *Dastgāhs*.
[^14]: To be implemented: https://en.wikipedia.org/wiki/Melakarta#Table_of_Melakarta_ragas
[^15]: Zur Zeit ist noch nicht klar, ob und in welchem EDO-System ich die arabischen Maqams implementieren will. Unter https://en.xen.wiki/w/Middle-Eastern_music finden sich neben ```edo72``` verschiedene Möglichkeiten.
[^16]: Beim Export als Midi muss allerdings die ```PitchBendRange``` auf das MIDI-Instrument abgestimmt sein, auf dem es wiedergegeben wird! Siehe ```TemporalObject.parseMidi()``` um ggf. eine Kalibrierungsdatei zu erzeugen.