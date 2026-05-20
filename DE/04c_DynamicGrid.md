# DynamicGrid

:::{admonition} Achtung!
:class: warning

```DynamicGrid``` ist noch nicht vollständig implementiert! Benutz es lieber nicht!
:::

Ein ```DynamicGrid``` erlaubt das Rastern von Dynamikwerten und die Übersetzung von reellen Lautstärken von Instrumenten in Dezibel in Midi-Werte.


```python
from GreasyPidgin.DynamicGrid import DynamicGrid

d1 = DynamicGrid()
for entry in d1.dynamicMapping:
    print(entry, d1.dynamicMapping[entry])
```
