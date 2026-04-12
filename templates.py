"""Templates MCP — Structures de livrables PPTX et Excel.

Expose les structures slide-par-slide et onglet-par-onglet
que Claude doit suivre pour generer des dossiers professionnels
conformes aux standards du cabinet.
"""

import json
from proptech_mcp_server import mcp


# ════════════════════════════════════════════════════
# TEMPLATE PPTX — DOSSIER INVESTISSEMENT (25 slides)
# ════════════════════════════════════════════════════

@mcp.resource("proptech://templates/pptx-dossier-investissement")
async def template_pptx_dossier() -> str:
    """Template PowerPoint 25 slides pour dossier d'investissement immobilier.

    Chaque slide a un titre, un objectif, le contenu attendu, et les sources de donnees.
    Basee sur les dossiers Gaillon et Pacy-sur-Eure valides par le cabinet.
    """
    return json.dumps({
        "format": "PowerPoint 16:9 (widescreen)",
        "style": {
            "couleur_primaire": "#1E56A0",
            "couleur_accent": "#2563EB",
            "couleur_fond": "#FFFFFF",
            "police_titres": "Calibri Bold",
            "police_corps": "Calibri",
            "taille_titre": 28,
            "taille_corps": 14,
        },
        "slides": [
            {
                "numero": 1,
                "titre": "PAGE DE GARDE",
                "objectif": "Premiere impression professionnelle",
                "contenu": [
                    "Nom de la ville en grand (ex: GAILLON (27600))",
                    "Sous-titre: Dossier d'Investissement Immobilier",
                    "Date du dossier",
                    "Logo ou nom du cabinet en bas",
                    "Photo du bien si disponible en fond",
                ],
                "source_donnees": "Parametres utilisateur",
            },
            {
                "numero": 2,
                "titre": "SOMMAIRE",
                "objectif": "Navigation rapide du dossier",
                "contenu": [
                    "Liste numerotee des sections principales",
                    "Utiliser des icones ou puces pour chaque section",
                    "Inclure les numeros de slides pour reference",
                ],
                "source_donnees": "Auto-genere",
            },
            {
                "numero": 3,
                "titre": "INTRODUCTION",
                "objectif": "Contexte et objectif du projet",
                "contenu": [
                    "Presentation en 3-5 lignes du projet",
                    "Type d'investissement (locatif, revente, renovation)",
                    "Montant total de l'operation",
                    "Objectif de rendement vise",
                    "Timeline du projet",
                ],
                "source_donnees": "Parametres utilisateur + contexte",
            },
            {
                "numero": 4,
                "titre": "LOCALISATION & ACCESSIBILITE",
                "objectif": "Montrer que l'emplacement est strategique",
                "contenu": [
                    "Carte de localisation (departement, region)",
                    "Distances aux grandes villes (Paris, Rouen, etc.)",
                    "Acces: autoroute, gare SNCF, bus",
                    "Temps de trajet vers les poles d'emploi",
                    "Population de la commune et bassin de vie",
                ],
                "source_donnees": "consulter_fiche_parcelle (transport, revenus)",
            },
            {
                "numero": 5,
                "titre": "CONTEXTE DU PROJET",
                "objectif": "Pourquoi cette opportunite maintenant",
                "contenu": [
                    "Comment le bien a ete identifie (off-market, annonce, prospection)",
                    "Signaux off-market detectes (SCI, decote, rotation)",
                    "Raison de la vente si connue",
                    "Urgence ou timing favorable",
                ],
                "source_donnees": "detecter_signaux_offmarket",
            },
            {
                "numero": 6,
                "titre": "DESCRIPTION DU PROJET",
                "objectif": "Vue d'ensemble du bien et de l'operation",
                "contenu": [
                    "Type de bien, surface totale, nb de lots",
                    "Etat actuel (habitable, a renover, a diviser)",
                    "Strategie: achat-revente, location, division",
                    "Schema ou plan du projet",
                ],
                "source_donnees": "Parametres utilisateur",
            },
            {
                "numero": 7,
                "titre": "PRESENTATION DU SITE",
                "objectif": "Faire visualiser le bien",
                "contenu": [
                    "Photos du bien (facade, interieur, terrain)",
                    "Informations cadastrales (parcelle, section)",
                    "Surface du terrain vs surface habitable",
                    "PLU : zone, droits a construire",
                ],
                "source_donnees": "consulter_fiche_parcelle (PLU, cadastre)",
            },
            {
                "numero": 8,
                "titre": "PROJET DE DECOUPAGE EN LOTS",
                "objectif": "Montrer la strategie de division si applicable",
                "contenu": [
                    "Schema de division: nb de lots, surfaces",
                    "Type de chaque lot (terrain, appartement, local, garage)",
                    "Destination: vente ou location pour chaque lot",
                    "Si pas de division: presenter le bien en l'etat",
                ],
                "source_donnees": "Parametres utilisateur",
            },
            {
                "numero": 9,
                "titre": "DETAIL DES LOTS",
                "objectif": "Fiche technique par lot",
                "contenu": [
                    "Tableau: Lot | Type | Surface | Destination | Prix estime",
                    "Pour chaque lot: description, atouts, travaux",
                    "Si terrains constructibles: COS, emprise au sol, regle PLU",
                ],
                "source_donnees": "Parametres utilisateur + estimer_valeur_bien par lot",
            },
            {
                "numero": 10,
                "titre": "BIENS EXISTANTS (maison, studio, garage)",
                "objectif": "Detail des biens habitables existants",
                "contenu": [
                    "Surface habitable, nb pieces, etat",
                    "DPE actuel et obligations",
                    "Estimation valeur unitaire",
                    "Potentiel locatif ou revente",
                ],
                "source_donnees": "estimer_valeur_bien + rechercher_dpe",
            },
            {
                "numero": 11,
                "titre": "ATOUTS & FAIBLESSES (SWOT)",
                "objectif": "Analyse equilibree forces/risques",
                "contenu": [
                    "Tableau SWOT en 4 quadrants:",
                    "Forces: prix bas, emplacement, potentiel division",
                    "Faiblesses: travaux, DPE, acces",
                    "Opportunites: marche haussier, demande locative",
                    "Menaces: reglementation, marche baissier",
                ],
                "source_donnees": "Synthese de toutes les analyses",
            },
            {
                "numero": 12,
                "titre": "ANALYSE DU MARCHE",
                "objectif": "Prouver que le marche est porteur",
                "contenu": [
                    "Prix median /m2 et evolution 5 ans",
                    "Volume de transactions (dynamisme)",
                    "Comparaison avec communes voisines",
                    "Graphique: evolution prix/m2 avec tendance",
                    "Tension locative de la zone",
                ],
                "source_donnees": "consulter_statistiques_prix + predire_evolution_prix",
            },
            {
                "numero": 13,
                "titre": "ETUDE DE MARCHE — BIENS SIMILAIRES",
                "objectif": "Benchmark prix pour justifier le prix de revente",
                "contenu": [
                    "Tableau: 10-15 comparables DVF recents",
                    "Colonnes: Adresse | Date | Surface | Prix | Prix/m2",
                    "Mediane, moyenne, fourchette",
                    "Positionnement du bien vs comparables",
                ],
                "source_donnees": "rechercher_transactions_dvf (filtre par type)",
            },
            {
                "numero": 14,
                "titre": "ETUDE DE MARCHE — SEGMENT SPECIFIQUE",
                "objectif": "Zoom sur le segment cible (studios, terrains, etc.)",
                "contenu": [
                    "Comparables filtres par le type exact du lot",
                    "Prix de vente constates pour ce segment",
                    "Demande locative specifique (studios = forte demande etudiante, etc.)",
                ],
                "source_donnees": "rechercher_transactions_dvf (filtre type_bien)",
            },
            {
                "numero": 15,
                "titre": "ETUDE COMPLEMENTAIRE (optionnel)",
                "objectif": "Analyse d'un segment additionnel si multi-lots",
                "contenu": [
                    "Meme structure que slide 14 pour un autre segment",
                    "Ex: si le projet a des terrains ET des appartements",
                ],
                "source_donnees": "rechercher_transactions_dvf",
            },
            {
                "numero": 16,
                "titre": "CONDITIONS D'ACHAT",
                "objectif": "Recap du deal negociable",
                "contenu": [
                    "Prix demande vs prix de marche (AVM)",
                    "Marge de negociation recommandee",
                    "Frais de notaire estimes (7.5% ancien)",
                    "Conditions suspensives (financement, urbanisme)",
                    "Timeline achat: compromis → acte → travaux",
                ],
                "source_donnees": "estimer_valeur_bien + resource frais-notaire",
            },
            {
                "numero": 17,
                "titre": "BUDGET TRAVAUX ESTIMATIF",
                "objectif": "Chiffrer les travaux necessaires",
                "contenu": [
                    "Tableau detaille poste par poste:",
                    "Gros oeuvre, second oeuvre, finitions",
                    "Mise aux normes DPE si F/G",
                    "Total HT et TTC",
                    "Aides disponibles (MaPrimeRenov, CEE)",
                    "Marge de securite (+10-15%)",
                ],
                "source_donnees": "estimer_cout_renovation + resource bareme-maprimenov",
            },
            {
                "numero": 18,
                "titre": "PRIX DE REVENTE PAR LOT",
                "objectif": "Projeter les prix de sortie",
                "contenu": [
                    "Tableau: Lot | Type | Surface | Prix vente estime | Base (AVM/comparables)",
                    "Total prix de revente",
                    "Comparaison avec prix d'achat + travaux",
                    "Plus-value brute estimee",
                ],
                "source_donnees": "estimer_valeur_bien pour chaque lot",
            },
            {
                "numero": 19,
                "titre": "RENTABILITE GLOBALE",
                "objectif": "Le chiffre cle que le banquier/investisseur veut voir",
                "contenu": [
                    "Tableau synthetique:",
                    "Prix achat + frais notaire + travaux = COUT TOTAL",
                    "Prix de revente total = RECETTES",
                    "PLUS-VALUE NETTE = Recettes - Cout total",
                    "RENDEMENT = Plus-value / Cout total x 100",
                    "ROI en % et en EUR",
                    "Duree estimee de l'operation",
                ],
                "source_donnees": "Calcul a partir des slides precedentes",
            },
            {
                "numero": 20,
                "titre": "STRATEGIE DE REVENTE / LOCATION",
                "objectif": "Plan d'action commercial",
                "contenu": [
                    "Timeline de mise en vente/location par lot",
                    "Canaux de commercialisation (agences, portails, off-market)",
                    "Scenario optimiste (6 mois) vs realiste (12 mois)",
                    "Impact du DPE sur la strategie",
                ],
                "source_donnees": "Analyse de marche + DPE",
            },
            {
                "numero": 21,
                "titre": "SIMULATION CASHFLOW",
                "objectif": "Projection financiere mensuelle",
                "contenu": [
                    "Tableau 12-24 mois: mois | depense | recette | solde",
                    "Phase 1: achat + travaux (depenses)",
                    "Phase 2: revenus location ou vente (recettes)",
                    "Point mort: mois ou le projet s'autofinance",
                    "Graphique cashflow cumule",
                ],
                "source_donnees": "simuler_financement",
            },
            {
                "numero": 22,
                "titre": "POURQUOI CET INVESTISSEMENT",
                "objectif": "Arguments de conviction (pour le banquier/partenaire)",
                "contenu": [
                    "5 arguments cles en bullet points",
                    "Prix sous le marche (ecart % AVM)",
                    "Marche local porteur (tendance haussiere)",
                    "Strategie claire et testee",
                    "Risques maitrisables",
                    "Rendement superieur au marche",
                ],
                "source_donnees": "Synthese globale",
            },
            {
                "numero": 23,
                "titre": "RECAPITULATIF DES LOTS",
                "objectif": "Vue synthetique en un coup d'oeil",
                "contenu": [
                    "Tableau final: tous les lots avec prix achat, travaux, revente, marge",
                    "Total general en bas",
                    "Code couleur: vert = marge > 20%, jaune = 10-20%, rouge = < 10%",
                ],
                "source_donnees": "Compilation slides 9-19",
            },
            {
                "numero": 24,
                "titre": "SOURCES & METHODOLOGIE",
                "objectif": "Credibiliser le dossier avec les sources",
                "contenu": [
                    "DVF : data.gouv.fr (DGFiP) — transactions reelles",
                    "DPE : ADEME — diagnostics energetiques",
                    "SIRENE : INSEE — registre des entreprises",
                    "Georisques : BRGM — risques naturels",
                    "AVM : modele PropTech — estimation par comparables ponderes",
                    "Disclaimer: estimation indicative",
                ],
                "source_donnees": "Auto-genere",
            },
            {
                "numero": 25,
                "titre": "CONCLUSION & PROCHAINES ETAPES",
                "objectif": "Call to action",
                "contenu": [
                    "Verdict final: GO / GO AVEC RESERVES / NO-GO",
                    "3 prochaines etapes concretes avec dates",
                    "Ex: 1. Visite du site (semaine N)",
                    "    2. Offre d'achat (semaine N+1)",
                    "    3. Compromis chez le notaire (semaine N+3)",
                    "Coordonnees de contact",
                ],
                "source_donnees": "Synthese + parametres utilisateur",
            },
        ],
    })


# ════════════════════════════════════════════════════
# TEMPLATE EXCEL — SYNTHESE FINANCIERE (5 onglets)
# ════════════════════════════════════════════════════

@mcp.resource("proptech://templates/excel-synthese-financiere")
async def template_excel_synthese() -> str:
    """Template Excel 5 onglets pour synthese financiere immobiliere.

    Structure basee sur les fichiers Synthese financiere valides.
    Chaque onglet a sa structure de colonnes et formules.
    """
    return json.dumps({
        "format": "Excel .xlsx",
        "onglets": [
            {
                "nom": "Projet",
                "objectif": "Fiche d'identite du projet",
                "lignes": [
                    {"label": "Lien de l'annonce", "valeur": "[URL]"},
                    {"label": "Adresse", "valeur": "[adresse complete]"},
                    {"label": "Ville", "valeur": "[ville]"},
                    {"label": "Code postal", "valeur": "[code_postal]"},
                    {"label": "Type de bien", "valeur": "[type]"},
                    {"label": "Surface totale", "valeur": "[surface] m2"},
                    {"label": "Surface terrain", "valeur": "[surface_terrain] m2"},
                    {"label": "Nombre de lots prevus", "valeur": "[nb_lots]"},
                    {"label": "DPE actuel", "valeur": "[classe_dpe]"},
                    {"label": "Annee construction", "valeur": "[annee]"},
                    {"label": "Prix demande", "valeur": "[prix] EUR"},
                    {"label": "Frais notaire (7.5%)", "valeur": "=prix*0.075"},
                    {"label": "Budget travaux", "valeur": "[travaux] EUR"},
                    {"label": "COUT TOTAL", "valeur": "=prix+frais+travaux", "format": "gras, fond bleu"},
                    {"label": "Source", "valeur": "PropTech MCP / DVF data.gouv.fr"},
                ],
            },
            {
                "nom": "Bilan",
                "objectif": "Bilan financier complet avec simulation credit et cashflow",
                "sections": [
                    {
                        "titre": "RESUME DU PROJET",
                        "colonnes": ["Label", "Valeur"],
                        "lignes": [
                            "Prix du bien", "Honoraires d'Agence", "Frais de notaire",
                            "Budget travaux", "COUT TOTAL ACQUISITION",
                            "Apport personnel", "Montant a emprunter",
                        ],
                    },
                    {
                        "titre": "SIMULATION CREDIT",
                        "colonnes": ["Label", "15 ans", "20 ans", "25 ans"],
                        "lignes": [
                            "Taux", "Mensualite", "Cout total credit",
                            "Total interets", "Cout total operation",
                        ],
                    },
                    {
                        "titre": "REVENUS LOCATIFS",
                        "colonnes": ["Lot", "Type", "Surface", "Loyer mensuel", "Loyer annuel"],
                        "lignes": ["Un lot par ligne", "Total en bas"],
                    },
                    {
                        "titre": "CASHFLOW MENSUEL",
                        "colonnes": ["Label", "Scenario 15 ans", "Scenario 20 ans", "Scenario 25 ans"],
                        "lignes": [
                            "Loyer total", "- Mensualite credit", "- Taxe fonciere (/12)",
                            "- Charges copro (/12)", "- Assurance PNO (/12)",
                            "- Vacance locative (5%)", "- Gestion locative (7%)",
                            "= CASHFLOW NET MENSUEL",
                        ],
                    },
                    {
                        "titre": "RENTABILITE",
                        "colonnes": ["Indicateur", "Valeur"],
                        "lignes": [
                            "Rendement brut (%)", "Rendement net (%)",
                            "Rendement net-net apres impots (%)",
                            "Cashflow annuel net", "TRI sur 10 ans",
                        ],
                    },
                    {
                        "titre": "COMPARAISON FISCALE",
                        "colonnes": ["Regime", "Revenu imposable", "Impot", "Cashflow net"],
                        "lignes": [
                            "LMNP Micro-BIC (abattement 50%)",
                            "LMNP Reel (amortissement)",
                            "Foncier Micro (abattement 30%)",
                            "Foncier Reel (deduction travaux)",
                            "SCI IS (taux 15/25%)",
                        ],
                    },
                    {
                        "titre": "SCENARIO REVENTE",
                        "colonnes": ["Lot", "Prix revente", "Marge", "Marge %"],
                        "lignes": ["Un lot par ligne", "TOTAL"],
                    },
                ],
            },
            {
                "nom": "Etude Marche (DVF)",
                "objectif": "Transactions comparables DVF pour justifier les prix",
                "colonnes": [
                    "Adresse", "Ville", "Type", "Surface (m2)",
                    "Prix (EUR)", "Prix/m2 (EUR)", "Date vente", "Source",
                ],
                "instructions": [
                    "Remplir avec les resultats de rechercher_transactions_dvf",
                    "Filtrer par type_bien similaire et rayon 5km",
                    "Trier par date decroissante",
                    "Ajouter une ligne MEDIANE et MOYENNE en bas",
                    "Mettre en surbrillance les biens les plus comparables",
                ],
                "source_donnees": "rechercher_transactions_dvf",
            },
            {
                "nom": "Etude Marche (Annonces)",
                "objectif": "Benchmark des prix actuellement en vente (si disponible)",
                "colonnes": [
                    "Adresse", "Type", "Surface", "Prix", "Prix/m2",
                    "Source (LBC/SeLoger)", "Lien",
                ],
                "instructions": [
                    "Optionnel : comparables en vente actuellement",
                    "Si pas de donnees d'annonces, noter 'Non disponible via API'",
                    "Utiliser les donnees DVF comme reference principale",
                ],
            },
            {
                "nom": "Etude Habitations",
                "objectif": "Focus sur le marche residentiel local",
                "sections": [
                    {
                        "titre": "Appartements",
                        "colonnes": ["Adresse", "Superficie", "Prix", "Date de la vente", "Prix/m2"],
                    },
                    {
                        "titre": "Maisons",
                        "colonnes": ["Adresse", "Superficie", "Prix", "Date de la vente", "Prix/m2"],
                    },
                ],
                "instructions": [
                    "Remplir via rechercher_transactions_dvf filtre Appartement puis Maison",
                    "10-15 comparables par type",
                    "Calculer mediane et moyenne par type",
                ],
                "source_donnees": "rechercher_transactions_dvf",
            },
        ],
    })
