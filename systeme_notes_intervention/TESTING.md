# Tests

La suite isolée n'utilise jamais la base personnelle installée :

```powershell
.\.build_venv\Scripts\python.exe -m unittest discover -s tests -v
```

La V3.1.4 comporte les tests automatisés couvrant notamment :

- première installation et profil générique ;
- création, renommage et séparation des clients ;
- priorité du tarif individuel ;
- migration additive de la base avec sauvegarde préalable ;
- notes, paiements en attente et rappels périodiques ;
- sauvegarde, contrôle d'intégrité et restauration ZIP ;
- refus d'une source Excel inaccessible sans blocage au démarrage ;
- synchronisation des numéros de version ;
- conservation du chemin de base lors d'un changement d'icône ;
- présence des dix icônes métier et de leurs aperçus ;
- transmission du choix d'icône au processus administrateur ;
- détection d'une ancienne installation locale pour la remplacer ;
- présence des grands boutons de durée et de montant.
- migration additive V3 et conservation des clients et interventions ;
- création, duplication, import, export et suppression contrôlée des modèles ;
- génération d'un PDF avec un modèle personnalisé ;
- ouverture de la fenêtre native WebView2 et arrêt du serveur à sa fermeture ;
- attribution dynamique et libération du port local afin d'éviter les conflits
  avec les autres applications ;
- isolation complète de la préversion par rapport aux données installées ;
- détection et installation conditionnelle du runtime Microsoft WebView2.
- quatre modes d'affichage, adaptation au DPI et mémorisation locale par ordinateur ;
- sélection du moteur natif WebView2 ou Cocoa selon le système ;
- emplacement des données dans `Application Support` sous macOS ;
- sélecteurs natifs de dossiers et de fichiers macOS.
- liste blanche limitée aux liens GitHub et à la page PayPal.Me validée ;
- affichage local du QR PayPal sans redirection web trompeuse ;
- fréquence, report et désactivation du rappel discret de soutien ;
- contenu limité du fichier GitHub `FUNDING.yml`.
- migration des préférences d'envoi et de relecture des mails par client ;
- aperçu mensuel des destinataires et désactivation des clients sans adresse ;
- modèles d'objet et de texte avec champs dynamiques ;
- envoi SMTP simulé avec pièces jointes PDF, sans message réel ;
- export des notes directement dans le dossier sélectionné.
- migration du schéma 3.1.3 vers le suivi administratif, avec sauvegarde et seconde exécution sans effet de bord ;
- conservation des anciennes interventions comme déjà traitées pour la déclaration ;
- persistance indépendante des états `Transmis`, `Déclaré` et `Payé` ;
- cohérence du montant reçu et du paiement en attente lors d'un changement de l'état `Payé` ;
- tableau `À suivre`, filtres, recherche et regroupement sur une seule ligne par intervention ;
- ignorance et réactivation d'un rappel précis sans effet sur les autres interventions ;
- nettoyage de l'ignorance lorsqu'un état est validé, puis réapparition normale s'il est décoché ;
- marquage `Transmis` limité aux emails réellement envoyés lorsque l'option est activée.

Contrôles complémentaires réalisés pour chaque livraison :

- compilation Python et contrôle syntaxique JavaScript ;
- test Playwright de l'éditeur à `1440 x 900` et `1024 x 768`, sans débordement ;
- lancement de l'exécutable PyInstaller dans sa vraie fenêtre Windows ;
- contrôle de l'assistant initial et de l'éditeur de modèles par accessibilité Windows ;
- fermeture de la fenêtre puis vérification de l'arrêt du processus et du port local ;
- construction de l'application autonome et de l'installateur x64 ;
- installation réelle par-dessus la version précédente uniquement après validation du candidat ;
- comparaison de la configuration et de la base avant/après ;
- contrôle visuel et textuel de la notice PDF.

Le workflow GitHub Actions `Construire les installateurs macOS` exécute les
tests portables sur deux machines macOS natives, construit les applications
Apple Silicon et Intel, vérifie le bundle, lance réellement l'exécutable et
contrôle son API locale avant de produire chaque DMG.
