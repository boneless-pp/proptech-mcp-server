"""Generateurs PPTX et Excel pour les workflows PropTech.

Utilise python-pptx et openpyxl pour creer des fichiers professionnels
a partir des donnees MCP PropTech.

Usage standalone (Claude Code):
    from generators import generate_dossier_pptx, generate_synthese_xlsx
    generate_dossier_pptx(data, output_path="dossier.pptx")
    generate_synthese_xlsx(data, output_path="synthese.xlsx")
"""

from __future__ import annotations
import os
from datetime import date


# ════════════════════════════════════════════════════
# EXCEL — SYNTHESE FINANCIERE
# ════════════════════════════════════════════════════

def generate_synthese_xlsx(data: dict, output_path: str = "synthese_financiere.xlsx") -> str:
    """Genere un Excel synthese financiere 5 onglets.

    Args:
        data: dict avec les cles suivantes:
            - projet: {ville, adresse, code_postal, prix, surface, nb_lots, dpe, type_bien}
            - lots: [{lot, type, surface, dpe, prix_revente}]
            - bilan: {frais_notaire, travaux, total_operation, prix_revente_total, marge}
            - simulation: dict retourne par simuler_financement
            - dvf: list de transactions DVF
            - estimation: dict retourne par estimer_valeur_bien
        output_path: chemin du fichier de sortie

    Returns: chemin absolu du fichier genere
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    # Styles
    title_font = Font(name="Calibri", size=14, bold=True, color="1E56A0")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E56A0", end_color="1E56A0", fill_type="solid")
    label_font = Font(name="Calibri", size=11, bold=True)
    value_font = Font(name="Calibri", size=11)
    money_format = '#,##0 "EUR"'
    pct_format = '0.0%'
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin'),
    )

    projet = data.get("projet", {})
    lots = data.get("lots", [])
    bilan = data.get("bilan", {})
    simulation = data.get("simulation", {})
    dvf = data.get("dvf", [])
    estimation = data.get("estimation", {})

    # ── Onglet 1 : Projet ──
    ws = wb.active
    ws.title = "Projet"
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 30

    ws['B2'] = "FICHE PROJET"
    ws['B2'].font = title_font

    info_rows = [
        ("Ville", projet.get("ville", "")),
        ("Adresse", projet.get("adresse", "")),
        ("Code postal", projet.get("code_postal", "")),
        ("Type de bien", projet.get("type_bien", "")),
        ("Prix demande", projet.get("prix", 0)),
        ("Surface totale", f"{projet.get('surface', 0)} m2"),
        ("DPE", projet.get("dpe", "N/C")),
        ("Nombre de lots", projet.get("nb_lots", 1)),
        ("Date analyse", date.today().strftime("%d/%m/%Y")),
        ("Source", "PropTech MCP / DVF data.gouv.fr"),
    ]
    for i, (label, val) in enumerate(info_rows, start=4):
        ws[f'B{i}'] = label
        ws[f'B{i}'].font = label_font
        ws[f'C{i}'] = val
        ws[f'C{i}'].font = value_font
        if isinstance(val, (int, float)) and "prix" in label.lower():
            ws[f'C{i}'].number_format = money_format

    # Lots
    if lots:
        row = 16
        ws[f'B{row}'] = "DETAIL DES LOTS"
        ws[f'B{row}'].font = title_font
        row += 1
        headers = ["Lot", "Type", "Surface", "DPE", "Prix revente"]
        for j, h in enumerate(headers):
            col = get_column_letter(j + 2)
            ws[f'{col}{row}'] = h
            ws[f'{col}{row}'].font = header_font
            ws[f'{col}{row}'].fill = header_fill
        for lot in lots:
            row += 1
            ws[f'B{row}'] = lot.get("lot", "")
            ws[f'C{row}'] = lot.get("type", "")
            ws[f'D{row}'] = lot.get("surface", 0)
            ws[f'E{row}'] = lot.get("dpe", "")
            ws[f'F{row}'] = lot.get("prix_revente", 0)
            ws[f'F{row}'].number_format = money_format

    # ── Onglet 2 : Bilan ──
    ws2 = wb.create_sheet("Bilan")
    ws2.column_dimensions['B'].width = 30
    ws2.column_dimensions['D'].width = 18
    ws2.column_dimensions['I'].width = 30
    ws2.column_dimensions['K'].width = 18

    ws2['B2'] = "RESUME DU PROJET"
    ws2['B2'].font = title_font

    prix = projet.get("prix", 0)
    frais_notaire = bilan.get("frais_notaire", round(prix * 0.075))
    travaux = bilan.get("travaux", 0)
    total_op = bilan.get("total_operation", prix + frais_notaire + travaux)

    bilan_rows = [
        ("Prix du bien", prix),
        ("Frais de notaire (7.5%)", frais_notaire),
        ("Travaux", travaux),
        ("Geometre / Archi", bilan.get("geometre", 0)),
        ("Diagnostics & DTG", bilan.get("diagnostics", 0)),
        ("Assurance + Taxe Fonciere", bilan.get("assurance_tf", 0)),
        ("TOTAL OPERATION", total_op),
    ]
    for i, (label, val) in enumerate(bilan_rows, start=3):
        ws2[f'B{i}'] = label
        ws2[f'B{i}'].font = label_font if "TOTAL" in label else value_font
        ws2[f'D{i}'] = val
        ws2[f'D{i}'].number_format = money_format
        if "TOTAL" in label:
            ws2[f'D{i}'].font = Font(name="Calibri", size=12, bold=True, color="1E56A0")

    # Revente
    revente_total = bilan.get("prix_revente_total", 0)
    marge = revente_total - total_op if revente_total else 0
    ws2['B12'] = "REVENTE"
    ws2['B12'].font = title_font
    ws2['B13'] = "Prix de revente total"
    ws2['D13'] = revente_total
    ws2['D13'].number_format = money_format
    ws2['B15'] = "MARGE SUR COUT DE REVIENT"
    ws2['B15'].font = title_font
    ws2['B16'] = "Benefice brut"
    ws2['D16'] = marge
    ws2['D16'].number_format = money_format
    ws2['B17'] = "Marge brute"
    ws2['D17'] = marge / total_op if total_op else 0
    ws2['D17'].number_format = pct_format

    # Simulation credit
    sim = simulation.get("data", simulation)
    if sim.get("mensualite"):
        ws2['B20'] = "SIMULATION CREDIT"
        ws2['B20'].font = title_font
        sim_rows = [
            ("Capital emprunte", sim.get("capital_emprunte", 0)),
            ("Taux annuel", f"{sim.get('taux_annuel', 0)}%"),
            ("Duree", f"{sim.get('duree_ans', 0)} ans"),
            ("Mensualite", sim.get("mensualite", 0)),
            ("Cout total credit", sim.get("cout_total", 0)),
            ("Total interets", sim.get("cout_interets", 0)),
        ]
        for i, (label, val) in enumerate(sim_rows, start=21):
            ws2[f'B{i}'] = label
            ws2[f'B{i}'].font = value_font
            ws2[f'D{i}'] = val
            if isinstance(val, (int, float)):
                ws2[f'D{i}'].number_format = money_format

    # PTZ
    ptz = sim.get("ptz", {})
    if ptz.get("eligible"):
        ws2['B29'] = "PTZ (Pret a Taux Zero)"
        ws2['B29'].font = title_font
        ws2['B30'] = "Eligible"
        ws2['D30'] = "OUI"
        ws2['D30'].font = Font(name="Calibri", size=11, bold=True, color="16A34A")
        ws2['B31'] = f"Zone {ptz.get('zone', '?')}"
        ws2['D31'] = ptz.get("montant_ptz", 0)
        ws2['D31'].number_format = money_format

    # ── Onglet 3 : Etude Marche DVF ──
    ws3 = wb.create_sheet("Etude Marche (DVF)")
    ws3.column_dimensions['B'].width = 35
    ws3.column_dimensions['C'].width = 15
    ws3.column_dimensions['D'].width = 12
    ws3.column_dimensions['E'].width = 15
    ws3.column_dimensions['F'].width = 15
    ws3.column_dimensions['G'].width = 12

    ws3['B2'] = f"Etude de marche DVF — {projet.get('ville', '')}"
    ws3['B2'].font = title_font

    dvf_headers = ["Adresse", "Ville", "Surface", "Prix", "Prix/m2", "Date"]
    for j, h in enumerate(dvf_headers):
        col = get_column_letter(j + 2)
        ws3[f'{col}4'] = h
        ws3[f'{col}4'].font = header_font
        ws3[f'{col}4'].fill = header_fill

    for i, tx in enumerate(dvf[:30], start=5):
        ws3[f'B{i}'] = tx.get("adresse", "")
        ws3[f'C{i}'] = tx.get("ville", "")
        ws3[f'D{i}'] = tx.get("surface", 0)
        ws3[f'E{i}'] = tx.get("prix", 0)
        ws3[f'E{i}'].number_format = money_format
        ws3[f'F{i}'] = tx.get("prix_m2", 0)
        ws3[f'F{i}'].number_format = '#,##0'
        ws3[f'G{i}'] = str(tx.get("date_mutation", tx.get("date", "")))

    # Totals
    row_total = 5 + len(dvf[:30])
    prices = [t.get("prix_m2", 0) for t in dvf if t.get("prix_m2")]
    if prices:
        prices.sort()
        ws3[f'B{row_total}'] = "MEDIANE"
        ws3[f'B{row_total}'].font = label_font
        ws3[f'F{row_total}'] = prices[len(prices) // 2]
        ws3[f'F{row_total}'].font = label_font
        ws3[f'B{row_total+1}'] = "MOYENNE"
        ws3[f'B{row_total+1}'].font = label_font
        ws3[f'F{row_total+1}'] = round(sum(prices) / len(prices))
        ws3[f'F{row_total+1}'].font = label_font

    # ── Onglet 4 : Etude Habitations ──
    ws4 = wb.create_sheet("Etude Habitations")
    ws4['C3'] = "Appartements"
    ws4['C3'].font = title_font
    hab_headers = ["Adresse", "Superficie", "Prix", "Date de la vente", "Prix/m2"]
    for j, h in enumerate(hab_headers):
        col = get_column_letter(j + 3)
        ws4[f'{col}4'] = h
        ws4[f'{col}4'].font = header_font
        ws4[f'{col}4'].fill = header_fill

    appts = [t for t in dvf if t.get("type_local", t.get("type", "")).lower().startswith("appart")]
    for i, tx in enumerate(appts[:10], start=5):
        ws4[f'C{i}'] = tx.get("adresse", "")
        ws4[f'D{i}'] = tx.get("surface", 0)
        ws4[f'E{i}'] = tx.get("prix", 0)
        ws4[f'E{i}'].number_format = money_format
        ws4[f'F{i}'] = str(tx.get("date_mutation", tx.get("date", "")))
        ws4[f'G{i}'] = tx.get("prix_m2", 0)

    row_maison = max(16, 5 + len(appts[:10]) + 2)
    ws4[f'C{row_maison}'] = "Maisons"
    ws4[f'C{row_maison}'].font = title_font
    for j, h in enumerate(hab_headers):
        col = get_column_letter(j + 3)
        ws4[f'{col}{row_maison+1}'] = h
        ws4[f'{col}{row_maison+1}'].font = header_font
        ws4[f'{col}{row_maison+1}'].fill = header_fill

    maisons = [t for t in dvf if t.get("type_local", t.get("type", "")).lower().startswith("maison")]
    for i, tx in enumerate(maisons[:10], start=row_maison + 2):
        ws4[f'C{i}'] = tx.get("adresse", "")
        ws4[f'D{i}'] = tx.get("surface", 0)
        ws4[f'E{i}'] = tx.get("prix", 0)
        ws4[f'E{i}'].number_format = money_format
        ws4[f'F{i}'] = str(tx.get("date_mutation", tx.get("date", "")))
        ws4[f'G{i}'] = tx.get("prix_m2", 0)

    # ── Onglet 5 : Comparables AVM ──
    ws5 = wb.create_sheet("Comparables AVM")
    ws5['B2'] = "Comparables utilises pour l'estimation AVM"
    ws5['B2'].font = title_font

    comps = estimation.get("comparables", [])
    if comps:
        comp_headers = ["Adresse", "Ville", "Surface", "Prix", "Prix/m2", "Date", "Distance", "Poids"]
        for j, h in enumerate(comp_headers):
            col = get_column_letter(j + 2)
            ws5[f'{col}4'] = h
            ws5[f'{col}4'].font = header_font
            ws5[f'{col}4'].fill = header_fill

        for i, c in enumerate(comps[:20], start=5):
            ws5[f'B{i}'] = c.get("adresse", "")
            ws5[f'C{i}'] = c.get("ville", "")
            ws5[f'D{i}'] = c.get("surface", 0)
            ws5[f'E{i}'] = c.get("prix", 0)
            ws5[f'E{i}'].number_format = money_format
            ws5[f'F{i}'] = c.get("prix_m2", 0)
            ws5[f'G{i}'] = c.get("date", "")
            ws5[f'H{i}'] = f"{c.get('distance_km', 0):.1f} km"
            ws5[f'I{i}'] = c.get("poids", 0)

    # Save
    abs_path = os.path.abspath(output_path)
    wb.save(abs_path)
    return abs_path


# ════════════════════════════════════════════════════
# PPTX — DOSSIER INVESTISSEMENT
# ════════════════════════════════════════════════════

def generate_dossier_pptx(data: dict, output_path: str = "dossier_investissement.pptx") -> str:
    """Genere un PowerPoint dossier d'investissement.

    Args:
        data: dict avec les cles: projet, stats, dvf, estimation, simulation, prediction
        output_path: chemin du fichier de sortie

    Returns: chemin absolu du fichier genere
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    prs = Presentation()
    prs.slide_width = Emu(9144000)   # 16:9
    prs.slide_height = Emu(5143500)

    projet = data.get("projet", {})
    stats = data.get("stats", {})
    dvf_list = data.get("dvf", [])
    estimation = data.get("estimation", {})
    simulation = data.get("simulation", {})
    prediction = data.get("prediction", {})
    ville = projet.get("ville", "")

    BLUE = RGBColor(0x1E, 0x56, 0xA0)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    DARK = RGBColor(0x33, 0x33, 0x33)

    def add_title_slide(title, subtitle=""):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        # Blue background
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BLUE

        txBox = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(1.5))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.size = Pt(18)
            p2.font.color.rgb = WHITE
            p2.alignment = PP_ALIGN.CENTER
        return slide

    def add_content_slide(title, content_lines):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        # Title bar
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = BLUE

        # Content
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(3.5))
        tf2 = content_box.text_frame
        tf2.word_wrap = True
        for line in content_lines:
            p = tf2.add_paragraph()
            p.text = line
            p.font.size = Pt(14)
            p.font.color.rgb = DARK
            p.space_after = Pt(6)
        return slide

    def add_table_slide(title, headers, rows):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        title_box = slide.shapes.add_textbox(Inches(0.3), Inches(0.2), Inches(9), Inches(0.6))
        p = title_box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = BLUE

        n_rows = min(len(rows) + 1, 15)
        n_cols = len(headers)
        table = slide.shapes.add_table(n_rows, n_cols, Inches(0.3), Inches(0.9), Inches(9.2), Inches(3.8)).table

        for j, h in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = h
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(10)
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            cell.fill.solid()
            cell.fill.fore_color.rgb = BLUE

        for i, row in enumerate(rows[:14]):
            for j, val in enumerate(row):
                cell = table.cell(i + 1, j)
                cell.text = str(val)
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.size = Pt(9)
        return slide

    # ═══ SLIDE 1 : PAGE DE GARDE ═══
    add_title_slide(
        f"{ville.upper()} ({projet.get('code_postal', '')})",
        f"Dossier d'Investissement Immobilier\n{date.today().strftime('%B %Y')}"
    )

    # ═══ SLIDE 2 : SOMMAIRE ═══
    add_content_slide("SOMMAIRE", [
        "1. Introduction & Contexte",
        "2. Description du projet",
        "3. Analyse du marche",
        "4. Transactions comparables DVF",
        "5. Estimation AVM",
        "6. Plan de financement",
        "7. Rentabilite & Cashflow",
        "8. Sources & Methodologie",
        "9. Conclusion & Prochaines etapes",
    ])

    # ═══ SLIDE 3 : INTRODUCTION ═══
    prix = projet.get("prix", 0)
    surface = projet.get("surface", 0)
    add_content_slide("INTRODUCTION", [
        f"Bien : {projet.get('type_bien', '')} de {surface} m2 a {ville}",
        f"Prix demande : {prix:,.0f} EUR ({prix/surface:,.0f} EUR/m2)" if surface else f"Prix : {prix:,.0f} EUR",
        f"DPE : {projet.get('dpe', 'N/C')}",
        "",
        "Ce dossier analyse la coherence du prix, la dynamique du marche local,",
        "et la rentabilite de l'investissement sur la base des donnees DVF publiques.",
    ])

    # ═══ SLIDE 4 : ANALYSE MARCHE ═══
    s = stats.get("data", stats)
    evolution = s.get("evolution", [])
    evo_lines = [f"  {e.get('annee')}: {e.get('prix_m2_moyen', 0):,.0f} EUR/m2 ({e.get('nb', 0)} ventes)" for e in evolution[-5:]]
    add_content_slide("ANALYSE DU MARCHE", [
        f"Prix median /m2 : {s.get('prix_m2_moyen', 0):,.0f} EUR",
        f"Transactions totales : {s.get('nb_transactions', 0)}",
        f"Surface moyenne : {s.get('surface_moyenne', 0):,.0f} m2",
        "",
        "Evolution par annee :",
    ] + evo_lines)

    # ═══ SLIDE 5 : COMPARABLES DVF ═══
    dvf_rows = []
    for tx in dvf_list[:12]:
        dvf_rows.append([
            tx.get("adresse", "")[:30],
            tx.get("ville", ""),
            f"{tx.get('surface', 0)} m2",
            f"{tx.get('prix', 0):,.0f}",
            f"{tx.get('prix_m2', 0):,.0f}",
            str(tx.get("date_mutation", tx.get("date", "")))[:10],
        ])
    add_table_slide("TRANSACTIONS DVF COMPARABLES", ["Adresse", "Ville", "Surface", "Prix", "EUR/m2", "Date"], dvf_rows)

    # ═══ SLIDE 6 : ESTIMATION AVM ═══
    est = estimation
    add_content_slide("ESTIMATION AVM", [
        f"Estimation : {est.get('estimation', 0):,.0f} EUR",
        f"Prix/m2 estime : {est.get('prix_m2_estime', 0):,.0f} EUR",
        f"Fourchette : {est.get('fourchette_basse', 0):,.0f} - {est.get('fourchette_haute', 0):,.0f} EUR",
        f"Score de confiance : {est.get('score_confiance', 0)}/100 ({est.get('confiance_label', '')})",
        f"Comparables utilises : {est.get('nb_comparables', 0)}",
        "",
        f"Ecart prix demande vs AVM : {((prix / est.get('estimation', 1)) - 1) * 100:+.1f}%" if est.get("estimation") else "",
    ])

    # ═══ SLIDE 7 : FINANCEMENT ═══
    sim = simulation.get("data", simulation)
    ptz = sim.get("ptz", {})
    add_content_slide("PLAN DE FINANCEMENT", [
        f"Capital emprunte : {sim.get('capital_emprunte', 0):,.0f} EUR",
        f"Taux : {sim.get('taux_annuel', 0)}% sur {sim.get('duree_ans', 0)} ans",
        f"Mensualite : {sim.get('mensualite', 0):,.0f} EUR/mois",
        f"Cout total credit : {sim.get('cout_total', 0):,.0f} EUR",
        f"Total interets : {sim.get('cout_interets', 0):,.0f} EUR",
        "",
        f"PTZ : {'ELIGIBLE' if ptz.get('eligible') else 'NON ELIGIBLE'}" + (f" — {ptz.get('montant_ptz', 0):,.0f} EUR (zone {ptz.get('zone', '?')})" if ptz.get("eligible") else ""),
    ])

    # ═══ SLIDE 8 : PREDICTIONS ═══
    pred = prediction.get("predictions", prediction.get("data", {}).get("predictions", []))
    tendance = prediction.get("tendances_historiques", prediction.get("data", {}).get("tendances_historiques", {}))
    pred_lines = [
        f"Variation 1 an historique : {tendance.get('variation_1ans_pct', 0):+.1f}%",
        f"Variation 5 ans historique : {tendance.get('variation_5ans_pct', 0):+.1f}%",
    ]
    if pred:
        for p in [pred[0], pred[11] if len(pred) > 11 else None, pred[-1] if len(pred) > 23 else None]:
            if p:
                pred_lines.append(f"  {p.get('mois', '')}: {p.get('prix_m2_predit', 0):,.0f} EUR/m2 [{p.get('fourchette_basse', 0):,.0f} - {p.get('fourchette_haute', 0):,.0f}]")
    add_content_slide("PREDICTIONS PRIX (3 ANS)", pred_lines)

    # ═══ SLIDE 9 : SOURCES ═══
    add_content_slide("SOURCES & METHODOLOGIE", [
        "DVF : data.gouv.fr (DGFiP) — transactions reelles enregistrees",
        "DPE : ADEME — diagnostics de performance energetique",
        "SIRENE : INSEE — registre des entreprises",
        "Georisques : BRGM — risques naturels et technologiques",
        "AVM : modele PropTech — estimation par comparables ponderes",
        "",
        "Estimation indicative — ne constitue pas un avis professionnel.",
        "Consultez un expert avant toute decision d'investissement.",
    ])

    # ═══ SLIDE 10 : CONCLUSION ═══
    verdict = "OPPORTUNITE" if est.get("estimation", 0) > prix * 1.05 else "A NEGOCIER" if est.get("estimation", 0) > prix * 0.9 else "PRIX ELEVE"
    add_content_slide("CONCLUSION", [
        f"VERDICT : {verdict}",
        "",
        f"Prix demande : {prix:,.0f} EUR | Estimation AVM : {est.get('estimation', 0):,.0f} EUR",
        f"Marche : {s.get('nb_transactions', 0)} transactions, tendance {'+' if tendance.get('variation_1ans_pct', 0) > 0 else ''}{tendance.get('variation_1ans_pct', 0):.1f}%/an",
        f"Mensualite credit : {sim.get('mensualite', 0):,.0f} EUR/mois",
        "",
        "Prochaines etapes :",
        "1. Visite du bien",
        "2. Negociation du prix",
        "3. Montage du dossier bancaire",
    ])

    abs_path = os.path.abspath(output_path)
    prs.save(abs_path)
    return abs_path
