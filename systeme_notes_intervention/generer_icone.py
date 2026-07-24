from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RACINE = Path(__file__).resolve().parent
SOURCE = RACINE / "application" / "assets" / "easy-cesu-icon-transparent.png"
ICONE_PNG = RACINE / "application" / "assets" / "easy-cesu-icon.png"
ICONE_ICO = RACINE / "application" / "assets" / "easy-cesu.ico"
FAVICON_ICO = RACINE / "application" / "static" / "favicon.ico"
ICONES_METIER = RACINE / "application" / "assets" / "shortcut-icons"
ICONES_INTERFACE = RACINE / "application" / "static" / "icons"
TAILLES_WINDOWS = (16, 20, 24, 32, 40, 48, 64, 128, 256)
METIERS = (
    "generique",
    "bricolage",
    "menage",
    "aide_a_domicile",
    "garde_d_enfants",
    "soutien_scolaire",
    "accompagnement",
    "assistance_administrative",
    "informatique",
)


def preparer_icone() -> Image.Image:
    """Recadre le dessin et conserve une marge stable autour de l'embleme."""
    with Image.open(SOURCE) as image_source:
        image = image_source.convert("RGBA")

    limites = image.getchannel("A").getbbox()
    if limites is None:
        raise RuntimeError("L'image source ne contient aucun pixel visible.")

    embleme = image.crop(limites)
    canevas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

    # Une marge de 6 % evite que Windows coupe le contour blanc dans les petites tailles.
    taille_maximale = round(1024 * 0.88)
    ratio = min(taille_maximale / embleme.width, taille_maximale / embleme.height)
    dimensions = (
        max(1, round(embleme.width * ratio)),
        max(1, round(embleme.height * ratio)),
    )
    embleme = embleme.resize(dimensions, Image.Resampling.LANCZOS)
    position = ((1024 - embleme.width) // 2, (1024 - embleme.height) // 2)
    canevas.alpha_composite(embleme, position)
    return canevas


def police(taille: int, *, gras: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Utilise une police Windows stable, avec un repli portable pour les builds."""
    dossier = Path(r"C:\Windows\Fonts")
    candidats = ["segoeuib.ttf", "arialbd.ttf"] if gras else ["segoeui.ttf", "arial.ttf"]
    for nom in candidats:
        chemin = dossier / nom
        if chemin.exists():
            return ImageFont.truetype(str(chemin), taille)
    return ImageFont.load_default()


def coeur_points(centre_x: int, centre_y: int, taille: int) -> list[tuple[int, int]]:
    return [
        (centre_x, centre_y + taille),
        (centre_x - taille, centre_y),
        (centre_x - taille, centre_y - taille // 2),
        (centre_x - taille // 2, centre_y - taille),
        (centre_x, centre_y - taille // 2),
        (centre_x + taille // 2, centre_y - taille),
        (centre_x + taille, centre_y - taille // 2),
        (centre_x + taille, centre_y),
    ]


def dessiner_pictogramme(draw: ImageDraw.ImageDraw, metier: str) -> None:
    blanc = "#ffffff"
    trait = 48
    if metier == "bricolage":
        draw.line((260, 650, 650, 260), fill=blanc, width=70)
        draw.rounded_rectangle((208, 590, 330, 710), radius=28, fill=blanc)
        draw.rounded_rectangle((555, 205, 725, 330), radius=24, fill=blanc)
        draw.line((255, 280, 635, 660), fill=blanc, width=50)
        draw.polygon([(195, 210), (360, 240), (300, 355)], fill=blanc)
    elif metier == "menage":
        draw.line((610, 180, 365, 650), fill=blanc, width=55)
        draw.polygon([(220, 625), (470, 560), (550, 720), (255, 740)], fill=blanc)
        draw.line((260, 650, 490, 605), fill="#17484f", width=18)
        draw.ellipse((215, 260, 275, 320), fill=blanc)
        draw.ellipse((300, 180, 385, 265), fill=blanc)
    elif metier == "aide_a_domicile":
        draw.polygon([(180, 420), (455, 190), (730, 420)], outline=blanc, width=55)
        draw.rounded_rectangle((250, 390, 660, 720), radius=28, outline=blanc, width=55)
        draw.polygon(coeur_points(455, 520, 105), fill="#f4b860")
    elif metier == "garde_d_enfants":
        draw.ellipse((190, 230, 455, 495), outline=blanc, width=48)
        draw.ellipse((470, 315, 690, 535), outline=blanc, width=44)
        draw.ellipse((275, 325, 300, 350), fill=blanc)
        draw.ellipse((345, 325, 370, 350), fill=blanc)
        draw.arc((255, 330, 400, 430), 20, 160, fill=blanc, width=22)
        draw.arc((520, 390, 640, 480), 20, 160, fill=blanc, width=20)
        draw.arc((165, 470, 475, 760), 195, 345, fill=blanc, width=52)
        draw.arc((440, 500, 725, 760), 195, 345, fill=blanc, width=48)
    elif metier == "soutien_scolaire":
        draw.polygon([(160, 275), (430, 330), (430, 700), (160, 620)], fill=blanc)
        draw.polygon([(450, 330), (720, 275), (720, 620), (450, 700)], fill=blanc)
        draw.line((440, 330, 440, 700), fill="#17484f", width=22)
        for y in (390, 465, 540):
            draw.line((215, y, 375, y + 28), fill="#17484f", width=16)
            draw.line((505, y + 28, 665, y), fill="#17484f", width=16)
    elif metier == "accompagnement":
        draw.ellipse((180, 210, 365, 395), fill=blanc)
        draw.ellipse((505, 210, 690, 395), fill=blanc)
        draw.arc((105, 355, 445, 735), 190, 350, fill=blanc, width=65)
        draw.arc((425, 355, 765, 735), 190, 350, fill=blanc, width=65)
        draw.line((340, 500, 530, 500), fill="#f4b860", width=46)
        draw.polygon([(540, 500), (475, 450), (475, 550)], fill="#f4b860")
    elif metier == "assistance_administrative":
        draw.rounded_rectangle((205, 170, 680, 735), radius=28, fill=blanc)
        draw.polygon([(555, 170), (680, 295), (555, 295)], fill="#d9ecf0")
        for y in (380, 470, 560, 650):
            draw.line((360, y, 600, y), fill="#17484f", width=22)
        draw.line((260, 375, 290, 410, 335, 350), fill="#f4b860", width=24, joint="curve")
        draw.line((260, 555, 290, 590, 335, 530), fill="#f4b860", width=24, joint="curve")
    elif metier == "informatique":
        draw.rounded_rectangle((165, 215, 715, 610), radius=30, outline=blanc, width=52)
        draw.rectangle((225, 275, 655, 550), fill="#d9ecf0")
        draw.polygon([(115, 650), (765, 650), (695, 735), (185, 735)], fill=blanc)
        draw.rounded_rectangle((355, 665, 525, 700), radius=15, fill="#17484f")
    else:
        draw.ellipse((175, 180, 380, 385), fill=blanc)
        draw.ellipse((500, 180, 705, 385), fill=blanc)
        draw.arc((105, 335, 450, 735), 190, 350, fill=blanc, width=65)
        draw.arc((430, 335, 775, 735), 190, 350, fill=blanc, width=65)
        draw.polygon(coeur_points(440, 490, 110), fill="#f4b860")


def creer_icone_metier(metier: str) -> Image.Image:
    """Crée un badge métier simple qui reste identifiable dans un petit raccourci."""
    image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((78, 90, 888, 900), fill=(10, 35, 39, 70))
    draw.ellipse((62, 54, 872, 864), fill="#178d95", outline="#ffffff", width=38)
    draw.ellipse((112, 104, 822, 814), outline="#0d666d", width=25)
    dessiner_pictogramme(draw, metier)

    # La pièce commune rappelle clairement le suivi de rémunération CESU.
    draw.ellipse((610, 610, 975, 975), fill="#ffc83d", outline="#ffffff", width=28)
    draw.ellipse((650, 650, 935, 935), outline="#d79d42", width=25)
    draw.text((792, 785), "€", font=police(215), fill="#ffffff", anchor="mm", stroke_width=6, stroke_fill="#d79d42")
    return image


def generer_icones_metier(icone_jardinage: Image.Image) -> None:
    ICONES_METIER.mkdir(parents=True, exist_ok=True)
    ICONES_INTERFACE.mkdir(parents=True, exist_ok=True)
    jardinage_png = ICONES_METIER / "jardinage.png"
    jardinage_ico = ICONES_METIER / "jardinage.ico"
    icone_jardinage.save(jardinage_png, format="PNG", optimize=True)
    apercu_jardinage = icone_jardinage.resize((64, 64), Image.Resampling.LANCZOS)
    apercu_jardinage.save(ICONES_METIER / "jardinage-preview.png", format="PNG", optimize=True)
    apercu_jardinage.save(ICONES_INTERFACE / "jardinage.png", format="PNG", optimize=True)
    icone_jardinage.save(jardinage_ico, format="ICO", sizes=[(taille, taille) for taille in TAILLES_WINDOWS])

    for metier in METIERS:
        image = creer_icone_metier(metier)
        image.save(ICONES_METIER / f"{metier}.png", format="PNG", optimize=True)
        apercu = image.resize((64, 64), Image.Resampling.LANCZOS)
        apercu.save(ICONES_METIER / f"{metier}-preview.png", format="PNG", optimize=True)
        apercu.save(ICONES_INTERFACE / f"{metier}.png", format="PNG", optimize=True)
        image.save(
            ICONES_METIER / f"{metier}.ico",
            format="ICO",
            sizes=[(taille, taille) for taille in TAILLES_WINDOWS],
        )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Image source introuvable : {SOURCE}")

    icone = preparer_icone()
    ICONE_PNG.parent.mkdir(parents=True, exist_ok=True)
    FAVICON_ICO.parent.mkdir(parents=True, exist_ok=True)

    icone.save(ICONE_PNG, format="PNG", optimize=True)
    icone.save(ICONE_ICO, format="ICO", sizes=[(taille, taille) for taille in TAILLES_WINDOWS])
    FAVICON_ICO.write_bytes(ICONE_ICO.read_bytes())
    generer_icones_metier(icone)

    print(f"Icone PNG : {ICONE_PNG}")
    print(f"Icone Windows : {ICONE_ICO}")
    print(f"Favicon : {FAVICON_ICO}")
    print(f"Icones metier : {ICONES_METIER}")


if __name__ == "__main__":
    main()
