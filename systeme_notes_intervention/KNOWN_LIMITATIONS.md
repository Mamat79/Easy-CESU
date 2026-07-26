# Limites connues

- L'installateur Windows x64 n'est pas signé numériquement. Windows peut donc afficher un avertissement SmartScreen.
- Les applications macOS sont signées localement mais ne sont pas encore
  signées avec un certificat Apple Developer ni notarialisées. Au premier
  lancement, il peut être nécessaire de faire un clic droit sur l'application
  puis de choisir `Ouvrir`.
- Une base SQLite placée sur un partage réseau ne doit pas être ouverte simultanément par deux ordinateurs.
- Les montants sont encore stockés sous forme de nombres décimaux SQLite et non en centimes entiers.
- Easy CESU ne synchronise aucune donnée en ligne et n'assure pas la résolution de conflits entre plusieurs copies.
- Le verrouillage de l'application par code reste à réaliser.
- Les pièces jointes et modèles de documents personnalisés sont prévus dans le schéma, mais leur gestion complète n'est pas encore disponible dans l'interface.
