# Easy CESU

Easy CESU est une application locale pour Windows et macOS destinée aux
professionnels et salariés des services à la personne. Elle centralise les
clients, interventions, tarifs, rappels, paiements, notes PDF et bilans Excel
sans imposer de compte en ligne.

**Version actuelle : 2026.1**

[Télécharger la dernière version](https://github.com/Mamat79/Easy-CESU/releases/latest)

## Télécharger

| Système | Fichier |
| --- | --- |
| Windows 11 x64 | [EasyCESU-Setup-x64-2026.1.exe](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.1/EasyCESU-Setup-x64-2026.1.exe) |
| macOS Apple Silicon | [EasyCESU-macOS-Apple-Silicon-2026.1.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.1/EasyCESU-macOS-Apple-Silicon-2026.1.dmg) |
| macOS Intel | [EasyCESU-macOS-Intel-2026.1.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.1/EasyCESU-macOS-Intel-2026.1.dmg) |

L'installateur Windows n'est pas encore signé numériquement. Windows peut donc
afficher un avertissement SmartScreen. Vérifiez l'empreinte SHA-256 publiée dans
la release avant de l'exécuter.

## Fonctions principales

- plusieurs comptes Easy CESU entièrement séparés ;
- clients, coordonnées, tarifs individuels et historique ;
- interventions avec durée, montant, état et description ;
- planning et rappels ponctuels ou récurrents ;
- suivi `Transmis`, `Déclaré` et `Payé` ;
- notes d'intervention PDF personnalisables ;
- préparation et envoi des emails avec pièces jointes ;
- bilans Excel par mois ou par année ;
- assistant de fin de contrat et archivage sans suppression ;
- sauvegardes ZIP vérifiées et restauration sur un autre ordinateur.

Easy CESU est indépendant et n'est ni affilié ni connecté automatiquement au
service officiel CESU.

## Essai et licence

- 30 jours d'essai gratuit sans rappel ;
- après 30 jours, Easy CESU reste entièrement utilisable ;
- seul un rappel non bloquant apparaît au démarrage ;
- une licence permanente coûte **29 € TTC**, en paiement unique ;
- le code reste valable après toutes les mises à jour compatibles.

[Acheter une licence Easy CESU avec Stripe](https://easy-cesu-license.mamat79-dce.workers.dev/buy)

Pour activer le code reçu :

1. ouvrir `Réglages` ;
2. aller à `Licence, aide et communauté` ;
3. cliquer sur `Gérer la licence` ;
4. coller le code et cliquer sur `Activer le code`.

Le code est vérifié localement. Easy CESU ne reçoit aucune donnée bancaire.

## Mise à jour sans perdre les données

Fermez Easy CESU, téléchargez le nouvel installateur puis installez-le au même
emplacement. Les données et la licence sont conservées séparément :

- Windows : `%LOCALAPPDATA%\EasyCESU` ;
- macOS : `~/Library/Application Support/EasyCESU`.

Une licence déjà activée reste donc active après la mise à jour. Une sauvegarde
ZIP régulière reste recommandée avant toute intervention importante.

## Aide

- [Signaler un problème](https://github.com/Mamat79/Easy-CESU/issues/new)
- [Consulter toutes les versions](https://github.com/Mamat79/Easy-CESU/releases)
- [Lire les notes de la version 2026.1](RELEASE_NOTES_2026.1.md)

Ce dépôt public est réservé à la distribution. Le code source et les clés de
signature des licences sont conservés dans un dépôt privé distinct.
