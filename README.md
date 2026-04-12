# PropTech Immobilier France — MCP Server

Le premier serveur MCP d'analyse immobiliere couvrant toute la France.

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

## Installation

```bash
pip install "mcp[cli]" httpx pydantic
```

## Configuration

Variables d'environnement requises :
- `PROPTECH_API_BASE` — URL de l'API (ex: `https://web-production-50ed3.up.railway.app/api/v1`)
- `PROPTECH_API_KEY` — Cle API Bearer (format `pt_xxx`)

### Claude Code (.mcp.json)
```json
{
  "mcpServers": {
    "proptech": {
      "command": "python",
      "args": ["mcp_server/proptech_mcp_server.py"],
      "env": {
        "PROPTECH_API_BASE": "https://votre-instance.railway.app/api/v1",
        "PROPTECH_API_KEY": "pt_votre_cle_ici"
      }
    }
  }
}
```

## Pricing

| Plan | Prix | Appels/mois |
|------|------|-------------|
| Free | 0 EUR | 50 |
| Pro | 29 EUR | 2 000 |
| Business | 99 EUR | 10 000 |
| Enterprise | Sur devis | Illimite |

## Sources de donnees

- DVF (Demandes de Valeurs Foncieres) — data.gouv.fr
- ADEME (DPE) — Diagnostics energetiques
- SIRENE — Registre des entreprises (SCI)
- IGN — Cadastre, PLU, batiments
- Georisques — Risques naturels/technologiques
- INSEE — Revenus, equipements (BPE, Filosofi)
- ARCEP — Eligibilite fibre
- BAN — Geocodage adresses
