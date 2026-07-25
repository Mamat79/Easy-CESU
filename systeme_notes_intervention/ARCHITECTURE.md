# Architecture

## État actuel

- `application/app_server.py` contient le serveur local, le stockage SQLite, les règles métier et les routes HTTP.
- `application/desktop_app.py` démarre ce serveur sur l'ordinateur puis l'affiche dans une fenêtre native WebView2. La fermeture de la fenêtre arrête le serveur.
- `application/reminder_logic.py` calcule les récurrences mensuelles et annuelles.
- `application/backup_restore.py` crée, vérifie et extrait les sauvegardes ZIP sans écrire avant validation.
- `application/static` contient l'interface HTML, CSS et JavaScript affichée dans la fenêtre native.
- `generer_notes_et_donnees.py` génère les notes PDF et calcule les synthèses mensuelles.
- `application/excel_export.py` produit le bilan Excel.
- `installateur_windows.py` installe et met à jour l'application Windows.

Les données d'exécution de l'application installée sont conservées dans `%LOCALAPPDATA%\EasyCESU`, séparées en données, pièces jointes, sauvegardes, configuration, journaux et temporaires. Chaque compte référence sa propre base SQLite et possède ses propres modèles de documents.

Le schéma V3 ajoute uniquement la table `document_templates`. Avant cette migration, Easy CESU crée une sauvegarde de la base. Les tables historiques de clients et d'interventions ne sont ni recréées ni vidées.

## Direction retenue

Le projet reste une application locale. Le serveur HTTP n'écoute que sur `127.0.0.1` et n'ouvre plus de navigateur externe dans la version empaquetée.

Le découpage sera introduit sans réécriture complète : chaque nouvelle règle métier devra être testable sans démarrer la fenêtre, et chaque migration de stockage devra être sauvegardée puis vérifiée.
