# Easy CESU 3.1.4

## Nouveautés

- Trois états indépendants sont visibles directement dans la liste des interventions : `Transmis`, `Déclaré` et `Payé`.
- Le tableau `À suivre` rassemble les interventions ayant encore une action administrative à effectuer.
- La liste peut être filtrée par transmission, déclaration ou paiement, et recherchée par client.
- Un rappel précis peut être ignoré pour une intervention, puis affiché et réactivé ultérieurement.
- L'option d'envoi par email peut marquer comme transmises uniquement les interventions dont l'envoi a réellement réussi.

## Mise à jour des données

La migration est automatique et crée d'abord une sauvegarde lorsque la base contient des données. Les anciennes interventions sont considérées comme déjà traitées pour le suivi de déclaration, car leur situation réelle ne peut pas être déduite. Les nouvelles interventions sont non déclarées par défaut.

Les clients, interventions, montants, paiements, rappels, profils, modèles, réglages et chemins existants sont conservés.

## Installation

- Windows 11 x64 : `EasyCESU-Setup-x64-3.1.4.exe`.
- macOS Apple Silicon : `EasyCESU-macOS-Apple-Silicon-3.1.4.dmg`.
- macOS Intel : `EasyCESU-macOS-Intel-3.1.4.dmg`.

Les installateurs macOS doivent être produits et testés sur des machines macOS natives par le workflow prévu dans le dépôt.
