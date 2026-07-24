# Tests

La suite isolée n'utilise jamais la base personnelle installée :

```powershell
.\.build_venv\Scripts\python.exe -m unittest discover -s tests -v
```

La V2.1.0 comporte 15 tests automatisés couvrant notamment :

- première installation et profil générique ;
- création, renommage et séparation des clients ;
- priorité du tarif individuel ;
- migration additive de la base avec sauvegarde préalable ;
- notes, paiements en attente et rappels périodiques ;
- sauvegarde, contrôle d'intégrité et restauration ZIP ;
- refus d'une source Excel inaccessible sans blocage au démarrage ;
- synchronisation des numéros de version ;
- conservation du chemin de base lors d'un changement d'icône ;
- présence des dix icônes métier et de leurs aperçus ;
- transmission du choix d'icône au processus administrateur ;
- détection d'une ancienne installation locale pour la remplacer ;
- présence des grands boutons de durée et de montant.

Contrôles complémentaires réalisés pour chaque livraison :

- compilation Python et contrôle syntaxique JavaScript ;
- test de l'interface dans Chrome à `1440 x 900` et `390 x 844` ;
- construction de l'application autonome et de l'installateur x64 ;
- installation réelle par-dessus la version précédente ;
- comparaison de la configuration et de la base avant/après ;
- contrôle visuel et textuel de la notice PDF.
