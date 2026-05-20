# Envelope

Jegliche Art von zweidimensionalen Abfolgen, Kurven und Hüllkurven wird in ```GreasyPidgin``` als ```Envelope``` dargestellt. Ein ```Envelope```-Objekt kann entweder aus einer Reihe von Werten oder Wertepaaren – sogenannten *breakpoint pairs* – erzeugt werden. Während der Konstruktion werden die Werte innerhalb des Objekts normalisiert. Intern wird eine ```Envelope``` als Kurve in einem ```XY```-Koordinatensystem gesehen.

## Konstruktoren

### Einzelwerte

Wird ```Envelope``` mit einem flachen ```list```- oder ```tuple```-Objekt initialisiert, werden die enthaltenen Werte in *breakpoint pairs* umgewandelt. Jedes Paar hat den gleichen ```x```-Abstand zum benachbarten Paar.

```python
from GreasyPidgin.Envelope import Envelope

env = Envelope([0,2,1,3,2,5,2,3,0,1,0])
print(env)

##########  OUTPUT  ############################################################
# Envelope
#    pointsNorm =[(0.0, 0.0), (0.1, 0.4), (0.2, 0.2), (0.3, 0.6), (0.4, 0.4), 
#                 (0.5, 1.0), (0.6, 0.4), (0.7, 0.6), (0.8, 0.0), (0.9, 0.2),
#                 (1.0, 0.0)]
#    x_range=(0.0, 10.0), y_range=(0.0, 5.0)
#    coefficients={})
```


### Wertepaare

Wird ```Envelope``` mit einem verschachtelten ```list``` oder ```tuple``` initialisiert, müssen die einzelnen Elemente **immer** ```x```- und ```y```-Wertpaare sein. In der Standardeinstellung werden die Elemente anhand ihres ```x```-Wertes sortiert.

```python
from GreasyPidgin.Envelope import Envelope
env = Envelope([(0,5),(1,1),(5,1),(4,2)])
print(env)
```

### Polynom-Berechnung

Eine Möglichkeit Daten zu komprimieren ist die Berechnung von polynomischen Funktionen verschiedener Ordnung.[^1] Dies erlaubt zum Beispiel alternative Fortführungen der Kurve außerhalb des definierten Wertebereiches (siehe: *Werte ausgeben*)

## Werte ausgeben

Mit der Methode ```.getValue()``` können Werte innerhalb der Kurve ausgegeben werden. Dabei gibt es sowohl die Möglichkeit ```x```- als auch ```y```-Werte normalisiert zu verwenden.

```python
from GreasyPidgin.Envelope import Envelope

env = Envelope([0,1,2,3,2,1,0])
# get the y-value for the position 0.5 of 6
print("0.5 of 6: ",env.getValue(xPos=0.5, normalizedX=False))
# get the y-value for the position 0.5 of 1 aka 3 of 6
print("0.5 of 1: ",env.getValue(xPos=0.5, normalizedX=True))
# get the normalized y-value at x = 0.5 of 6
print("y-norm: ",env.getValue(xPos=0.5, normalizedY = True))
# get the normalized y-value at normalized x
print("y-norm @ x-norm: ",env.getValue(xPos=0.5, normalizedX=True, normalizedY = True))

##########  OUTPUT  ############################################################
# 0.5 of 6:  0.5
# 0.5 of 1:  3.0
# y-norm:  0.16666666666666666
# y-norm @ x-norm:  1.0
```
Wird ein Wert außerhalb des Wertebereichs abgefragt, wird entweder per Standard interpoliert, alternativ kann der letzte gültige Wert ausgegeben werden.

```python
from GreasyPidgin.Envelope import Envelope

env = Envelope([0,1,2,3,2,1,0])
print(env.getValue(11))
print(env.getValue(11, interpolateOutsideOfRange=False))

##########  OUTPUT  ############################################################
# -5.0
# 0.0
```

Werden bei der Konstruktion des Objekts Polynome berechnet, können alternativ auch diese innerhalb und außerhalb des Wertebereiches abgerufen werden.

```python
from GreasyPidgin.Envelope import Envelope

env = Envelope([0,1,2,3,1,2,4], polyFit=True)
print("just x: ",env.getValue(0.5, normalizedX=True))
print("1st order: ",env.getValue(0.5, normalizedX=True,polyDegree=1))
print("2nd order: ",env.getValue(0.5, normalizedX=True,polyDegree=2))
print("3rd order: ",env.getValue(0.5, normalizedX=True,polyDegree=3))
print("4th order: ",env.getValue(0.5, normalizedX=True,polyDegree=4))
print("5th order: ",env.getValue(0.5, normalizedX=True,polyDegree=5))

##########  OUTPUT  ############################################################
# just x:  3.0
# 1st order:  1.8571428571428568
# 2nd order:  1.9047619047619047
# 3rd order:  1.904761904761903
# 4th order:  2.3722943722943786
# 5th order:  2.372294372294444
```

## Envelope anzeigen

Mittels ```.display()``` kann die ```Envelope``` unter Zuhilfenahme von ```matplotlib``` dargestellt werden. Wird ```show_polynomials=True``` gesetzt, können außerdem die Polynome angezeigt werden.

```python
from GreasyPidgin.Envelope import Envelope

env = Envelope([0,1.5,1,3,1,2,4], polyFit=True)
env.display(show_polynomials=True)
```
[^1]: Keine vertieften Mathekenntnisse nötig! Kurzgesagt, umso höher die Ordnung, desto komplexere Auf-und-Abs sind darstellbar. Generell gilt: Es kann nur sichergestellt werden, dass alle Punkte auf der Kurve liegen, wenn die Ordnung der Kurve der Anzahl der Punkte entspricht. 