# Easy CESU 3.1.5

Easy CESU 3.1.5 ajoute la préparation d'une fin de contrat et l'archivage
réversible des clients, sans modifier les fonctions publiées en 3.1.4.

## Nouveautés

- assistant de fin de contrat accessible depuis la liste des clients ;
- aperçu des interventions, heures, tarifs historiques et montants ;
- PDF préparatoire clair avec récapitulatif mensuel, détail des interventions,
  liste des démarches et liens officiels CESU et France Travail ;
- archivage facultatif du client après la génération ;
- filtre des clients actifs, archivés ou de tous les clients ;
- désarchivage en un clic si la relation de travail reprend ;
- désactivation facultative des rappels encore actifs.

## Mise à jour

L'installateur 3.1.5 peut remplacer la version 3.1.4. La configuration, les
comptes et la base existante sont repris automatiquement. Une sauvegarde est
créée avant la migration additive du schéma 7. Aucune restauration manuelle
n'est nécessaire pour une mise à jour ordinaire.

Une installation neuve démarre avec `Mon compte`, l'activité `Autre` et une
base vide. Aucun nom, client, tarif individuel ou chemin personnel n'est
préchargé.

## Limite réglementaire

Le dossier produit est une aide de préparation, pas un document officiel.
Easy CESU ne calcule pas les indemnités de rupture, de préavis ou de congés
payés. Le particulier employeur doit finaliser la démarche et vérifier les
montants depuis son compte CESU. Informations officielles vérifiées le
3 août 2026.

## Fichiers

- `EasyCESU-Setup-x64-3.1.5.exe` : Windows 11 x64 ;
- `EasyCESU-macOS-Apple-Silicon-3.1.5.dmg` : Mac Apple Silicon ;
- `EasyCESU-macOS-Intel-3.1.5.dmg` : Mac Intel ;
- `Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf` : notice complète.
