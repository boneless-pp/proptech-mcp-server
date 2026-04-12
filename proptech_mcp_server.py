"""PropTech MCP Server — Expose l'API immobiliere comme outils MCP.

13 tools pour analyser le marche immobilier francais :
- Transactions DVF, estimation AVM, prediction prix
- Passoires DPE, renovation energetique, aides
- Prospection off-market, fiche parcelle
- Simulation financiere, risques naturels
- Gestion portefeuille

Usage:
    # Dev (stdio, lance par Claude Code)
    PROPTECH_API_BASE=http://localhost:5000/api/v1 PROPTECH_API_KEY=pt_xxx python proptech_mcp_server.py

    # Prod (HTTP, service Railway)
    MCP_TRANSPORT=streamable_http MCP_PORT=8080 python proptech_mcp_server.py
"""

from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("proptech-mcp")

# ════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════

API_BASE = os.environ.get("PROPTECH_API_BASE", "http://localhost:5000/api/v1")
API_KEY = os.environ.get("PROPTECH_API_KEY", "")
TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")
PORT = int(os.environ.get("MCP_PORT", "8080"))

# ════════════════════════════════════════════════════
# HTTP CLIENT (lifespan-managed)
# ════════════════════════════════════════════════════

_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(server):
    """Initialise le client HTTP async partage."""
    global _client
    _client = httpx.AsyncClient(
        base_url=API_BASE,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30.0,
    )
    log.info("PropTech MCP connecte a %s", API_BASE)
    yield
    await _client.aclose()
    log.info("PropTech MCP arrete")


mcp = FastMCP(
    "PropTech Immobilier",
    instructions="Outils d'analyse immobiliere francaise : transactions DVF, estimation AVM, DPE, off-market, simulation credit, renovation. 20 tools couvrant le cycle complet investisseur immobilier.",
    lifespan=lifespan,
)


# ════════════════════════════════════════════════════
# RATE LIMITING (simple in-memory, per-tool)
# ════════════════════════════════════════════════════

import time
from collections import defaultdict

_call_log: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = int(os.environ.get("MCP_RATE_LIMIT", "30"))  # calls per minute
_RATE_WINDOW = 60  # seconds


def _check_rate_limit(tool_name: str) -> str | None:
    """Returns error message if rate limited, None otherwise."""
    now = time.time()
    window_start = now - _RATE_WINDOW
    _call_log[tool_name] = [t for t in _call_log[tool_name] if t > window_start]
    if len(_call_log[tool_name]) >= _RATE_LIMIT:
        return f"Rate limit atteint ({_RATE_LIMIT} appels/min pour {tool_name}). Reessayez dans quelques secondes."
    _call_log[tool_name].append(now)
    return None


# ════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════

async def _get(path: str, params: dict | None = None, tool_name: str = "") -> dict:
    """GET vers l'API PropTech avec gestion d'erreurs et rate limiting."""
    if tool_name:
        rl = _check_rate_limit(tool_name)
        if rl:
            return {"error": rl}
    r = await _client.get(path, params={k: v for k, v in (params or {}).items() if v is not None})
    r.raise_for_status()
    return r.json()


async def _post(path: str, json_data: dict, tool_name: str = "") -> dict:
    """POST vers l'API PropTech avec gestion d'erreurs et rate limiting."""
    if tool_name:
        rl = _check_rate_limit(tool_name)
        if rl:
            return {"error": rl}
    r = await _client.post(path, json={k: v for k, v in json_data.items() if v is not None})
    r.raise_for_status()
    return r.json()


def _err(e: Exception) -> str:
    """Formate une erreur pour le LLM."""
    if isinstance(e, httpx.HTTPStatusError):
        try:
            body = e.response.json()
            return f"Erreur API ({e.response.status_code}): {body.get('error', str(body))}"
        except Exception:
            return f"Erreur API ({e.response.status_code}): {e.response.text[:200]}"
    return f"Erreur: {e}"


# ════════════════════════════════════════════════════
# PYDANTIC MODELS (Input validation)
# ════════════════════════════════════════════════════

class DVFParams(BaseModel):
    code_postal: Optional[str] = Field(None, description="Code postal (ex: 33000)")
    ville: Optional[str] = Field(None, description="Nom de la ville (ex: Bordeaux)")
    departement: Optional[str] = Field(None, description="Code departement (ex: 33)")
    type_bien: Optional[str] = Field(None, description="Type: Appartement, Maison, Local, Dependance")
    prix_min: Optional[float] = Field(None, description="Prix minimum en euros")
    prix_max: Optional[float] = Field(None, description="Prix maximum en euros")
    limit: Optional[int] = Field(50, description="Nombre max de resultats (defaut: 50)")


class AVMParams(BaseModel):
    code_postal: str = Field(..., description="Code postal du bien (requis)")
    surface: float = Field(..., description="Surface habitable en m2 (requis)")
    type_bien: Optional[str] = Field(None, description="Appartement, Maison, ou autre")
    nombre_pieces: Optional[int] = Field(None, description="Nombre de pieces")
    classe_dpe: Optional[str] = Field(None, description="Classe DPE: A, B, C, D, E, F, G")
    prix_demande: Optional[float] = Field(None, description="Prix demande (pour verdict)")


class PredictionParams(BaseModel):
    code_postal: Optional[str] = Field(None, description="Code postal")
    departement: Optional[str] = Field(None, description="Code departement")
    type_bien: Optional[str] = Field(None, description="Appartement ou Maison")


class DPEParams(BaseModel):
    code_postal: Optional[str] = Field(None, description="Code postal")
    adresse: Optional[str] = Field(None, description="Adresse du bien")


class PassoiresParams(BaseModel):
    departement: Optional[str] = Field(None, description="Code departement (ex: 33)")
    ville: Optional[str] = Field(None, description="Nom de la ville")
    classe_dpe: Optional[str] = Field(None, description="Filtrer par classe: F ou G")


class OffMarketParams(BaseModel):
    departement: Optional[str] = Field(None, description="Code departement (requis si pas de ville)")
    ville: Optional[str] = Field(None, description="Nom de la ville")


class ParcelleParams(BaseModel):
    latitude: float = Field(..., description="Latitude GPS (ex: 44.8378)")
    longitude: float = Field(..., description="Longitude GPS (ex: -0.5792)")


class RisquesParams(BaseModel):
    latitude: float = Field(..., description="Latitude GPS")
    longitude: float = Field(..., description="Longitude GPS")


class SimulationParams(BaseModel):
    montant: float = Field(..., description="Prix du bien en euros")
    taux_annuel: float = Field(3.5, description="Taux d'interet annuel en %")
    duree_ans: int = Field(20, description="Duree du credit en annees")
    apport: float = Field(0, description="Apport personnel en euros")
    revenu_mensuel: float = Field(0, description="Revenu mensuel net (pour capacite)")
    code_dept: str = Field("75", description="Departement pour eligibilite PTZ")


class RenovationParams(BaseModel):
    surface: float = Field(..., description="Surface en m2")
    classe_dpe: str = Field(..., description="Classe DPE actuelle: E, F, ou G")
    type_batiment: Optional[str] = Field(None, description="maison ou appartement")


# ════════════════════════════════════════════════════
# MCP TOOLS
# ════════════════════════════════════════════════════

@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def rechercher_transactions_dvf(params: DVFParams) -> str:
    """Recherche des transactions immobilieres DVF (Demandes de Valeurs Foncieres).

    Interroge la base de 6,7 millions de transactions reelles publiees par la DGFiP.
    Utile pour : connaitre les prix de vente reels d'un quartier, comparer les prix/m2,
    identifier les tendances de marche.

    Retourne : liste de transactions avec adresse, date, prix, surface, type, prix/m2.
    """
    try:
        data = await _get("/dvf", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def estimer_valeur_bien(params: AVMParams) -> str:
    """Estime la valeur d'un bien immobilier par comparaison avec les transactions DVF.

    Le modele AVM (Automated Valuation Model) identifie les ventes comparables dans le secteur,
    les pondere par proximite geographique, similarite de surface et recence,
    puis applique des ajustements (DPE, etage, equipements, localisation).

    Retourne : estimation en euros, fourchette de confiance, score de fiabilite /100,
    liste des comparables utilises, rendement locatif estime.
    """
    try:
        data = await _post("/avm", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def predire_evolution_prix(params: PredictionParams) -> str:
    """Predit l'evolution des prix immobiliers sur 3 ans (modele Prophet).

    Analyse les tendances historiques DVF et projette les prix futurs
    avec intervalles de confiance. Utile pour les decisions d'investissement.

    Retourne : prix median actuel, predictions mensuelles, tendance haussiere/baissiere,
    variation estimee a 1 an et 3 ans.
    """
    try:
        data = await _get("/predict", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def consulter_statistiques_prix(
    ville: str = Field(description="Nom de la ville"),
) -> str:
    """Consulte les statistiques de prix immobilier d'une ville.

    Retourne : prix median /m2, evolution recente, volume de transactions,
    repartition par type de bien, tendances.
    """
    try:
        data = await _get("/prix", {"ville": ville})
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def rechercher_dpe(params: DPEParams) -> str:
    """Recherche les diagnostics de performance energetique (DPE) via l'ADEME.

    Permet de connaitre la classe energetique (A a G) d'un bien ou d'une zone.
    Les classes F et G sont des passoires thermiques soumises a des restrictions locatives.

    Retourne : liste de DPE avec classe, consommation kWh/an, emissions CO2, surface.
    """
    try:
        data = await _get("/dpe", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def detecter_passoires_dpe(params: PassoiresParams) -> str:
    """Detecte les passoires energetiques (DPE F ou G) dans une zone.

    Croise les donnees ADEME et le portefeuille pour identifier les biens
    a forte decote energetique. La loi Climat & Resilience interdit
    progressivement leur mise en location : G depuis 2025, F en 2028.

    Utile pour : prospection de biens a renover, strategie achat-renovation.
    Retourne : liste de passoires avec adresse, classe DPE, surface, source.
    """
    try:
        data = await _get("/passoires", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def detecter_signaux_offmarket(params: OffMarketParams) -> str:
    """Detecte les signaux off-market indiquant des opportunites d'achat.

    L'algorithme croise DVF et SIRENE pour identifier des biens a forte
    probabilite de vente avant qu'ils n'arrivent sur le marche :
    - SCI (societes civiles immobilieres) detectees via SIRENE
    - Decotes significatives (>30% sous la mediane du secteur)
    - Rotations rapides (2+ ventes en 5 ans)
    - Zones en baisse de prix

    Chaque signal recoit un score de 0 a 100.
    """
    try:
        data = await _get("/off-market", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def consulter_fiche_parcelle(params: ParcelleParams) -> str:
    """Consulte la fiche complete d'une parcelle en agregeant 9+ sources de donnees.

    A partir de coordonnees GPS, recupere en parallele :
    PLU (zones urbanisme), transports proches, ecoles, fibre,
    revenus du quartier (INSEE), transactions DVF a proximite.

    Utile pour : due diligence avant achat, evaluation d'un emplacement.
    """
    try:
        data = await _get("/parcelle", {"lat": params.latitude, "lng": params.longitude})
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def evaluer_risques_naturels(params: RisquesParams) -> str:
    """Evalue les risques naturels et technologiques d'un emplacement (Georisques).

    Verifie : inondation, mouvement de terrain, seisme, radon, SEVESO,
    retrait-gonflement des argiles, cavites souterraines.

    Retourne : niveau de risque global, detail par categorie, impact sur le prix.
    """
    try:
        data = await _get("/risques", {"lat": params.latitude, "lng": params.longitude})
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "idempotentHint": True},
)
async def simuler_financement(params: SimulationParams) -> str:
    """Simule un credit immobilier complet : mensualite, PTZ, cashflow.

    Calcule la mensualite, le cout total du credit, verifie le taux d'usure,
    simule l'eligibilite au Pret a Taux Zero (PTZ) par zone et profil,
    et evalue la capacite d'emprunt si le revenu est fourni.

    Retourne : mensualite, cout total, PTZ (montant, zone, quotite),
    capacite d'emprunt max, impact du taux sur le pouvoir d'achat.
    """
    try:
        data = await _post("/simulation", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def estimer_cout_renovation(params: RenovationParams) -> str:
    """Estime le cout de renovation energetique et les aides disponibles.

    Calcule le budget pour passer d'une classe DPE (E/F/G) a la classe cible (C/D),
    detaille les postes de travaux (isolation, chauffage, fenetres),
    et estime les aides MaPrimeRenov par profil fiscal.

    Retourne : cout total, postes de travaux, aides par tranche de revenus,
    reste a charge, plus-value estimee apres renovation.
    """
    try:
        data = await _post("/renovation", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def lister_biens_portefeuille(
    statut: Optional[str] = Field(None, description="Filtrer par statut: active, vendu, prospect"),
    ville: Optional[str] = Field(None, description="Filtrer par ville"),
) -> str:
    """Liste les biens immobiliers du portefeuille de l'organisation.

    Retourne : liste paginee avec adresse, ville, prix, surface, DPE, statut.
    """
    try:
        params = {}
        if statut:
            params["statut"] = statut
        if ville:
            params["ville"] = ville
        data = await _get("/properties", params)
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def consulter_compte_api() -> str:
    """Consulte les informations du compte API : organisation, plan, usage, quotas.

    Utile pour verifier les limites restantes avant de lancer des analyses.
    """
    try:
        data = await _get("/account")
        return str(data)
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════
# MCP TOOLS — ECRITURE (destructifs)
# ════════════════════════════════════════════════════

class CreatePropertyParams(BaseModel):
    ville: str = Field(..., description="Ville du bien (ex: Bordeaux)")
    code_postal: str = Field(..., description="Code postal (ex: 33000)")
    prix_demande: float = Field(..., description="Prix demande en euros")
    adresse: Optional[str] = Field(None, description="Adresse complete")
    surface: Optional[float] = Field(None, description="Surface habitable en m2")
    type_bien: Optional[str] = Field(None, description="Appartement, Maison, Local")
    nombre_pieces: Optional[int] = Field(None, description="Nombre de pieces")
    classe_dpe: Optional[str] = Field(None, description="Classe DPE: A a G")
    commentaire: Optional[str] = Field(None, description="Note ou commentaire libre")


class UpdatePropertyParams(BaseModel):
    property_id: str = Field(..., description="ID du bien a modifier")
    prix_demande: Optional[float] = Field(None, description="Nouveau prix en euros")
    statut: Optional[str] = Field(None, description="active, vendu, retire")
    surface: Optional[float] = Field(None, description="Surface en m2")
    classe_dpe: Optional[str] = Field(None, description="Classe DPE: A a G")
    commentaire: Optional[str] = Field(None, description="Note ou commentaire")


class CreateProspectParams(BaseModel):
    entreprise: str = Field(..., description="Nom de l'entreprise ou du bien (requis)")
    adresse: Optional[str] = Field(None, description="Adresse du bien")
    ville: Optional[str] = Field(None, description="Ville")
    code_postal: Optional[str] = Field(None, description="Code postal")
    statut: Optional[str] = Field("A Contacter", description="A Contacter, Contacte, En Discussion, Offre Envoyee, Gagne, Perdu")
    contact_nom: Optional[str] = Field(None, description="Nom du contact")
    contact_email: Optional[str] = Field(None, description="Email du contact")
    contact_telephone: Optional[str] = Field(None, description="Telephone du contact")
    notes: Optional[str] = Field(None, description="Notes libres")
    type_prospect: Optional[str] = Field(None, description="passoire, sci, off_market, manual")
    signal_detail: Optional[str] = Field(None, description="Detail du signal detecte")
    classe_dpe: Optional[str] = Field(None, description="Classe DPE si connue")
    surface: Optional[float] = Field(None, description="Surface en m2")
    prix: Optional[float] = Field(None, description="Prix estime en euros")


class UpdateProspectParams(BaseModel):
    prospect_id: str = Field(..., description="ID du prospect a modifier")
    statut: Optional[str] = Field(None, description="Nouveau statut CRM")
    notes: Optional[str] = Field(None, description="Notes mises a jour")
    contact_nom: Optional[str] = Field(None, description="Nom du contact")
    contact_email: Optional[str] = Field(None, description="Email du contact")
    contact_telephone: Optional[str] = Field(None, description="Telephone")


class BugReportParams(BaseModel):
    title: str = Field(..., description="Titre du bug (min 5 caracteres)")
    description: str = Field(..., description="Description detaillee (min 10 caracteres)")
    category: Optional[str] = Field("bug", description="bug, feature, ux, data, performance")
    severity: Optional[str] = Field("medium", description="low, medium, high, critical")
    page: Optional[str] = Field(None, description="Page concernee (ex: /dashboard)")


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def creer_bien(params: CreatePropertyParams) -> str:
    """Ajoute un bien immobilier au portefeuille de l'organisation.

    Cree un nouveau bien avec ses caracteristiques (ville, prix, surface, DPE).
    Le bien apparaitra dans l'onglet Biens du dashboard et sera pris en compte
    dans les estimations AVM et analyses.

    IMPORTANT : Cette action cree des donnees. Confirmez les details avec l'utilisateur.
    """
    try:
        data = await _post("/properties", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
)
async def modifier_bien(params: UpdatePropertyParams) -> str:
    """Modifie un bien existant dans le portefeuille.

    Met a jour le prix, le statut, la surface, le DPE ou le commentaire.
    Utilisez d'abord lister_biens_portefeuille() pour obtenir l'ID du bien.
    """
    try:
        payload = {k: v for k, v in params.model_dump().items() if k != 'property_id' and v is not None}
        r = await _client.patch(f"/properties/{params.property_id}", json=payload)
        r.raise_for_status()
        return str(r.json())
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
)
async def supprimer_bien(
    property_id: str = Field(description="ID du bien a supprimer"),
) -> str:
    """Supprime definitivement un bien du portefeuille.

    ATTENTION : Cette action est irreversible. Le bien sera retire de toutes
    les analyses, estimations et rapports.
    """
    try:
        r = await _client.delete(f"/properties/{property_id}")
        r.raise_for_status()
        return str(r.json())
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def creer_prospect(params: CreateProspectParams) -> str:
    """Ajoute un prospect au pipeline CRM de prospection.

    Cree un nouveau prospect avec ses informations (entreprise, adresse, contact).
    Le prospect apparaitra dans l'onglet Prospection (vue Table et Kanban).

    Utile apres avoir detecte un signal off-market ou une passoire DPE interessante.
    """
    try:
        data = await _post("/prospects", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
)
async def modifier_prospect(params: UpdateProspectParams) -> str:
    """Met a jour un prospect CRM (statut, notes, contact).

    Permet de faire avancer un prospect dans le pipeline :
    A Contacter → Contacte → En Discussion → Offre Envoyee → Gagne/Perdu
    """
    try:
        payload = {k: v for k, v in params.model_dump().items() if k != 'prospect_id' and v is not None}
        r = await _client.patch(f"/prospects/{params.prospect_id}", json=payload)
        r.raise_for_status()
        return str(r.json())
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
)
async def supprimer_prospect(
    prospect_id: str = Field(description="ID du prospect a supprimer"),
) -> str:
    """Supprime definitivement un prospect du pipeline CRM.

    ATTENTION : Cette action est irreversible.
    """
    try:
        r = await _client.delete(f"/prospects/{prospect_id}")
        r.raise_for_status()
        return str(r.json())
    except Exception as e:
        return _err(e)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
)
async def signaler_bug(params: BugReportParams) -> str:
    """Signale un bug ou une suggestion d'amelioration.

    Le rapport sera visible dans le dashboard admin de monitoring.
    Utile pour remonter des problemes detectes pendant l'utilisation.
    """
    try:
        data = await _post("/bugs", params.model_dump())
        return str(data)
    except Exception as e:
        return _err(e)


# ════════════════════════════════════════════════════
# ENTRYPOINT
# ════════════════════════════════════════════════════

if __name__ == "__main__":
    if TRANSPORT == "streamable_http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=PORT)
    else:
        mcp.run(transport="stdio")
