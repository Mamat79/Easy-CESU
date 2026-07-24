# Architecture

## État actuel

- `application/app_server.py` contient le serveur local, le stockage SQLite, les règles métier et les routes HTTP.
- `application/reminder_logic.py` calcule les récurrences mensuelles et annuelles.
- `application/backup_restore.py` crée, vérifie et extrait les sauvegardes ZIP sans écrire avant validation.
- `application/static` contient l'interface HTML, CSS et JavaScript servie localement dans le navigateur.
- `generer_notes_et_donnees.py` génère les notes PDF et calcule les synthèses mensuelles.
- `application/excel_export.py` produit le bilan Excel.
- `installateur_windows.py` installe et met à jour l'application Windows.

Les données d'exécution de l'application installée sont conservées dans `%LOCALAPPDATA%\EasyCESU`, séparées en données, pièces jointes, sauvegardes, configuration, journaux et temporaires. Chaque compte référence sa propre base SQLite.

## Direction retenue

Le projet restera une application locale. Les prochains modules seront séparés progressivement autour de : Clients, Interventions, Planning, Documents, Bilans, Analyses, Sauvegarde et Paramètres.

Le découpage sera introduit sans réécriture complète : chaque nouvelle règle métier devra être testable sans démarrer le navigateur, et chaque migration de stockage devra être sauvegardée puis vérifiée.
