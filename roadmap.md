Voici une roadmap détaillée, étape par étape, pour implémenter le challenge **AI Banking Assistant** proprement.

---

# Roadmap détaillée — AI Banking Assistant

## Objectif final

Construire une API :

```http
POST /chat
```

capable de recevoir :

```json
{
  "customer_id": "C1024",
  "message": "Quel est le statut de mon virement TR4587 ?"
}
```

et de répondre :

```json
{
  "answer": "Votre virement TR4587 est actuellement en attente.",
  "source": "get_transfer_status"
}
```

avec un système qui choisit automatiquement entre :

- **RAG** pour les questions générales ;
- **Tools/APIs** pour les données client ;
- **RAG + Tools** quand les deux sont nécessaires.

---

# Phase 0 — Préparation du projet

## Objectif

Poser le cadre, éviter de partir dans tous les sens.

## Tâches

### 1. Lire le sujet et identifier les exigences

Tu dois clairement comprendre les attentes :

- assistant bancaire basé sur un LLM ;
- base de connaissances RAG ;
- outils/APIs pour données client ;
- sélection automatique de la source ;
- éviter les appels inutiles ;
- ne jamais inventer une information ;
- exposer `POST /chat` ;
- livrer code, README, pipeline RAG, outils, tests, architecture.

### 2. Définir le périmètre MVP

Commence par une version simple mais complète :

```text
MVP = API /chat + router + 5 outils mockés + RAG simple + quelques tests
```

### 3. Choisir la stack

Recommandation simple :

```text
Backend : FastAPI
LLM : OpenAI, Mistral, Ollama ou équivalent
RAG : LangChain ou LlamaIndex
Vector store : ChromaDB ou FAISS
Embeddings : OpenAI embeddings ou sentence-transformers
Tests : pytest
Validation : Pydantic
```

Si tu veux aller vite :

```text
FastAPI + ChromaDB + OpenAI/Mistral + pytest
```

### 4. Créer le repository

Structure recommandée :

```text
ai-banking-assistant/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── tools/
│   ├── rag/
│   └── tests/
├── README.md
├── requirements.txt
└── run.md
```

---

# Phase 1 — Créer les données mockées

## Objectif

Simuler les APIs bancaires avant d’implémenter la logique intelligente.

## Outils à implémenter

### 1. `get_account_balance(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "available_balance": 2450.75,
  "currency": "EUR",
  "account_type": "current"
}
```

### 2. `get_transactions(customer_id, start_date=None, end_date=None)`

Retourne une liste de transactions :

```json
[
  {
    "transaction_id": "TX1001",
    "date": "2026-08-08",
    "label": "Supermarché",
    "amount": -45.30,
    "currency": "EUR"
  }
]
```

### 3. `get_card_info(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "card_type": "Gold",
  "status": "active",
  "expiration_date": "2027-05-31",
  "payment_limit": 3000,
  "used_amount": 2400
}
```

### 4. `get_transfer_status(transfer_id)`

Retourne :

```json
{
  "transfer_id": "TR4587",
  "amount": 1500,
  "beneficiary": "M. Dupont",
  "date": "2026-08-09",
  "status": "rejected",
  "reason": "insufficient_balance"
}
```

### 5. `get_customer_info(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "name": "Jean Martin",
  "account_status": "
Voici une roadmap détaillée, étape par étape, pour implémenter le challenge **AI Banking Assistant** proprement.

---

# Roadmap détaillée — AI Banking Assistant

## Objectif final

Construire une API :

```http
POST /chat
```

capable de recevoir :

```json
{
  "customer_id": "C1024",
  "message": "Quel est le statut de mon virement TR4587 ?"
}
```

et de répondre :

```json
{
  "answer": "Votre virement TR4587 est actuellement en attente.",
  "source": "get_transfer_status"
}
```

avec un système qui choisit automatiquement entre :

- **RAG** pour les questions générales ;
- **Tools/APIs** pour les données client ;
- **RAG + Tools** quand les deux sont nécessaires.

---

# Phase 0 — Préparation du projet

## Objectif

Poser le cadre, éviter de partir dans tous les sens.

## Tâches

### 1. Lire le sujet et identifier les exigences

Tu dois clairement comprendre les attentes :

- assistant bancaire basé sur un LLM ;
- base de connaissances RAG ;
- outils/APIs pour données client ;
- sélection automatique de la source ;
- éviter les appels inutiles ;
- ne jamais inventer une information ;
- exposer `POST /chat` ;
- livrer code, README, pipeline RAG, outils, tests, architecture.

### 2. Définir le périmètre MVP

Commence par une version simple mais complète :

```text
MVP = API /chat + router + 5 outils mockés + RAG simple + quelques tests
```

### 3. Choisir la stack

Recommandation simple :

```text
Backend : FastAPI
LLM : OpenAI, Mistral, Ollama ou équivalent
RAG : LangChain ou LlamaIndex
Vector store : ChromaDB ou FAISS
Embeddings : OpenAI embeddings ou sentence-transformers
Tests : pytest
Validation : Pydantic
```

Si tu veux aller vite :

```text
FastAPI + ChromaDB + OpenAI/Mistral + pytest
```

### 4. Créer le repository

Structure recommandée :

```text
ai-banking-assistant/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── tools/
│   ├── rag/
│   └── tests/
├── README.md
├── requirements.txt
└── run.md
```

---

# Phase 1 — Créer les données mockées

## Objectif

Simuler les APIs bancaires avant d’implémenter la logique intelligente.

## Outils à implémenter

### 1. `get_account_balance(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "available_balance": 2450.75,
  "currency": "EUR",
  "account_type": "current"
}
```

### 2. `get_transactions(customer_id, start_date=None, end_date=None)`

Retourne une liste de transactions :

```json
[
  {
    "transaction_id": "TX1001",
    "date": "2026-08-08",
    "label": "Supermarché",
    "amount": -45.30,
    "currency": "EUR"
  }
]
```

### 3. `get_card_info(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "card_type": "Gold",
  "status": "active",
  "expiration_date": "2027-05-31",
  "payment_limit": 3000,
  "used_amount": 2400
}
```

### 4. `get_transfer_status(transfer_id)`

Retourne :

```json
{
  "transfer_id": "TR4587",
  "amount": 1500,
  "beneficiary": "M. Dupont",
  "date": "2026-08-09",
  "status": "rejected",
  "reason": "insufficient_balance"
}
```

### 5. `get_customer_info(customer_id)`

Retourne :

```json
{
  "customer_id": "C1024",
  "name": "Jean Martin",
  "account_status": "active",
  "risk_profile": "standard"
}
```

## À prévoir

Gérer les erreurs :

```python
customer_not_found
transfer_not_found
service_unavailable
invalid_parameter
```

## Validation

Tu dois pouvoir tester :

```python
get_account_balance("C1024")
get_transfer_status("TR4587")
get_transactions("C1024")
```

et obtenir des réponses cohérentes.

---

# Phase 2 — Créer la base de connaissances RAG

## Objectif

Avoir une base documentaire simple pour les questions générales.

## Documents à créer

Tu peux créer des fichiers Markdown :

```text
knowledge_base/
├── account_fees.md
├── account_opening.md
├── card_limits.md
├── card_policy.md
├── fraud_policy.md
├── international_transfer_fees.md
├── loan_information.md
├── lost_card_procedure.md
└── transfer_policy.md
```

## Exemples de contenu

### `international_transfer_fees.md`

```markdown
Les virements internationaux peuvent inclure :
- des frais d'émission ;
- des frais de banque intermédiaire ;
- des frais de conversion de devise.

Les frais varient selon le pays de destination et la devise.
```

### `lost_card_procedure.md`

```markdown
En cas de perte de carte bancaire :
1. Faire opposition immédiatement.
2. Déclarer la perte dans l'application ou auprès du service client.
3. Demander une nouvelle carte si nécessaire.
```

### `transfer_policy.md`

```markdown
Un virement peut être rejeté pour :
- solde insuffisant ;
- plafond dépassé ;
- bénéficiaire non conforme ;
- suspicion de fraude ;
- informations manquantes.

En cas de rejet, le client doit vérifier le motif puis corriger le problème avant de soumettre à nouveau le virement.
```

## Étapes RAG

### 1. Charger les documents

```python
load_documents()
```

### 2. Découper en chunks

Exemple :

```python
chunk_size = 500
chunk_overlap = 50
```

### 3. Générer les embeddings

```python
embeddings = EmbeddingModel()
```

### 4. Stocker dans un vector store

```python
ChromaDB / FAISS
```

### 5. Créer le retriever

```python
retriever.search("frais virement international")
```

## Validation

Pour la question :

```text
Quels sont les frais pour un virement international ?
```

le retriever doit retourner un document lié à :

```text
international_transfer_fees
```

---

# Phase 3 — Créer le routeur / orchestrateur

## Objectif

Décider si la question relève du RAG, d’un outil, ou des deux.

## Règles de routage

### RAG seul

Questions générales :

```text
Quels sont les frais pour un virement international ?
Comment fonctionne le plafond d’une carte bancaire ?
Quelles sont les conditions pour obtenir une carte Gold ?
Que dois-je faire en cas de perte de ma carte ?
Quels documents sont nécessaires pour ouvrir un compte ?
```

### Tool seul

Questions personnelles :

```text
Quel est mon solde ?
Quels sont mes derniers paiements ?
Quel est le statut de mon virement TR4587 ?
Quel est actuellement mon plafond de carte ?
Est-ce que ma carte est toujours active ?
```

### Tool + RAG

Questions qui nécessitent une donnée client puis une explication générale :

```text
Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?
Puis-je effectuer un paiement de 1000 € aujourd’hui avec ma carte ?
```

---

## Implémentation du routeur

### Option 1 : routeur simple par règles

Commence par ça.

Exemple :

```python
def route(message: str):
    if contains_transfer_id(message):
        if asks_for_procedure_or_reason(message):
            return Route(tool="get_transfer_status", needs_rag=True)
        return Route(tool="get_transfer_status", needs_rag=False)

    if asks_for_balance(message):
        return Route(tool="get_account_balance", needs_rag=False)

    if asks_for_transactions(message):
        return Route(tool="get_transactions", needs_rag=False)

    if asks_for_card_info(message):
        return Route(tool="get_card_info", needs_rag=False)

    return Route(tool=None, needs_rag=True)
```

### Option 2 : routeur LLM

Ensuite, tu peux améliorer avec un LLM.

Prompt :

```text
Tu es un routeur pour un assistant bancaire.

Tu dois choisir la meilleure source d’information parmi :
- RAG
- get_account_balance
- get_transactions
- get_card_info
- get_transfer_status
- get_customer_info

Réponds uniquement au format JSON :
{
  "tool": "...",
  "parameters": {...},
  "needs_rag": true/false,
  "reason": "..."
}
```

## Validation

Teste ces cas :

```text
Quel est mon solde ?
→ get_account_balance

Quels sont les frais pour un virement international ?
→ RAG

Quel est le statut de mon virement TR4587 ?
→ get_transfer_status

Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?
→ get_transfer_status + RAG
```

---

# Phase 4 — Implémenter la logique métier principale

## Objectif

Créer le flux complet de `/chat`.

## Flux recommandé

```text
POST /chat
  |
  v
Validation du payload
  |
  v
Router
  |
  v
Si RAG seul :
    recherche RAG
    réponse LLM
  |
Si Tool seul :
    appel outil
    réponse LLM
  |
Si Tool + RAG :
    appel outil
    construction requête RAG
    recherche RAG
    réponse LLM combinée
```

---

## Exemple de logique

```python
def handle_chat(customer_id: str, message: str):
    route = router.classify(message, customer_id)

    if route.missing_parameter:
        return clarification_response(route)

    if route.tool and route.needs_rag:
        tool_result = tool_service.call(route.tool, route.parameters)
        rag_query = build_rag_query(message, tool_result)
        docs = rag_service.search(rag_query)
        answer = llm_service.answer_with_tool_and_rag(message, tool_result, docs)
        return {"answer": answer, "source": f"{route.tool}+RAG"}

    if route.tool:
        tool_result = tool_service.call(route.tool, route.parameters)
        answer = llm_service.answer_with_tool(message, tool_result)
        return {"answer": answer, "source": route.tool}

    docs = rag_service.search(message)
    answer = llm_service.answer_with_rag(message, docs)
    return {"answer": answer, "source": "RAG"}
```

---

## Gestion des paramètres manquants

Exemple :

```text
Quel est le statut de mon virement ?
```

Si aucun `transfer_id` n’est fourni :

```json
{
  "answer": "Merci de fournir l’identifiant du virement concerné.",
  "source": "clarification"
}
```

Ne jamais inventer :

```text
TR1234
```

---

# Phase 5 — Implémenter l’API FastAPI

## Objectif

Exposer le endpoint demandé.

## Endpoint principal

```http
POST /chat
```

## Payload

```json
{
  "customer_id": "C1024",
  "message": "Quel est le statut de mon virement TR4587 ?"
}
```

## Réponse

```json
{
  "answer": "Votre virement TR4587 est actuellement en attente.",
  "source": "get_transfer_status"
}
```

---

## Schéma Pydantic

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    customer_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    source: str
```

---

## Route FastAPI

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return orchestrator.handle_chat(request.customer_id, request.message)
```

---

## Endpoints utiles optionnels

```http
GET /health
```

```http
GET /tools
```

```http
POST /rag/search
```

Mais le livrable principal reste :

```http
POST /chat
```

---

# Phase 6 — Intégrer le LLM correctement

## Objectif

Générer des réponses naturelles sans inventer.

## Prompt système recommandé

```text
Tu es un assistant bancaire.

Règles :
1. Réponds uniquement à partir des informations fournies par les outils ou la base de connaissances.
2. N’invente jamais une donnée client.
3. Si une information est manquante, dis-le clairement.
4. Sois clair, concis et professionnel.
5. Si une donnée personnelle est fournie par un outil, utilise-la comme source principale.
6. Si une règle générale est fournie par la documentation, utilise-la pour expliquer la procédure.
```

---

## Prompt pour réponse tool seul

```text
Question utilisateur : {message}

Résultat de l’outil :
{tool_result}

Réponds uniquement à partir du résultat de l’outil.
```

---

## Prompt pour RAG seul

```text
Question utilisateur : {message}

Documents pertinents :
{documents}

Réponds uniquement à partir des documents fournis.
Si l’information est absente, dis que tu ne peux pas répondre.
```

---

## Prompt pour Tool + RAG

```text
Question utilisateur : {message}

Résultat de l’outil :
{tool_result}

Documents pertinents :
{documents}

Explique la situation personnelle du client en utilisant le résultat de l’outil.
Explique ensuite les règles ou actions possibles en utilisant les documents.
N’invente aucune information.
```

---

# Phase 7 — Gérer les erreurs

## Objectif

Montrer que ton système est robuste.

## Erreurs à gérer

### 1. Client introuvable

```json
{
  "error": "customer_not_found"
}
```

Réponse :

```text
Je n’ai trouvé aucun compte associé à cet identifiant client.
```

---

### 2. Virement introuvable

```json
{
  "error": "transfer_not_found"
}
```

Réponse :

```text
Aucun virement avec cet identifiant n’a été trouvé.
```

---

### 3. API indisponible

```json
{
  "error": "service_unavailable"
}
```

Réponse :

```text
Je ne peux pas accéder à vos données pour le moment. Veuillez réessayer plus tard.
```

---

### 4. Paramètre manquant

Exemple :

```text
Quel est le statut de mon virement ?
```

Réponse :

```text
Merci de fournir l’identifiant du virement concerné.
```

---

### 5. RAG sans résultat

Si aucun document pertinent :

```text
Je n’ai pas trouvé cette information dans la documentation disponible.
```

---

# Phase 8 — Ajouter des tests

## Objectif

Prouver que ton système fonctionne sur les cas clés.

## Tests prioritaires

### Test 1 : router balance

```python
def test_route_balance():
    route = router.classify("Quel est mon solde ?")
    assert route.tool == "get_account_balance"
    assert route.needs_rag is False
```

---

### Test 2 : router RAG

```python
def test_route_rag_international_fees():
    route = router.classify("Quels sont les frais pour un virement international ?")
    assert route.tool is None
    assert route.needs_rag is True
```

---

### Test 3 : router transfer status

```python
def test_route_transfer_status():
    route = router.classify("Quel est le statut de mon virement TR4587 ?")
    assert route.tool == "get_transfer_status"
    assert route.parameters["transfer_id"] == "TR4587"
    assert route.needs_rag is False
```

---

### Test 4 : router transfer rejected + RAG

```python
def test_route_transfer_rejected_with_rag():
    route = router.classify("Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?")
    assert route.tool == "get_transfer_status"
    assert route.needs_rag is True
```

---

### Test 5 : API `/chat`

```python
def test_chat_balance():
    response = client.post("/chat", json={
        "customer_id": "C1024",
        "message": "Quel est mon solde ?"
    })

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["source"] == "get_account_balance"
```

---

### Test 6 : outil mocké

```python
def test_get_transfer_status():
    result = get_transfer_status("TR4587")
    assert result["transfer_id"] == "TR4587"
    assert result["status"] in ["pending", "completed", "rejected"]
```

---

### Test 7 : RAG retrieval

```python
def test_rag_retrieval_international_fees():
    docs = rag_service.search("frais virement international")
    assert any("international" in doc.lower() for doc in docs)
```

---

# Phase 9 — Créer le README

## Objectif

Permettre au recruteur de comprendre rapidement ton projet.

## Structure recommandée

```markdown
# AI Banking Assistant

## Description
Assistant bancaire basé sur un LLM capable d’utiliser une base RAG et des outils/APIs.

## Architecture
Schéma + explication du routage.

## Installation
Commandes d’installation.

## Lancement
Commandes pour démarrer l’API.

## Utilisation
Exemples de requêtes curl ou JSON.

## Choix techniques
Stack, router, RAG, outils, LLM.

## Tests
Commande pour lancer les tests.

## Limites
Ce qui peut être amélioré.
```

---

## Exemples à inclure dans le README

### Question RAG

```json
{
  "customer_id": "C1024",
  "message": "Quels sont les frais pour un virement international ?"
}
```

Réponse attendue :

```json
{
  "answer": "Les virements internationaux peuvent inclure des frais d'émission, des frais de banque intermédiaire et des frais de conversion.",
  "source": "RAG"
}
```

---

### Question tool

```json
{
  "customer_id": "C1024",
  "message": "Quel est mon solde ?"
}
```

Réponse attendue :

```json
{
  "answer": "Votre solde disponible est de 2450.75 EUR.",
  "source": "get_account_balance"
}
```

---

### Question tool + RAG

```json
{
  "customer_id": "C1024",
  "message": "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?"
}
```

Réponse attendue :

```json
{
  "answer": "Votre virement TR4587 a été refusé pour solde insuffisant. Veuillez vérifier votre solde ou réduire le montant du virement.",
  "source": "get_transfer_status+RAG"
}
```

---

# Phase 10 — Améliorations bonus

## Objectif

Te démarquer si tu as le temps.

## Bonus utiles

### 1. Logging structuré

```json
{
  "route": "get_transfer_status+RAG",
  "tool_called": "get_transfer_status",
  "rag_query": "rejected transfer insufficient balance",
  "latency_ms": 820
}
```

---

### 2. Évaluation automatique

Crée un fichier :

```json
[
  {
    "message": "Quel est mon solde ?",
    "expected_source": "get_account_balance"
  },
  {
    "message": "Quels sont les frais pour un virement international ?",
    "expected_source": "RAG"
  },
  {
    "message": "Mon virement TR4587 a été refusé. Pourquoi ?",
    "expected_source": "get_transfer_status+RAG"
  }
]
```

Puis mesure la précision du routage.

---

### 3. Citations RAG

```json
{
  "answer": "...",
  "source": "RAG",
  "documents": [
    "international_transfer_fees.md"
  ]
}
```

---

### 4. Gestion de conversation

Ajouter :

```json
{
  "conversation_id": "abc123"
}
```

Mais seulement si tu as déjà un MVP solide.

---

### 5. Sécurité

- validation stricte des entrées ;
- ne pas logger les données sensibles ;
- vérifier que `customer_id` est autorisé ;
- limiter les appels outils au client concerné.

---

# Planning recommandé

## Version courte — 3 jours

### Jour 1

- setup projet ;
- création des outils mockés ;
- structure FastAPI ;
- endpoint `/chat` basique.

### Jour 2

- création de la base RAG ;
- ingestion des documents ;
- retriever ;
- router simple ;
- réponse RAG.

### Jour 3

- intégration outils ;
- combinaison tool + RAG ;
- gestion erreurs ;
- tests ;
- README.

---

## Version confortable — 5 jours

### Jour 1 — Cadrage et outils

- analyse du sujet ;
- setup projet ;
- mock des 5 outils ;
- gestion des erreurs.

### Jour 2 — RAG

- création des documents ;
- chunking ;
- embeddings ;
- vector store ;
- recherche RAG.

### Jour 3 — Router et orchestration

- routage par règles ;
- routage LLM optionnel ;
- logique RAG / tool / tool+RAG ;
- gestion des paramètres manquants.

### Jour 4 — API et LLM

- FastAPI ;
- prompts ;
- réponses structurées ;
- logs ;
- tests manuels.

### Jour 5 — Tests, README et polish

- tests automatisés ;
- README complet ;
- diagramme d’architecture ;
- nettoyage du code ;
- démo finale.

---

# Ordre exact recommandé

Voici l’ordre le plus efficace :

```text
1. Créer les outils mockés
2. Créer la base de connaissances RAG
3. Créer le routeur simple
4. Créer l’API /chat
5. Connecter RAG
6. Connecter Tools
7. Gérer Tool + RAG
8. Gérer erreurs et paramètres manquants
9. Ajouter tests
10. Rédiger README
11. Ajouter bonus si le temps le permet
```

---

# Checklist finale

Avant de livrer, vérifie que tu as :

## Fonctionnel

- [ ] `POST /chat` fonctionne ;
- [ ] les questions générales utilisent RAG ;
- [ ] les questions personnelles utilisent les outils ;
- [ ] les questions mixtes utilisent outils + RAG ;
- [ ] aucun appel inutile ;
- [ ] aucune donnée inventée ;
- [ ] les paramètres manquants sont gérés ;
- [ ] les erreurs API sont gérées.

## Technique

- [ ] code Python propre ;
- [ ] structure modulaire ;
- [ ] pipeline RAG fonctionnel ;
- [ ] outils mockés fonctionnels ;
- [ ] intégration LLM fonctionnelle ;
- [ ] tests automatisés ;
- [ ] README clair.

## Démo

- [ ] tu peux montrer une question RAG ;
- [ ] tu peux montrer une question outil ;
- [ ] tu peux montrer une question combinée ;
- [ ] tu peux montrer une erreur ou clarification ;
- [ ] tu peux expliquer ton architecture en 2 minutes.

---

# Résultat attendu

À la fin, ton système doit ressembler à ceci :

```text
POST /chat
   |
   v
Orchestrator
   |
   |--- Router
   |       |
   |       |--- RAG only
   |       |--- Tool only
   |       |--- Tool + RAG
   |
   |--- Tool Service
   |       |
   |       |--- get_account_balance
   |       |--- get_transactions
   |       |--- get_card_info
   |       |--- get_transfer_status
   |       |--- get_customer_info
   |
   |--- RAG Service
   |       |
   |       |--- documents bancaires
   |       |--- embeddings
   |       |--- vector store
   |       |--- retriever
   |
   |--- LLM Service
           |
           |--- réponse finale
```

Si tu veux, je peux ensuite te donner directement :

1. **le code FastAPI complet**,  
2. **le code du router**,  
3. **le pipeline RAG**,  
4. **les prompts LLM**,  
5. ou **un README prêt à copier-coller**.