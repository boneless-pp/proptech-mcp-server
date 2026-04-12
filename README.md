# PropTech Immobilier France -- MCP Server

Le premier serveur MCP d'analyse immobiliere couvrant toute la France.
20 outils pour investisseurs, agents et promoteurs immobiliers.

## Quickstart (2 minutes)

### 1. Installer les dependances
```bash
pip install "mcp[cli]" httpx pydantic
```

### 2. Obtenir une cle API
Rendez-vous sur https://web-production-50ed3.up.railway.app et creez un compte.
Puis generez une cle API via `POST /api/v1/keys`.

### 3. Configurer Claude Code
Ajoutez a votre `.mcp.json` (racine du projet) :
```json
{
  "mcpServers": {
    "proptech": {
      "command": "python",
      "args": ["proptech_mcp_server.py"],
      "env": {
        "PROPTECH_API_BASE": "https://web-production-50ed3.up.railway.app/api/v1",
        "PROPTECH_API_KEY": "pt_votre_cle_ici"
      }
    }
  }
}
```

### 4. Relancez Claude Code
Les 20 tools PropTech apparaissent automatiquement.

### 5. Testez
Dites a Claude : "Estime la valeur d'un appartement de 65m2 a Bordeaux 33000"

## 20 outils disponibles

### Lecture (13 tools)
| Outil | Description |
|-------|-------------|
| `rechercher_transactions_dvf` | 6.7M+ transactions DVF reelles (data.gouv.fr) |
| `estimer_valeur_bien` | Estimation AVM par comparables ponderes |
| `predire_evolution_prix` | Prediction prix a 3 ans (Prophet) |
| `consulter_statistiques_prix` | Stats marche par ville |
| `rechercher_dpe` | Diagnostics energetiques ADEME |
| `detecter_passoires_dpe` | Passoires F/G + cout renovation |
| `detecter_signaux_offmarket` | SCI, decotes, rotations, baisses |
| `consulter_fiche_parcelle` | Fiche parcelle 9 sources |
| `evaluer_risques_naturels` | Georisques (inondation, seisme, radon) |
| `simuler_financement` | Credit + PTZ + capacite d'emprunt |
| `estimer_cout_renovation` | Renovation + aides MaPrimeRenov |
| `lister_biens_portefeuille` | Portfolio de l'organisation |
| `consulter_compte_api` | Usage et quotas |

### Ecriture (7 tools)
| Outil | Description |
|-------|-------------|
| `creer_bien` | Ajouter un bien au portfolio |
| `modifier_bien` | Mettre a jour prix, DPE, statut |
| `supprimer_bien` | Retirer un bien |
| `creer_prospect` | Sauvegarder un prospect CRM |
| `modifier_prospect` | Avancer dans le pipeline |
| `supprimer_prospect` | Supprimer un prospect |
| `signaler_bug` | Reporter un bug |

## Configuration

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `PROPTECH_API_BASE` | URL de l'API PropTech | Oui |
| `PROPTECH_API_KEY` | Cle API Bearer (format `pt_xxx`) | Oui |
| `MCP_TRANSPORT` | `stdio` (dev) ou `streamable_http` (prod) | Non (defaut: stdio) |
| `MCP_PORT` | Port HTTP (prod) | Non (defaut: 8080) |
| `MCP_RATE_LIMIT` | Appels max par minute par tool | Non (defaut: 30) |

## Pricing

| Plan | Prix | Appels/mois |
|------|------|-------------|
| Free | 0 EUR | 50 |
| Pro | 29 EUR | 2 000 |
| Business | 99 EUR | 10 000 |
| Enterprise | Sur devis | Illimite |

## Tests

```bash
PROPTECH_API_KEY=pt_votre_cle python test_mcp_tools.py
```

Resultat attendu : 20/20 passed.

## Sources de donnees

- **DVF** (Demandes de Valeurs Foncieres) -- data.gouv.fr, DGFiP
- **ADEME** -- Diagnostics de Performance Energetique (DPE)
- **SIRENE** -- Registre des entreprises (detection SCI)
- **IGN** -- Cadastre, PLU, batiments
- **Georisques** -- Risques naturels et technologiques
- **INSEE** -- Revenus (Filosofi), equipements (BPE)
- **ARCEP** -- Eligibilite fibre optique
- **BAN** -- Base Adresse Nationale (geocodage)

## Deploiement production

```bash
docker build -t proptech-mcp .
docker run -e PROPTECH_API_BASE=https://... -e PROPTECH_API_KEY=pt_... -e MCP_TRANSPORT=streamable_http -p 8080:8080 proptech-mcp
```

## Licence

Proprietary -- PropTech SaaS
