# Easy CESU - suivi des activités CESU

Easy CESU suit les clients, les interventions, les rappels, les paiements, les notes d'intervention et les bilans. Il convient au jardinage, au ménage, au bricolage, à l'aide à domicile, à la garde d'enfants, au soutien scolaire, à l'administratif, à l'informatique et aux autres services à la personne.

Easy CESU est un outil indépendant de suivi d'activité. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Utiliser l'application

Sous Windows, depuis le Bureau ou le menu Démarrer, ouvre :

```text
Easy CESU V3
```

Sous macOS, ouvre `Easy CESU` depuis le dossier `Applications`.

Easy CESU s'ouvre dans sa propre fenêtre. Il n'est plus nécessaire d'ouvrir Chrome ni de conserver une fenêtre de commande.

Pour le développement seulement, le serveur local reste lançable avec :

```powershell
.\Lancer_application.ps1
```

Ouvre ensuite :

```text
http://127.0.0.1:8765
```

Dans l'application, tu peux saisir une intervention avec date, client, durée, tarif net horaire et description. Les grands boutons moins et plus modifient la durée par 30 minutes et les tarifs ou montants par 0,50 euro. La saisie directe reste possible.
Le compte actif se change directement en haut de la page principale.
L'onglet `Base de donnees` sert a importer une base recue ou a exporter une copie complete. L'onglet `Reglages` sert a creer, modifier ou supprimer un compte, ainsi qu'a definir l'identite affichee sur les notes, le tarif net horaire par defaut, le dossier des notes et le dossier des exports. Les chemins moins courants sont ranges dans `Options avancees`.
L'onglet `Clients` sert a gerer le repertoire et les rappels de chaque client. Le champ `Tarif individuel` est optionnel : laisse-le vide pour utiliser le tarif par defaut, ou remplis-le pour que ce tarif soit prioritaire pour ce client. L'onglet `Planning` rassemble les rappels en retard, du jour et a venir.
En fin de mois, choisis l'annee et le mois puis clique sur `Generer les notes`.
L'application te demande alors ou ranger les notes PDF.
Les PDF sont créés directement dans le dossier choisi, sans sous-dossier supplémentaire.

Pour envoyer les notes par email, ouvre `Réglages` > `Envoi des notes par email`, renseigne le serveur SMTP de ton adresse et personnalise l'objet ou le texte du message. Le mot de passe est enregistré uniquement dans le coffre sécurisé de l'ordinateur. Dans chaque fiche client, tu peux choisir si le client est sélectionné par défaut et si son message doit être relu avant l'envoi. Le bouton `Envoyer les notes` affiche toujours la liste des destinataires avant toute expédition. L'option proposée dans cette fenêtre marque comme `Transmis` uniquement les interventions dont le mail a réellement été envoyé.

Dans la liste mensuelle des interventions, les cases `Transmis` et `Payé` peuvent être cochées directement, sans rouvrir la fiche.

Dans `Planning`, clique sur `Nouveau rappel` pour créer un rappel général ou choisir un client. La première échéance peut être une date précise et la répétition peut être quotidienne, hebdomadaire, mensuelle ou annuelle. Le champ `Intervalle` permet par exemple de choisir tous les 3 mois. Le même éditeur est accessible depuis la fiche d'un client avec le bouton `Ajouter un rappel`.

Le bouton `Bilan Excel` te demande aussi le dossier de sortie, puis cree `Bilan activite application YYYY.xlsx`.
La creation et la restauration d'une sauvegarde ZIP sont regroupees dans l'onglet `Base de donnees`, qui affiche le compte concerne et la base actuellement utilisee.
Au premier lancement, apres l'import d'une base ou apres la creation d'un compte, l'assistant demande un seul dossier principal. Easy CESU y cree automatiquement des sous-dossiers separes pour la base, les notes et les exports de ce compte. Dans `Reglages`, le bouton `Choisir un dossier principal` permet de relancer cet assistant. Les emplacements restent modifiables individuellement dans les reglages avances.

## Creer un compte pour une autre personne

Va dans `Reglages`, clique sur `Nouveau compte`, remplis le nom du compte, l'identite a afficher sur les notes, le tarif par defaut, les sources et les dossiers souhaites, puis clique sur `Creer le compte`.

Chaque compte a ses propres clients, interventions et tarifs individuels. Les nouveaux comptes démarrent vides pour éviter de mélanger les clients de deux activités.

Pour revenir a un autre compte, utilise la liste `Compte` en haut de la page principale.

Easy CESU s'arrête automatiquement à la fermeture de sa fenêtre. Les autres applications et les onglets Chrome restent indépendants.

Pour arreter l'application :

```powershell
.\Arreter_application.ps1
```

## Installateur Windows recommande

Pour creer un installateur `.exe` complet, double-clique sur :

```text
Construire installateur Easy CESU.cmd
```

Le resultat est cree ici, avec son numero de version et `x64` dans le nom :

```text
systeme_notes_intervention\sorties\EasyCESU-Setup-x64-3.1.3.exe
```

Cet installateur contient Easy CESU, Python, ses bibliothèques et le programme officiel Microsoft WebView2 utilisé seulement si ce composant manque. Il installe par défaut dans `C:\Program Files\Easy CESU`, permet de choisir un autre dossier, propose une icône selon le métier, crée les raccourcis Bureau/Menu Démarrer au choix et peut ouvrir la notice à la fin. Si tu gardes `Program Files`, Windows demandera une autorisation.
Si une version est deja installee, l'installateur le signale et propose soit de la remplacer, soit d'installer une copie en plus. Pour une mise a jour, il ferme automatiquement Easy CESU avant de remplacer les fichiers puis relance la nouvelle version si l'option est cochee.
La configuration et la base sont conservées dans `%LOCALAPPDATA%\EasyCESU` et ne sont pas remplacées lors d'une mise à jour.

## Installation macOS

Télécharge le DMG adapté au Mac :

- `EasyCESU-macOS-Apple-Silicon-3.1.3.dmg` pour les Mac M1 et suivants ;
- `EasyCESU-macOS-Intel-3.1.3.dmg` pour les Mac Intel.

Ouvre le DMG, puis glisse `Easy CESU` dans le dossier `Applications`. Au
premier lancement, si macOS bloque l'ouverture, fais un clic droit sur
`Easy CESU`, choisis `Ouvrir`, puis confirme.

Les données macOS sont conservées dans
`~/Library/Application Support/EasyCESU`. Une sauvegarde ZIP créée sous
Windows peut être restaurée sur Mac ; l'assistant demande ensuite les nouveaux
dossiers à utiliser sur cet ordinateur.

L'installateur n'embarque pas ta base de donnees. Pour transmettre l'etat actuel a quelqu'un :

1. Sur ton PC, va dans `Base de donnees` > `Creer la sauvegarde`, puis choisis un dossier.
2. Donne a la personne `EasyCESU-Setup-x64-3.1.3.exe` et le fichier `.zip` cree.
3. Sur son PC, elle lance l'installateur, choisit le repertoire d'installation puis ouvre Easy CESU.
4. Au premier lancement, elle choisit `Restaurer une sauvegarde` et selectionne le fichier `.zip` recu.
5. L'assistant demande ensuite un seul dossier principal et cree automatiquement les dossiers de la base, des notes et des bilans Excel.

Dans `Options avancees`, le bouton `Utiliser une base sans la copier` sert plutot a travailler directement sur une base placee dans un dossier partage.

## Personnaliser les notes d'intervention

1. Ouvre l'onglet `Modèles`.
2. Choisis le modèle actuel, clique sur `Nouveau` ou utilise `Dupliquer`.
3. Modifie les textes, les couleurs, les tailles, les marges ou l'ordre des blocs.
4. Contrôle le résultat dans l'aperçu A4 à droite.
5. Coche `Utiliser ce modèle pour les prochaines notes`, puis clique sur `Enregistrer`.
6. Utilise `PDF d'essai` pour vérifier le document final avant la génération mensuelle.

Chaque compte conserve ses propres modèles. L'import et l'export JSON permettent d'échanger une mise en page sans transférer les clients ni les interventions.

## Aide et communauté

Dans `Réglages`, la section `Aide et communauté` permet d'ouvrir le dépôt
GitHub public, de consulter le code et la documentation, de signaler un
problème ou de soutenir volontairement Easy CESU en scannant le QR PayPal
affiché dans l'application.

Easy CESU reste entièrement gratuit et open source. Le soutien ne débloque
aucune fonctionnalité et ne crée aucun abonnement. Le rappel discret apparaît
après 30 jours puis au maximum une fois tous les 90 jours. Décoche l'option
correspondante ou choisis `Ne plus afficher` pour le désactiver définitivement.

## Version executable autonome

Pour creer un programme Windows autonome, double-clique sur :

```text
Construire executable portable.cmd
```

Le resultat est cree dans :

```text
systeme_notes_intervention\dist\Easy CESU\Easy CESU.exe
```

Un ZIP portable est aussi cree dans `systeme_notes_intervention\sorties`.
Cette version contient Python et les dependances. Sur l'autre ordinateur, il suffit de dezipper le dossier puis de lancer `Easy CESU.exe`.

Le dossier de l'executable contient aussi `Installer sur ce PC.cmd`, qui copie l'application dans `%LOCALAPPDATA%\Easy CESU` et cree un raccourci sur le Bureau.

## Lancer la generation

Dans PowerShell, depuis ce dossier :

```powershell
.\Generer_notes_et_bilans.ps1 -Annee 2026
```

Pour un mois seulement :

```powershell
.\Generer_notes_et_bilans.ps1 -Annee 2026 -Mois 6
```

Par defaut, les notes PDF deja presentes dans le dossier annuel/mensuel ne sont pas remplacees.
Pour les recreer :

```powershell
.\Generer_notes_et_bilans.ps1 -Annee 2026 -RemplacerNotes
```

## Ce qui est produit

- `Bilan activite application YYYY.xlsx` : le tableur de bilan dans le dossier des exports.
- `donnees_application_YYYY.json` : les donnees normalisees utilisees par le tableur.
- `sorties\rapport_generation_YYYY.txt` : un resume rapide de la generation.
- Les notes PDF sont rangees dans le dossier `Notes d'intervention\YYYY\MM. Mois YYYY`.

## Onglets du tableur

- `Synthese` : total clients, interventions, heures, net et brut estime.
- `Bilan mensuel` : recapitulatif mois par mois.
- `Bilan clients` : recapitulatif client par client avec CESU et adresse si retrouvee.
- `Interventions` : une ligne par intervention, avec date, heures, montant et source.
- `Client par mois` : lecture rapide des heures par client et par mois.
- `Anomalies` : points a corriger, par exemple un numero CESU manquant.
- `Parametres` : chemins sources et hypotheses de calcul.

## A saisir au quotidien

Continue a remplir les heures dans les onglets mensuels du classeur de suivi, une ligne par client et une colonne par jour.
Le script relit cette grille et calcule automatiquement les notes et les bilans.
