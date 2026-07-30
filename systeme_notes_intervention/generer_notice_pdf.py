"""Génère la notice PDF générique distribuée avec Easy CESU."""

from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
APP_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUTPUT_PDF = ROOT / "output" / "pdf" / "Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"
SORTIES_PDF = ROOT / "sorties" / "Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"

TEAL = colors.HexColor("#17484F")
TEAL_SOFT = colors.HexColor("#E5F0F2")
AMBER = colors.HexColor("#F4B860")
INK = colors.HexColor("#102023")
MUTED = colors.HexColor("#52666B")
LINE = colors.HexColor("#CFDADD")
WHITE = colors.white


def section(number: str, title: str, lines: list[str], styles: dict[str, ParagraphStyle]) -> KeepTogether:
    body = [Paragraph(title, styles["section_title"])]
    for line in lines:
        body.append(Paragraph(f"- {line}", styles["step"]))
    content = Table([[item] for item in body], colWidths=[154 * mm])
    content.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.1 * mm),
            ]
        )
    )
    number_box = Table([[Paragraph(number, styles["number"]) ]], colWidths=[11 * mm], rowHeights=[11 * mm])
    number_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), TEAL),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0, TEAL),
            ]
        )
    )
    table = Table([[number_box, content]], colWidths=[15 * mm, 154 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return KeepTogether([table, Spacer(1, 1.2 * mm)])


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 9 * mm, f"Easy CESU V{APP_VERSION} - Notice d'installation et d'utilisation")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def build_notice(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    sample = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=26,
            textColor=TEAL,
            spaceAfter=1.5 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=MUTED,
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=INK,
            spaceAfter=1.3 * mm,
        ),
        "step": ParagraphStyle(
            "Step",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=INK,
            leftIndent=3 * mm,
            firstLineIndent=-3 * mm,
            spaceAfter=0.7 * mm,
        ),
        "number": ParagraphStyle(
            "Number",
            parent=sample["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=14,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "box_title": ParagraphStyle(
            "BoxTitle",
            parent=sample["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=TEAL,
            spaceAfter=1.2 * mm,
        ),
        "box": ParagraphStyle(
            "Box",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12,
            textColor=INK,
            spaceAfter=0.7 * mm,
        ),
    }

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=19 * mm,
        title=f"Easy CESU V{APP_VERSION} - Notice d'installation et d'utilisation",
        author="Easy CESU",
        subject="Installer Easy CESU et récupérer une base de données",
    )

    story = [
        Paragraph("Easy CESU", styles["title"]),
        Paragraph("Installer l'application, personnaliser et envoyer les notes, retrouver une sauvegarde", styles["subtitle"]),
        Spacer(1, 5 * mm),
    ]

    files_box = Table(
        [
            [Paragraph("Les fichiers à conserver", styles["box_title"])],
            [
                Paragraph(
                    f"<b>EasyCESU-Setup-x64-{APP_VERSION}.exe</b> pour Windows<br/>"
                    f"<b>EasyCESU-macOS-Apple-Silicon-{APP_VERSION}.dmg</b> pour les Mac M1 et suivants<br/>"
                    f"<b>EasyCESU-macOS-Intel-{APP_VERSION}.dmg</b> pour les Mac Intel<br/>"
                    "<b>EasyCESU-....zip</b> pour récupérer un compte, les clients, les tarifs, les interventions, les rappels et les notes",
                    styles["box"],
                )
            ],
        ],
        colWidths=[169 * mm],
    )
    files_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), TEAL_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2 * mm),
            ]
        )
    )
    story.extend([files_box, Spacer(1, 5 * mm)])

    story.extend(
        [
            section(
                "1",
                "Installer Easy CESU",
                [
                    f"Sous Windows, double-cliquer sur <b>EasyCESU-Setup-x64-{APP_VERSION}.exe</b>, puis choisir le dossier, l'icône et les raccourcis.",
                    "Sous macOS, ouvrir le DMG correspondant au processeur du Mac puis glisser Easy CESU dans Applications.",
                    "Au premier lancement sur Mac, faire un clic droit sur Easy CESU puis choisir Ouvrir si macOS signale un développeur non identifié.",
                    "Lors d'une mise à jour, choisir <b>Oui</b> pour remplacer la version existante : l'installateur ferme l'ancienne version automatiquement.",
                    "Easy CESU s'ouvre ensuite dans sa propre fenêtre. Aucun onglet Chrome n'est nécessaire.",
                ],
                styles,
            ),
            section(
                "2",
                "Restaurer les données",
                [
                    "Au premier lancement, choisir <b>Restaurer une sauvegarde</b>, ou ouvrir ensuite <b>Base de données</b>.",
                    "Choisir l'archive <b>.zip</b> reçue. Les clients, tarifs, interventions et rappels sont rechargés.",
                    "Easy CESU vérifie l'archive et crée une sauvegarde de précaution avant une restauration sur un compte existant.",
                ],
                styles,
            ),
            section(
                "3",
                "Configurer le profil et les dossiers",
                [
                    "Au premier lancement, suivre les cinq étapes : restauration éventuelle, nom, activité, dossier principal et sauvegarde.",
                    "Choisir une activité (jardinage, ménage, bricolage, aide à domicile, informatique ou autre) adapte les exemples sans bloquer les autres prestations.",
                    "Easy CESU y crée automatiquement des sous-dossiers séparés pour la base, les notes et les exports.",
                    "Ce choix reste modifiable dans <b>Réglages</b> avec <b>Choisir un dossier principal</b>.",
                ],
                styles,
            ),
            section(
                "4",
                "Saisir et suivre l'activité",
                [
                    "Créer les clients dans <b>Clients</b>, puis saisir les interventions. Le tarif individuel d'un client reste prioritaire sur le tarif général.",
                    "Les grands boutons moins et plus règlent la durée par 30 minutes et les tarifs ou montants par 0,50 euro. La saisie directe reste possible.",
                    "Utiliser l'onglet <b>Notes et paiements</b> pour ajouter une note à faire ou créer explicitement un paiement en attente.",
                    "Une note ne modifie jamais un paiement automatiquement. Cliquer sur <b>Reçu</b> uniquement lorsque le paiement est effectivement reçu.",
                ],
                styles,
            ),
            section(
                "5",
                "Créer un modèle de note",
                [
                    "Ouvrir <b>Modèles</b>, puis choisir le modèle à modifier ou cliquer sur <b>Nouveau</b>.",
                    "Modifier les textes, couleurs, marges et tailles. L'aperçu A4 se met à jour immédiatement.",
                    "Utiliser les flèches pour réorganiser l'identité, le titre et le tableau, puis cliquer sur <b>Enregistrer</b>.",
                    "Cocher <b>Utiliser ce modèle</b> pour qu'il soit appliqué aux prochaines notes. Le bouton <b>PDF d'essai</b> permet de contrôler le résultat final.",
                ],
                styles,
            ),
            section(
                "6",
                "Envoyer les notes par email",
                [
                    "Dans <b>Réglages &gt; Envoi des notes par email</b>, renseigner le serveur SMTP, l'adresse d'expédition et le mot de passe demandé par le fournisseur de messagerie.",
                    "Le mot de passe reste dans le coffre sécurisé de l'ordinateur. Il n'est pas placé dans la base ni dans une sauvegarde transférée.",
                    "Personnaliser l'objet et le texte avec les champs {client}, {mois}, {annee}, {heures}, {montant} et {nom}.",
                    "Dans chaque fiche client, choisir si le client doit être sélectionné par défaut et si son mail doit être relu avant l'envoi.",
                    "Cliquer sur <b>Envoyer les notes</b>, vérifier les cases du tableau, modifier les mails signalés puis valider. Aucun mail n'est envoyé automatiquement.",
                ],
                styles,
            ),
            section(
                "7",
                "Sauvegarder ou transférer les données",
                [
                    "Sélectionner le bon compte en haut de la page.",
                    "Aller dans <b>Base de données</b>, cliquer sur <b>Créer la sauvegarde</b>, puis choisir un dossier.",
                    "Conserver le fichier <b>.zip</b> obtenu ou le transmettre avec l'installateur à un autre ordinateur.",
                ],
                styles,
            ),
        ]
    )

    story.extend(
        [
            section(
                "8",
                "Mettre à jour sans perdre les données",
                [
                    "Fermer Easy CESU, puis lancer le nouvel installateur.",
                    "Quand une version existante est détectée, choisir <b>Oui : remplacer / mettre à jour</b> et conserver le dossier proposé.",
                    "Le programme est remplacé, mais la configuration et la base restent dans le dossier de données de l'utilisateur.",
                    "Aucune restauration n'est nécessaire pour une simple mise à jour.",
                ],
                styles,
            ),
            section(
                "9",
                "Choisir l'icône selon le métier",
                [
                    "Sous Windows, choisir l'icône souhaitée dans l'installateur avant de créer les raccourcis.",
                    "L'icône Jardinage d'origine reste disponible, ainsi que les icônes ménage, bricolage, aide à domicile, garde d'enfants, soutien scolaire, accompagnement, administratif, informatique et générique.",
                    "Le choix peut aussi être mémorisé dans <b>Réglages &gt; Icône des raccourcis</b> pour la prochaine mise à jour.",
                ],
                styles,
            ),
            section(
                "10",
                "Bonnes pratiques de sauvegarde",
                [
                    "Créer régulièrement une sauvegarde ZIP dans un dossier différent de celui de la base.",
                    "Conserver plusieurs sauvegardes datées et vérifier qu'au moins une copie se trouve sur un autre disque ou un espace synchronisé.",
                    "Ne jamais partager la même base ouverte simultanément sur deux ordinateurs.",
                ],
                styles,
            ),
            Spacer(1, 7 * mm),
            section(
                "11",
                "Aide et communauté",
                [
                    "Ouvrir <b>Réglages &gt; Aide et communauté</b> pour consulter le code, la documentation ou signaler un problème sur le dépôt public Easy CESU.",
                    "Le soutien PayPal est entièrement facultatif. La fenêtre affiche un QR code à scanner avec l'application PayPal du téléphone et un bouton PayPal.Me utilisable sur ordinateur. Il ne débloque aucune fonction, ne crée aucun abonnement et peut être ignoré sans limiter l'application.",
                    "Le rappel de soutien apparaît au maximum une fois par trimestre et peut être désactivé définitivement dans les réglages.",
                ],
                styles,
            ),
        ]
    )

    reminder = Table(
        [
            [Paragraph("À retenir", styles["box_title"])],
            [
                Paragraph(
                    "Chaque compte possède ses propres clients, tarifs et interventions. "
                    "L'installateur ne contient aucune donnée personnelle. Easy CESU est un outil indépendant de suivi d'activité, sans lien automatique avec le service officiel CESU. "
                    "Easy CESU s'arrête automatiquement lorsque sa fenêtre est fermée. Le projet reste gratuit et open source.",
                    styles["box"],
                )
            ],
        ],
        colWidths=[169 * mm],
    )
    reminder.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4E2")),
                ("BOX", (0, 0), (-1, -1), 0.8, AMBER),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    story.append(KeepTogether([reminder]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    build_notice(OUTPUT_PDF)
    SORTIES_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_PDF, SORTIES_PDF)
    print(SORTIES_PDF)


if __name__ == "__main__":
    main()
