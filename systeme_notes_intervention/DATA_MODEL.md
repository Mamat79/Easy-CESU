# Modèle de données

## Modèle actuel

La base SQLite comporte cinq tables métier :

- `clients` : nom, identifiant CESU, email, adresse, téléphone et tarif individuel optionnel.
- `interventions` : date, client, durée, tarif horaire, travaux, lieu, état transmis et état payé.
- `easy_cesu_metadata` : métadonnées du compte attachées à la base.
- `reminders` : rappel lié à un client, échéance, récurrence, anticipation, statut et prochaine occurrence.
- `reminder_occurrences` : historique distinct de chaque échéance, avec son statut traité ou ignoré.

Les relations sont actuellement assurées par le nom du client et non par une clé technique. Cette compatibilité doit être préservée pendant la future migration vers un identifiant de client.

La relation entre un rappel et le client utilise le nom du client pour rester compatible avec le modèle existant. Le renommage d'un client est propagé par clé étrangère SQLite.

## Éléments à ajouter progressivement

- Archivage du client, date de création et date de dernière intervention.
- Prestation habituelle, durée habituelle, fréquence et informations pratiques.
- Horaires, statut d'intervention, récurrence, frais et observations.
- Lien versionné entre une intervention et la fiche générée.

## Règles de migration

Avant toute évolution du schéma : sauvegarde contrôlée, migration sur copie, test de lecture, test de retour arrière et documentation du changement.

Les montants sont aujourd'hui stockés en `REAL`. Cette limite est connue : une migration future utilisera une représentation décimale ou des centimes entiers pour les calculs monétaires.
