# Easy CESU - suivi des activités CESU

Easy CESU suit les clients, les interventions, les rappels, les paiements, les notes d'intervention et les bilans. Il convient au jardinage, au ménage, au bricolage, à l'aide à domicile, à la garde d'enfants, au soutien scolaire, à l'administratif, à l'informatique et aux autres services à la personne.

Easy CESU est un outil indépendant de suivi d'activité. Il n'est ni affilié ni connecté automatiquement au service officiel CESU.

## Utiliser l'application

Depuis l'Explorateur Windows, double-clique sur :

```text
Ouvrir Easy CESU.cmd
```

Ce fichier demarre l'application puis ouvre la page dans le navigateur.

Lance l'application locale :

```powershell
.\Lancer_application.ps1
```

Ouvre ensuite :

```text
http://127.0.0.1:8765
```

Dans l'application, tu peux saisir une intervention avec date, client, durée, tarif net horaire, lieu et description. Les grands boutons moins et plus modifient la durée par 30 minutes et les tarifs ou montants par 0,50 euro. La saisie directe reste possible.
Le compte actif se change directement en haut de la page principale.
L'onglet `Base de donnees` sert a importer une base recue ou a exporter une copie complete. L'onglet `Reglages` sert a creer, modifier ou supprimer un compte, ainsi qu'a definir l'identite affichee sur les notes, le tarif net horaire par defaut, le dossier des notes et le dossier des exports. Les chemins moins courants sont ranges dans `Options avancees`.
L'onglet `Clients` sert a gerer le repertoire et les rappels de chaque client. Le champ `Tarif individuel` est optionnel : laisse-le vide pour utiliser le tarif par defaut, ou remplis-le pour que ce tarif soit prioritaire pour ce client. L'onglet `Planning` rassemble les rappels en retard, du jour et a venir.
En fin de mois, choisis l'annee et le mois puis clique sur `Generer les notes`.
L'application te demande alors ou ranger les notes PDF.

Le bouton `Bilan Excel` te demande aussi le dossier de sortie, puis cree `Bilan activite application YYYY.xlsx`.
La creation et la restauration d'une sauvegarde ZIP sont regroupees dans l'onglet `Base de donnees`, qui affiche le compte concerne et la base actuellement utilisee.
Au premier lancement, apres l'import d'une base ou apres la creation d'un compte, l'assistant demande un seul dossier principal. Easy CESU y cree automatiquement des sous-dossiers separes pour la base, les notes et les exports de ce compte. Dans `Reglages`, le bouton `Choisir un dossier principal` permet de relancer cet assistant. Les emplacements restent modifiables individuellement dans les reglages avances.

## Creer un compte pour une autre personne

Va dans `Reglages`, clique sur `Nouveau compte`, remplis le nom du compte, l'identite a afficher sur les notes, le tarif par defaut, les sources et les dossiers souhaites, puis clique sur `Creer le compte`.

Chaque compte a ses propres clients, interventions et tarifs individuels. Les nouveaux comptes démarrent vides pour éviter de mélanger les clients de deux activités.

Pour revenir a un autre compte, utilise la liste `Compte` en haut de la page principale.

Easy CESU s'arrete automatiquement quelques secondes apres la fermeture du dernier onglet de l'application. Un simple rechargement de la page ne l'arrete pas.
Les autres projets ouverts dans Chrome restent independants : Easy CESU reconnait uniquement ses propres onglets et choisit automatiquement un autre port local si un projet utilise deja le port habituel.

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
systeme_notes_intervention\sorties\EasyCESU-Setup-x64-2.1.0.exe
```

Cet installateur contient Easy CESU et toutes ses dépendances. Il installe par défaut dans `C:\Program Files\Easy CESU`, permet de choisir un autre dossier, propose une icône selon le métier, crée les raccourcis Bureau/Menu Démarrer au choix et peut ouvrir la notice à la fin. Si tu gardes `Program Files`, Windows demandera une autorisation.
Si une version est deja installee, l'installateur le signale et propose soit de la remplacer, soit d'installer une copie en plus. Pour une mise a jour, il ferme automatiquement Easy CESU avant de remplacer les fichiers puis relance la nouvelle version si l'option est cochee.
La configuration et la base sont conservées dans `%LOCALAPPDATA%\EasyCESU` et ne sont pas remplacées lors d'une mise à jour.

L'installateur n'embarque pas ta base de donnees. Pour transmettre l'etat actuel a quelqu'un :

1. Sur ton PC, va dans `Base de donnees` > `Creer la sauvegarde`, puis choisis un dossier.
2. Donne a la personne `EasyCESU-Setup-x64-2.1.0.exe` et le fichier `.zip` cree.
3. Sur son PC, elle lance l'installateur, choisit le repertoire d'installation puis ouvre Easy CESU.
4. Au premier lancement, elle choisit `Restaurer une sauvegarde` et selectionne le fichier `.zip` recu.
5. L'assistant demande ensuite un seul dossier principal et cree automatiquement les dossiers de la base, des notes et des bilans Excel.

Dans `Options avancees`, le bouton `Utiliser une base sans la copier` sert plutot a travailler directement sur une base placee dans un dossier partage.

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
