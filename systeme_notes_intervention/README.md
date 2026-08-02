# Easy CESU

Easy CESU est une application locale Windows et macOS de suivi d'activité pour
les prestations à domicile. Elle permet de gérer les clients, saisir des
interventions, produire des notes d'intervention PDF, exporter un bilan Excel,
planifier des rappels et transférer un compte par sauvegarde ZIP vérifiée.

La V3 s'ouvre dans sa propre fenêtre, sans onglet Chrome. Elle reste utilisable pour tous les métiers CESU : l'activité et l'icône des raccourcis sont configurables. Les durées se règlent par pas de 30 minutes et les tarifs ou montants par pas de 0,50 euro grâce à de grands boutons moins et plus.

Depuis la version 3.1.4, chaque intervention possède trois états administratifs
indépendants : `Transmis`, `Déclaré` et `Payé`. Ils sont modifiables directement
dans la liste des interventions. Le tableau `À suivre`, dans l'onglet
`Notes et paiements`, regroupe sur une seule ligne les actions encore manquantes.
Un rappel peut être ignoré ou réactivé pour une intervention et une action
précises, sans modifier le suivi des autres interventions du client.

L'onglet `Modèles` permet de créer plusieurs mises en page de notes d'intervention. Les textes, couleurs, marges, tailles et ordre des blocs se modifient avec un aperçu A4 immédiat. Chaque compte conserve ses propres modèles.

Easy CESU est un outil indépendant de suivi d'activité. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Utilisation

- Ouvrir l'application depuis le raccourci Easy CESU.
- Choisir le compte actif en haut de l'écran.
- Saisir les interventions ou consulter les clients.
- Utiliser `Planning` pour les rappels en retard, du jour et à venir.
- Utiliser `Notes et paiements > À suivre` pour contrôler les transmissions,
  déclarations CESU et paiements restant à traiter.
- Utiliser `Modèles` pour personnaliser les prochaines notes PDF.
- Utiliser `Clients` pour ajouter les rappels liés à une personne.
- Utiliser `Base de données` pour créer ou restaurer une sauvegarde ZIP complète.
- Utiliser `Réglages` pour les dossiers, les coordonnées et le tarif par défaut.
- Utiliser `Réglages > Aide et communauté` pour consulter le projet public,
  signaler un problème ou soutenir facultativement son développement.

Au premier lancement, l'assistant propose de commencer avec une base vide ou de restaurer une sauvegarde. Il demande ensuite un dossier principal et y crée des sous-dossiers séparés pour la base, les notes et les exports.

Les données permanentes sont séparées du programme :

- Windows : `%LOCALAPPDATA%\EasyCESU` ;
- macOS : `~/Library/Application Support/EasyCESU`.

Les sous-dossiers `data`, `attachments`, `backups`, `config`, `logs`, `temp`
et les données techniques de la fenêtre restent conservés lors d'une mise à
jour.

L'installateur contient Python et les bibliothèques de l'application. Windows
utilise Microsoft WebView2 et macOS utilise le moteur Cocoa/WebKit du système.

## Développement

Les tests utilisent uniquement des bases temporaires fictives :

```powershell
.\.build_venv\Scripts\python.exe -m unittest discover -s tests -v
```

Le contrôle visuel V3 s'exécute avec :

```powershell
.\.build_venv\Scripts\python.exe tests\v3_ui_smoke.py
```

Sur macOS, `bash Construire_macOS.sh` construit l'application `.app`, vérifie
son lancement et produit le fichier `.dmg`. GitHub Actions exécute ce processus
séparément pour les Mac Apple Silicon et Intel.

Les documents de référence sont dans `ARCHITECTURE.md`, `DATA_MODEL.md`, `ROADMAP.md`, `TESTING.md` et `KNOWN_LIMITATIONS.md`.
