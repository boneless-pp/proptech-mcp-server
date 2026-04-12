"""Tests pour les 20 tools MCP PropTech.

Teste chaque tool contre l'API de production.
Usage: PROPTECH_API_KEY=pt_xxx python test_mcp_tools.py
"""

import asyncio
import os
import sys
import json

import httpx

API_BASE = os.environ.get("PROPTECH_API_BASE", "https://web-production-50ed3.up.railway.app/api/v1")
API_KEY = os.environ.get("PROPTECH_API_KEY", "")

PASS = 0
FAIL = 0
SKIP = 0


async def test_tool(client: httpx.AsyncClient, name: str, method: str, path: str,
                     params: dict = None, json_data: dict = None, expect_status: int = 200):
    """Teste un endpoint API correspondant a un tool MCP."""
    global PASS, FAIL, SKIP
    try:
        if method == "GET":
            r = await client.get(path, params=params)
        else:
            r = await client.post(path, json=json_data)

        if r.status_code == expect_status:
            # Verify response is valid JSON
            d = r.json()
            PASS += 1
            print(f"  \033[32mOK\033[0m {name} ({r.status_code})")
            return d
        else:
            FAIL += 1
            body = ""
            try:
                body = r.json().get("error", r.text[:100])
            except Exception:
                body = r.text[:100]
            print(f"  \033[31mFAIL\033[0m {name} — expected {expect_status}, got {r.status_code}: {body}")
            return None
    except Exception as e:
        FAIL += 1
        print(f"  \033[31mFAIL\033[0m {name} — exception: {e}")
        return None


async def main():
    global PASS, FAIL

    if not API_KEY:
        print("\033[31mERROR: PROPTECH_API_KEY not set\033[0m")
        print("Usage: PROPTECH_API_KEY=pt_xxx python test_mcp_tools.py")
        sys.exit(1)

    print(f"\n\033[1mPropTech MCP Server — Test Suite\033[0m")
    print(f"API: {API_BASE}")
    print(f"Key: {API_KEY[:12]}...")
    print()

    async with httpx.AsyncClient(
        base_url=API_BASE,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=20.0,
    ) as c:

        # ═══ LECTURE (13 tools) ═══
        print("\033[1m--- LECTURE (13 tools) ---\033[0m")

        # 1. Health (no auth)
        await test_tool(c, "health", "GET", "/health")

        # 2. Account
        await test_tool(c, "consulter_compte_api", "GET", "/account")

        # 3. Properties list
        await test_tool(c, "lister_biens_portefeuille", "GET", "/properties")

        # 4. DVF search
        await test_tool(c, "rechercher_transactions_dvf", "GET", "/dvf",
                        params={"departement": "33", "limit": "3"})

        # 5. AVM estimation
        await test_tool(c, "estimer_valeur_bien", "POST", "/avm",
                        json_data={"code_postal": "33000", "surface": 65})

        # 6. Price prediction
        await test_tool(c, "predire_evolution_prix", "GET", "/predict",
                        params={"code_postal": "33000"})

        # 7. Price stats
        await test_tool(c, "consulter_statistiques_prix", "GET", "/prix",
                        params={"ville": "Bordeaux"})

        # 8. DPE search
        await test_tool(c, "rechercher_dpe", "GET", "/dpe",
                        params={"code_postal": "33000", "adresse": "rue Sainte-Catherine"})

        # 9. Passoires DPE
        await test_tool(c, "detecter_passoires_dpe", "GET", "/passoires",
                        params={"departement": "33"})

        # 10. Off-market
        await test_tool(c, "detecter_signaux_offmarket", "GET", "/off-market",
                        params={"departement": "33"})

        # 11. Risques
        await test_tool(c, "evaluer_risques_naturels", "GET", "/risques",
                        params={"lat": "44.8378", "lng": "-0.5792"})

        # 12. Simulation
        await test_tool(c, "simuler_financement", "POST", "/simulation",
                        json_data={"montant": 300000, "taux_annuel": 3.5, "duree_ans": 20})

        # 13. Renovation
        await test_tool(c, "estimer_cout_renovation", "POST", "/renovation",
                        json_data={"surface": 80, "classe_dpe": "G"})

        # ═══ ECRITURE (7 tools) ═══
        print("\n\033[1m--- ECRITURE (7 tools) ---\033[0m")

        # 14. Create property
        d = await test_tool(c, "creer_bien", "POST", "/properties",
                           json_data={"ville": "MCP Test City", "code_postal": "99999",
                                      "prix_demande": 123456, "surface": 42},
                           expect_status=201)
        prop_id = d.get("data", {}).get("id") if d else None

        # 15. Update property (PATCH only)
        if prop_id:
            r = await c.patch(f"/properties/{prop_id}", json={"prix_demande": 130000})
            if r.status_code == 200:
                PASS += 1
                print(f"  \033[32mOK\033[0m modifier_bien PATCH ({r.status_code})")
            else:
                FAIL += 1
                print(f"  \033[31mFAIL\033[0m modifier_bien PATCH ({r.status_code})")
        else:
            FAIL += 1
            print(f"  \033[31mFAIL\033[0m modifier_bien — no property ID from create")

        # 16. Delete property
        if prop_id:
            r = await c.delete(f"/properties/{prop_id}")
            if r.status_code == 200:
                PASS += 1
                print(f"  \033[32mOK\033[0m supprimer_bien ({r.status_code})")
            else:
                FAIL += 1
                print(f"  \033[31mFAIL\033[0m supprimer_bien ({r.status_code})")
        else:
            FAIL += 1
            print(f"  \033[31mFAIL\033[0m supprimer_bien — skipped")

        # 17. Create prospect
        d = await test_tool(c, "creer_prospect", "POST", "/prospects",
                           json_data={"entreprise": "SCI MCP Test", "ville": "Paris",
                                      "statut": "A Contacter"},
                           expect_status=201)
        prosp_id = d.get("data", {}).get("id") if d else None

        # 18. Update prospect
        if prosp_id:
            r = await c.patch(f"/prospects/{prosp_id}", json={"statut": "Contacte"})
            if r.status_code == 200:
                PASS += 1
                print(f"  \033[32mOK\033[0m modifier_prospect ({r.status_code})")
            else:
                FAIL += 1
                print(f"  \033[31mFAIL\033[0m modifier_prospect ({r.status_code})")
        else:
            FAIL += 1
            print(f"  \033[31mFAIL\033[0m modifier_prospect — no prospect ID")

        # 19. Delete prospect
        if prosp_id:
            r = await c.delete(f"/prospects/{prosp_id}")
            if r.status_code == 200:
                PASS += 1
                print(f"  \033[32mOK\033[0m supprimer_prospect ({r.status_code})")
            else:
                FAIL += 1
                print(f"  \033[31mFAIL\033[0m supprimer_prospect ({r.status_code})")
        else:
            FAIL += 1
            print(f"  \033[31mFAIL\033[0m supprimer_prospect — skipped")

        # 20. Bug report
        await test_tool(c, "signaler_bug", "POST", "/bugs",
                       json_data={"title": "MCP test bug report auto",
                                  "description": "Test automatise du tool signaler_bug via le MCP server"},
                       expect_status=201)

    # ═══ RESULTS ═══
    total = PASS + FAIL
    print(f"\n\033[1m{'='*50}\033[0m")
    print(f"\033[1mResults: {PASS}/{total} passed\033[0m", end="")
    if FAIL > 0:
        print(f" — \033[31m{FAIL} FAILED\033[0m")
    else:
        print(f" — \033[32mALL PASSED\033[0m")
    print()

    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
