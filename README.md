<p align="center">
  <img src="systeme_notes_intervention/application/assets/shortcut-icons/generique-preview.png" width="96" alt="Icône Easy CESU">
</p>

# Easy CESU

Easy CESU est une application Windows locale pour gérer des clients, des interventions, des rappels, des paiements et des documents liés aux prestations à domicile.

La version 2.1 s'adapte aux principaux métiers CESU : jardinage, bricolage, ménage, aide à domicile, garde d'enfants, soutien scolaire, accompagnement, assistance administrative, informatique et autres services.

**[Télécharger la dernière version Windows](https://github.com/Mamat79/easy-cesu/releases/latest)**

## Points clés

- Fonctionne sans connexion Internet et sans installation manuelle de Python.
- Conserve les données dans le profil Windows, séparément du programme.
- Met à jour une installation existante sans remplacer la configuration ni la base.
- Propose une icône de raccourci adaptée au métier.
- Règle les durées par pas de 30 minutes et les montants par pas de 0,50 euro.
- Génère des notes d'intervention PDF et des bilans Excel.
- Sauvegarde et restaure un dossier Easy CESU complet.

Easy CESU est un outil indépendant. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Installation

1. Télécharger `EasyCESU-Setup-x64-2.1.0.exe` depuis la page des versions.
2. Fermer Easy CESU si une version est déjà ouverte.
3. Lancer l'installateur et choisir le dossier, l'icône et les raccourcis.
4. Au premier démarrage, créer une base ou restaurer une sauvegarde.

Une désinstallation ordinaire conserve les données personnelles. L'installateur n'est pas signé numériquement ; Windows peut donc afficher un avertissement SmartScreen.

## Documentation

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

La reconstruction complète est décrite dans [le README technique](systeme_notes_intervention/README.md).
