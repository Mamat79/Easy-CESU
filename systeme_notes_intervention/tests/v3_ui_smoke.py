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
        page.locator('[data-view="templates"]').click()
        page.locator("#templatePaper").wait_for(state="visible")
        if page.locator("#templateTitleInput").input_value() != "RELEVÉ DES PRESTATIONS":
            raise AssertionError("Le modèle enregistré n'est pas rechargé.")

        page.set_viewport_size({"width": 1024, "height": 768})
        page.screenshot(path=str(OUTPUT_DIR / "templates-compact.png"))
        if page.locator("body").evaluate("(element) => element.scrollWidth > element.clientWidth + 2"):
            raise AssertionError("L'éditeur crée un débordement horizontal à 1024 px.")
        browser.close()

    if console_errors:
        raise AssertionError("Erreurs JavaScript : " + " | ".join(console_errors))
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
