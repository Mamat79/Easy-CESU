# Architecture

## État actuel

- `application/app_server.py` contient le serveur local, le stockage SQLite, les règles métier et les routes HTTP.
- `application/desktop_app.py` démarre ce serveur sur l'ordinateur puis
  l'affiche dans une fenêtre native WebView2 sous Windows ou Cocoa/WebKit sous
  macOS. La fermeture de la fenêtre arrête le serveur.
- `application/reminder_logic.py` calcule les récurrences mensuelles et annuelles.
- `application/backup_restore.py` crée, vérifie et extrait les sauvegardes ZIP sans écrire avant validation.
- `application/static` contient l'interface HTML, CSS et JavaScript affichée dans la fenêtre native.
- `generer_notes_et_donnees.py` génère les notes PDF et calcule les synthèses mensuelles.
- `application/excel_export.py` produit le bilan Excel.
- `installateur_windows.py` installe et met à jour l'application Windows.
- `Construire_macOS.sh` produit l'application `.app` et l'installateur `.dmg`
  sur un runner macOS natif.

Les données d'exécution sont conservées dans `%LOCALAPPDATA%\EasyCESU` sous
Windows et `~/Library/Application Support/EasyCESU` sous macOS. Elles sont
séparées en données, pièces jointes, sauvegardes, configuration, journaux et
temporaires. Chaque compte référence sa propre base SQLite et possède ses
propres modèles de documents.

Le schéma V3 ajoute uniquement la table `document_templates`. Le schéma 6 de la version 3.1.4 ajoute l'état `declared` aux interventions et la table `intervention_followup_ignores`. Avant une migration portant sur une base contenant des données, Easy CESU crée une sauvegarde. Les tables historiques de clients et d'interventions ne sont ni recréées ni vidées.

Les changements rapides des états administratifs utilisent une route dédiée plutôt que la mise à jour complète d'une intervention. La logique métier est centralisée dans `update_intervention_administrative_status` : elle valide l'état demandé, préserve les montants reçus saisis manuellement, synchronise les paiements liés et retire les ignorances devenues inutiles. Le tableau `À suivre` est alimenté par `list_intervention_followups`, qui regroupe les actions manquantes sur une seule ligne par intervention.

## Direction retenue

Le projet reste une application locale. Le serveur HTTP n'écoute que sur `127.0.0.1` et n'ouvre plus de navigateur externe dans la version empaquetée.

Le découpage sera introduit sans réécriture complète : chaque nouvelle règle métier devra être testable sans démarrer la fenêtre, et chaque migration de stockage devra être sauvegardée puis vérifiée.
