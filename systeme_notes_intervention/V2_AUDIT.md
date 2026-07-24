# Audit Easy CESU avant V2

Date : 19 juillet 2026

## Architecture conservée

- Application Windows locale autonome : `application/desktop_app.py` démarre le serveur local `application/app_server.py` puis ouvre l'interface web locale.
- Interface existante : HTML, CSS et JavaScript dans `application/static`.
- Stockage : une base SQLite par compte, conservée hors du programme installé dans `%LOCALAPPDATA%\\EasyCESU`.
- Sauvegardes : archives ZIP avec manifeste, empreintes SHA-256 et contrôle SQLite avant restauration.
- Documents : notes d'intervention PDF et bilan Excel existants.
- Installateur : application autonome x64 avec mise à jour, raccourcis et désinstallation qui préserve les données.

## Fonctions déjà opérationnelles à préserver

- Comptes multiples et sélection du compte actif.
- Clients avec coordonnées et tarif individuel prioritaire.
- Interventions avec date, durée, tarif, lieu, description, transmission et paiement.
- Bilans et comparaisons par jour, semaine, mois ou année.
- Rappels client ponctuels ou récurrents avec occurrences.
- Génération de documents, export Excel et export JSON.
- Sauvegarde, restauration et transfert entre ordinateurs.

## Schéma actuel

- `clients` : identité et coordonnées, reliées aux interventions par le nom du client.
- `interventions` : informations de saisie actuelles, sans horaires réels ni statut métier complet.
- `reminders` et `reminder_occurrences` : rappels et leur historique.
- `easy_cesu_metadata` : profil attaché à la base.

## Risques de régression identifiés

1. Les liens historiques utilisent le nom du client. La V2 ajoutera des identifiants sans supprimer cette compatibilité.
2. Les chemins de sources externes peuvent être indisponibles sur un autre PC. Ils doivent rester facultatifs et ne jamais bloquer le démarrage.
3. Les bases existantes doivent être migrées sur place uniquement après sauvegarde et contrôle d'intégrité.
4. Les fonctions de génération de notes reposent sur les colonnes existantes : elles resteront disponibles pendant l'ajout des nouveaux champs.
5. L'installateur actuel est fonctionnel, mais son choix d'icône doit être enrichi sans modifier les données utilisateur.

## Décision de migration

La V2 reste une évolution du même projet et de la même base SQLite. Les nouvelles tables et colonnes seront ajoutées de manière additive, avec une version de schéma, des migrations idempotentes et une sauvegarde automatique avant migration.
