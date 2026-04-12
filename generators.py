"""Generateurs PPTX et Excel pour les workflows PropTech.

Reproduit fidelement la structure des templates valides :
- Excel : Synthese financiere (2).xlsx — double colonne prix conservateur/cible
- PPTX : Gaillon_Investissement_25slides.pptx — dossier investissement pro

Usage:
    from generators import generate_dossier_pptx, generate_synthese_xlsx
    generate_synthese_xlsx(data, output_path="synthese.xlsx")
    generate_dossier_pptx(data, output_path="dossier.pptx")
"""

from __future__ import annotations
import os
from datetime import date


# ════════════════════════════════════════════════════
# STYLES PARTAGES
# ════════════════════════════════════════════════════

BLUE_HEX = "1E56A0"
DARK_HEX = "0D1117"
GREEN_HEX = "16A34A"
RED_HEX = "DC2626"
AMBER_HEX = "F59E0B"
LIGHT_BLUE_HEX = "EFF6FF"
MONEY_FMT = '#,##0 "€"'
PCT_FMT = '0.0%'


def _xl_styles():
    """Retourne les styles openpyxl pour le template."""
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    return {
        "title": Font(name="Calibri", size=14, bold=True, color=BLUE_HEX),
        "section": Font(name="Calibri", size=12, bold=True, color=BLUE_HEX),
        "header": Font(name="Calibri", size=10, bold=True, color="FFFFFF"),
        "header_fill": PatternFill(start_color=BLUE_HEX, end_color=BLUE_HEX, fill_type="solid"),
        "label": Font(name="Calibri", size=10, bold=True),
        "value": Font(name="Calibri", size=10),
        "total_font": Font(name="Calibri", size=11, bold=True, color=BLUE_HEX),
        "total_fill": PatternFill(start_color=LIGHT_BLUE_HEX, end_color=LIGHT_BLUE_HEX, fill_type="solid"),
        "green": Font(name="Calibri", size=10, bold=True, color=GREEN_HEX),
        "red": Font(name="Calibri", size=10, bold=True, color=RED_HEX),
        "border": Border(
            left=Side(style='thin', color="CCCCCC"),
            right=Side(style='thin', color="CCCCCC"),
            top=Side(style='thin', color="CCCCCC"),
            bottom=Side(style='thin', color="CCCCCC"),
        ),
        "center": Alignment(horizontal="center", vertical="center"),
    }


# ════════════════════════════════════════════════════
# EXCEL — SYNTHESE FINANCIERE (template fidele)
# ════════════════════════════════════════════════════

def generate_synthese_xlsx(data: dict, output_path: str = "synthese_financiere.xlsx") -> str:
    """Genere un Excel synthese financiere fidelement au template.

    Structure : Projet (lots avec prix conservateur/cible),
    Bilan (double colonne), Etude DVF, Etude Habitations, Comparables AVM.

    Args:
        data: dict avec cles: projet, lots, bilan, simulation, dvf, estimation
        output_path: chemin fichier sortie
    Returns: chemin absolu du fichier genere
    """
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    S = _xl_styles()

    projet = data.get("projet", {})
    lots = data.get("lots", [])
    bilan = data.get("bilan", {})
    simulation = data.get("simulation", {})
    dvf = data.get("dvf", [])
    estimation = data.get("estimation", {})

    prix = projet.get("prix", 0)
    ville = projet.get("ville", "")

    # ═══ ONGLET 1 : PROJET ═══
    ws = wb.active
    ws.title = "Projet"
    for col, w in [('B', 22), ('C', 8), ('D', 18), ('E', 15), ('F', 12),
                   ('G', 8), ('H', 10), ('I', 12), ('J', 14), ('K', 14),
                   ('L', 12), ('M', 14), ('N', 12)]:
        ws.column_dimensions[col].width = w

    # Info bien
    info = [
        ("Lien de l'annonce", projet.get("lien", "")),
        ("Ville", f"{ville} ({projet.get('code_postal', '')})"),
        ("Adresse", projet.get("adresse", "")),
        ("Prix annonce", prix),
        ("Surface totale", projet.get("surface", 0)),
        ("Surface habitable", projet.get("surface_habitable", projet.get("surface", 0))),
        ("Nombre de lots", projet.get("nb_lots", len(lots) or 1)),
    ]
    for i, (label, val) in enumerate(info, start=5):
        ws[f'B{i}'] = label
        ws[f'B{i}'].font = S["label"]
        ws[f'D{i}'] = val
        ws[f'D{i}'].font = S["value"]
        if isinstance(val, (int, float)) and val > 1000:
            ws[f'D{i}'].number_format = MONEY_FMT

    # Tableau lots avec DOUBLE prix
    row = 14
    ws[f'C{row}'] = "Detail des lots"
    ws[f'C{row}'].font = S["section"]
    ws[f'K{row}'] = "Revente Basse"
    ws[f'K{row}'].font = S["section"]
    ws[f'M{row}'] = "Revente Cible"
    ws[f'M{row}'].font = S["section"]

    row = 15
    headers_lot = ["Lot", "Etage", "Typologie", "Surface", "DPE", "Etat", "Loue/Vide", "Compteur", "Prix", "Prix/m2", "Prix", "Prix/m2"]
    cols_lot = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    for j, (col, h) in enumerate(zip(cols_lot, headers_lot)):
        ws[f'{col}{row}'] = h
        ws[f'{col}{row}'].font = S["header"]
        ws[f'{col}{row}'].fill = S["header_fill"]
        ws[f'{col}{row}'].alignment = S["center"]

    total_revente_basse = 0
    total_revente_cible = 0
    total_surface = 0

    for i, lot in enumerate(lots, start=16):
        ws[f'C{i}'] = lot.get("lot", i - 15)
        ws[f'D{i}'] = lot.get("etage", "RDC")
        ws[f'E{i}'] = lot.get("type", lot.get("typologie", ""))
        surface_lot = lot.get("surface", 0)
        ws[f'F{i}'] = surface_lot
        ws[f'G{i}'] = lot.get("dpe", "-")
        ws[f'H{i}'] = lot.get("etat", "Bon")
        ws[f'I{i}'] = lot.get("loue", "Vide")
        ws[f'J{i}'] = lot.get("compteur", "Oui")

        prix_bas = lot.get("prix_conservateur", lot.get("prix_revente", 0))
        prix_cible = lot.get("prix_cible", lot.get("prix_revente_cible", prix_bas * 1.2 if prix_bas else 0))

        ws[f'K{i}'] = prix_bas
        ws[f'K{i}'].number_format = MONEY_FMT
        ws[f'L{i}'] = round(prix_bas / surface_lot) if surface_lot else 0
        ws[f'M{i}'] = prix_cible
        ws[f'M{i}'].number_format = MONEY_FMT
        ws[f'N{i}'] = round(prix_cible / surface_lot) if surface_lot else 0

        total_revente_basse += prix_bas
        total_revente_cible += prix_cible
        total_surface += surface_lot

    # TOTAL
    row_total = 16 + len(lots)
    ws[f'C{row_total}'] = "TOTAL"
    ws[f'C{row_total}'].font = S["total_font"]
    ws[f'F{row_total}'] = total_surface
    ws[f'F{row_total}'].font = S["total_font"]
    ws[f'K{row_total}'] = total_revente_basse
    ws[f'K{row_total}'].number_format = MONEY_FMT
    ws[f'K{row_total}'].font = S["total_font"]
    ws[f'L{row_total}'] = round(total_revente_basse / total_surface) if total_surface else 0
    ws[f'L{row_total}'].font = S["total_font"]
    ws[f'M{row_total}'] = total_revente_cible
    ws[f'M{row_total}'].number_format = MONEY_FMT
    ws[f'M{row_total}'].font = S["total_font"]
    ws[f'N{row_total}'] = round(total_revente_cible / total_surface) if total_surface else 0
    ws[f'N{row_total}'].font = S["total_font"]

    # ═══ ONGLET 2 : BILAN (DOUBLE COLONNE) ═══
    ws2 = wb.create_sheet("Bilan")
    for col, w in [('B', 28), ('D', 16), ('I', 28), ('K', 16)]:
        ws2.column_dimensions[col].width = w

    frais_notaire = bilan.get("frais_notaire", round(prix * 0.03))
    travaux = bilan.get("travaux", 0)
    geometre = bilan.get("geometre", 0)
    diagnostics = bilan.get("diagnostics", 0)
    assurance_tf = bilan.get("assurance_tf", 0)
    honoraires = bilan.get("honoraires", 0)
    total_op = prix + honoraires + frais_notaire + travaux + geometre + diagnostics + assurance_tf

    bilan_lignes = [
        ("Prix du bien", prix),
        ("Honoraires d'Agence", honoraires),
        ("Frais d'acquisition (3%)", frais_notaire),
        ("Travaux", travaux),
        ("Geometre /Archi", geometre),
        ("Diagnotics & DTG", diagnostics),
        ("Assurances + Taxe Fonciere", assurance_tf),
    ]

    # Ecrire les 2 colonnes
    for side, col_label, col_val in [("gauche", "B", "D"), ("droite", "I", "K")]:
        label_col = col_label
        val_col = col_val

        ws2[f'{label_col}3'] = "RESUME DU PROJET"
        ws2[f'{label_col}3'].font = S["section"]

        for i, (label, val) in enumerate(bilan_lignes, start=4):
            ws2[f'{label_col}{i}'] = label
            ws2[f'{label_col}{i}'].font = S["label"] if i < 11 else S["value"]
            ws2[f'{val_col}{i}'] = val
            ws2[f'{val_col}{i}'].number_format = MONEY_FMT

        ws2[f'{label_col}11'] = "TOTAL OPERATION"
        ws2[f'{label_col}11'].font = S["total_font"]
        ws2[f'{val_col}11'] = total_op
        ws2[f'{val_col}11'].number_format = MONEY_FMT
        ws2[f'{val_col}11'].font = S["total_font"]

        # Revente
        ws2[f'{label_col}14'] = "REVENTE"
        ws2[f'{label_col}14'].font = S["section"]
        ws2[f'{label_col}15'] = "Prix de revente"

        revente = total_revente_basse if side == "gauche" else total_revente_cible
        ws2[f'{val_col}15'] = revente
        ws2[f'{val_col}15'].number_format = MONEY_FMT

        # Revenus locatifs
        revenus_loc = bilan.get("revenus_locatifs", 0)
        if revenus_loc:
            ws2[f'{label_col}16'] = "Revenus locatifs actuels"
            ws2[f'{val_col}16'] = f"{revenus_loc:,.0f} EUR/an"

        # Marge
        ws2[f'{label_col}17'] = "MARGE SUR COUT DE REVIENT"
        ws2[f'{label_col}17'].font = S["section"]

        marge = revente - total_op
        ws2[f'{label_col}18'] = "Benefice brut"
        ws2[f'{val_col}18'] = marge
        ws2[f'{val_col}18'].number_format = MONEY_FMT
        ws2[f'{val_col}18'].font = S["green"] if marge > 0 else S["red"]

        ws2[f'{label_col}19'] = "Marge brute"
        ws2[f'{val_col}19'] = marge / total_op if total_op else 0
        ws2[f'{val_col}19'].number_format = PCT_FMT
        ws2[f'{val_col}19'].font = S["green"] if marge > 0 else S["red"]

    # Labels colonnes
    ws2['B1'] = "PRIX CONSERVATEUR"
    ws2['B1'].font = S["title"]
    ws2['I1'] = "PRIX CIBLE"
    ws2['I1'].font = S["title"]

    # ═══ ONGLET 3 : ETUDE DVF ═══
    ws3 = wb.create_sheet("Etude DVF")
    for col, w in [('B', 35), ('C', 12), ('D', 14), ('E', 14), ('F', 12)]:
        ws3.column_dimensions[col].width = w

    ws3['D2'] = f"Etude de marche ville : {ville}"
    ws3['D2'].font = S["title"]

    # Segmentation par type
    types_seen = set()
    for tx in dvf:
        t = tx.get("type_local", tx.get("type", "Autre"))
        types_seen.add(t)

    row = 4
    for type_bien in sorted(types_seen):
        txs = [t for t in dvf if (t.get("type_local", t.get("type", "")) == type_bien)]
        if not txs:
            continue

        ws3[f'B{row}'] = type_bien
        ws3[f'B{row}'].font = S["section"]
        row += 1

        for col_letter, header in [('B', 'Adresse'), ('C', 'Superficie'), ('D', 'Prix'), ('E', 'Date de la vente'), ('F', 'Prix/m2')]:
            ws3[f'{col_letter}{row}'] = header
            ws3[f'{col_letter}{row}'].font = S["header"]
            ws3[f'{col_letter}{row}'].fill = S["header_fill"]
        row += 1

        prices_m2 = []
        for tx in txs[:12]:
            ws3[f'B{row}'] = tx.get("adresse", "")
            ws3[f'C{row}'] = tx.get("surface", 0)
            ws3[f'D{row}'] = tx.get("prix", 0)
            ws3[f'D{row}'].number_format = MONEY_FMT
            ws3[f'E{row}'] = str(tx.get("date_mutation", tx.get("date", "")))[:10]
            pm2 = tx.get("prix_m2", 0)
            ws3[f'F{row}'] = round(pm2) if pm2 else 0
            if pm2:
                prices_m2.append(pm2)
            row += 1

        # TOTAL
        if prices_m2:
            prices_m2.sort()
            ws3[f'B{row}'] = "TOTAL"
            ws3[f'B{row}'].font = S["total_font"]
            ws3[f'C{row}'] = round(sum(t.get("surface", 0) for t in txs[:12]) / len(txs[:12])) if txs else 0
            ws3[f'D{row}'] = round(sum(t.get("prix", 0) for t in txs[:12]) / len(txs[:12])) if txs else 0
            ws3[f'D{row}'].number_format = MONEY_FMT
            ws3[f'F{row}'] = round(sum(prices_m2) / len(prices_m2))
            ws3[f'F{row}'].font = S["total_font"]
            row += 1

        row += 2  # espace entre segments

    # ═══ ONGLET 4 : ETUDE HABITATIONS ═══
    ws4 = wb.create_sheet("Etude Habitations")
    for col, w in [('C', 35), ('D', 12), ('E', 14), ('F', 16), ('G', 12)]:
        ws4.column_dimensions[col].width = w

    hab_headers = ["Adresse", "Superficie", "Prix", "Date de la vente", "Prix/m2"]

    # Appartements
    ws4['C3'] = "Appartements"
    ws4['C3'].font = S["title"]
    for j, h in enumerate(hab_headers):
        col = get_column_letter(j + 3)
        ws4[f'{col}4'] = h
        ws4[f'{col}4'].font = S["header"]
        ws4[f'{col}4'].fill = S["header_fill"]

    appts = [t for t in dvf if "appart" in (t.get("type_local", t.get("type", "")).lower())]
    for i, tx in enumerate(appts[:10], start=5):
        ws4[f'C{i}'] = tx.get("adresse", "")
        ws4[f'D{i}'] = tx.get("surface", 0)
        ws4[f'E{i}'] = tx.get("prix", 0)
        ws4[f'E{i}'].number_format = MONEY_FMT
        ws4[f'F{i}'] = str(tx.get("date_mutation", tx.get("date", "")))[:10]
        ws4[f'G{i}'] = round(tx.get("prix_m2", 0))

    row_total_a = 5 + len(appts[:10])
    if appts:
        ws4[f'C{row_total_a}'] = "TOTAL"
        ws4[f'C{row_total_a}'].font = S["total_font"]
        ws4[f'D{row_total_a}'] = round(sum(t.get("surface", 0) for t in appts[:10]) / len(appts[:10]))
        ws4[f'E{row_total_a}'] = round(sum(t.get("prix", 0) for t in appts[:10]) / len(appts[:10]))
        ws4[f'E{row_total_a}'].number_format = MONEY_FMT
        pm2_list = [t.get("prix_m2", 0) for t in appts[:10] if t.get("prix_m2")]
        ws4[f'G{row_total_a}'] = round(sum(pm2_list) / len(pm2_list)) if pm2_list else 0
        ws4[f'G{row_total_a}'].font = S["total_font"]

    # Maisons
    row_m = max(row_total_a + 2, 18)
    ws4[f'C{row_m}'] = "Maisons"
    ws4[f'C{row_m}'].font = S["title"]
    for j, h in enumerate(hab_headers):
        col = get_column_letter(j + 3)
        ws4[f'{col}{row_m + 1}'] = h
        ws4[f'{col}{row_m + 1}'].font = S["header"]
        ws4[f'{col}{row_m + 1}'].fill = S["header_fill"]

    maisons = [t for t in dvf if "maison" in (t.get("type_local", t.get("type", "")).lower())]
    for i, tx in enumerate(maisons[:12], start=row_m + 2):
        ws4[f'C{i}'] = tx.get("adresse", "")
        ws4[f'D{i}'] = tx.get("surface", 0)
        ws4[f'E{i}'] = tx.get("prix", 0)
        ws4[f'E{i}'].number_format = MONEY_FMT
        ws4[f'F{i}'] = str(tx.get("date_mutation", tx.get("date", "")))[:10]
        ws4[f'G{i}'] = round(tx.get("prix_m2", 0))

    row_total_m = row_m + 2 + len(maisons[:12])
    if maisons:
        ws4[f'C{row_total_m}'] = "TOTAL"
        ws4[f'C{row_total_m}'].font = S["total_font"]
        ws4[f'D{row_total_m}'] = round(sum(t.get("surface", 0) for t in maisons[:12]) / len(maisons[:12]))
        ws4[f'E{row_total_m}'] = round(sum(t.get("prix", 0) for t in maisons[:12]) / len(maisons[:12]))
        ws4[f'E{row_total_m}'].number_format = MONEY_FMT
        pm2_m = [t.get("prix_m2", 0) for t in maisons[:12] if t.get("prix_m2")]
        ws4[f'G{row_total_m}'] = round(sum(pm2_m) / len(pm2_m)) if pm2_m else 0
        ws4[f'G{row_total_m}'].font = S["total_font"]

    # ═══ ONGLET 5 : COMPARABLES AVM ═══
    ws5 = wb.create_sheet("Comparables AVM")
    for col, w in [('B', 32), ('C', 14), ('D', 10), ('E', 14), ('F', 10), ('G', 12), ('H', 10), ('I', 8)]:
        ws5.column_dimensions[col].width = w

    ws5['B2'] = f"Estimation AVM — {ville}"
    ws5['B2'].font = S["title"]

    est = estimation
    if est.get("estimation"):
        ws5['B3'] = f"Valeur estimee : {est['estimation']:,.0f} EUR | Fourchette : {est.get('fourchette_basse', 0):,.0f} - {est.get('fourchette_haute', 0):,.0f} EUR | Confiance : {est.get('score_confiance', 0)}/100"
        ws5['B3'].font = S["value"]

    comps = est.get("comparables", [])
    if comps:
        comp_headers = ["Adresse", "Ville", "Surface", "Prix", "Prix/m2", "Date", "Distance", "Poids"]
        for j, h in enumerate(comp_headers):
            col = get_column_letter(j + 2)
            ws5[f'{col}5'] = h
            ws5[f'{col}5'].font = S["header"]
            ws5[f'{col}5'].fill = S["header_fill"]

        for i, c in enumerate(comps[:25], start=6):
            ws5[f'B{i}'] = c.get("adresse", "")
            ws5[f'C{i}'] = c.get("ville", "")
            ws5[f'D{i}'] = c.get("surface", 0)
            ws5[f'E{i}'] = c.get("prix", 0)
            ws5[f'E{i}'].number_format = MONEY_FMT
            ws5[f'F{i}'] = round(c.get("prix_m2", 0))
            ws5[f'G{i}'] = c.get("date", "")
            ws5[f'H{i}'] = f"{c.get('distance_km', 0):.1f} km"
            ws5[f'I{i}'] = round(c.get("poids", 0), 3)

    abs_path = os.path.abspath(output_path)
    wb.save(abs_path)
    return abs_path


# ════════════════════════════════════════════════════
# PPTX — DOSSIER INVESTISSEMENT (avec graphiques)
# ════════════════════════════════════════════════════

def generate_dossier_pptx(data: dict, output_path: str = "dossier_investissement.pptx") -> str:
    """Genere un PowerPoint dossier d'investissement avec graphiques.

    Args:
        data: dict avec cles: projet, stats, dvf, estimation, simulation, prediction, lots
        output_path: chemin fichier sortie
    Returns: chemin absolu du fichier genere
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.chart.data import CategoryChartData

    prs = Presentation()
    prs.slide_width = Emu(9144000)
    prs.slide_height = Emu(5143500)

    projet = data.get("projet", {})
    stats = data.get("stats", {}).get("data", data.get("stats", {}))
    dvf_list = data.get("dvf", [])
    estimation = data.get("estimation", {})
    simulation = data.get("simulation", {}).get("data", data.get("simulation", {}))
    prediction = data.get("prediction", {})
    lots = data.get("lots", [])
    ville = projet.get("ville", "")
    prix = projet.get("prix", 0)

    BLUE = RGBColor(0x1E, 0x56, 0xA0)
    DARK = RGBColor(0x0D, 0x11, 0x17)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    LIGHT = RGBColor(0x33, 0x33, 0x33)
    GREEN = RGBColor(0x16, 0xA3, 0x4A)
    RED = RGBColor(0xDC, 0x26, 0x26)

    def _bg_dark(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = DARK

    def _add_title_bar(slide, text, y=Inches(0.2)):
        box = slide.shapes.add_textbox(Inches(0.4), y, Inches(9), Inches(0.5))
        p = box.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = BLUE
        return box

    def _add_kpi_card(slide, x, y, label, value, color=BLUE):
        """Ajoute une KPI card avec fond arrondi."""
        from pptx.enum.shapes import MSO_SHAPE
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.1), Inches(1.0))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(0xEF, 0xF6, 0xFF)
        shape.line.fill.background()

        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = str(value)
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = color
        p.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(9)
        p2.font.color.rgb = LIGHT
        p2.alignment = PP_ALIGN.CENTER

    def _add_text_block(slide, lines, x=Inches(0.5), y=Inches(1.0), w=Inches(9), h=Inches(3.5)):
        box = slide.shapes.add_textbox(x, y, w, h)
        tf = box.text_frame
        tf.word_wrap = True
        for line in lines:
            p = tf.add_paragraph()
            if line.startswith("**"):
                p.text = line.replace("**", "")
                p.font.bold = True
                p.font.size = Pt(13)
                p.font.color.rgb = BLUE
            else:
                p.text = line
                p.font.size = Pt(11)
                p.font.color.rgb = LIGHT
            p.space_after = Pt(4)

    def _add_table(slide, headers, rows, x=Inches(0.3), y=Inches(1.2), w=Inches(9.2), h=Inches(3.5)):
        n_rows = min(len(rows) + 1, 16)
        n_cols = len(headers)
        tbl_shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, h)
        table = tbl_shape.table

        for j, hdr in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = hdr
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(9)
                para.font.bold = True
                para.font.color.rgb = WHITE
            cell.fill.solid()
            cell.fill.fore_color.rgb = BLUE

        for i, row in enumerate(rows[:15]):
            for j, val in enumerate(row):
                cell = table.cell(i + 1, j)
                cell.text = str(val)
                for para in cell.text_frame.paragraphs:
                    para.font.size = Pt(8)
                # Alternance couleurs
                if i % 2 == 1:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)

    # ═══ SLIDE 1 : PAGE DE GARDE (dark) ═══
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    _bg_dark(s1)
    box = s1.shapes.add_textbox(Inches(1), Inches(1.2), Inches(8), Inches(2))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = f"{ville.upper()} ({projet.get('code_postal', '')})"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Dossier d'Investissement Immobilier"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(0x6C, 0xB4, 0xEE)
    p2.alignment = PP_ALIGN.CENTER
    p3 = tf.add_paragraph()
    p3.text = date.today().strftime("%B %Y")
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    p3.alignment = PP_ALIGN.CENTER

    # ═══ SLIDE 2 : KPIs DASHBOARD ═══
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s2, "SYNTHESE — INDICATEURS CLES")

    est_val = estimation.get("estimation", 0)
    score = estimation.get("score_confiance", 0)
    mensualite = simulation.get("mensualite", 0)
    ecart = round(((prix / est_val) - 1) * 100, 1) if est_val else 0

    _add_kpi_card(s2, Inches(0.3), Inches(0.9), "PRIX DEMANDE", f"{prix:,.0f} EUR")
    _add_kpi_card(s2, Inches(2.5), Inches(0.9), "ESTIMATION AVM", f"{est_val:,.0f} EUR", GREEN if ecart < 0 else RED)
    _add_kpi_card(s2, Inches(4.7), Inches(0.9), "ECART", f"{ecart:+.1f}%", GREEN if ecart < 0 else RED)
    _add_kpi_card(s2, Inches(6.9), Inches(0.9), "CONFIANCE", f"{score}/100", BLUE)

    _add_kpi_card(s2, Inches(0.3), Inches(2.2), "MENSUALITE", f"{mensualite:,.0f} EUR/mois")
    _add_kpi_card(s2, Inches(2.5), Inches(2.2), "PRIX MEDIAN /M2", f"{stats.get('prix_m2_moyen', 0):,.0f} EUR")
    _add_kpi_card(s2, Inches(4.7), Inches(2.2), "TRANSACTIONS", f"{stats.get('nb_transactions', 0)}")

    ptz = simulation.get("ptz", {})
    ptz_text = f"OUI — {ptz.get('montant_ptz', 0):,.0f} EUR" if ptz.get("eligible") else "NON"
    _add_kpi_card(s2, Inches(6.9), Inches(2.2), "PTZ ELIGIBLE", ptz_text, GREEN if ptz.get("eligible") else RED)

    # ═══ SLIDE 3 : EVOLUTION PRIX (graphique) ═══
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s3, "EVOLUTION DU MARCHE")

    evolution = stats.get("evolution", [])
    if evolution:
        chart_data = CategoryChartData()
        chart_data.categories = [str(e.get("annee", "")) for e in evolution]
        chart_data.add_series("Prix moyen /m2", [e.get("prix_m2_moyen", 0) for e in evolution])
        chart = s3.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.0), Inches(5.5), Inches(3.5), chart_data
        ).chart
        chart.has_legend = False
        chart.style = 2
        # Volume a droite
        vol_data = CategoryChartData()
        vol_data.categories = [str(e.get("annee", "")) for e in evolution]
        vol_lines = [f"{e.get('annee', '')}: {e.get('nb', 0)} ventes — {e.get('prix_m2_moyen', 0):,.0f} EUR/m2" for e in evolution]
        box = s3.shapes.add_textbox(Inches(6.2), Inches(1.0), Inches(3.5), Inches(3.5))
        tf = box.text_frame
        tf.word_wrap = True
        for line in vol_lines:
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(10)
            p.font.color.rgb = LIGHT

    # ═══ SLIDE 4 : COMPARABLES DVF ═══
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s4, "TRANSACTIONS DVF COMPARABLES")
    dvf_rows = []
    for tx in dvf_list[:12]:
        dvf_rows.append([
            tx.get("adresse", "")[:25],
            tx.get("ville", "")[:15],
            f"{tx.get('surface', 0)} m2",
            f"{tx.get('prix', 0):,.0f}",
            f"{tx.get('prix_m2', 0):,.0f}",
            str(tx.get("date_mutation", tx.get("date", "")))[:10],
        ])
    _add_table(s4, ["Adresse", "Ville", "Surface", "Prix", "EUR/m2", "Date"], dvf_rows)

    # ═══ SLIDE 5 : ESTIMATION AVM ═══
    s5 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s5, "ESTIMATION DE VALEUR (AVM)")
    _add_text_block(s5, [
        f"**Valeur estimee : {est_val:,.0f} EUR**",
        f"Prix/m2 estime : {estimation.get('prix_m2_estime', 0):,.0f} EUR",
        f"Fourchette : {estimation.get('fourchette_basse', 0):,.0f} — {estimation.get('fourchette_haute', 0):,.0f} EUR",
        f"Score de confiance : {score}/100 ({estimation.get('confiance_label', '')})",
        f"Comparables utilises : {estimation.get('nb_comparables', 0)}",
        "",
        f"Ecart prix demande vs AVM : {ecart:+.1f}%",
        "VERDICT : " + ("OPPORTUNITE" if ecart < -5 else "PRIX COHERENT" if abs(ecart) <= 10 else "PRIX ELEVE"),
    ])

    # ═══ SLIDE 6 : FINANCEMENT ═══
    s6 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s6, "PLAN DE FINANCEMENT")
    _add_text_block(s6, [
        f"**Capital emprunte : {simulation.get('capital_emprunte', 0):,.0f} EUR**",
        f"Taux : {simulation.get('taux_annuel', 0)}% sur {simulation.get('duree_ans', 0)} ans",
        f"Mensualite : {mensualite:,.0f} EUR/mois",
        f"Cout total credit : {simulation.get('cout_total', 0):,.0f} EUR",
        f"Total interets : {simulation.get('cout_interets', 0):,.0f} EUR",
        "",
        f"**PTZ : {'ELIGIBLE' if ptz.get('eligible') else 'NON ELIGIBLE'}**" + (f" — {ptz.get('montant_ptz', 0):,.0f} EUR (zone {ptz.get('zone', '?')})" if ptz.get("eligible") else ""),
        f"Capacite emprunt : {simulation.get('capacite_emprunt', {}).get('capacite_emprunt', 0):,.0f} EUR" if simulation.get("capacite_emprunt") else "",
    ])

    # ═══ SLIDE 7 : LOTS (si disponibles) ═══
    if lots:
        s7 = prs.slides.add_slide(prs.slide_layouts[6])
        _add_title_bar(s7, "RECAPITULATIF DES LOTS — PRIX CONSERVATEUR / CIBLE")
        lot_rows = []
        for lot in lots:
            surf = lot.get("surface", 0)
            p_bas = lot.get("prix_conservateur", lot.get("prix_revente", 0))
            p_cible = lot.get("prix_cible", lot.get("prix_revente_cible", 0))
            lot_rows.append([
                lot.get("lot", ""),
                lot.get("type", lot.get("typologie", "")),
                f"{surf}",
                f"{p_bas:,.0f}",
                f"{round(p_bas/surf) if surf else 0}",
                f"{p_cible:,.0f}",
                f"{round(p_cible/surf) if surf else 0}",
            ])
        _add_table(s7, ["Lot", "Type", "Surface", "Prix Bas", "/m2", "Prix Cible", "/m2"], lot_rows)

    # ═══ SLIDE 8 : SOURCES ═══
    s8 = prs.slides.add_slide(prs.slide_layouts[6])
    _add_title_bar(s8, "SOURCES & METHODOLOGIE")
    _add_text_block(s8, [
        "**Sources des donnees**",
        "DVF : data.gouv.fr (DGFiP) — transactions reelles enregistrees",
        "DPE : ADEME — diagnostics de performance energetique",
        "SIRENE : INSEE — registre des entreprises",
        "Georisques : BRGM — risques naturels et technologiques",
        "AVM : modele PropTech — estimation par comparables ponderes",
        "",
        "Estimation indicative — ne constitue pas un avis professionnel.",
        "Consultez un expert avant toute decision d'investissement.",
        f"Document genere le {date.today().strftime('%d/%m/%Y')} par PropTech MCP.",
    ])

    # ═══ SLIDE 9 : CONCLUSION ═══
    s9 = prs.slides.add_slide(prs.slide_layouts[6])
    _bg_dark(s9)
    verdict = "OPPORTUNITE" if ecart < -5 else "A NEGOCIER" if ecart < 10 else "PRIX ELEVE"
    box = s9.shapes.add_textbox(Inches(1), Inches(0.8), Inches(8), Inches(3.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = f"VERDICT : {verdict}"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = GREEN if "OPPORTUNITE" in verdict else RGBColor(0xF5, 0x9E, 0x0B) if "NEGOCIER" in verdict else RED
    p.alignment = PP_ALIGN.CENTER

    for line in [
        "",
        f"Prix demande : {prix:,.0f} EUR | Estimation AVM : {est_val:,.0f} EUR",
        f"Mensualite credit : {mensualite:,.0f} EUR/mois",
        "",
        "PROCHAINES ETAPES :",
        "1. Visite du bien",
        "2. Negociation du prix",
        "3. Montage du dossier bancaire",
    ]:
        p2 = tf.add_paragraph()
        p2.text = line
        p2.font.size = Pt(13) if line.startswith("PROCHAINES") else Pt(11)
        p2.font.bold = line.startswith("PROCHAINES")
        p2.font.color.rgb = WHITE
        p2.alignment = PP_ALIGN.CENTER

    abs_path = os.path.abspath(output_path)
    prs.save(abs_path)
    return abs_path
