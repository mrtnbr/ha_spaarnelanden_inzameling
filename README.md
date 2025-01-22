Een sensor component voor het ophalen (scrapen) van informatie van https://inzameling.spaarnelanden.nl/ voor Home Assistant.

Handleiding:
- Voeg toe aan Home Assistant, via HACS of handmatig
- Zoek je container nummer op op https://inzameling.spaarnelanden.nl/
- Zet de volgende regels in je Home Assistant yaml configuratie bestand, onder `sensors:`
~~~
- platform: spaarnelanden_inzameling
  containers:
  - 12345
~~~

Opmerkingen:
- Dit is het eerste ~en enige~ wat ik ooit in elkaar heb geklust in Python. *Alle verbeteringen zijn welkom, deel ze hier met mij (en de rest van de wereld :))!*
- De webpagina die wordt opgehaald is "groot" (3,4 MB), doe het niet te vaak. De variabele TIME_BETWEEN_UPDATES (in sensor.py) bewaakt dit en staat op 10 minuten.
- Voor zover ik heb kunnen ontdekken, werkt Spaarnelanden de gegevens voor de container bij op een paar momenten:
  - Container is geleegd
  - Container is 100% vol
  - De tijd is 6:00

Known issues:
- Als Home Assistant opstart, is er nog geen info van de sensor en staat deze op 'Unknown'.
