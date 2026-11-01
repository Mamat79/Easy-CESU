# Easy CESU

Easy CESU est une application locale pour Windows et macOS destinée aux
professionnels et salariés des services à la personne. Elle centralise les
clients, interventions, tarifs, rappels, paiements, notes PDF et bilans Excel
sans imposer de compte en ligne.

**Version actuelle : 2026.9.1**

La version 2026.9.1 est disponible pour Windows. Les paquets Mac 2026.9.1 sont en préparation ; les versions Mac 2026.6 restent disponibles.

[Voir la version Windows 2026.9.1](https://github.com/Mamat79/Easy-CESU/releases/tag/v2026.9.1)

## Télécharger

| Système | Fichier |
| --- | --- |
| Windows 11 x64 | [EasyCESU-Setup-x64-2026.9.1.exe](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.9.1/EasyCESU-Setup-x64-2026.9.1.exe) |
| macOS Apple Silicon | [EasyCESU-macOS-Apple-Silicon-2026.6.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.6/EasyCESU-macOS-Apple-Silicon-2026.6.dmg) |
| macOS Intel | [EasyCESU-macOS-Intel-2026.6.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.6/EasyCESU-macOS-Intel-2026.6.dmg) |
| Notice complète | [Easy_CESU_2026.9.1_Notice_Installation_et_Utilisation.pdf](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.9.1/Easy_CESU_2026.9.1_Notice_Installation_et_Utilisation.pdf) |

L'installateur Windows n'est pas encore signé numériquement. Windows peut donc
afficher un avertissement SmartScreen. Vérifiez l'empreinte SHA-256 publiée dans
la release avant de l'exécuter.

Sur Mac, ouvrez le DMG adapté à votre processeur puis glissez Easy CESU dans
Applications. La version Intel est testée sous Rosetta sur Apple Silicon. Les applications Mac ne sont pas notarisées par Apple ; si macOS
bloque la première ouverture, autorisez Easy CESU dans Réglages Système,
Confidentialité et sécurité, après avoir vérifié sa provenance et son empreinte.


## Mises à jour depuis le logiciel

Une vérification quotidienne signale les nouvelles versions. Ouvrez Réglages > Mises à jour du logiciel pour rechercher une version ou désactiver la recherche automatique. Télécharger et installer vérifie le fichier, sauvegarde vos comptes, remplace l'application et la relance. Les données et la licence restent conservées ; Windows ou macOS peut demander une autorisation.

Les versions antérieures à 2026.6 doivent installer cette version une première fois depuis GitHub pour disposer de cette fonction.

## Nouveautés 2026.9.1

Ajoutez des fichiers à la note PDF pendant la relecture d'un client. Choisissez **Envoi classique**, **Placer dans les brouillons** ou **Programmer l'envoi**, puis appliquez au besoin une action commune aux clients cochés dans le récapitulatif. La confirmation finale reste obligatoire.

Les brouillons sont déposés dans votre vraie messagerie par IMAP sécurisé, avec les destinataires, copies, contenu et pièces jointes. Avec Gmail, une demande différée devient un brouillon **à programmer soi-même dans Gmail** : l'avertissement est visible avant confirmation et le résultat rappelle la date et l'heure demandées. Une fois la programmation confirmée dans Gmail, Easy CESU et le PC peuvent être fermés. Les brouillons ne sont jamais marqués Transmis automatiquement.

Le correctif 2026.9.1 conserve l'identité et une activation locale valide lorsqu'on ressaisit le même code de licence. Une tentative refusée préserve l'activation précédente ; les erreurs du service sans détail indiquent leur statut HTTP. Les licences permanentes déjà émises restent valables.

Les fonctions précédentes sont conservées : colonnes Durée et Net alignées, dates regroupées abrégées et tri par clic sur les titres.

## Regroupement des interventions

Regroupez les interventions affichées en une ligne par client, avec leur nombre, la durée totale et le montant total. Les cases Transmis, Déclaré et Payé agissent sur toutes les interventions représentées par cette ligne. Les états partiels restent visibles et les filtres limitent les interventions concernées. Un bouton permet de retrouver les lignes détaillées.

Elle inclut aussi les nouveautés 2026.5 : adresses en copie, sélection de colonnes en une action et relecture des emails avec Précédent et Suivant. Le récapitulatif final conserve tous les clients retenus déjà cochés et permet de modifier chaque email avant de confirmer.

## Fonctions principales

- plusieurs comptes Easy CESU entièrement séparés ;
- clients, coordonnées, tarifs individuels et historique ;
- interventions avec durée, montant, état et description ;
- planning et rappels ponctuels ou récurrents ;
- suivi `Transmis`, `Déclaré` et `Payé` ;
- notes d'intervention PDF personnalisables ;
- préparation et envoi des emails avec pièces jointes ;
- bilans Excel par mois ou par année ;
- assistant de fin de contrat, estimation préparatoire des indemnités et archivage sans suppression ;
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
- [Lire la notice complète](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.9.1/Easy_CESU_2026.9.1_Notice_Installation_et_Utilisation.pdf)
- [Lire les notes de la version 2026.9.1](RELEASE_NOTES_2026.9.1.md)
