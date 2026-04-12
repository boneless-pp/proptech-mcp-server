"""Prompts MCP — 7 workflows immobiliers professionnels.

Chaque prompt guide Claude a orchestrer les tools PropTech
dans le bon ordre pour produire un livrable professionnel.
"""

from proptech_mcp_server import mcp


# ════════════════════════════════════════════════════
# 1. DOSSIER BANQUE
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_dossier_banque",
    description="Genere un dossier d'investissement complet pour presenter a un banquier. Inclut estimation AVM, comparables DVF, plan financement, simulation cashflow, comparaison fiscale.",
)
async def dossier_banque(
    adresse: str,
    code_postal: str,
    type_bien: str,
    surface: float,
    prix: float,
    apport: float = 0,
    taux: float = 3.5,
    duree_ans: int = 20,
    loyer_vise: float = 0,
    regime_fiscal: str = "lmnp",
) -> str:
    return f"""Tu es un analyste immobilier senior. Genere un DOSSIER D'INVESTISSEMENT BANCAIRE complet et professionnel.

## BIEN ANALYSE
- Adresse : {adresse}, {code_postal}
- Type : {type_bien} | Surface : {surface} m2
- Prix demande : {prix:,.0f} EUR | Apport : {apport:,.0f} EUR
- Loyer vise : {loyer_vise:,.0f} EUR/mois
- Credit : {taux}% sur {duree_ans} ans | Regime : {regime_fiscal}

## ETAPES A SUIVRE (dans cet ordre)

1. **Estimation AVM** — Appelle `estimer_valeur_bien` avec code_postal={code_postal}, surface={surface}, type_bien={type_bien}, prix_demande={prix}
   → Verifie si le prix demande est coherent avec le marche (flag si ecart > 15%)

2. **Comparables DVF** — Appelle `rechercher_transactions_dvf` avec code_postal={code_postal}, type_bien={type_bien}, limit=20
   → Selectionne les 10 comparables les plus pertinents (surface similaire, recents)

3. **Tendance marche** — Appelle `consulter_statistiques_prix` avec ville correspondant au {code_postal}
   → Montre l'evolution 5 ans et la tendance (haussiere/baissiere/stable)

4. **Prediction prix** — Appelle `predire_evolution_prix` avec code_postal={code_postal}, type_bien={type_bien}
   → Projette les prix a 1, 2 et 3 ans

5. **Simulation credit** — Appelle `simuler_financement` avec montant={prix}, taux_annuel={taux}, duree_ans={duree_ans}, apport={apport}
   → Calcule mensualite, cout total, taux d'endettement, eligibilite PTZ

6. **Cout renovation** — Si DPE F ou G, appelle `estimer_cout_renovation` avec surface={surface}, classe_dpe concernee
   → Estime les travaux et aides MaPrimeRenov

7. **Fiche parcelle** — Si coordonnees disponibles, appelle `consulter_fiche_parcelle`
   → PLU, transports, ecoles, risques

## FORMAT DU LIVRABLE

Produis un rapport structure en Markdown avec ces sections :

### 1. SYNTHESE EXECUTIVE (1 page)
- Verdict : Opportunite / A negocier / A eviter
- Prix demande vs estimation AVM (ecart %)
- Rendement brut et net estimes
- Cashflow mensuel net apres credit
- Score de confiance /100

### 2. ANALYSE DU BIEN
- Estimation AVM avec fourchette
- 10 comparables DVF (tableau : adresse, date, prix, surface, prix/m2)
- Positionnement prix du bien vs marche

### 3. ANALYSE DU MARCHE
- Evolution prix/m2 sur 5 ans (decrire la tendance)
- Volume de transactions (dynamisme)
- Predictions a 3 ans
- Tension locative de la zone

### 4. PLAN DE FINANCEMENT
- Tableau : prix + frais notaire + travaux = cout total
- Mensualite credit vs loyer vise
- Taux d'endettement (rappel : max 35% HCSF)
- Cashflow mensuel detaille (loyer - credit - charges - impots)

### 5. COMPARAISON FISCALE
- Tableau comparatif LMNP micro / LMNP reel / Foncier reel / SCI IS
- Impot annuel estime pour chaque regime
- Recommandation du regime optimal

### 6. ENVIRONNEMENT & RISQUES
- Fiche parcelle (PLU, transports, ecoles)
- Risques naturels
- DPE et obligations

### 7. CONCLUSION
- Go / No-Go argumente
- Points forts et points de vigilance
- Prochaines etapes recommandees

### DISCLAIMER
"Document a usage indicatif — ne constitue pas un conseil en investissement. Les estimations sont basees sur les donnees DVF publiques (data.gouv.fr) et le modele AVM PropTech. Consultez un professionnel avant toute decision."

## STYLE
- Ton professionnel, factuel, chiffre
- Format : tableaux pour les donnees, listes pour les analyses
- Devise : EUR avec separateur milliers (espace)
- Toujours citer les sources (DVF data.gouv.fr, ADEME, INSEE)
"""


# ════════════════════════════════════════════════════
# 2. ETUDE DE MARCHE
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_etude_marche",
    description="Produit une etude de marche immobilier professionnelle pour une zone geographique. Inclut evolution prix, volumes, DPE, predictions, opportunites.",
)
async def etude_marche(
    code_postal: str,
    type_bien: str = "",
    periode_annees: int = 5,
) -> str:
    type_filtre = f", type_bien={type_bien}" if type_bien else ""
    return f"""Tu es un analyste de marche immobilier. Produis une ETUDE DE MARCHE PROFESSIONNELLE.

## ZONE ANALYSEE
- Code postal : {code_postal}
- Type de bien : {type_bien or "Tous types"}
- Periode : {periode_annees} dernieres annees

## ETAPES

1. **Stats marche** — `consulter_statistiques_prix` avec ville du {code_postal}
2. **Transactions recentes** — `rechercher_transactions_dvf` avec code_postal={code_postal}{type_filtre}, limit=50
3. **Predictions** — `predire_evolution_prix` avec code_postal={code_postal}
4. **Passoires DPE** — `detecter_passoires_dpe` avec departement={code_postal[:2]}
5. **Signaux off-market** — `detecter_signaux_offmarket` avec departement={code_postal[:2]}

## LIVRABLE — Rapport Markdown structure

### 1. CONTEXTE GEOGRAPHIQUE
- Presentation de la zone (departement, ville, bassin economique)
- Population, emploi, attractivite

### 2. EVOLUTION DES PRIX (graphique decrit)
- Prix median /m2 actuel
- Evolution sur {periode_annees} ans (hausse/baisse en %)
- Comparaison avec la moyenne departementale

### 3. VOLUME DES TRANSACTIONS
- Nombre de ventes par an
- Tendance (acceleration/ralentissement)
- Delai moyen de vente estime

### 4. REPARTITION PAR TYPE
- Appartements vs Maisons (% et prix moyens)
- Par nombre de pieces
- Par tranche de prix

### 5. PREDICTIONS A 3 ANS
- Scenario optimiste / realiste / pessimiste
- Facteurs d'influence (taux, demographie, emploi)

### 6. PANORAMA DPE
- Repartition des classes energetiques
- Nombre de passoires F/G
- Impact Loi Climat sur le parc

### 7. OPPORTUNITES DETECTEES
- Top 10 signaux off-market avec scores
- Passoires DPE a fort potentiel renovation

### 8. SYNTHESE & RECOMMANDATIONS
- Le marche est-il porteur pour l'investissement ?
- Quel type de bien privilegier ?
- Budget recommande pour un premier investissement

Source : DVF (data.gouv.fr), ADEME (DPE), SIRENE, PropTech AVM.
Disclaimer : Estimation indicative — ne constitue pas un avis professionnel.
"""


# ════════════════════════════════════════════════════
# 3. RAPPORT PROSPECTION
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_rapport_prospection",
    description="Identifie et analyse les meilleures opportunites off-market dans une zone. Scoring, fiches detaillees, simulations financieres.",
)
async def rapport_prospection(
    code_postal: str,
    budget_max: float,
    type_bien: str = "",
    objectif: str = "locatif",
) -> str:
    return f"""Tu es un expert en prospection immobiliere off-market. Produis un RAPPORT DE PROSPECTION complet.

## CRITERES
- Zone : {code_postal} | Budget max : {budget_max:,.0f} EUR
- Type : {type_bien or "Tous"} | Objectif : {objectif}

## ETAPES

1. **Signaux off-market** — `detecter_signaux_offmarket` avec departement={code_postal[:2]}
   → Filtre par budget < {budget_max:,.0f} EUR

2. **Passoires DPE** — `detecter_passoires_dpe` avec departement={code_postal[:2]}
   → Croise avec signaux pour identifier les opportunites renovation

3. **Top 5** — Pour chaque opportunite du top 5 :
   a. `estimer_valeur_bien` avec les parametres du bien
   b. `simuler_financement` avec montant=prix, apport=20%
   c. `estimer_cout_renovation` si passoire DPE

## LIVRABLE

### 1. METHODOLOGIE
- Explication du scoring off-market (SCI, decotes, rotations, baisses)
- Criteres de filtrage appliques

### 2. TABLEAU RECAPITULATIF
| # | Adresse | Type | Signal | Score | Prix | Estimation | Ecart | DPE |
Pour chaque opportunite detectee

### 3. FICHES TOP 5 (1 section par bien)
- Score et signaux detectes
- Prix demande vs estimation AVM
- DPE et cout renovation si applicable
- Simulation financement (mensualite, cashflow)
- Rendement brut/net estime
- Verdict : Priorite haute / moyenne / basse

### 4. COMPARATIF TOP 5
Tableau synthetique : rendement, cashflow, risque, effort renovation

### 5. RECOMMANDATION
- Meilleure opportunite et pourquoi
- Plan d'action en 5 etapes
- Calendrier de suivi (relances proprietaires)

Objectif {objectif} : adapte les recommandations en consequence.
"""


# ════════════════════════════════════════════════════
# 4. AVIS DE VALEUR
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_avis_valeur",
    description="Produit un avis de valeur professionnel pour un bien specifique. Document utilise par les agents immobiliers pour obtenir un mandat de vente.",
)
async def avis_valeur(
    adresse: str,
    code_postal: str,
    type_bien: str,
    surface: float,
    nb_pieces: int = 0,
    classe_dpe: str = "",
) -> str:
    return f"""Tu es un expert en evaluation immobiliere. Produis un AVIS DE VALEUR professionnel.

## BIEN
- Adresse : {adresse}, {code_postal}
- Type : {type_bien} | Surface : {surface} m2 | Pieces : {nb_pieces or "N/C"}
- DPE : {classe_dpe or "Non renseigne"}

## ETAPES

1. **Estimation AVM** — `estimer_valeur_bien` avec code_postal={code_postal}, surface={surface}, type_bien={type_bien}, classe_dpe={classe_dpe}
2. **Comparables** — `rechercher_transactions_dvf` avec code_postal={code_postal}, type_bien={type_bien}, limit=15
3. **Marche local** — `consulter_statistiques_prix` avec ville du {code_postal}
4. **Risques** — `evaluer_risques_naturels` si coordonnees disponibles

## LIVRABLE — Avis de valeur formate

### EN-TETE
Avis de valeur — {adresse}, {code_postal}
Date : [date du jour]

### ESTIMATION
- **Valeur estimee : [montant] EUR**
- Fourchette : [bas] EUR a [haut] EUR
- Prix/m2 estime : [montant] EUR/m2
- Score de confiance : [X]/100

### METHODE D'EVALUATION
Estimation par comparaison avec [N] transactions DVF reelles
enregistrees dans un rayon de 2 km sur les 3 dernieres annees.
Ajustements appliques : surface, DPE, localisation.

### COMPARABLES RETENUS
| Adresse | Date | Surface | Prix | Prix/m2 | Ecart |
(Top 8 comparables les plus pertinents)

### ANALYSE DU MARCHE LOCAL
- Prix median /m2 : [X] EUR
- Tendance : hausse/baisse de [X]% sur 1 an
- Volume : [X] transactions sur 12 mois
- Tension : marche tendu/detendu

### ENVIRONNEMENT
- Transports, ecoles, commerces a proximite
- DPE et obligations reglementaires

### DISCLAIMER
"Cet avis de valeur est etabli a titre indicatif sur la base des transactions
DVF publiques (source : data.gouv.fr) et du modele AVM PropTech.
Il ne constitue pas une expertise immobiliere au sens de la Charte de l'Expertise.
Pour une evaluation certifiee, consultez un expert agree."
"""


# ════════════════════════════════════════════════════
# 5. ANALYSE RENTABILITE
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_analyse_rentabilite",
    description="Analyse complete de rentabilite d'un investissement locatif avec comparaison de 9 scenarios (3 durees x 3 regimes fiscaux).",
)
async def analyse_rentabilite(
    code_postal: str,
    type_bien: str,
    surface: float,
    prix: float,
    loyer_mensuel: float,
    travaux: float = 0,
    charges_copro: float = 0,
    taxe_fonciere: float = 0,
) -> str:
    return f"""Tu es un conseiller en investissement locatif. Produis une ANALYSE DE RENTABILITE multi-scenarios.

## BIEN
- Code postal : {code_postal} | Type : {type_bien} | Surface : {surface} m2
- Prix : {prix:,.0f} EUR | Travaux : {travaux:,.0f} EUR
- Loyer mensuel vise : {loyer_mensuel:,.0f} EUR
- Charges copro : {charges_copro:,.0f} EUR/an | Taxe fonciere : {taxe_fonciere:,.0f} EUR/an

## ETAPES

1. **Verification prix** — `estimer_valeur_bien` avec code_postal={code_postal}, surface={surface}, prix_demande={prix}

2. **3 simulations duree** — Appelle `simuler_financement` 3 fois :
   - 15 ans : montant={prix}, duree_ans=15
   - 20 ans : montant={prix}, duree_ans=20
   - 25 ans : montant={prix}, duree_ans=25

3. **Tendance** — `consulter_statistiques_prix` pour projeter la plus-value

4. **DPE** — `rechercher_dpe` avec code_postal={code_postal} pour verifier les obligations

## LIVRABLE

### 1. SYNTHESE (tableau 3x3)
| | LMNP Reel | Foncier Reel | SCI IS |
|15 ans| cashflow / rendement | ... | ... |
|20 ans| ... | ... | ... |
|25 ans| ... | ... | ... |

### 2. DETAIL PAR SCENARIO (pour chaque combinaison)
- Mensualite credit
- Charges annuelles (copro + TF + assurance + gestion)
- Revenu imposable selon le regime
- Impot annuel estime (TMI 30% par defaut)
- Cashflow mensuel net apres impot
- Rendement net-net

### 3. INDICATEURS CLES
- Rendement brut : loyer annuel / prix total x 100
- Rendement net : (loyer - charges) / prix total x 100
- Cashflow : loyer - credit - charges - impots
- Point mort : annee ou le bien s'autofinance
- TRI sur 10 ans (avec plus-value estimee)

### 4. RECOMMANDATION
- Meilleur scenario et pourquoi
- Le bien est-il autofinance ? (cashflow >= 0)
- Risques identifies (vacance locative, travaux, DPE)

Calculs en EUR, formatage francais. Citer les sources DVF et les hypotheses.
"""


# ════════════════════════════════════════════════════
# 6. VEILLE MARCHE
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_veille_marche",
    description="Briefing periodique sur l'etat d'un marche immobilier local. KPIs, transactions recentes, opportunites, alertes.",
)
async def veille_marche(
    code_postal: str,
    type_bien: str = "",
) -> str:
    return f"""Tu es un analyste de veille immobiliere. Produis un BRIEFING MARCHE synthetique.

## ZONE : {code_postal} | Type : {type_bien or "Tous"}

## ETAPES
1. `consulter_statistiques_prix` avec ville du {code_postal}
2. `rechercher_transactions_dvf` avec code_postal={code_postal}, limit=10
3. `detecter_signaux_offmarket` avec departement={code_postal[:2]}
4. `detecter_passoires_dpe` avec departement={code_postal[:2]}

## FORMAT — Briefing email/Markdown court

### MARCHE {code_postal} — Briefing [date]

**KPIs CLES**
- Prix median /m2 : [X] EUR ([+/-X]% vs mois precedent)
- Volume transactions 12 mois : [X]
- Delai moyen de vente : [X] jours
- Nouvelles opportunites off-market : [X]

**TOP 3 TRANSACTIONS RECENTES**
1. [type] [surface]m2 — [prix] EUR ([prix/m2] EUR/m2) — [date]
2. ...
3. ...

**TOP 3 OPPORTUNITES**
1. [signal] — [adresse] — Score [X]/100 — [detail]
2. ...
3. ...

**ALERTES**
- [Alertes DPE, changements reglementaires, tendances]

**TENDANCE EN 1 PHRASE**
[Resume en une phrase : "Le marche de [ville] est [stable/haussier/baissier] avec [X] opportunites detectees."]

---
Source : DVF data.gouv.fr, ADEME, SIRENE | PropTech MCP
"""


# ════════════════════════════════════════════════════
# 7. DUE DILIGENCE
# ════════════════════════════════════════════════════

@mcp.prompt(
    name="proptech_due_diligence",
    description="Verification complete avant achat — checklist Go/No-Go avec feux tricolores sur tous les criteres (prix, marche, risques, DPE, PLU).",
)
async def due_diligence(
    adresse: str,
    code_postal: str,
    type_bien: str,
    surface: float,
    prix_demande: float,
) -> str:
    return f"""Tu es un expert en due diligence immobiliere. Produis une CHECKLIST GO/NO-GO complete.

## BIEN A VERIFIER
- Adresse : {adresse}, {code_postal}
- Type : {type_bien} | Surface : {surface} m2
- Prix demande : {prix_demande:,.0f} EUR

## ETAPES DE VERIFICATION

1. **PRIX** — `estimer_valeur_bien` avec code_postal={code_postal}, surface={surface}, type_bien={type_bien}, prix_demande={prix_demande}
   → VERT si ecart < 10% | JAUNE si 10-20% | ROUGE si > 20% au-dessus

2. **MARCHE** — `consulter_statistiques_prix` + `predire_evolution_prix`
   → VERT si tendance haussiere | JAUNE si stable | ROUGE si baissiere

3. **RISQUES** — `evaluer_risques_naturels` avec coordonnees GPS
   → VERT si risque faible | JAUNE si risque moyen | ROUGE si risque eleve

4. **DPE** — `rechercher_dpe` avec adresse={adresse}, code_postal={code_postal}
   → VERT si A-D | JAUNE si E | ROUGE si F-G (interdiction location)

5. **PARCELLE** — `consulter_fiche_parcelle` avec coordonnees
   → Verifier PLU (zone constructible), servitudes, fibre, transports

6. **HISTORIQUE** — `rechercher_transactions_dvf` avec code_postal={code_postal}
   → JAUNE si reventes rapides (< 3 ans) sur le meme bien

7. **OFF-MARKET** — `detecter_signaux_offmarket` avec departement={code_postal[:2]}
   → Verifier si ce bien apparait dans les signaux (SCI, decote, rotation)

## LIVRABLE — Checklist avec feux

### CHECKLIST DUE DILIGENCE — {adresse}

| Critere | Status | Detail |
|---------|--------|--------|
| Prix coherent | [VERT/JAUNE/ROUGE] | Ecart X% vs estimation AVM |
| Marche porteur | [VERT/JAUNE/ROUGE] | Tendance X% sur 1 an |
| Risques naturels | [VERT/JAUNE/ROUGE] | Detail des risques |
| DPE conforme | [VERT/JAUNE/ROUGE] | Classe X, obligations |
| PLU favorable | [VERT/JAUNE/ROUGE] | Zone, servitudes |
| Transports | [VERT/JAUNE/ROUGE] | Distance station |
| Fibre optique | [VERT/JAUNE/ROUGE] | Eligible/non eligible |
| Historique ventes | [VERT/JAUNE/ROUGE] | Nb reventes, duree detention |
| Signaux off-market | [INFO] | SCI, decote, rotation detectes |

### VERDICT GLOBAL
- Score : [X] criteres VERT / [X] JAUNE / [X] ROUGE
- **DECISION : GO / GO AVEC RESERVES / NO-GO**

### JUSTIFICATION
Pour chaque critere JAUNE ou ROUGE, explication detaillee et action recommandee.

### PROCHAINES ETAPES
Si GO : 1. Visiter 2. Negocier 3. Notaire 4. Financement 5. Travaux
Si NO-GO : Raisons et alternatives suggerees

Disclaimer : Verification indicative basee sur les donnees publiques.
Consultez un notaire et un diagnostiqueur avant toute acquisition.
"""
