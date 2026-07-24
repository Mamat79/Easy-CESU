# Validation Easy CESU 2.1.0

## Fonctions livrées

- Application universelle pour les principaux métiers CESU.
- Choix d'une icône métier lors de l'installation et dans les réglages.
- Grands boutons de réglage des durées par pas de 30 minutes.
- Grands boutons de réglage des tarifs et montants par pas de 0,50 euro.
- Mise à jour sur place sans remplacement de la configuration ni de la base.
- Raccourcis Bureau et menu Démarrer versionnés.
- Installateur Windows 11 x64 autonome.

## Vérifications exécutées

- Compilation des modules Python modifiés.
- Vérification de syntaxe JavaScript.
- Suite isolée : 15 tests réussis.
- Contrôle visuel de l'interface en 1440 x 900 et 390 x 844.
- Contrôle des boutons de 42 x 42 pixels et de leurs pas de réglage.
- Contrôle de l'affichage des durées en `h:mm` et de l'absence d'indication sous les champs.
- Contrôle des dix icônes disponibles.
- Installation locale depuis l'installateur final.
- Conservation exacte de la configuration et de la base pendant l'installation.
- Vérification de la version `2.1.0` via `/api/app-info`.
- Vérification visuelle de la notice PDF.

## Livrables

- `EasyCESU-Setup-x64-2.1.0.exe`
- `Easy_CESU_V2_Notice_Installation_et_Utilisation.pdf`

## Limites connues

- L'installateur n'est pas signé numériquement : Windows peut afficher un avertissement SmartScreen.
- Une base placée sur un partage réseau ne doit pas être ouverte simultanément depuis plusieurs ordinateurs.
