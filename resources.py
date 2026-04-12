"""Resources MCP — Donnees de reference immobilieres France.

Expose des baremes, calendriers et taux utiles aux workflows
sans necessiter d'appel API. Accessible via proptech://reference/*.
"""

import json
from proptech_mcp_server import mcp


@mcp.resource("proptech://reference/calendrier-dpe")
async def calendrier_dpe() -> str:
    """Calendrier d'interdiction de location par classe DPE (Loi Climat & Resilience)."""
    return json.dumps({
        "G": {"interdit_depuis": "01/01/2025", "statut": "INTERDIT", "impact": "Location interdite, vente avec decote 15-25%"},
        "F": {"interdit_a_partir": "01/01/2028", "statut": "BIENTOT INTERDIT", "impact": "Pression a la vente, decote 10-15%"},
        "E": {"interdit_a_partir": "01/01/2034", "statut": "A SURVEILLER", "impact": "Renovation recommandee, decote 5-8%"},
        "D": {"statut": "CONFORME", "impact": "Aucune restriction"},
        "C": {"statut": "CONFORME", "impact": "Bien classe, valorisation +2-3%"},
        "B": {"statut": "PERFORMANT", "impact": "Valorisation +4-5%"},
        "A": {"statut": "EXCELLENT", "impact": "Valorisation +5-8%, tres recherche"},
        "source": "Loi Climat & Resilience du 22 aout 2021, decrets 2023-2025",
    })


@mcp.resource("proptech://reference/fiscalite-immobiliere")
async def fiscalite_immobiliere() -> str:
    """Comparatif des regimes fiscaux immobiliers en France 2026."""
    return json.dumps({
        "lmnp_micro": {
            "nom": "LMNP Micro-BIC",
            "plafond_recettes": 77700,
            "abattement": "50%",
            "avantages": "Simple, pas de comptabilite",
            "inconvenients": "Pas d'amortissement, pas de deduction travaux",
            "ideal_pour": "Petites surfaces, peu de charges",
        },
        "lmnp_reel": {
            "nom": "LMNP au Reel",
            "plafond_recettes": "Aucun",
            "amortissement": True,
            "duree_amortissement_immeuble": "25-30 ans",
            "duree_amortissement_mobilier": "5-10 ans",
            "avantages": "Amortissement = quasi zero impot pendant 10-15 ans",
            "inconvenients": "Comptable obligatoire (~600-1200 EUR/an)",
            "ideal_pour": "Investissement locatif meuble, surfaces moyennes",
        },
        "foncier_micro": {
            "nom": "Micro-Foncier",
            "plafond_recettes": 15000,
            "abattement": "30%",
            "avantages": "Ultra simple",
            "inconvenients": "Abattement faible, pas de deduction travaux",
            "ideal_pour": "Location nue, peu de charges",
        },
        "foncier_reel": {
            "nom": "Foncier au Reel",
            "plafond_recettes": "Aucun",
            "deduction_travaux": True,
            "deficit_foncier": {"plafond": 10700, "report": "10 ans"},
            "avantages": "Deduction integrale des travaux, deficit foncier",
            "inconvenients": "Location nue obligatoire 3 ans apres deficit",
            "ideal_pour": "Biens a renover avec gros travaux",
        },
        "sci_is": {
            "nom": "SCI a l'IS",
            "taux_is": "15% jusqu'a 42500 EUR, 25% au-dela",
            "amortissement": True,
            "avantages": "Amortissement + taux IS reduit + tresorerie en societe",
            "inconvenients": "Plus-value pro a la revente (pas d'abattement duree), double imposition dividendes",
            "ideal_pour": "Patrimoine > 3 biens, strategie long terme, transmission",
        },
        "source": "Code General des Impots 2026, bareme LMNP/LMP mis a jour",
    })


@mcp.resource("proptech://reference/taux-credit-2026")
async def taux_credit_2026() -> str:
    """Taux de credit immobilier moyens en France - avril 2026."""
    return json.dumps({
        "15_ans": {"excellent": 2.9, "bon": 3.2, "moyen": 3.5},
        "20_ans": {"excellent": 3.1, "bon": 3.5, "moyen": 3.8},
        "25_ans": {"excellent": 3.3, "bon": 3.7, "moyen": 4.0},
        "taux_usure": {
            "moins_10_ans": 4.31,
            "10_a_20_ans": 5.12,
            "plus_20_ans": 5.67,
        },
        "regles_hcsf": {
            "taux_endettement_max": 35,
            "duree_max_ans": 25,
            "exception_primo_accedant": "Tolerance 2 ans de plus (27 ans max)",
            "source": "HCSF decision 29 sept 2021, toujours en vigueur 2026",
        },
        "source": "Banque de France / courtiers, avril 2026",
    })


@mcp.resource("proptech://reference/frais-notaire")
async def frais_notaire() -> str:
    """Bareme frais de notaire ancien vs neuf."""
    return json.dumps({
        "ancien": {
            "taux_moyen": 7.5,
            "details": {
                "droits_mutation": 5.81,
                "emoluments_notaire": 0.8,
                "frais_divers": 0.9,
            },
            "exemple_200k": "~15 000 EUR",
        },
        "neuf": {
            "taux_moyen": 2.5,
            "details": "TVA incluse dans prix, emoluments reduits",
            "exemple_200k": "~5 000 EUR",
        },
        "source": "Bareme notaires 2026",
    })


@mcp.resource("proptech://reference/bareme-maprimenov-2026")
async def bareme_maprimenov() -> str:
    """Bareme MaPrimeRenov 2026 par profil fiscal et type de travaux."""
    return json.dumps({
        "profils": {
            "bleu": {"revenu_max_idf": 23541, "revenu_max_hors_idf": 17009, "label": "Tres modeste"},
            "jaune": {"revenu_max_idf": 28657, "revenu_max_hors_idf": 21805, "label": "Modeste"},
            "violet": {"revenu_max_idf": 40018, "revenu_max_hors_idf": 30549, "label": "Intermediaire"},
            "rose": {"revenu_max_idf": "Au-dela", "revenu_max_hors_idf": "Au-dela", "label": "Aise"},
        },
        "aides_renovation_globale": {
            "bleu": {"forfait": 63000, "pct_max": 80},
            "jaune": {"forfait": 45000, "pct_max": 60},
            "violet": {"forfait": 30000, "pct_max": 45},
            "rose": {"forfait": 15000, "pct_max": 30},
        },
        "bonus_sortie_passoire": 10000,
        "cee_complementaire": "10-15% du cout des travaux (primes CEE)",
        "condition": "Logement de plus de 15 ans, residence principale du locataire",
        "source": "ANAH / MaPrimeRenov bareme 2026",
    })


@mcp.resource("proptech://reference/zones-tendues")
async def zones_tendues() -> str:
    """Zones tendues et encadrement des loyers en France 2026."""
    return json.dumps({
        "villes_encadrement_loyers": [
            "Paris", "Lyon", "Villeurbanne", "Lille", "Hellemmes", "Lomme",
            "Montpellier", "Bordeaux", "Strasbourg", "Grenoble", "Marseille",
        ],
        "nb_communes_zone_tendue": "environ 1100 communes (zone A, A bis, B1)",
        "regles": {
            "loyer_reference": "Fixe par prefecture chaque annee",
            "majoration_max": "20% au-dessus du loyer de reference",
            "complement_loyer": "Justifie par caracteristiques exceptionnelles",
            "sanction": "Amende + remboursement au locataire",
        },
        "ptz": {
            "zone_a_bis": "Paris + petite couronne",
            "zone_a": "Grandes agglomerations",
            "zone_b1": "Villes moyennes dynamiques",
            "zone_b2_c": "Reste du territoire (PTZ limite)",
        },
        "source": "Decret zones tendues 2023, mise a jour 2026",
    })
