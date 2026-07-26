# Easy CESU 3.0.0

Easy CESU V3 devient la version principale pour Windows et macOS.

## Téléchargements

- `EasyCESU-Setup-x64-3.0.0.exe` : Windows 11 x64.
- `EasyCESU-macOS-Apple-Silicon-3.0.0.dmg` : Mac M1, M2, M3, M4 et suivants.
- `EasyCESU-macOS-Intel-3.0.0.dmg` : Mac Intel.
- `Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf` : notice en français.

## Nouveautés principales

- Fenêtre d'application dédiée, sans onglet Chrome.
- Serveur local isolé sur un port libre et arrêté avec la fenêtre.
- Éditeur visuel des modèles de notes d'intervention.
- Modèles séparés pour chaque compte et utilisés par les vrais PDF mensuels.
- Compatibilité macOS avec le moteur natif Cocoa/WebKit.
- Données conservées séparément du logiciel sur Windows et macOS.
- Migration automatique et sauvegardée depuis la V2.1.0.

## Installation macOS

Ouvrir le DMG correspondant au processeur du Mac et glisser `Easy CESU` dans
`Applications`. Cette première version Mac n'est pas notarialisée par Apple.
Au premier lancement, faire un clic droit sur `Easy CESU`, choisir `Ouvrir`,
puis confirmer.

## Mise à jour Windows

L'installateur remplace le logiciel existant sans supprimer la configuration,
les comptes, les clients ni les interventions. Une sauvegarde de sécurité est
créée avant la migration de la base.

## Contrôles

- 26 tests automatisés portables.
- Tests d'installation et de mise à jour Windows.
- Construction et lancement réels sur runners macOS Apple Silicon et Intel.
- Contrôle d'intégrité SQLite et conservation des données existantes.
