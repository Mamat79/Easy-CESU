# Easy CESU

Easy CESU est une application locale pour Windows et macOS destinée aux
professionnels et salariés des services à la personne. Elle centralise les
clients, interventions, tarifs, rappels, paiements, notes PDF et bilans Excel
sans imposer de compte en ligne.

**Version actuelle : 2026**

[Télécharger la dernière version](https://github.com/Mamat79/Easy-CESU/releases/latest)

## Télécharger

| Système | Fichier |
| --- | --- |
| Windows 11 x64 | [EasyCESU-Setup-x64-2026.exe](https://github.com/Mamat79/Easy-CESU/releases/download/v2026/EasyCESU-Setup-x64-2026.exe) |
| macOS Apple Silicon | [EasyCESU-macOS-Apple-Silicon-2026.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026/EasyCESU-macOS-Apple-Silicon-2026.dmg) |
| macOS Intel | [EasyCESU-macOS-Intel-2026.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026/EasyCESU-macOS-Intel-2026.dmg) |

L'installateur Windows n'est pas signé numériquement. Windows peut donc
afficher un avertissement SmartScreen. Vérifiez l'empreinte SHA-256 publiée
avec la version avant de l'exécuter.

## Fonctions principales

- plusieurs comptes Easy CESU entièrement séparés ;
- clients, coordonnées, tarifs individuels et historique ;
- interventions avec durée, montant, état et description ;
- planning et rappels ponctuels ou récurrents ;
- suivi `Transmis`, `Déclaré` et `Payé` ;
- notes d'intervention PDF personnalisables ;
- préparation et envoi des emails avec pièces jointes ;
- bilans Excel par mois ou par année ;
- assistant de fin de contrat et archivage sans suppression ;
- sauvegardes ZIP vérifiées et restauration sur un autre ordinateur.

Easy CESU est indépendant et n'est ni affilié ni connecté automatiquement au
service officiel CESU.

## Installation

### Windows

1. Fermez Easy CESU si une version est déjà ouverte.
2. Téléchargez `EasyCESU-Setup-x64-2026.exe`.
3. Lancez l'installateur et choisissez le dossier et les raccourcis.
4. Pour une mise à jour, installez la nouvelle version au même emplacement.

### macOS

1. Téléchargez le fichier correspondant au processeur du Mac.
2. Ouvrez le fichier DMG.
3. Glissez `Easy CESU` dans `Applications`.
4. Au premier lancement, utilisez clic droit puis `Ouvrir` si macOS affiche un
   avertissement concernant un développeur non identifié.

## Conservation des données

Les données sont conservées séparément de l'application :

- Windows : `%LOCALAPPDATA%\EasyCESU` ;
- macOS : `~/Library/Application Support/EasyCESU`.

Une mise à jour ordinaire conserve les comptes, clients, interventions,
réglages et chemins configurés. Une sauvegarde ZIP régulière reste recommandée.

## Aide

- [Signaler un problème](https://github.com/Mamat79/Easy-CESU/issues/new)
- [Consulter les téléchargements](https://github.com/Mamat79/Easy-CESU/releases)
- [Lire les notes de la version 2026](RELEASE_NOTES_2026.md)
