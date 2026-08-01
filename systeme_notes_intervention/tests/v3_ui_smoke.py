from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "tmp" / "v3-ui"
URL = os.environ.get("EASY_CESU_UI_URL", "http://127.0.0.1:8875")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not chrome.exists():
        raise RuntimeError("Google Chrome est introuvable pour le contrôle visuel.")

    console_errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(chrome), headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
        page.on("pageerror", lambda error: console_errors.append(str(error)))
        page.goto(URL, wait_until="domcontentloaded")
        page.locator("#statusLine").wait_for()
        page.wait_for_timeout(1000)
        if page.locator("#setupAssistantDialog").is_visible():
            page.locator("#setupAssistantLaterBtn").click()
        page.locator("#yearFilter").fill("2026")
        page.locator("#yearFilter").dispatch_event("change")
        page.locator("#monthFilter").select_option("7")
        page.wait_for_function("document.querySelectorAll('#interventionsBody tr').length === 3")

        status_headers = page.locator(".interventions-table thead .status-col").all_inner_texts()
        if status_headers != ["Transmis", "Déclaré", "Payé"]:
            raise AssertionError(f"Ordre inattendu des états administratifs : {status_headers}")
        if page.locator("#interventionsBody tr").count() != 3:
            raise AssertionError("La liste principale ne reprend pas les trois interventions de contrôle.")
        page.screenshot(path=str(OUTPUT_DIR / "interventions-desktop.png"), full_page=True)

        dupont_row = page.locator("#interventionsBody tr", has_text="M. Dupont")
        dupont_declared = dupont_row.locator('[data-administrative-status="declared"]')
        if dupont_declared.is_checked():
            raise AssertionError("L'intervention de contrôle doit commencer non déclarée.")
        dupont_declared.click()
        page.wait_for_function(
            "document.querySelector('#interventionsBody tr:nth-child(2) [data-administrative-status=declared]').checked === true"
        )
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(600)
        if page.locator("#setupAssistantDialog").is_visible():
            page.locator("#setupAssistantLaterBtn").click()
        page.locator("#yearFilter").fill("2026")
        page.locator("#yearFilter").dispatch_event("change")
        page.locator("#monthFilter").select_option("7")
        page.wait_for_function("document.querySelectorAll('#interventionsBody tr').length === 3")
        dupont_declared = page.locator("#interventionsBody tr", has_text="M. Dupont").locator('[data-administrative-status="declared"]')
        if not dupont_declared.is_checked():
            raise AssertionError("L'état déclaré n'est pas conservé après rechargement.")
        dupont_declared.click()
        page.wait_for_function(
            "document.querySelector('#interventionsBody tr:nth-child(2) [data-administrative-status=declared]').checked === false"
        )

        page.locator('[data-view="followup"]').click()
        page.locator("#interventionFollowupsBody").wait_for(state="visible")
        if page.locator("#interventionFollowupsBody tr").count() != 2:
            raise AssertionError("Le tableau À suivre doit afficher deux interventions incomplètes, une seule fois chacune.")
        page.screenshot(path=str(OUTPUT_DIR / "followup-desktop.png"), full_page=True)

        page.locator("#followupTypeFilter").select_option("paid")
        page.wait_for_function("document.querySelectorAll('#interventionFollowupsBody tr').length === 1")
        if "Mme Martin" not in page.locator("#interventionFollowupsBody").inner_text():
            raise AssertionError("Le filtre À payer n'affiche pas l'intervention attendue.")
        page.locator("#followupTypeFilter").select_option("")
        page.locator("#followupSearchInput").fill("Dupont")
        page.wait_for_timeout(500)
        if page.locator("#interventionFollowupsBody tr").count() != 1:
            raise AssertionError("La recherche par client ne filtre pas le tableau À suivre.")
        page.locator("#followupSearchInput").fill("")
        page.wait_for_timeout(500)

        martin_row = page.locator("#interventionFollowupsBody tr", has_text="Mme Martin")
        martin_row.locator('[data-ignore-followup][data-reminder-type="transmitted"]').click()
        page.wait_for_timeout(400)
        page.locator("#followupShowIgnoredInput").check()
        page.wait_for_timeout(400)
        martin_row = page.locator("#interventionFollowupsBody tr", has_text="Mme Martin")
        if "Transmission ignoré" not in martin_row.inner_text():
            raise AssertionError("Le rappel ignoré n'est pas visible sur demande.")
        martin_row.locator('[data-reactivate-followup][data-reminder-type="transmitted"]').click()
        page.wait_for_timeout(400)
        martin_row = page.locator("#interventionFollowupsBody tr", has_text="Mme Martin")
        if "À transmettre" not in martin_row.inner_text():
            raise AssertionError("Le rappel réactivé ne réapparaît pas immédiatement.")

        page.locator('[data-view="templates"]').click()
        page.locator("#templatePaper").wait_for(state="visible")
        page.wait_for_function("document.querySelectorAll('#templateSelect option').length > 0")
        page.screenshot(path=str(OUTPUT_DIR / "templates-desktop.png"))

        paper_box = page.locator("#templatePaper").bounding_box()
        stage_box = page.locator(".template-paper-stage").bounding_box()
        if not paper_box or not stage_box or paper_box["width"] <= 400 or paper_box["height"] <= 550:
            raise AssertionError("L'aperçu A4 n'a pas une taille exploitable.")
        if paper_box["x"] < stage_box["x"] or paper_box["x"] + paper_box["width"] > stage_box["x"] + stage_box["width"] + 1:
            raise AssertionError("L'aperçu A4 déborde horizontalement de sa zone.")

        page.locator(".template-controls summary", has_text="Textes affichés").click()
        page.locator("#templateTitleInput").fill("RELEVÉ DES PRESTATIONS")
        page.locator(".template-controls summary", has_text="Texte et couleurs").click()
        page.locator("#templateHeaderColorInput").fill("#d9ecf0")
        page.locator("#templateTitleSizeInput").fill("15")
        if page.locator("#templateUnsavedBadge").is_hidden():
            raise AssertionError("L'état non enregistré n'est pas signalé.")
        if "RELEVÉ DES PRESTATIONS" not in page.locator("#templatePaper").inner_text():
            raise AssertionError("Le titre modifié n'apparaît pas dans l'aperçu.")

        page.locator("#templateSaveBtn").click()
        page.wait_for_function("document.querySelector('#templateUnsavedBadge').hidden === true")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        if page.locator("#setupAssistantDialog").is_visible():
            page.locator("#setupAssistantLaterBtn").click()
        page.locator("#yearFilter").fill("2026")
        page.locator("#yearFilter").dispatch_event("change")
        page.locator("#monthFilter").select_option("7")
        page.wait_for_function("document.querySelectorAll('#interventionsBody tr').length === 3")
        page.locator('[data-view="templates"]').click()
        page.locator("#templatePaper").wait_for(state="visible")
        page.wait_for_function("document.querySelectorAll('#templateSelect option').length > 0")
        if page.locator("#templateTitleInput").input_value() != "RELEVÉ DES PRESTATIONS":
            raise AssertionError("Le modèle enregistré n'est pas rechargé.")

        page.locator('[data-view="settings"]').click()
        page.locator("#communityTitle").wait_for(state="visible")
        page.locator(".email-settings summary").click()
        page.locator("#smtpHostInput").wait_for(state="visible")
        if page.locator("#smtpHostInput").input_value() != "smtp.example.test":
            raise AssertionError("La configuration email du compte n'est pas chargée.")
        page.screenshot(path=str(OUTPUT_DIR / "email-settings-desktop.png"), full_page=True)

        page.locator("#emailNotesBtn").click()
        page.locator("#emailNotesDialog").wait_for(state="visible")
        if page.locator("#emailRecipientsBody tr").count() != 3:
            raise AssertionError("La liste d'envoi ne reprend pas les trois clients du mois.")
        if page.locator('[data-email-client="Mme Bernard"]').is_enabled():
            raise AssertionError("Un client sans adresse email ne doit pas être sélectionnable.")
        page.screenshot(path=str(OUTPUT_DIR / "email-recipients-desktop.png"))
        page.locator("#emailNotesSendBtn").click()
        page.locator("#emailReviewDialog").wait_for(state="visible")
        if "M. Dupont" not in page.locator("#emailReviewClient").inner_text():
            raise AssertionError("Le client marqué pour relecture n'ouvre pas l'éditeur.")
        page.screenshot(path=str(OUTPUT_DIR / "email-review-desktop.png"))
        page.locator("#emailReviewCancelBtn").click()

        if not page.locator("#supportReminderEnabledInput").is_checked():
            raise AssertionError("Le rappel discret doit être activé par défaut.")
        if page.locator("#supportReminder").is_visible():
            raise AssertionError("Le rappel de soutien ne doit pas apparaître avant 30 jours.")
        page.screenshot(path=str(OUTPUT_DIR / "community-desktop.png"), full_page=True)

        page.set_viewport_size({"width": 1024, "height": 768})
        page.screenshot(path=str(OUTPUT_DIR / "community-compact.png"), full_page=True)
        page.locator('[data-view="followup"]').click()
        page.screenshot(path=str(OUTPUT_DIR / "followup-compact.png"), full_page=True)
        if page.locator("body").evaluate("(element) => element.scrollWidth > element.clientWidth + 2"):
            raise AssertionError("L'interface crée un débordement horizontal à 1024 px.")
        browser.close()

    if console_errors:
        raise AssertionError("Erreurs JavaScript : " + " | ".join(console_errors))
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
