# UI Navigation Guide - Where to Add API Credentials

## Overview Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  LOGIN (localhost:3001/login)                                       │
│  ├─ Select "Admin Login"                                            │
│  └─ Enter: admin@dra.com / AdminTest123!                           │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                                                    │
│  ├─ Sidebar: Dashboard | Clients | Jobs | Settings                  │
│  │                                                                  │
│  └─ Click: CLIENTS                                                  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENTS LIST                                                       │
│  ├─ Shows all clients                                               │
│  │                                                                  │
│  └─ Click: "Add Client" OR click on existing client                 │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENT DETAIL PAGE                                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Test Store                        [Run Now] [Connectors] [Users]│ │
│  │  test-store                                                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Stats Cards: Connectors | Total Jobs | Status                      │
│                                                                     │
│  ┌─ Connectors Section ──────────────────────────────────────────┐  │
│  │  No connectors configured.                                    │  │
│  │                                                               │  │
│  │  [Add Connector]  ◄─── CLICK THIS BUTTON                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ADD CONNECTOR MODAL                                                │
│                                                                     │
│  Type: [▼ Shopify          ]  ◄─── SELECT TYPE (Easiest ⭐)         │
│        [  WooCommerce     ]                                         │
│        [  Google Analytics 4 ]                                      │
│                                                                     │
│  ┌─ Configuration ─────────────────────────────────────────────┐   │
│  │                                                            │   │
│  │  FOR SHOPIFY: ⭐ RECOMMENDED (Easiest)                    │   │
│  │  ├─ Shop URL: [your-store.myshopify.com]                  │   │
│  │  └─ Access Token: [shpat_xxxxxxxxxxxx]                    │   │
│  │                                                            │   │
│  │  FOR WOOCOMMERCE:                                         │   │
│  │  ├─ Store URL: [https://your-store.com]                   │   │
│  │  ├─ Consumer Key: [ck_xxxxxxxxxxxx]                       │   │
│  │  └─ Consumer Secret: [cs_xxxxxxxxxxxx]                    │   │
│  │                                                            │   │
│  │  FOR GA4:                                                 │   │
│  │  ├─ Property ID: [______________]  (9-digit number)       │   │
│  │  └─ Service Account JSON: [paste entire JSON file]        │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [Cancel]  [Test]  [Create Connector]                               │
└─────────────────────────────────────────────────────────────────────┘

IMPORTANT BUTTONS:
├── [Test] - Verifies credentials work before saving
└── [Create Connector] - Saves the connector configuration

After adding BOTH connectors (GA4 + Store):
└── Go back to Client Detail and click [Run Now] to start reconciliation
