# Validation Easy CESU 3.0.0

Date : 26 juillet 2026

## Portée

- Branche principale : `main`.
- Commit candidat : `4e2c695be86fd823eba29cde1a0641218a91f8aa`.
- Mise à jour réelle de la V2.1.0 vers la V3.0.0 sur le PC de développement.
- Installation active : `C:\Users\mamat\AppData\Local\Easy CESU`.
- Bases et configurations personnelles exclues du dépôt et des paquets.

## Contrôles exécutés

- 26 tests automatisés réussis sous Windows.
- 18 tests portables exécutés sur chaque runner macOS, avec un test de cycle
  serveur remplacé sur Mac par le lancement réel du bundle construit.
- Compilation Python réussie.
- Contrôle syntaxique JavaScript réussi.
- Contrôle `git diff --check` réussi.
- Parcours Playwright de l'éditeur réussi à 1440 et 1024 pixels.
- Construction PyInstaller x64 réussie.
- Ouverture de l'exécutable dans une fenêtre Windows `Easy CESU V3`.
- Affichage de l'assistant de premier démarrage.
- Ouverture et contrôle visuel de l'onglet `Modèles`.
- Fermeture de la fenêtre, arrêt du processus et libération du port local.
- Attribution dynamique d'un port libre par Windows pour la fenêtre native,
  sans collision avec PATATE déjà actif sur un autre port.
- Génération et rendu d'un PDF par défaut et d'un PDF personnalisé.
- Rendu visuel des deux pages de la notice V3.
- Installateur V3 exécuté avec le code de sortie 0.
- Comparaison du paquet et de l'installation : 247 fichiers présents et
  identiques, hors script de désinstallation volontairement régénéré.
- Raccourcis `Easy CESU V3` créés sur le Bureau et dans le menu Démarrer.
- Version 3.0.0 enregistrée dans la liste des applications Windows.
- Lancement depuis l'installation, serveur local limité à `127.0.0.1` sur un
  port dynamique et réponse `/api/app-info` indiquant la version 3.0.0.
- Fermeture de la vraie fenêtre Windows : processus terminé et port libéré,
  tandis que PATATE est resté actif sur le port 8766.
- Construction, signature ad hoc, lancement réel et vérification du DMG sur
  les runners GitHub macOS Apple Silicon et Intel.
- Workflow macOS réussi :
  `https://github.com/Mamat79/Easy-CESU/actions/runs/30194291945`.
- Rendu visuel final des deux pages A4 de la notice V3.

## Fichiers candidats

- Windows x64, 41 391 927 octets :
  `e9782d039673ac8525105038e5ea04d62c872ed15dffdaf8bbe18a4431fed2b5`.
- macOS Apple Silicon, 22 573 569 octets :
  `9a0977f7b7b2e7b242c087a726f14c455490dfffde1392d5bcda9a2ab47f372b`.
- macOS Intel, 23 995 283 octets :
  `5fcdcaefbbbf8ecbef3002e1ada6dfd34c2584b04c67e5afa8179b194ae2e64f`.
- Notice PDF, 7 192 octets :
  `b80fcaa1b11bd64559f2bb8f15999e919ce24d546614394428447bf27fb99573`.

## Protection des données

Une empreinte SHA-256 a été calculée avant le test sur les quatre fichiers de
configuration et de base des emplacements V2 actuels et historiques. Les quatre
empreintes étaient identiques après fermeture de la préversion V3.

La préversion utilise un dossier dédié et désactive la reprise automatique des
anciens chemins. L'installateur final conserve au contraire la migration
versionnée nécessaire à une vraie mise à jour V2 vers V3.

La mise à jour réelle a conservé 148 clients et 1 237 interventions. Le schéma
est passé de la version 2 à la version 3 et un premier modèle de note a été
créé. Deux sauvegardes ont été vérifiées :

- sauvegarde externe avant installation ;
- sauvegarde automatique `avant-migration-v3` créée au premier lancement.

L'installateur prépare désormais le nouveau moteur dans un dossier séparé puis
le bascule en une opération rapide. Le nettoyage de l'ancien moteur est limité
à cinq secondes afin que l'installateur ne reste jamais bloqué. Sur ce PC,
Windows conserve encore une ancienne DLL inactive de 124 Ko ; elle est hors du
moteur utilisé par la V3 et n'a aucun effet fonctionnel.

## Limites connues

- L'exécutable Windows n'est pas signé par un certificat commercial et peut
  donc déclencher Microsoft SmartScreen.
- Les applications macOS utilisent une signature ad hoc et ne sont pas
  notariées par Apple. Le premier lancement peut demander `Clic droit > Ouvrir`.
- Le candidat Windows a été validé sur le PC de développement avec la base
  existante. La mise à jour du PC de Clothilde reste une opération séparée.
