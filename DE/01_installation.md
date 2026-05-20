# Installation

```GreasyPidgin``` ist eine Umgebung, die vor allem in ```Python``` geschrieben ist, daher ist der erste Schritt sicherzustellen, dass ```Python``` installiert ist.

## Python installieren

Unter https://www.python.org/downloads lässt sich die aktuelle Version von ```Python``` 

## Optional: Installation von miniconda

```Python``` hat eine Tendenz, dass verschiedene Projekte verschiedene Versionen von Libraries benötigen, welche wiederum verschiedene Versionen von ```Python``` benötigen. Um sicherzustellen, dass bei der Arbeit mit ```GreasyPidgin``` keine Konflikte auftreten, empfiehlt es sich ein virtuelles Environment anzulegen, innerhalb dessen ausschließlich ```GreasyPidgin``` verwendet wird. Eine Möglichkeit dafür bietet ```Conda```, zum Beispiel in der Variante ```miniconda```

Unter https://www.anaconda.com/docs/getting-started/miniconda/install lässt sich die aktuelle Version von ```miniconda``` finden sowie Hinweise zur Installation.
Um ein ```miniconda``` Environment für  ```GreasyPidgin``` anzulegen, öffne ein Terminal und führe folgenden Code aus:

```bash
conda create --name greasypidgin python=3.14
```

um es zu aktivieren:

```bash
conda activate greasypidgin
```

## Installation von GreasyPidgin
Lade das Repository von https://gitea.com/sem-16161d/GreasyPidgin wie folgt herunter. Clicke auf **Code -> Download ZIP** und entpacke die Datei in dem Verzeichnis, wo es landen soll.
Öffne ein Terminal, und wechsele auf den Ordner, den du angelegt hast via ```cd``` – change directory – wie folgt:
```bash
 cd path/to/directory/of/GreasyPidgin
 ```
Um ```GreasyPidgin``` zu installieren führe eine lokale Installation via ```pip``` aus. Stelle zuvor sicher, dass das ```GreasyPidgin``` Environment aktiv ist!
```bash
pip install -e .
```
Um sicherzustellen, dass ```GreasyPidgin``` installiert in denem Environment installiert ist, starte ```Python``` via

```bash
python3
```

Oder

```bash
python
```

Und führe dann in der ```Python```-shell folgenden Code aus:

```python
from GreasyPidgin.GreasyPidgin import GreasyPidgin
print(GreasyPidgin())
```

Im Terminalfester solltest du dann folgenden Printout erhalten:

```python
########################################################################

    ,--.
   ( @° \
  <´,..·_\
   )_.-'/`·,
  /-'``     `·,
 |  GREASY   0)`·-___
  \ PIDGIN  0) 0)0 );)`--,__
   \,    _:0) 0)0_);;):;)-->>
     "-,   ,--´
        \,/
      ,_//
     ,_-'-,


            
   name     : GreasyPidgin
   id       : 0
   start    : 0.000
   dur      : 0.000
   ensemble : Ensemble(players=0, names=[], 
   tmpObjs  : 0
```