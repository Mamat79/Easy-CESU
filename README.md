# Easy CESU

Easy CESU est une application locale pour Windows et macOS destinée aux
professionnels et salariés des services à la personne. Elle centralise les
clients, interventions, tarifs, rappels, paiements, notes PDF et bilans Excel
sans imposer de compte en ligne.

**Version actuelle : 2026.8**

La version 2026.8 est disponible pour Windows. Les paquets Mac 2026.8 sont en préparation ; les versions Mac 2026.6 restent disponibles.

[Voir la version Windows 2026.8](https://github.com/Mamat79/Easy-CESU/releases/tag/v2026.8)

## Télécharger

| Système | Fichier |
| --- | --- |
| Windows 11 x64 | [EasyCESU-Setup-x64-2026.8.exe](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.8/EasyCESU-Setup-x64-2026.8.exe) |
| macOS Apple Silicon | [EasyCESU-macOS-Apple-Silicon-2026.6.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.6/EasyCESU-macOS-Apple-Silicon-2026.6.dmg) |
| macOS Intel | [EasyCESU-macOS-Intel-2026.6.dmg](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.6/EasyCESU-macOS-Intel-2026.6.dmg) |
| Notice complète | [Easy_CESU_2026.8_Notice_Installation_et_Utilisation.pdf](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.8/Easy_CESU_2026.8_Notice_Installation_et_Utilisation.pdf) |

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

## Nouveautés 2026.8

Les titres **Durée** et **Net** sont alignés avec leurs valeurs. Les dates regroupées sont abrégées en **du 3 au 30**, **du 17 au 25** ou **le 17**, pour le mois affiché. Cliquez sur un titre de colonne pour trier les lignes ; un second clic inverse le tri. Client se trie par ordre alphabétique, les durées, montants et nombres d'interventions par valeur numérique. Le tri fonctionne en affichage détaillé et regroupé.

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
- [Lire la notice complète](https://github.com/Mamat79/Easy-CESU/releases/download/v2026.8/Easy_CESU_2026.8_Notice_Installation_et_Utilisation.pdf)
- [Lire les notes de la version 2026.8](RELEASE_NOTES_2026.8.md)
