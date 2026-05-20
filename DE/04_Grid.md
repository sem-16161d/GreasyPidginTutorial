# Grid

Ein ```Grid``` (de: *Raster*) ist ein ```set```, das zur Quantisierung von Daten genutzt werden kann. Die grundlegenden Methoden um ein ```Grid``` zu erzeugen sind Übersetzungen der ```Array```-Konstruktoren aus ```SuperCollider```[^1]. 

## Ein Grid erzeugen

### Direktes Initialisieren

Ein ```Grid``` kann im einfachsten Fall direkt aus einem ```set```, ```tuple``` oder ```list``` erzeugt werden. Dabei ist allerdings zu beachten, dass ```Grid``` ein ```set``` ist und daher jeder Wert einzigartig sein muss und ein ```list```-Objekt nicht verschachtelt sein darf.

```python
from GreasyPidgin.Grid import Grid

print(Grid([1, 3, 5, 7]))
print(Grid({2,4,6,8}))
print(Grid((1,2,3)))

##########  OUTPUT  ############################################################
#> Grid(size=4, range=(1, 7), preview=[1, 3, 5, 7])
#> Grid(size=4, range=(2, 8), preview=[2, 4, 6, 8])
#> Grid(size=3, range=(1, 3), preview=[1, 2, 3])
```

### Die arithmetische Reihe (1,2,3,4,...)

Für die meisten Anwendungsfälle ist eine einfache arithmetische Reihe, die passende Art und Weise ein ```Grid``` zu erzeugen. Via ```.series(start, step, size)``` wird ein ```Grid``` erzeugt, das vom Startwert ```start``` ausgehend ```size - 1``` mal den Wert ```step``` aufsummiert.

```python
from GreasyPidgin.Grid import Grid

print(Grid.series(0, 1, 10))
print(Grid.series(0, 0.1, 5))

##########  OUTPUT  ############################################################
#> Grid(size=10, range=(0, 9), preview=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
#> Grid(size=5, range=(0.0, 0.4), preview=[0.0, 0.1, 0.2, 0.3, 0.4])
```

### Die geometrische Reihe (1, 2, 4, 8,...)

In einer geometrischen Reihe haben zwei benachbarte Reihenglieder stets das gleiche Verhältnis. Via ```.geom(start, ration, size, *, decimals = 100)``` wird die Reihe konstruiert, indem vom Startwert ```start``` ausgehend der letzte Wert der Reihe interativ mit der ```ratio``` multipliziert wird. 

```python
from GreasyPidgin.Grid import Grid

print(Grid.geom(1, 2, 8))

##########  OUTPUT  ############################################################
#> Grid(size=8, range=(1, 128), preview=[1, 2, 4, 8, 16, 32, 64, 128])

```

Diese erlaubt es zum Beispiel die Frequenzen für *equal distance octave (EDO)* -Stimmungen zu berechnen. Mittels des Methodenslots ```decimals``` lassen sich zusätzlich die Nachkommastellen durch runden reduzieren.

```python
from GreasyPidgin.Grid import Grid

print(Grid.geom(442, 2**(1/12), 13, 2))

##########  OUTPUT  ############################################################
#> Grid(size=13, range=(442.0, 884.0), preview=[442.0, 468.28, 496.13, 525.63, 556.89, 590.0, 625.08, 662.25, 701.63, 743.35, 787.55, 834.38, 884.0])
```

### Initialisieren durch lineare Interpolation

Komplementär zur arithmetischen Reihe, bei der die Schrittgröße aber kein Endwert festgelegt ist, erzeugt ```.linearInterpolation(start, end, size, *, decimals = 100, includeEnd = True)``` ein ```Grid```, indem die Schrittgröße aus ```start```, ```end``` und ```size``` bestimmt wird.  Mittels des Methodenslots ```decimals``` lassen sich zusätzlich die Nachkommastellen durch runden reduzieren, mittels ```includeEnd``` lässt sich wählen, ob der Endwert Teil der Reihe ist oder nicht.

```python
from GreasyPidgin.Grid import Grid

print(Grid.linearInterpolation(0, 10, 5))
print(Grid.linearInterpolation(0, 10, 5, includeEnd= False))
print(Grid.linearInterpolation(0, 2.111, 5))
print(Grid.linearInterpolation(0, 2.111, 5, decimals=1))

##########  OUTPUT  ############################################################
#> Grid(size=5, range=(0.0, 10.0), preview=[0.0, 2.5, 5.0, 7.5, 10.0])
#> Grid(size=5, range=(0.0, 8.0), preview=[0.0, 2.0, 4.0, 6.0, 8.0])
#> Grid(size=5, range=(0.0, 2.111), preview=[0.0, 0.52775, 1.0555, 1.58325, 2.111])
#> Grid(size=5, range=(0.0, 2.1), preview=[0.0, 0.5, 1.1, 1.6, 2.1])

```

### Fibonacci-artiges Grid

```.fib(size, a, b)``` erlaubt es ein Fibonacci-artiges ```Grid``` zu erstellen, bei dem der nächste Wert immer die Summe beider vorherigen Werte ist. Initialisiert man mit Wertepaaren aus der Fibonacci-Reihe – z.B.: ```a= 1, b = 2``` – erhält man die Fortsetzung innerhalb der Fibonacci-Reihe[^2].

```python
from GreasyPidgin.Grid import Grid

print(Grid.fib(10,1,2))

##########  OUTPUT  ############################################################
#> Grid(size=10, range=(1, 89), preview=[1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
```
```.fib``` ist allerdings nicht auf ```int``` begrenzt sondern erlaubt auch ```float```-Werte.
```python
from math import e, pi
from GreasyPidgin.Grid import Grid

print(Grid.fib(5,e, pi))

##########  OUTPUT  ############################################################
#> Grid(size=5, range=(2.718281828459045, 14.861341617687469), preview=[2.718281828459045, 3.141592653589793, 5.859874482048838, 9.00146713563863, 14.861341617687469])
```
### Initialisieren mit Zufallswerten

Man mag sich fragen, warum man es notwendig sein kann Daten auf Zufallswerte zu quantisieren. Aber ```Grid``` erlaubt eine Initialisierung mit Zufallswerten, sowohl ```int``` als auch ```float``` basiert. Sollen ```int```-Werte erzeugt werden, muss dieses explizit über das Argument ```integer = True``` ausgdrückt werden.

```python
from GreasyPidgin.Grid import Grid

print(Grid.rand(5,0,12.77))
print(Grid.rand(5,0,12.77,integer=True))
print(Grid.rand(5,0,13))
print(Grid.rand(5,0,13,integer=True))

##########  OUTPUT  ############################################################
### als Beispiel, duh! 
#> Grid(size=5, range=(0.2856196224877912, 7.789117475083042), preview=[0.2856196224877912, 4.079976016998381, 5.363352927568584, 6.151736837079151, 7.789117475083042])
#> Grid(size=5, range=(2, 11), preview=[2, 8, 9, 10, 11])
#> Grid(size=5, range=(0.44959703668048456, 7.894089566506886), preview=[0.44959703668048456, 3.3165137492950127, 3.822080408499572, 7.612798394949432, 7.894089566506886])
#> Grid(size=5, range=(2, 11), preview=[2, 3, 5, 9, 11])
```

### Initialisieren über eine Funktion

```Grid.fill(size, func_or_value)``` erlaubt es ein ```Grid``` mit einer Konstanten[^3] oder mittels einer Funktion zu füllen. Die Funktion kann dabei als anonyme Funktion definiert werden[^4]. Dies ist vor allem eine Legacy-Option, die in der Praxis eher selten zur Anwendung kommt, und durch das direkte Initialisieren durch den Output einer Funktion in Form von ```set```, ```tuple``` oder ```list``` abgelöst wird.

```python
from GreasyPidgin.Grid import Grid

print(Grid.fill(10, lambda i: 2**i))

##########  OUTPUT  ############################################################
#> Grid(size=10, range=(1, 512), preview=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512])
```

## Quantisieren

Wie eingangs erwähnt dient ```Grid``` vor allem dazu Daten zu quantisieren. Mittels der Methode ```.quantise(value)``` ist dieses möglich. Es können nur ```int``` und ```float``` quantisiert werden. Sollen ein ```iterable``` wie ```set```, ```list``` oder ```tuple``` quantisiert werden, muss sichergestellt sein, dass diese nur Zahlen enthalten.

```python
from GreasyPidgin.Grid import Grid

g = Grid.series(0,0.5, 10)
print(g.quantise(1.23456789))
print(g.quantise([1.2345, 2.3456]))
print(g.quantise((1.2345, 2.3456)))
print(g.quantise({1.2345, 2.3456}))

##########  OUTPUT  ############################################################
#> 1.0
#> [1.0, 2.5]
#> (1.0, 2.5)
#> {1.0, 2.5}
```

## Sieben

Eine weitere Funktion von ```Grid``` ist die Möglichkeit ein Sieb auf sich selbst anzuwenden[^5]. Die Siebtheorie selbst stammt aus der analystischen Zahlentheorie und bezeichnet eine Reihe von Techniken, mittels derer eine Menge gefiltert wird, so dass am Ende nur die Zahlen enthalten sind, die nicht durch das Sieb gefallen sind.

### Hintergrund: Das Sieb des Eratosthenes

Das älteste dokumentierte Sieb, das auch als solches bezeichnet wurde ist das Sieb des Eratosthenes aus dem 3. Jhd vor Christus. Dieses Sieb dient dazu Primzahlen aus einer beliebigen Menge natürlicher Zahlen herauszufiltern. Im ersten Schritt werden dafür alle Zahlen geordnet auf einem Zahlenstrang notiert. In Python entspricht das einer Liste, die mittels ```[i+2 for i in range(100-2)]``` erzeugt wird. Ausgehend von der ```2``` als kleinste Primzahl werden via Modulo alle ganzzahlingen Vielfachen von ```2``` aus der Liste entfernt und die zwei als letzte Primzahl an die Liste ```primes``` gehängt. Die nächste größere Zahl ```3``` *muss* nun wieder auch eine Primzahl sein.

```python
allIntergers = [i+2 for i in range(100-2)]
lenTS = len(allIntergers)
primes = []

while lenTS > 0:
    newPrime = allIntergers[0]
    primes.append(newPrime)
    for i in allIntergers:
        if i%newPrime == 0:
            allIntergers.remove(i)
    lenTS = len(allIntergers)

print(primes)

##########  OUTPUT  ############################################################
#> [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
```

Diese einfachste Form des Siebs basiert nur auf einem Parameter, der Schrittgröße, in Form der aufsteigenden Primzahlen.

### Xenakis

Iannis Xenakis entwickelte seine Form der Siebtheorie während seiner Zeit in Westdeutschland um 1963. Im Gegensatz zu Eratosthenes, ging es Xenakis nicht darum, Primzahlen zu bestimmen, sondern vor allem eine sortierte Menge (*well sorted set*) so zu filtern und mit anderen Filtrierungen der gleichen Menge so zu kombinieren, dass eine neuartige mathematisch fundierte harmonische Sprache entsteht, die sich an keiner bisher etablierten Harmonik – weder tonaler, noch serieller – orientiert. Neu in Xenakis' Denken ist dabei die Einführung eines Offsets, ab dem die Menge gefiltert wird. 

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =0)
g.sieve(stepSize = 3, offsetIndex =1)
for s in g.sieved:
    print(g.sieved[s]['sievedGrid'])

##########  OUTPUT  ############################################################
#> Grid(size=7, range=(0, 18), preview=[0, 3, 6, 9, 12, 15, 18])
#> Grid(size=7, range=(1, 19), preview=[1, 4, 7, 10, 13, 16, 19])
```

### Erweiteretes Sieben

In der Implementation von ```Grid.sieve()``` gibt es nun die Möglichkeit die traditionellen Siebverfahren als auch Erweiterungen dieser zu nutzen. Mittels ```stepSize``` und ```offsetIndex``` lassen sich alle Siebe nach Xenakis anwenden. Wird ein Grid gesiebt, wird das Ergebnis im Dictionary des Slots ```Grid.sieved``` gespeichert. Innerhalb von ```Grid``` zählt eine Variable hoch, wie oft bereits gesiebt wurde; dieses wird als ```key``` für das ```dict``` genutzt. 

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =1)
g.sieve(stepSize = 3, offsetIndex =1, discardOffset= False)
for key in g.sieved:
    print(key)

##########  OUTPUT  ############################################################
#> sieved_0
#> sieved_1
```

Zusätzlich erlaubt ```discardOffset``` die sonst übersprungen Indices in das Resultat mit aufzunehmen.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =1)
g.sieve(stepSize = 3, offsetIndex =1, discardOffset= False)
for s in g.sieved:
    print(g.sieved[s]['sievedGrid'])

##########  OUTPUT  ############################################################
#> Grid(size=7, range=(1, 19), preview=[1, 4, 7, 10, 13, 16, 19])
#> Grid(size=8, range=(0, 19), preview=[0, 1, 4, 7, 10, 13, 16, 19])
```

Mittels ```inverse``` wird das Sieb umgekehrt. In dieser komplementären Filtrierung werden also alle Werte ausgegeben, die nicht im Sieb hängenbleiben.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =1)
g.sieve(stepSize = 3, offsetIndex =1, inverse=True)
for s in g.sieved:
    print(g.sieved[s]['sievedGrid'])

##########  OUTPUT  ############################################################
#> Grid(size=7, range=(1, 19), preview=[1, 4, 7, 10, 13, 16, 19])
#> Grid(size=12, range=(2, 18), preview=[2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18])
```

```reverse``` wiederum erlaubt die Filtrierung in umgekehrter Reihenfolge durchzuführen. Da das Umkehren des Inputs vor der Offset-Operation erfolgt, lassen sich damit Filtrierungen erzeugen, die nicht auf das Ende eines ```Grid``` angewendet werden.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset = False)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset = False, reverse=True)
for s in g.sieved:
    print(g.sieved[s]['sievedGrid'])

##########  OUTPUT  ############################################################
#> Grid(size=10, range=(0, 17), preview=[0, 1, 2, 3, 4, 5, 8, 11, 14, 17])
#> Grid(size=10, range=(2, 19), preview=[2, 5, 8, 11, 14, 15, 16, 17, 18, 19])
```

Mittels des Parameters ```rotation``` lässt sich eine weitere Offset-Operation durchführen, nachdem  ```offsetIndex``` und ```reverse``` angewendet wurden.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset=False)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset=False,rotation=1)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset=False, reverse=True)
g.sieve(stepSize = 3, offsetIndex =5, discardOffset=False, reverse=True,rotation=1)

for s in g.sieved:
    print(s,": ",g.sieved[s]['sievedGrid'])

##########  OUTPUT  ############################################################
#> sieved_0 :  Grid(size=10, range=(0, 17), preview=[0, 1, 2, 3, 4, 5, 8, 11, 14, 17])
#> sieved_1 :  Grid(size=10, range=(0, 18), preview=[0, 1, 2, 3, 4, 6, 9, 12, 15, 18])
#> sieved_2 :  Grid(size=10, range=(2, 19), preview=[2, 5, 8, 11, 14, 15, 16, 17, 18, 19])
#> sieved_3 :  Grid(size=10, range=(1, 19), preview=[1, 4, 7, 10, 13, 15, 16, 17, 18, 19])
```

Das ```dict``` enthält außerdem alle Informationen, über das angewendete Sieb.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
g.sieve(stepSize = 3, offsetIndex =5)
key = 'sieved_0'
sieved = g.sieved[key]
print(key)
for param in sieved:
    print(f"{param}: {sieved[param]}")

##########  OUTPUT  ############################################################
#> sieved_0
#> sievedGrid: Grid(size=5, range=(5, 17), preview=[5, 8, 11, 14, 17])
#> stepSize: 3
#> offsetIndex: 5
#> discardOffset: True
#> inverse: False
#> reverse: False
#> rotation: 0
```

## Sampling

Neben dem Sieben ist ```Sampling``` eine weitere Möglichkeit, Elemente aus einem Grid auszuwählen. Sampling ruft die ```random.sample()```-Funktion auf und wählt zufällig ```numElements``` Elemente aus dem Grid aus und erzeugt ein neues Grid mit dieser Auswahl.

```python
from GreasyPidgin.Grid import Grid
g  = Grid.series(0, 1, 20)
for _ in range(5):
    g.sample(5)
for i in range(5):
    print(g.sampled['sampled_'+str(i)])
```

[^1]: Siehe https://docs.supercollider.online/Classes/Array.html
[^2]: **Achtung!** Auch hier werden doppelte Werte gelöscht! Die tatsächliche Fibonacci-Reihe [0,1,1,2,3,5,8,...] lässt sich nicht als ```set``` darstellen!
[^3]: **Achtung!** Es wird ein ```grid``` mit der Länge 1 erzeugt!
[^4]: Siehe https://www.w3schools.com/python/python_lambda.asp
[^5]: Für einen Deepdive des Ursprungs dieser Idee siehe: https://www.iannis-xenakis.org/en/sieve-theory/ 