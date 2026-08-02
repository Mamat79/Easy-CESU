# Modèle de données

## Modèle actuel

La base SQLite comporte notamment les tables métier suivantes :

- `clients` : nom, identifiant CESU, email, adresse, téléphone et tarif individuel optionnel.
- `interventions` : date, client, durée, tarif horaire, travaux, lieu et états indépendants `transmitted`, `declared` et `paid`.
- `easy_cesu_metadata` : métadonnées du compte attachées à la base.
- `reminders` : rappel lié à un client, échéance, récurrence, anticipation, statut et prochaine occurrence.
- `reminder_occurrences` : historique distinct de chaque échéance, avec son statut traité ou ignoré.
- `service_categories` et `intervention_services` : catégories de prestations et associations aux interventions.
- `intervention_notes` : notes et éléments à suivre liés aux interventions.
- `pending_payments` : paiements attendus, partiels ou reçus.
- `document_templates` : modèles de notes personnalisés par compte.
- `intervention_followup_ignores` : rappel administratif ignoré pour une intervention et un seul type d'action.
- `contract_terminations` : dossier préparatoire généré pour une fin de contrat,
  dates utiles, motif, préavis, chemin du PDF et synthèse figée au moment de la
  génération.

Les relations sont actuellement assurées par le nom du client et non par une clé technique. Cette compatibilité doit être préservée pendant la future migration vers un identifiant de client.

La relation entre un rappel et le client utilise le nom du client pour rester compatible avec le modèle existant. Le renommage d'un client est propagé par clé étrangère SQLite.

## Éléments à ajouter progressivement

- Date de dernière intervention calculée ou matérialisée pour accélérer les grandes bases.
- Prestation habituelle, durée habituelle, fréquence et informations pratiques.
- Horaires, statut d'intervention, récurrence, frais et observations.
- Lien versionné entre une intervention et la fiche générée.

## Règles de migration

Avant toute évolution du schéma : sauvegarde contrôlée, migration sur copie, test de lecture, test de retour arrière et documentation du changement.

Les montants sont aujourd'hui stockés en `REAL`. Cette limite est connue : une migration future utilisera une représentation décimale ou des centimes entiers pour les calculs monétaires.

## Migration 3.1.4

Le schéma 6 ajoute la colonne `interventions.declared`, initialisée à vrai pour les interventions déjà présentes lors de la migration. Les nouvelles interventions sont créées non déclarées. Cette stratégie évite de présenter tout l'historique comme restant à déclarer alors que l'application ne peut pas connaître sa situation réelle.

La table `intervention_followup_ignores` impose l'unicité de la paire `intervention_id + reminder_type`. Les seuls types admis sont `transmitted`, `declared` et `paid`. La clé étrangère avec suppression en cascade évite de conserver une ignorance après la suppression de son intervention.

## Migration 3.1.5

Le schéma 7 crée `contract_terminations` sans modifier les interventions. La clé
étrangère suit le renommage du client et empêche la suppression accidentelle
d'un client possédant un dossier de fin de contrat. Plusieurs dossiers restent
possibles pour un même client afin de gérer une reprise puis une nouvelle fin de
relation.

Le champ `clients.is_archived`, déjà présent dans le schéma, devient accessible
depuis l'interface. Archiver ne supprime aucune intervention, aucun rappel et
aucun document. Les clients archivés sont seulement exclus des nouveaux choix
d'intervention. La migration crée une sauvegarde `avant-migration-v7` lorsqu'une
base contient déjà des données et reste sans effet lors d'une seconde exécution.
