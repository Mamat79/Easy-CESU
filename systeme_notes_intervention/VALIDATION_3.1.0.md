# Validation Easy CESU 3.1.0

Date : 26 juillet 2026

## Portée

- Branche publiée : `main`.
- Commit du code et du workflow validés :
  `1c32d09801db4b8120c123b12866c58edce67384`.
- Installation active : `C:\Users\mamat\AppData\Local\Easy CESU`.
- Données personnelles conservées hors du dépôt et des installateurs.

## Contrôles exécutés

- 28 tests automatisés réussis sous Windows.
- Compilation Python et contrôle syntaxique JavaScript réussis.
- Contrôle `git diff --check` réussi.
- Parcours Playwright réussi à 1600 x 1000 et 1024 x 768.
- Section `Aide et communauté` contrôlée dans la vraie fenêtre installée.
- Rappel de soutien absent avant 30 jours, limité à 90 jours entre deux
  affichages et désactivable.
- Ouverture externe limitée aux quatre liens publics autorisés.
- Fichier `.github/FUNDING.yml` limité au lien PayPal public.
- Absence de mention ou de configuration GitHub Sponsors.
- Notice PDF régénérée et contrôle visuel de ses deux pages A4.
- Construction PyInstaller Windows x64 réussie.
- Installation réelle de la version 3.1.0 et création des raccourcis Bureau et
  menu Démarrer avec l'icône Jardinage existante.
- Réponse `/api/app-info` de l'installation : version `3.1.0`.
- Premier lancement arrêté par la fermeture de la fenêtre : processus terminé
  et port `22108` libéré.
- Relance depuis l'installation réussie dans une fenêtre native sur le port
  dynamique `28158`.
- Construction et vérification des DMG Apple Silicon et Intel réussies :
  `https://github.com/Mamat79/Easy-CESU/actions/runs/30207183912`.

## Fichiers candidats

- Windows x64, 41 394 776 octets :
  `923a3d514e4d1a43396d1123d417e5cdb87fb2d6500eb52d302d9efc7b587638`.
- macOS Apple Silicon, 22 577 494 octets :
  `90cd133b04bb4988f0c79dd0b635b401a446f225e7573e079cd626194dfbb193`.
- macOS Intel, 24 018 904 octets :
  `0647b52984a5abaa4bc45a2e3eb660df0fb256d255db47eeb945e4496ef151b3`.
- Notice PDF, 7 611 octets :
  `6bd0aa83f83488bb35ac514b061296e5cf4d89b9c20a5449c0e21d636e671bab`.

## Protection des données

Avant la mise à jour, la base a passé `PRAGMA integrity_check` avec le résultat
`ok`. Une sauvegarde de précaution a été créée :

`C:\Users\mamat\AppData\Local\EasyCESU\backups\pre-update-3.1.0-20260726_165409.zip`

Après installation et relance :

- intégrité SQLite : `ok` ;
- clients : `148` ;
- interventions : `1 237` ;
- modèle de note : `1` ;
- compte actif : `clotilde-jardins`.

La nouvelle préférence de rappel est ajoutée dans la configuration locale sans
modifier les clients ni les interventions.

## Limites connues

- L'installateur Windows n'est pas signé par un certificat commercial et peut
  déclencher Microsoft SmartScreen.
- Les applications macOS utilisent une signature ad hoc et ne sont pas
  notariées par Apple. Le premier lancement peut demander
  `Clic droit > Ouvrir`.
- Aucun paiement n'est traité dans Easy CESU. Le bouton de soutien ouvre
  uniquement la page PayPal publique dans le navigateur par défaut.
