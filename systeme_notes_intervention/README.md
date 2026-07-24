# Easy CESU

Easy CESU est une application locale de suivi d'activité pour les prestations à domicile. Elle permet de gérer les clients, saisir des interventions, produire des notes d'intervention PDF, exporter un bilan Excel, planifier des rappels et transférer un compte par sauvegarde ZIP vérifiée.

La V2.1 est utilisable pour tous les métiers CESU. L'activité et l'icône des raccourcis sont configurables. Les durées se règlent par pas de 30 minutes et les tarifs ou montants par pas de 0,50 euro grâce à de grands boutons moins et plus.

Easy CESU est un outil indépendant de suivi d'activité. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Utilisation

- Ouvrir l'application depuis le raccourci Easy CESU.
- Choisir le compte actif en haut de l'écran.
- Saisir les interventions ou consulter les clients.
- Utiliser `Planning` pour les rappels en retard, du jour et à venir.
- Utiliser `Clients` pour ajouter les rappels liés à une personne.
- Utiliser `Base de données` pour créer ou restaurer une sauvegarde ZIP complète.
- Utiliser `Réglages` pour les dossiers, les coordonnées et le tarif par défaut.

Au premier lancement, l'assistant propose de commencer avec une base vide ou de restaurer une sauvegarde. Il demande ensuite un dossier principal et y crée des sous-dossiers séparés pour la base, les notes et les exports.

Les données permanentes de la version installée sont séparées du programme dans `%LOCALAPPDATA%\EasyCESU` : `data`, `attachments`, `backups`, `config`, `logs` et `temp`. Une mise à jour ne les supprime pas.

## Développement

Les tests utilisent uniquement des bases temporaires fictives :

```powershell
.\.build_venv\Scripts\python.exe -m unittest discover -s tests -v
```

Les documents de référence sont dans `ARCHITECTURE.md`, `DATA_MODEL.md`, `ROADMAP.md`, `TESTING.md` et `KNOWN_LIMITATIONS.md`.
