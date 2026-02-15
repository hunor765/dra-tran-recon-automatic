# DRA Transaction Reconciliation Platform - API Map

## Base URL
`http://localhost:8000` (Local Development)

## Authentication
All protected endpoints require a Bearer Token from Supabase Auth.
`Authorization: Bearer <token>`

## 1. Clients
Manage client organizations.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/clients/` | List all clients. query: `skip`, `limit` |
| `POST` | `/api/v1/clients/` | Create a new client. Body: `{name, slug, logo_url}` |
| `GET` | `/api/v1/clients/{id}` | Get client details |
| `PUT` | `/api/v1/clients/{id}` | Update client details |
| `DELETE` | `/api/v1/clients/{id}` | Delete a client |

## 2. Connectors
Manage data source connections (GA4, Shopify, WooCommerce).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/clients/{client_id}/connectors` | List connectors for a client |
| `POST` | `/api/v1/clients/{client_id}/connectors` | Create a connector. Body: `{type, config}` |
| `GET` | `/api/v1/connectors/{id}` | Get connector details |
| `PUT` | `/api/v1/connectors/{id}` | Update connector configuration |
| `DELETE` | `/api/v1/connectors/{id}` | Delete a connector |
| `POST` | `/api/v1/connectors/{id}/test` | Test connection configuration |

## 3. Jobs
Manage reconciliation jobs and audits.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/jobs/` | List jobs. Query: `client_id`, `status`, `limit` |
| `GET` | `/api/v1/jobs/{id}` | Get detailed job result |
| `POST` | `/api/v1/jobs/run/{client_id}` | Trigger a manual reconciliation job |

## 4. Admin
Admin-specific dashboards and controls.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/stats` | Get aggregate dashboard stats (counts, rates, etc.) |
| `GET` | `/api/v1/admin/jobs` | Get all jobs (admin view) |

## 5. Users & Access
Manage user access to specific clients.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/clients/{client_id}/users` | List users with access to this client |
| `POST` | `/api/v1/clients/{client_id}/invite` | Invite a user. Body: `{email, role}` |
| `DELETE` | `/api/v1/users/{user_client_id}` | Revoke user access |

## 6. Schedules
Manage automated run schedules.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/clients/{client_id}/schedule` | Get current schedule configuration |
| `POST` | `/api/v1/schedules/trigger/{client_id}` | (Legacy) Trigger job |

## Data Models

### Job Result Summary (JSON)
Stored in `jobs.result_summary`.
```json
{
  "match_rate": 98.5,
  "total_backend_value": 150000.00,
  "total_ga4_value": 148000.00,
  "missing_count": 15,
  "missing_ids": ["ORD-101", "ORD-102"]
}
```

### Connector Types
1. **ga4**: `{ "property_id": "...", "credentials_json": "..." }`
2. **shopify**: `{ "shop_url": "...", "access_token": "..." }`
3. **woocommerce**: `{ "url": "...", "consumer_key": "...", "consumer_secret": "..." }`
