# Easy CESU 2026.9.1

Disponible pour Windows. Les paquets Mac 2026.9.1 sont en préparation ; les versions Mac 2026.6 restent disponibles. La mise à jour automatique sera proposée après qualification des deux paquets Mac.

Ce correctif protège les licences permanentes lors de la nouvelle saisie de leur code : une activation locale valide est réutilisée hors ligne, la même identité est conservée si un reçu doit être renouvelé et une tentative refusée préserve toute activation précédente valide. Les erreurs de service sans détail indiquent maintenant leur statut HTTP. Les clés et les droits déjà émis restent inchangés.

Les nouveautés email de la version 2026.9 sont incluses :

La préparation des notes par email propose maintenant des pièces jointes supplémentaires, des brouillons dans votre messagerie et une demande d'envoi différé avec un repli explicite lorsqu'il faut terminer la programmation dans la boîte mail.

- Ajoutez ou retirez des fichiers pendant la relecture du message d'un client. Sa note PDF reste jointe automatiquement ; les fichiers supplémentaires sont propres à ce client.
- Choisissez **Envoi classique**, **Placer dans les brouillons** ou **Programmer l'envoi** avec une date et une heure futures.
- Dans le récapitulatif, appliquez une action à tous les clients cochés ou ajustez chaque ligne. Les clients retenus sont déjà cochés par défaut ; le retour en édition conserve le contenu, les fichiers et les choix.
- La confirmation finale reste obligatoire avant toute action de messagerie.
- Les brouillons sont déposés dans votre vraie boîte mail par une connexion IMAP sécurisée, avec destinataires, copies, objet, texte et pièces jointes. Avec `smtp.gmail.com`, le serveur Gmail est reconnu automatiquement ; l'identifiant et le mot de passe d'application déjà enregistrés sont réutilisés. Les autorisations IMAP doivent permettre le dépôt.
- Avec la connexion Gmail actuelle, une demande d'envoi différé crée un **brouillon à programmer manuellement**. L'avertissement est visible avant confirmation. Le résultat rappelle d'ouvrir Gmail et de programmer soi-même le message à la date et à l'heure demandées. Easy CESU ne présente jamais ce brouillon comme un envoi déjà programmé.
- Une fois la programmation confirmée dans Gmail, vous pouvez fermer Easy CESU et éteindre le PC.
- Le résultat reste affiché par client : envoyé, brouillon créé, programmation manuelle nécessaire ou échec. Seuls les envois réels peuvent marquer les interventions **Transmis**. La reprise des échecs certains ne reprend pas les succès ; un résultat incertain demande une vérification dans la messagerie avant toute nouvelle tentative.

Limites des fichiers supplémentaires : 10 Mio par fichier, 18 Mio et 20 fichiers par client ; message complet limité à 25 Mio. Le stockage temporaire est séparé par compte et par client, puis nettoyé après utilisation ou annulation ; les restes expirent après 24 heures lors du nettoyage.

## Installation et mise à jour

Installez le paquet adapté à votre ordinateur au même emplacement que la version précédente. Les comptes, interventions, réglages et licences sont conservés. Les versions depuis 2026.6 disposent du parcours **Réglages > Mises à jour du logiciel**. Le mot de passe de messagerie reste dans le coffre sécurisé du système.

L'installateur Windows n'est pas signé numériquement. Les versions Mac actuellement disponibles ne sont pas notarisées par Apple ; la qualification Intel est réalisée sous Rosetta sur Apple Silicon.
