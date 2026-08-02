from __future__ import annotations

import html
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


LEGAL_INFORMATION_VERIFIED_ON = "2026-08-03"
CESU_CONTRACT_END_URL = (
    "https://www.cesu.urssaf.fr/info/accueil/gerer-la-relation-de-travail/"
    "la-fin-du-contrat-de-travail-et/comment-gerer-une-fin-de-contrat.html"
)
CESU_DOCUMENTS_URL = (
    "https://www.cesu.urssaf.fr/info/accueil/gerer-la-relation-de-travail/"
    "la-fin-du-contrat-de-travail-et/quels-sont-les-documents-a-remet/"
    "col-principale/quels-sont-les-documents-a-remet.html"
)
FRANCE_TRAVAIL_URL = (
    "https://www.francetravail.fr/employeur/vous-etes-un-particulier-employe/"
    "vous-cessez-demployer-a-domicile/comment-saisir-en-ligne-lattesta.html"
)


REASON_LABELS = {
    "licenciement": "Licenciement à l'initiative du particulier employeur",
    "demission": "Démission du salarié",
    "rupture_conventionnelle": "Rupture conventionnelle",
    "fin_cdd": "Fin de contrat à durée déterminée",
    "retraite": "Départ ou mise à la retraite",
    "deces_employeur": "Décès du particulier employeur",
    "autre": "Autre situation",
}

NOTICE_LABELS = {
    "effectue": "Préavis effectué",
    "partiel": "Préavis partiellement effectué",
    "non_effectue_employeur": "Préavis non effectué à la demande de l'employeur",
    "non_effectue_salarie": "Préavis non effectué à la demande du salarié",
    "non_applicable": "Pas de préavis",
    "a_verifier": "Situation du préavis à vérifier",
}


def _text(value: object, fallback: str = "Non renseigné") -> str:
    cleaned = str(value or "").strip()
    return cleaned or fallback


def _html(value: object, fallback: str = "Non renseigné") -> str:
    return html.escape(_text(value, fallback)).replace("\n", "<br/>")


def _date_label(value: object) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Non renseignée"
    try:
        return datetime.fromisoformat(raw).strftime("%d/%m/%Y")
    except ValueError:
        return raw


def _hours_label(value: object) -> str:
    total_minutes = max(0, round(float(value or 0) * 60))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours} h {minutes:02d}" if minutes else f"{hours} h"


def _money_label(value: object) -> str:
    return f"{float(value or 0):,.2f} €".replace(",", " ").replace(".", ",")


def _paragraph_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ContractTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=colors.HexColor("#18453B"),
            alignment=TA_LEFT,
            spaceAfter=4 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ContractSubtitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#9A4F12"),
            spaceAfter=6 * mm,
        ),
        "heading": ParagraphStyle(
            "ContractHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#18453B"),
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
        ),
        "body": ParagraphStyle(
            "ContractBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=colors.HexColor("#28322F"),
            spaceAfter=2 * mm,
        ),
        "small": ParagraphStyle(
            "ContractSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#4F5E59"),
        ),
        "table_header": ParagraphStyle(
            "ContractTableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "table": ParagraphStyle(
            "ContractTable",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9.2,
            textColor=colors.HexColor("#28322F"),
        ),
        "table_right": ParagraphStyle(
            "ContractTableRight",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9.2,
            textColor=colors.HexColor("#28322F"),
            alignment=TA_RIGHT,
        ),
        "check": ParagraphStyle(
            "ContractCheck",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            leftIndent=2 * mm,
            spaceAfter=1.5 * mm,
        ),
    }


def _footer(canvas: Canvas, doc: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#5A6863"))
    canvas.drawRightString(A4[0] - 18 * mm, 8.5 * mm, str(doc.page))
    canvas.restoreState()


def _summary_rows(interventions: Iterable[dict]) -> list[dict]:
    periods: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0, "hours": 0.0, "amount": 0.0})
    for item in interventions:
        period = str(item.get("date") or "")[:7]
        periods[period]["count"] += 1
        periods[period]["hours"] += float(item.get("duration_hours") or 0)
        periods[period]["amount"] += float(item.get("amount_net") or 0)
    return [
        {"period": period, **values}
        for period, values in sorted(periods.items())
        if period
    ]


def build_contract_end_pdf(
    output_path: Path,
    dossier: dict,
    interventions: list[dict],
    employee: dict,
    employer: dict,
) -> Path:
    """Produit une aide de préparation, jamais un document officiel de rupture."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = _paragraph_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="Easy CESU - Dossier préparatoire de fin de contrat",
        author="Easy CESU",
        subject="Récapitulatif de la relation de travail et démarches officielles à effectuer",
    )
    story: list[object] = []

    story.append(Paragraph("Dossier préparatoire de fin de contrat", styles["title"]))
    story.append(
        Paragraph(
            "Document d'aide à la préparation. Il ne remplace ni les documents officiels, "
            "ni les calculs réalisés depuis le compte employeur CESU.",
            styles["subtitle"],
        )
    )

    identity_data = [
        [Paragraph("Salarié(e)", styles["table_header"]), Paragraph("Particulier employeur", styles["table_header"])],
        [
            Paragraph(
                f"<b>{_html(employee.get('name'))}</b><br/>"
                f"{_html(employee.get('address'), '')}<br/>"
                f"{_html(employee.get('email'), '')}",
                styles["body"],
            ),
            Paragraph(
                f"<b>{_html(employer.get('name'))}</b><br/>"
                f"{_html(employer.get('address'), '')}<br/>"
                f"{_html(employer.get('email'), '')}<br/>"
                f"Numéro CESU : {_html(employer.get('cesu'))}",
                styles["body"],
            ),
        ],
    ]
    identity_table = Table(identity_data, colWidths=[82 * mm, 82 * mm])
    identity_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23665A")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#9CB8AF")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D5D0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    story.append(identity_table)

    story.append(Paragraph("Informations sur la fin de contrat", styles["heading"]))
    notice_period = "Non renseignée"
    if dossier.get("notice_start_date") or dossier.get("notice_end_date"):
        notice_period = f"{_date_label(dossier.get('notice_start_date'))} au {_date_label(dossier.get('notice_end_date'))}"
    contract_rows = [
        ["Type de contrat", str(dossier.get("contract_type") or "CDI").upper()],
        ["Motif indiqué", REASON_LABELS.get(str(dossier.get("reason") or "autre"), "Autre situation")],
        ["Date d'embauche", _date_label(dossier.get("contract_start_date"))],
        ["Date de notification", _date_label(dossier.get("notification_date"))],
        ["Préavis", NOTICE_LABELS.get(str(dossier.get("notice_status") or "a_verifier"), "À vérifier")],
        ["Période de préavis", notice_period],
        ["Dernier jour travaillé", _date_label(dossier.get("last_worked_date"))],
        ["Date de fin du contrat", _date_label(dossier.get("contract_end_date"))],
    ]
    contract_table = Table(contract_rows, colWidths=[52 * mm, 112 * mm])
    contract_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0ED")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D5D0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]
        )
    )
    story.append(contract_table)
    if str(dossier.get("notes") or "").strip():
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<b>Observations :</b> {_html(dossier.get('notes'))}", styles["body"]))

    total_hours = sum(float(item.get("duration_hours") or 0) for item in interventions)
    total_amount = sum(float(item.get("amount_net") or 0) for item in interventions)
    first_date = interventions[0].get("date") if interventions else ""
    last_date = interventions[-1].get("date") if interventions else ""
    story.append(Paragraph("Récapitulatif Easy CESU", styles["heading"]))
    totals = Table(
        [
            ["Interventions", "Heures enregistrées", "Montant net enregistré", "Période couverte"],
            [
                str(len(interventions)),
                _hours_label(total_hours),
                _money_label(total_amount),
                f"{_date_label(first_date)} au {_date_label(last_date)}" if interventions else "Aucune intervention",
            ],
        ],
        colWidths=[31 * mm, 39 * mm, 45 * mm, 49 * mm],
    )
    totals.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23665A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9CB8AF")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D5D0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    story.append(totals)
    story.append(
        Paragraph(
            "Ces chiffres proviennent uniquement des interventions présentes dans Easy CESU. "
            "Ils doivent être comparés aux déclarations et bulletins de salaire disponibles dans le compte CESU.",
            styles["small"],
        )
    )

    summary = _summary_rows(interventions)
    if summary:
        story.append(Paragraph("Totaux par mois", styles["heading"]))
        summary_data = [["Mois", "Interventions", "Heures", "Montant net"]]
        for item in summary:
            period_date = datetime.strptime(item["period"], "%Y-%m")
            summary_data.append(
                [
                    period_date.strftime("%m/%Y"),
                    str(int(item["count"])),
                    _hours_label(item["hours"]),
                    _money_label(item["amount"]),
                ]
            )
        summary_table = Table(summary_data, repeatRows=1, colWidths=[43 * mm, 39 * mm, 39 * mm, 43 * mm])
        summary_table.setStyle(_standard_table_style())
        story.append(summary_table)

    story.append(PageBreak())
    story.append(Paragraph("Détail des interventions enregistrées", styles["heading"]))
    detail_data = [
        [
            Paragraph("Date", styles["table_header"]),
            Paragraph("Travail réalisé", styles["table_header"]),
            Paragraph("Durée", styles["table_header"]),
            Paragraph("Tarif net/h", styles["table_header"]),
            Paragraph("Montant net", styles["table_header"]),
        ]
    ]
    for item in interventions:
        detail_data.append(
            [
                Paragraph(_date_label(item.get("date")), styles["table"]),
                Paragraph(_html(item.get("task"), "Intervention"), styles["table"]),
                Paragraph(_hours_label(item.get("duration_hours")), styles["table_right"]),
                Paragraph(_money_label(item.get("hourly_rate")), styles["table_right"]),
                Paragraph(_money_label(item.get("amount_net")), styles["table_right"]),
            ]
        )
    if len(detail_data) == 1:
        detail_data.append(["-", "Aucune intervention enregistrée", "-", "-", "-"])
    detail_table = Table(
        detail_data,
        repeatRows=1,
        colWidths=[24 * mm, 69 * mm, 22 * mm, 24 * mm, 27 * mm],
    )
    detail_table.setStyle(_standard_table_style())
    story.append(detail_table)

    story.append(PageBreak())
    story.append(Paragraph("Démarches à effectuer par le particulier employeur", styles["heading"]))
    story.append(
        Paragraph(
            "Pour un employeur adhérent au CESU, les démarches de fin de contrat sont à effectuer "
            "depuis la rubrique <b>Gérer une fin de contrat</b> de son compte employeur CESU.",
            styles["body"],
        )
    )
    checklist = [
        "Se connecter au compte employeur CESU et ouvrir « Gérer une fin de contrat ».",
        "Vérifier le motif, les dates du contrat, le préavis et le dernier jour travaillé.",
        "Comparer les interventions Easy CESU avec les déclarations et bulletins de salaire CESU.",
        "Réaliser la dernière déclaration et vérifier les sommes calculées par le service officiel.",
        "Régler le dernier salaire et les indemnités éventuellement dues selon le résultat officiel.",
        "Générer puis remettre le certificat de travail et le reçu pour solde de tout compte.",
        "Générer l'attestation employeur France Travail, la vérifier, la signer et en remettre un exemplaire au salarié.",
        "Conserver une copie des documents remis et la preuve de leur transmission.",
    ]
    for item in checklist:
        story.append(Paragraph(f"[ ] {item}", styles["check"]))

    story.append(Spacer(1, 3 * mm))
    documents = Table(
        [
            [Paragraph("Documents officiels à remettre", styles["table_header"])],
            [Paragraph("[ ] Certificat de travail", styles["body"])],
            [Paragraph("[ ] Reçu pour solde de tout compte", styles["body"])],
            [Paragraph("[ ] Attestation employeur France Travail", styles["body"])],
        ],
        colWidths=[164 * mm],
    )
    documents.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23665A")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#9CB8AF")),
                ("INNERGRID", (0, 1), (-1, -1), 0.35, colors.HexColor("#C8D5D0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    story.append(documents)

    story.append(Paragraph("Sources officielles", styles["heading"]))
    source_links = [
        ("Urssaf CESU - Gérer une fin de contrat", CESU_CONTRACT_END_URL),
        ("Urssaf CESU - Documents à remettre", CESU_DOCUMENTS_URL),
        ("France Travail - Attestation du particulier employeur", FRANCE_TRAVAIL_URL),
    ]
    for label, url in source_links:
        story.append(Paragraph(f'- <link href="{url}" color="#1F5E91">{label}</link>', styles["body"]))
    story.append(
        Paragraph(
            f"Informations réglementaires vérifiées le {_date_label(LEGAL_INFORMATION_VERIFIED_ON)}. "
            "Les règles pouvant évoluer, le particulier employeur doit toujours consulter les sources officielles au moment de la démarche.",
            styles["small"],
        )
    )

    warning = Table(
        [
            [Paragraph("Important", styles["table_header"])],
            [
                Paragraph(
                    "Easy CESU ne calcule pas l'indemnité de licenciement, l'indemnité de précarité, "
                    "les congés payés ou l'indemnité de préavis. Ces montants dépendent du contrat, du motif, "
                    "de l'ancienneté et de données de paie qui doivent être validées par le service officiel.",
                    styles["body"],
                )
            ],
        ],
        colWidths=[164 * mm],
    )
    warning.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A45417")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFF2E5")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C87831")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(KeepTogether([warning]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path


def _standard_table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23665A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D5D0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8F6")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 1.45 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.45 * mm),
        ]
    )
