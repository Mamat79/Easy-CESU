# Plan de migration Easy CESU V2

## Lot 1 - Fondations et compatibilité

1. Versionner le schéma SQLite.
2. Créer une sauvegarde contrôlée avant toute migration V2.
3. Ajouter sans suppression : catégories de prestations, notes, paiements en attente, documents et paramètres V2.
4. Ajouter aux interventions les horaires prévus/réels, le statut, la pause, le déplacement et les montants prévus/reçus.
5. Conserver les colonnes et les traitements historiques.

## Lot 2 - Configuration universelle

1. Profil professionnel enrichi et activités multiples.
2. Assistant de premier démarrage en cinq étapes : profil, activités, données, sauvegardes, vérification.
3. Vérification d'écriture des dossiers personnalisés et choix explicite en présence d'une base.
4. Sauvegarde quotidienne et rotation configurable.

## Lot 3 - Suivi opérationnel

1. Notes liées au client ou à une intervention, avec catégorie, priorité, statut et rappel éventuel.
2. Paiements en attente, sans modification automatique depuis une note libre.
3. Catégories de prestations configurables et archivables.
4. Planning universel, statuts d'intervention et filtres.

## Lot 4 - Expérience et diffusion

1. Accueil utile et recherche globale.
2. Identité visuelle configurable et iconographie métier.
3. Installateur avec sélection de l'icône du raccourci Bureau.
4. Notice PDF V2 issue des écrans réels, rapport de validation et kit de transfert.

## Règles de validation

- Toute migration est exécutée dans l'ordre et peut être rejouée sans effet secondaire.
- Une migration échouée ne remplace jamais la base d'origine.
- Les tests couvrent les bases v1, les accents, les chemins Windows avec espaces et les sources réseau indisponibles.
