# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

Currently no authentication required. In production, add API key authentication.

## Endpoints

### 1. Health Check

Check if the service is running and properly configured.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-28T10:30:00Z",
  "version": "1.0.0",
  "langsmith_connected": true
}
```

---

### 2. Triage Single Ticket

Process a single support ticket.

**Endpoint:** `POST /triage`

**Request Body:**
```json
{
  "ticket_id": "optional-custom-id",  // Optional: Auto-generated if not provided
  "user_id": "user_1234",             // Required
  "query": "Why was I charged twice?", // Required
  "user_email": "john@example.com",    // Optional
  "user_name": "John Doe"              // Optional
}
```

**Response:**
```json
{
  "ticket_id": "ticket_abc123",
  "user_id": "user_1234",
  "intent": "billing",
  "confidence": 0.95,
  "reasoning": "Clear billing inquiry about duplicate charge",
  "entities": {
    "amount": null,
    "order_id": null,
    "urgency_keywords": [],
    "has_urgent_language": false
  },
  "action": "escalate",
  "team": "billing_tier1",
  "priority": "medium",
  "timestamp": "2024-12-28T10:30:00Z",
  "processing_time_ms": 1250.5,
  "trace_url": "https://smith.langchain.com/public/abc123/r"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request
- `500` - Server error

---

### 3. Batch Triage

Process multiple tickets at once (max 10).

**Endpoint:** `POST /triage/batch`

**Request Body:**
```json
[
  {
    "user_id": "user_1",
    "query": "I need a refund"
  },
  {
    "user_id": "user_2",
    "query": "Dashboard won't load"
  }
]
```

**Response:**
```json
{
  "total": 2,
  "processed": 2,
  "results": [
    { /* TicketResponse */ },
    { /* TicketResponse */ }
  ]
}
```

---

### 4. Get Metrics

Get basic system metrics.

**Endpoint:** `GET /metrics`

**Response:**
```json
{
  "message": "Detailed metrics available in LangSmith",
  "langsmith_project": "support-triage-agent",
  "langsmith_url": "https://smith.langchain.com/",
  "timestamp": "2024-12-28T10:30:00Z"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | string | Unique ticket identifier |
| `user_id` | string | User who submitted the ticket |
| `intent` | string | Classification: billing, technical, account, sales, general |
| `confidence` | float | Confidence score (0-1) |
| `reasoning` | string | Why this classification was chosen |
| `entities` | object | Extracted entities from query |
| `action` | string | "escalate" or "auto_resolve" |
| `team` | string | Team to route to (if escalating) |
| `priority` | string | "low", "medium", "high", or "critical" |
| `processing_time_ms` | float | Time taken to process |
| `trace_url` | string | LangSmith trace URL for debugging |

## Error Responses
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2024-12-28T10:30:00Z"
}
```

## Examples

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/triage",
    json={
        "user_id": "user_123",
        "query": "How do I reset my password?"
    }
)

result = response.json()
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")
print(f"Trace: {result['trace_url']}")
```

### cURL
```bash
curl -X POST "http://localhost:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "query": "Refund request"}'
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/triage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_123',
    query: 'Why was I charged twice?'
  })
});

const result = await response.json();
console.log('Intent:', result.intent);
console.log('Trace:', result.trace_url);
```

## Rate Limits

Currently no rate limits. In production, recommend:
- 100 requests/minute per API key
- 10 tickets max per batch request

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI where you can test all endpoints.
