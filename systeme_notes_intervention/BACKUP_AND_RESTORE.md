# Sauvegarde et restauration

## Fonction actuelle

Dans `Base de données`, `Créer la sauvegarde` produit une archive ZIP du compte actif. Elle contient une image SQLite cohérente, le profil du compte, les métadonnées et les pièces jointes éventuelles. Un manifeste avec empreintes SHA-256 est contrôlé à la création et avant toute restauration.

## Procédure de restauration

1. Ouvrir `Base de données`.
2. Sélectionner le compte concerné.
3. Cliquer sur `Restaurer une sauvegarde`.
4. Choisir l'archive `.zip` reçue.
5. Easy CESU vérifie le manifeste, les tailles, les empreintes et l'intégrité SQLite, puis crée une sauvegarde de précaution du compte actif avant restauration.
6. Vérifier le compte, les clients, les interventions et les rappels après l'import.

## Sécurité

Les archives sont refusées si elles contiennent un chemin absolu, une remontée de dossier, un lien symbolique, un manifeste incohérent ou une base SQLite invalide. Le volume et le nombre de fichiers sont limités avant extraction.

Les sauvegardes automatiques programmées et leur rotation ne sont pas encore proposées.
