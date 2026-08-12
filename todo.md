# AI Banking Assistant — TODO / Roadmap

> **Statut global** : 🟢 **Phases 0–5 livrées** (Setup, Mock data, RAG docs, structure FastAPI, schéma Pydantic) ·
> 🟡 **Phase 6+ partiellement entamée** (orchestrateur / RAG / monitoring non intégrés à l'API) ·
> 🔴 **À faire** : Router, LLM service, branchement orchestrateur→API, monitoring, tests E2E, polish.

---

## 0. Vision produit

API unique `POST /chat` qui :

1. Reçoit `customer_id` + `message` (FR principalement).
2. Décide **automatiquement** entre trois modes :
   - **RAG seul** — questions générales (frais virement international, plafonds carte, procédure perte carte, etc.).
   - **Tool seul** — données personnelles (solde, transactions, carte, virement, fiche client).
   - **Tool + RAG** — donnée perso + explication de procédure (ex. virement refusé « pourquoi, que faire ? »).
3. Répond en JSON : `{"answer": "…", "source": "tool | RAG | tool+RAG", "documents": [...]?}`.
4. Ne **jamais inventer** une donnée client.
5. Carve‑out **observabilité** : Prometheus/Grafana + RAGAS.

---

## 1. État de l'existant (audit du repo)

| Composant | Fichier | Statut | Commentaire |
|---|---|---|---|
| Project scaffolding | `app/` (`api/`, `core/`, `models/`, `services/`, `tools/`, `rag/`, `tests/`) | ✅ | |
| Dépendances | `requirements.txt` | 🟡 | FastAPI 0.104, Chroma 0.4.22, LangChain 0.1.0, sentence-transformers, pandas — **manque** `google-generativeai` |
| Config | `app/core/config.py` | ✅ | `Settings` (Pydantic) — `APP_NAME`, `VERSION`, `API_V1_STR`, `EMBEDDING_MODEL`, `CHROMA_DB_PATH` |
| App FastAPI | `app/main.py` | ✅ | CORS + routes `/`, `/api/v1/chat`, `/health` |
| Schémas | `app/models/chat.py` | ✅ | `ChatRequest`, `ChatResponse`, `ToolRoute`, `*Response` |
| Routeur FastAPI | `app/api/chat.py` | 🟡 | `/chat` + `/health` présents, mais appelent `BankingOrchestrator` qui lève `NotImplementedError` |
| Orchestrateur | `app/services/orchestrator.py` | 🔴 | Squelette vide — `handle_chat` = `NotImplementedError` |
| Outils mockés | `app/tools/banking_tools.py` | ✅ | 5 fonctions ; regardent des CSV `data/*.csv` → `get_account_balance`, `get_transactions`, `get_card_info`, `get_transfer_status`, `get_customer_info` |
| RAG pipeline | `app/rag/rag_pipeline.py` | 🟡 | `BankingRAGPipeline` complet (load / chunk 500/50 / Chroma / HuggingFace / `k=4` / prompt FR) ; **pas instancié ni branché** |
| Données CSV | `data/{customers,accounts,cards,transactions,transfers}.csv` | ✅ | 5 clients seed `C1024..C1028` ; virement test `TR4587` (rejected, solde), `TR4588` (pending), `TR4589` (completed) |
| KB | `data/knowledge_base/*.md` (9 fichiers) | ✅ | `account_fees`, `account_opening`, `card_limits`, `card_policy`, `fraud_policy`, `international_transfer_fees`, `loan_information`, `lost_card_procedure`, `transfer_policy` |
| Tests | `app/tests/test_setup.py`, `app/tests/test_data.py` | ✅ | Existence fichiers + structure CSV — **pas de tests router / API / RAG** |
| `.env` | `app/.env` | ✅ | vide pour l'instant |
| `run.py` | `run.py` | ✅ | `uvicorn` port 8000 reload |
| Documentation | `README.md`, `architecture.md`, `roadmap.md`, `CLAUDE.md` | ✅ | |
| Monitoring | `app/monitoring/` | 🔴 | Dossier **inexistant** — Prometheus / Grafana / RAGAS à créer |

---

## 2. Phase 6 — Compléter le routage et l'orchestration (PRIORITÉ 1)

> Sans ça, l'API renvoie toujours `NotImplementedError`.

### 2.1 Implémenter le routeur

- **Créer** `app/services/router.py`
- **Classe** `RouteDecision` (dataclass) : `tool: str | None`, `parameters: dict`, `needs_rag: bool`, `missing_parameter: str | None`, `route_type: Literal["tool", "rag", "tool+rag", "clarification"]`.
- **Stratégie hybride** :
  1. **Regex / heuristiques** d'abord (priorité perf & robustesse) :
     - `TR\d{2,}` → détecte un `transfer_id`.
     - Mots clés `solde / balance` → `get_account_balance`.
     - Mots clés `transactions / paiements / opérations / historique` → `get_transactions`.
     - `carte / plafond / status` → `get_card_info`.
     - `mes informations / mon profil / fiche client` → `get_customer_info`.
     - `pourquoi / que dois-je faire / refusé / rejeté / comment` → flag `needs_rag=True`.
  2. **Fallback LLM** (optionnel phase 6bis) : prompt JSON qui retourne `{tool, parameters, needs_rag, reason}` — utilise le même LLM que le service de réponse.
- **Paramètres** :
  - `customer_id` injecté par défaut (depuis `ChatRequest`).
  - `transfer_id` extrait via regex.
  - `start_date` / `end_date` extraits via regex (`du JJ/MM/AAAA au JJ/MM/AAAA`).
- **Sorties** :
  - Si `contains_transfer_id` & pas d'ID → `missing_parameter="transfer_id"` → renvoie une **clarification** (`source="clarification"`).
  - Sinon renvoie la décision.

### 2.2 Implémenter un service LLM

- **Créer** `app/services/llm_service.py`
- **Provider** : **Google Gemini** via le SDK `google-generativeai`. Initialisation : `genai.configure(api_key=settings.GOOGLE_API_KEY)` puis `model = genai.GenerativeModel(...)`.
- **Trois prompts** distincts (FR) :
  1. `tool_only_prompt` — n'utilise QUE le résultat d'outil.
  2. `rag_only_prompt` — n'utilise QUE les docs RAG.
  3. `tool_rag_prompt` — combine les deux : "expliquez la situation perso, puis la règle générale".
- **Garde-fous** :
  - `temperature=0.1–0.2`.
  - Consigne explicite « n'invente aucune information » systématiquement dans le system prompt.
  - Système prompt racine :
    ```
    Tu es un assistant bancaire.
    Règles :
    1. Réponds uniquement à partir des informations fournies.
    2. N'invente jamais un identifiant, un solde, un statut ou un nom.
    3. Si une info manque, dis-le.
    4. Sois clair, concis et professionnel.
    ```

### 2.3 Implémenter l'orchestrateur

- **Mettre à jour** `app/services/orchestrator.py` :
  - Constructeur : instancie `Router`, `BankingRAGPipeline` (initialize), `LLMService`, `ToolService` (wrapper sur les 5 fonctions).
  - `handle_chat(customer_id, message)` :
    ```
    1. route = router.classify(customer_id, message)
    2. si route.missing_parameter -> clarification_response()
    3. si route.tool and route.needs_rag:
         tool_result = tool_service.call(route.tool, route.parameters)
         docs = rag_service.search(build_rag_query(message, tool_result))
         answer = llm.answer_tool_rag(message, tool_result, docs)
         return ChatResponse(answer, source=f"{route.tool}+RAG", documents=[doc.metadata['source'] for doc in docs])
    4. si route.tool:
         tool_result = tool_service.call(route.tool, route.parameters)
         answer = llm.answer_tool(message, tool_result)
         return ChatResponse(answer, source=route.tool)
    5. sinon (RAG only):
         docs = rag_service.search(message)
         answer = llm.answer_rag(message, docs)
         return ChatResponse(answer, source="RAG", documents=...)
    ```

### 2.4 Gestion d'erreurs

- **Mapper** les exceptions des outils :
  - `customer_not_found` → 200 avec `answer="Je n'ai trouvé aucun compte associé à cet identifiant client."` (+ `source="error"`).
  - `transfer_not_found` → idem formulation.
  - `FileNotFoundError` → 503 / `service_unavailable`.
  - `ValidationError` Pydantic → 422 géré par FastAPI.
- **Time-out** : timeout global 30 s sur `/chat` (middleware ou `asyncio.wait_for`).
- **Log structuré** (`json` par requête) : `route`, `tool_called`, `rag_query`, `latency_ms`, `status`.

### 2.5 Tests Phase 6

- `app/tests/test_router.py` — couvre les 4 routes (RAG, tool, tool+RAG, clarification).
- `app/tests/test_tools.py` — couvre les 5 outils + cas `customer_not_found` / `transfer_not_found`.
- `app/tests/test_api.py` — `TestClient` FastAPI sur `/chat` (4 cas fonctionnels).

---

## 3. Phase 7 — LLM branché et prompts (PRIORITÉ 1)

### 3.1 Choix du provider

- **Provider** : **Google Gemini** via `google-generativeai` (SDK officiel `google.generativeai`).
- **Modèles recommandés** :
  - **Production** : `gemini-1.5-pro` (qualité, raisonnement, contexte long).
  - **MVP / dev** : `gemini-1.5-flash` (rapide, peu cher, multilingue FR).
- **Variable d'env** : `GOOGLE_API_KEY` dans `app/.env` (à charger via `python-dotenv`).
- **.env.example** à créer documentant la clé.
- **Ajout aux dépendances** : `google-generativeai==0.3.2` dans `requirements.txt`.
- **Configuration** : initialiser le client une seule fois dans `LLMService.__init__` via `genai.configure(api_key=settings.GOOGLE_API_KEY)`.
- **Tarification Gemini** : free tier 15 RPM / 1 M TPM sur Flash → largement suffisant pour un MVP.

### 3.2 Prompts finaux

- Stocker dans `app/services/prompts.py` (centralisation).
- Tester chaque prompt manuellement avec les 3 exemples du `README.md`.

### 3.3 Latence / cache

- **Cache sémantique** léger (optionnel) : cache la sortie pour `(customer_id, message)` hashé — TTL 5 min.
- Instruments : `prometheus_client.Counter("cache_hits", ...)`.

---

## 4. Phase 8 — Monitoring & Observability (PRIORITÉ 2)

> `CLAUDE.md` annonce déjà la phase 6 monitoring, **mais elle n'est pas réalisée**.

### 4.1 Prometheus

- **Créer** `app/monitoring/metrics.py`
- **Métriques** :
  - `Counter("chat_requests_total", ["route_type"])` — par route (`rag`, `tool`, `tool_rag`, `clarification`, `error`).
  - `Histogram("chat_request_latency_seconds", ["route_type"])`.
  - `Counter("tool_calls_total", ["tool", "status"])`.
  - `Histogram("tool_latency_seconds", ["tool"])`.
  - `Counter("rag_queries_total")`.
  - `Histogram("rag_latency_seconds")`.
  - `Counter("cache_hits_total")`.
  - `Counter("error_total", ["type"])`.
- **Middleware** FastAPI : instrumenter `/chat` pour mesurer latence + status.
- **Endpoint** `GET /metrics` (via `prometheus_client.make_asgi_app()`).

### 4.2 Grafana

- **Créer** `monitoring/grafana/dashboards/banking_assistant.json` (export JSON).
- **3 dashboards** (cf. `architecture.md`) :
  1. *Overview* — request rate, error rate, p50/p95/p99 latency par route.
  2. *RAG quality* — RAGAS scores + volume de requêtes RAG.
  3. *Tools & errors* — tool success/failure, cache hit/miss.
- **Provisioning** : `monitoring/grafana/provisioning/datasources/datasource.yml` + `dashboards/dashboards.yml`.
- **Docker compose** (`monitoring/docker-compose.yml`) : Prometheus + Grafana.

### 4.3 RAGAS

- **Créer** `app/monitoring/ragas_eval.py`
- **Jeu de test** : `data/eval/ragas_testset.json` (10–20 requêtes annotées manuellement).
- **Métriques** : `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`.
- **Online sampling** : 5 % des requêtes prod notées en arrière-plan.
- **Offline CI** : `make eval-rag` lance l'évaluation sur le testset, génère un rapport Markdown.

---

## 5. Phase 9 — Tests & qualité (PRIORITÉ 2)

### 5.1 Tests unitaires

- **Framework** : `pytest` + `pytest-asyncio`.
- **Couverture cible** : ≥ 80 % sur `app/services/`, `app/tools/`, `app/rag/`, `app/api/`.
- **Fichiers à créer** :
  - `app/tests/test_router.py` (priorité haute)
  - `app/tests/test_tools.py`
  - `app/tests/test_rag.py`
  - `app/tests/test_api.py`
  - `app/tests/test_orchestrator.py`
  - `app/tests/test_error_handling.py`

### 5.2 Tests d'intégration

- **End-to-end** sur 4 scénarios :
  1. RAG : "Quels sont les frais pour un virement international ?"
  2. Tool : "Quel est mon solde ?" (`C1024`)
  3. Tool+RAG : "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?"
  4. Clarification : "Quel est le statut de mon virement ?" (sans ID)
- **Cas d'erreur** : customer inexistant, transfer inexistant, message vide.

### 5.3 Qualité code

- **Linter** : `ruff` (rapide, remplace flake8+isort).
- **Formatter** : `black`.
- **Type hints** : déjà en cours — viser 100 % sur `app/services/`.
- **Pre-commit** : `.pre-commit-config.yaml` (lint + format + tests sur staged).

---

## 6. Phase 10 — Documentation & polish (PRIORITÉ 3)

### 6.1 README

- **Mettre à jour** `README.md` :
  - Description + schéma d'architecture (ASCII ou mermaid).
  - **Installation** : `python -m venv .venv`, `pip install -r requirements.txt`, `cp .env.example .env`.
  - **Lancement** : `python run.py` (uvicorn sur 8000).
  - **Exemples** : 3 requêtes curl (RAG / tool / tool+RAG).
  - **Tests** : `pytest app/tests -v`.
  - **Monitoring** : `docker compose -f monitoring/docker-compose.yml up`.
  - **Limites** : pas d'auth, données mockées, LLM externe.

### 6.2 Exemples curl

```bash
# RAG
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C1024","message":"Quels sont les frais pour un virement international ?"}'

# Tool
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C1024","message":"Quel est mon solde ?"}'

# Tool + RAG
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C1024","message":"Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?"}'
```

### 6.3 Diagrammes

- Garder `architecture.md` à jour au fil des phases.
- Ajouter dans `docs/` (optionnel) un diagramme de séquence pour le flux `/chat`.

### 6.4 Bonus

- **Citations RAG** : réponse inclut `documents: ["international_transfer_fees.md"]`.
- **Logging structuré** JSON (déjà listé en 2.4).
- **Évaluation automatique** : dataset `data/eval/testset.json` avec `expected_source` — un script `scripts/eval_routing.py` calcule la précision du routeur.
- **Conversation multi-tours** (optionnel, après MVP) : `conversation_id` qui passe un historique léger.

---

## 7. Sécurité & production-readiness

- **Validation stricte** : `customer_id` non vide, longueur limitée, pattern alphanumérique.
- **Ne pas logger** : `customer_id` complet en production (PII) — utiliser des hashes.
- **Auth** (non MVP, mais à mentionner) : JWT ou API key.
- **Rate limiting** : `slowapi` ou middleware custom (10 req/s par IP).
- **Limitation outils** : chaque outil limité au `customer_id` du `ChatRequest` (vérifier côté `ToolService`).
- **.env** : ajouter `.env.example` listant les variables attendues.

---

## 8. Améliorations futures (backlog)

- 🔁 **Router LLM** (option 2 du `roadmap.md`) quand le regex est insuffisant.
- 🗣️ **Multi-tour** : `conversation_id` + mémoire légère.
- 🌍 **i18n** : extension EN/AR.
- 📊 **Streaming** : SSE sur `/chat` pour réponses LLM token par token.
- 🧪 **A/B testing** : deux prompts RAG côte à côte via Prometheus.
- 🗄️ **DB réelle** : remplacer les CSV par Postgres.
- 🔐 **Vault** : stockage des clés API.
- 🩺 **Healthcheck étendu** : `/health/live`, `/health/ready` (ping LLM, Chroma, CSV).

---

## 9. Checklist de livraison finale

### Fonctionnel
- [ ] `POST /chat` retourne 200 + JSON valide
- [ ] Question RAG → `source="RAG"`
- [ ] Question tool → `source="get_*"`
- [ ] Question mixte → `source="get_*+RAG"`
- [ ] Paramètre manquant → `source="clarification"`
- [ ] Customer / transfer introuvable → réponse explicite, pas d'invention
- [ ] Aucun appel outil inutile (RAG‑only = pas d'appel outil)

### Technique
- [ ] `pytest` ≥ 80 % de coverage
- [ ] `ruff` + `black` passent
- [ ] `GET /metrics` retourne du Prometheus valide
- [ ] Grafana affiche les 3 dashboards
- [ ] RAGAS score > 0.7 sur le testset
- [ ] README complet avec exemples curl
- [ ] `.env.example` à jour

### Démo
- [ ] 1 question RAG
- [ ] 1 question tool
- [ ] 1 question tool+RAG
- [ ] 1 clarification
- [ ] 1 erreur
- [ ] 1 tour de Grafana

---

## 10. Ordre d'exécution recommandé

```
1. Routeur (2.1)            ─┐
2. LLM service (2.2)         ├─ débloquent l'API
3. Orchestrateur (2.3)       │
4. Erreurs (2.4)            ─┘
5. Tests Phase 6 (2.5)
6. Monitoring Prometheus (4.1)
7. Cache LLM (3.3)
8. Tests intégration (5.2)
9. RAGAS (4.3)
10. Grafana (4.2)
11. Polish README (6.1–6.3)
12. Sécurité (7)
13. Bonus / backlog (8)
```

---

## 11. Variables d'environnement attendues (`.env`)

```env
# LLM — Google Gemini
GOOGLE_API_KEY=your-google-api-key-here
LLM_MODEL=gemini-1.5-flash
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1024

# RAG
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_db
RAG_K=4

# App
APP_NAME=AI Banking Assistant
LOG_LEVEL=INFO
RATE_LIMIT_PER_MIN=60

# Monitoring
ENABLE_METRICS=true
RAGAS_SAMPLE_RATE=0.05
```

---

## 12. Risques identifiés

| Risque | Mitigation |
|---|---|
| LLM hallucine un identifiant de virement | System prompt strict + tests de régression |
| Chroma non persisté → ré-index à chaque démarrage | `persist_directory` déjà configuré ; vérifier au premier run |
| Outils CSV ne gèrent pas l'encodage | `pandas` UTF-8 OK ; valider accents dans les tests |
| Latence LLM élevée | `gemini-1.5-flash` (rapide) ; timeout 30 s ; cache LLM |
| Multilingue FR cassé par l'embedding | `all-MiniLM-L6-v2` couvre FR (acceptable) ; alternative `multilingual-e5` |
| `GOOGLE_API_KEY` manquante ou invalide | Erreur explicite au démarrage + test E2E qui valide la clé |
| Quota Gemini dépassé (429) | `gpt-3.5`-style fallback non applicable ici → backoff exponentiel + alerte Prometheus `rate_limit_total` |
| PII dans les logs | Logger un hash du `customer_id` |

---

> **Action immédiate** : implémenter `Router` → `LLMService` → `Orchestrator` → brancher dans `app/api/chat.py` → écrire les tests (2.1–2.5). C'est le goulot d'étranglement qui empêche l'API de répondre quoi que ce soit.
