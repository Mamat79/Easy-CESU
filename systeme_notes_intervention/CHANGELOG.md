# Journal des changements

## 2.1.0 - 2026-07-24

- Grands boutons moins et plus pour régler les durées par 30 minutes et les tarifs ou montants par 0,50 euro.
- Durées affichées au format heures et minutes (`1:00`, `1:30`, `2:00`) sans indication supplémentaire sous le champ.
- Suppression de l'indication du pas sous les champs Durée et Net horaire pour éviter toute ambiguïté.
- Saisie directe toujours possible pour conserver les valeurs historiques précises.
- Choix visuel de l'icône métier dans l'installateur : générique, jardinage, bricolage, ménage, aide à domicile, garde d'enfants, soutien scolaire, accompagnement, administratif ou informatique.
- L'installateur reprend automatiquement l'icône mémorisée par le compte actif lors d'une mise à jour.
- La configuration et la base restent hors du dossier du programme et ne sont pas remplacées par la mise à jour.
- Libellé d'intervention rendu générique pour tous les métiers CESU.

## 2.0.0 - 2026-07-19

- L'installateur reste réactif pendant la copie, ferme sa fenêtre avant d'ouvrir la notice ou l'application et ne laisse plus de confirmation cachée.
- Les raccourcis de la version initiale V2 portent le nom court `Easy CESU V2` ; les futures versions intermédiaires pourront afficher leur numéro complet.
- Évolution d'Easy CESU en outil configurable pour les activités CESU et les services à la personne.
- Migration additive de la base avec sauvegarde ZIP automatique avant passage au schéma V2.
- Profil professionnel enrichi : activité principale, identité commerciale et dossier de sauvegardes.
- Interventions enrichies : prestation, état, horaires prévus et réels, pause, déplacement et montants prévus ou reçus.
- Nouvel onglet Suivi pour les catégories de prestations, les notes reportables et les paiements en attente.
- Assistant de premier démarrage en cinq étapes : restauration, profil, activité, dossiers et sauvegarde.
- Les notes n'ont aucun effet financier automatique : un paiement à suivre doit être créé explicitement.

## 1.1.9 - 2026-07-19

- Un fichier Excel source inaccessible, protégé ou corrompu ne bloque plus le démarrage d'Easy CESU.
- Les clients déjà enregistrés dans la base restent disponibles même lorsque le partage réseau est indisponible.

## 1.1.8 - 2026-07-19

- Une restauration n'importe plus les chemins des anciens fichiers Excel, notes, exports ou données.
- La base vide d'un premier lancement n'est plus sauvegardée avant restauration, ce qui évite un accès inutile au partage réseau.

## 1.1.7 - 2026-07-19

- Correction de l'encodage UTF-8 des chemins choisis dans les dialogues Windows.
- Les dossiers contenant des accents, notamment `Jardinière paysagiste`, sont désormais enregistrés correctement.

## 1.1.6 - 2026-07-19

- Correction du choix de fichier de restauration : seul un fichier ZIP existant peut désormais être validé.
- Le ZIP complet de transfert est maintenant accepté directement : Easy CESU y retrouve automatiquement la sauvegarde incluse.

## 1.1.5 - 2026-07-18

- Le bilan principal permet désormais de naviguer entre les vues Jour, Semaine, Mois et Année.
- Les graphiques longs se défilent horizontalement pour préserver la lisibilité des jours et semaines.
- Correction des libellés coupés et des valeurs superposées dans les graphiques de comparaison détaillés.

## 1.1.4 - 2026-07-18

- Import historique contrôlé des suivis de paie 2020 à 2025 dans la base Easy CESU.
- Simplification du Bilan annuel : année visible, chiffres clés, courbe du net et barres d'heures.
- Les comparaisons détaillées restent disponibles dans une section dédiée.

## 1.1.3 - 2026-07-18

- Refonte de l'onglet Bilan : comparaisons par jour, semaine, mois ou année avec la période précédente ou l'année passée.
- Correction de la mise en page du Planning, désormais affiché sur toute la largeur.

## 1.1.2 - 2026-07-18

- Correction : l'installateur conserve désormais le raccourci Easy CESU sur le Bureau après l'installation.

## 1.1.1 - 2026-07-18

- Ajout de l'onglet Bilan avec indicateurs annuels et graphiques mensuels des heures et du salaire net.

## 1.1.0 - 2026-07-15

- Ajout des rappels liés aux clients, de leur historique et du planning intégré.
- Ajout des récurrences une fois, mensuelle et annuelle, y compris les fins de mois et le 29 février.
- Ajout des sauvegardes ZIP vérifiées, avec manifeste, empreintes et restauration sécurisée.
- Déplacement des données installées vers `%LOCALAPPDATA%\EasyCESU` avec migration non destructive depuis l'ancienne version.
- Installateur Windows x64 versionné, journalisé et inscrit auprès de Windows.

## Non versionné - 2026-07-12

- Audit initial du projet et sauvegarde locale vérifiée des réglages et bases actives.
- Ajout d'exclusions locales pour les données personnelles, sauvegardes, builds et journaux techniques.
- Ajout d'une suite de tests isolés pour les clients, interventions, sauvegardes et configuration initiale.
- Ajout de la mention d'indépendance vis-à-vis du service officiel CESU dans l'interface et la documentation.
- Ajout de la documentation d'architecture, du modèle de données, de confidentialité et de feuille de route.

## Version installée antérieure

- Gestion multi-comptes et bases séparées.
- Import et export de base SQLite.
- Génération de notes d'intervention PDF et bilan Excel.
- Assistant de choix du dossier principal.
