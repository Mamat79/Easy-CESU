# Validation Easy CESU 3.0.0

Date : 25 juillet 2026

## Portée

- Branche : `v3/native-desktop-template-editor`
- Mise à jour réelle de la V2.1.0 vers la V3.0.0 sur le PC de développement.
- Installation active : `C:\Users\mamat\AppData\Local\Easy CESU`.
- Bases et configurations personnelles exclues du dépôt et des paquets.

## Contrôles exécutés

- 22 tests unitaires isolés réussis.
- Compilation Python réussie.
- Contrôle syntaxique JavaScript réussi.
- Contrôle `git diff --check` réussi.
- Parcours Playwright de l'éditeur réussi à 1440 et 1024 pixels.
- Construction PyInstaller x64 réussie.
- Ouverture de l'exécutable dans une fenêtre Windows `Easy CESU V3`.
- Affichage de l'assistant de premier démarrage.
- Ouverture et contrôle visuel de l'onglet `Modèles`.
- Fermeture de la fenêtre, arrêt du processus et libération du port 8765.
- Génération et rendu d'un PDF par défaut et d'un PDF personnalisé.
- Rendu visuel des deux pages de la notice V3.
- Installateur V3 exécuté avec le code de sortie 0.
- Comparaison du paquet et de l'installation : 247 fichiers présents et
  identiques, hors script de désinstallation volontairement régénéré.
- Raccourcis `Easy CESU V3` créés sur le Bureau et dans le menu Démarrer.
- Version 3.0.0 enregistrée dans la liste des applications Windows.
- Lancement depuis l'installation, serveur local limité à `127.0.0.1:8765` et
  réponse `/api/app-info` indiquant la version 3.0.0.

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

## Reste à faire avant publication stable

- Tester l'installateur candidat sur une seconde machine Windows 11 x64.
- Tester la mise à jour logicielle sur le PC de Clothilde, sans remplacer sa
  base déjà restaurée.
- Publier la version stable seulement après ces contrôles.
