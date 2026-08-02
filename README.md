<p align="center">
  <img src="systeme_notes_intervention/application/assets/shortcut-icons/generique-preview.png" width="96" alt="Icône Easy CESU">
</p>

# Easy CESU

Easy CESU est une application locale pour Windows et macOS permettant de gérer
des clients, des interventions, des rappels, des paiements et des documents
liés aux prestations à domicile.

**Version actuelle : 3.1.5**

La version 3 s'adapte aux principaux métiers CESU : jardinage, bricolage,
ménage, aide à domicile, garde d'enfants, soutien scolaire, accompagnement,
assistance administrative, informatique et autres services.

**[Télécharger la dernière version Windows ou macOS](https://github.com/Mamat79/Easy-CESU/releases/latest)**

| Système | Téléchargement |
| --- | --- |
| Windows 11 x64 | [EasyCESU-Setup-x64-3.1.5.exe](https://github.com/Mamat79/Easy-CESU/releases/download/v3.1.5/EasyCESU-Setup-x64-3.1.5.exe) |
| macOS Apple Silicon | [EasyCESU-macOS-Apple-Silicon-3.1.5.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v3.1.5/EasyCESU-macOS-Apple-Silicon-3.1.5.dmg) |
| macOS Intel | [EasyCESU-macOS-Intel-3.1.5.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v3.1.5/EasyCESU-macOS-Intel-3.1.5.dmg) |

## Fonctions principales

### Plusieurs comptes indépendants

- Créer plusieurs comptes et passer rapidement de l'un à l'autre.
- Conserver pour chaque compte ses propres clients, tarifs, interventions,
  rappels, modèles de documents et réglages.
- Adapter le nom, l'activité et l'icône au jardinage, au ménage, au bricolage,
  à l'aide à domicile ou à un autre service CESU.

### Clients, interventions et planning

- Gérer les coordonnées, préférences, rappels et historique de chaque client.
- Planifier puis enregistrer les interventions avec leur durée, leur tarif et le
  travail réalisé.
- Utiliser un tarif général ou un tarif individuel prioritaire pour certains clients.
- Ajouter des rappels ponctuels ou récurrents dans le planning ou la fiche client.

### Notes d'intervention et emails

- Générer en une fois les notes d'intervention PDF d'un mois.
- Créer et modifier leur mise en page dans un éditeur visuel avec aperçu A4.
- Préparer un modèle d'email avec des champs automatiques comme le client, le
  mois, le nombre d'heures et le montant.
- Choisir les clients destinataires, relire certains messages puis envoyer les
  notes directement depuis Easy CESU.

### Suivi administratif et bilans

- Cocher directement `Transmis`, `Déclaré` et `Payé` pour chaque intervention.
- Retrouver dans `À suivre` toutes les actions encore manquantes et ignorer une
  exception sans masquer les futures interventions du client.
- Consulter les chiffres et les évolutions par jour, semaine, mois ou année.
- Comparer les périodes et exporter un bilan Excel détaillé.

### Fin de contrat et archivage

- Préparer pour un client un PDF récapitulant les dates, heures, tarifs et
  montants enregistrés pendant la relation de travail.
- Retrouver dans ce dossier la liste des démarches et documents officiels à
  préparer sur le compte employeur CESU, avec les liens vers les sources Urssaf
  CESU et France Travail.
- Archiver le client sans supprimer son historique, puis le désarchiver si la
  relation de travail reprend.
- Masquer automatiquement les clients archivés lors de la saisie d'une nouvelle
  intervention, tout en les conservant dans les historiques et les bilans.

### Sauvegarde et portabilité

- Choisir l'emplacement de la base, des sauvegardes, des notes PDF et des exports.
- Sauvegarder un dossier Easy CESU complet et le restaurer sur un autre ordinateur.
- Fonctionner localement sans compte en ligne ni connexion Internet obligatoire.
- Mettre l'application à jour sans remplacer la configuration ni la base.

Easy CESU est un outil indépendant. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Installation Windows

1. Télécharger `EasyCESU-Setup-x64-3.1.5.exe` depuis la page des versions.
2. Fermer Easy CESU si une version est déjà ouverte.
3. Lancer l'installateur et choisir le dossier, l'icône et les raccourcis.
4. Au premier démarrage, créer une base ou restaurer une sauvegarde.

Une désinstallation ordinaire conserve les données personnelles. L'installateur n'est pas signé numériquement ; Windows peut donc afficher un avertissement SmartScreen.

## Installation macOS

Deux installateurs sont fournis :

- `EasyCESU-macOS-Apple-Silicon-3.1.5.dmg` pour les Mac M1, M2, M3, M4 et suivants ;
- `EasyCESU-macOS-Intel-3.1.5.dmg` pour les anciens Mac Intel.

Ouvrir le fichier DMG puis glisser `Easy CESU` dans `Applications`. La première
fois, faire un clic droit sur l'application puis choisir `Ouvrir` si macOS
signale qu'elle provient d'un développeur non identifié. La version 3.1.5 n'est
pas notarialisée par Apple.

Les données sont enregistrées dans
`~/Library/Application Support/EasyCESU`, séparément de l'application.

## Mise à jour depuis une version précédente

Lancer le nouvel installateur puis choisir le remplacement de la version
existante. Le programme est mis à jour sans effacer la configuration, les
clients ni les interventions.

Lors du premier passage en 3.1.4, une sauvegarde de sécurité est créée avant la
migration de la base. Les anciennes interventions sont considérées comme déjà
traitées pour le suivi de déclaration ; les nouvelles interventions commencent
avec `Déclaré` non coché.

Lors du premier passage en 3.1.5, une nouvelle sauvegarde est créée avant
l'ajout des dossiers de fin de contrat. La base et les chemins déjà configurés
sont repris automatiquement : aucune restauration ni nouvelle configuration
n'est demandée pour une simple mise à jour.

Emplacements par défaut des données :

- Windows : `%LOCALAPPDATA%\EasyCESU` ;
- macOS : `~/Library/Application Support/EasyCESU`.

## Aide, code source et soutien

Easy CESU est développé par **Mamat Leroy** et reste entièrement gratuit et
open source.

- [Consulter le code et la documentation](https://github.com/Mamat79/Easy-CESU)
- [Signaler un problème ou proposer une amélioration](https://github.com/Mamat79/Easy-CESU/issues/new)
- [Soutenir volontairement Easy CESU avec le QR ou PayPal.Me](SUPPORT.md)

Une contribution financière est entièrement facultative. Elle ne débloque
aucune fonctionnalité, ne crée aucun abonnement et ne donne accès à aucune
version spéciale.

## Documentation

- [Notice PDF d'installation et d'utilisation 3.1.5](https://github.com/Mamat79/Easy-CESU/releases/download/v3.1.5/Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf)
- [Mode d'emploi](systeme_notes_intervention/MODE_EMPLOI.md)
- [Architecture](systeme_notes_intervention/ARCHITECTURE.md)
- [Modèle de données](systeme_notes_intervention/DATA_MODEL.md)
- [Sauvegarde et restauration](systeme_notes_intervention/BACKUP_AND_RESTORE.md)
- [Confidentialité et sécurité](systeme_notes_intervention/PRIVACY_AND_SECURITY.md)
- [Tests et validation](systeme_notes_intervention/TESTING.md)
- [Limites connues](systeme_notes_intervention/KNOWN_LIMITATIONS.md)

## Développement

Le code principal se trouve dans `systeme_notes_intervention`. Les tests n'utilisent que des bases temporaires fictives :

```powershell
cd systeme_notes_intervention
.\.build_venv\Scripts\python.exe -m unittest discover -s tests -v
```

La construction macOS s'exécute sur un Mac avec :

```bash
cd systeme_notes_intervention
bash Construire_macOS.sh
```

La reconstruction complète est décrite dans [le README technique](systeme_notes_intervention/README.md).
