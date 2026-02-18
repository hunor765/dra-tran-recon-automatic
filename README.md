# DRA Transaction Reconciliation Platform

> E-commerce transaction reconciliation platform for GA4 and backend systems (Shopify, WooCommerce).

## 📁 Project Structure

```
.
├── apps/
│   ├── platform/          # Main web application (FastAPI + Next.js)
│   │   ├── backend/       # FastAPI backend API
│   │   ├── frontend/      # Next.js frontend
│   │   └── database/      # SQL schemas & migrations
│   │
│   └── scheduler/         # Automated reconciliation worker
│       └── src/
│
├── docs/                  # Documentation
│   ├── DEVELOPER_GUIDE.md # Developer setup & guidelines
│   ├── BRAND_GUIDELINES.md # Design system
│   ├── platform/          # Platform-specific docs
│   └── scheduler/         # Scheduler docs
│
├── scripts/               # Utility scripts
│   ├── dev/              # Development helpers
│   └── analysis/         # Data analysis scripts
│
└── client 2/             # Client-specific analysis (separate)
```

## 🚀 Quick Start

### Backend
```bash
cd apps/platform/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd apps/platform/frontend
npm install
npm run dev
```

### Scheduler
```bash
cd apps/scheduler/src
python main.py
```

## 📖 Documentation

- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Brand Guidelines](docs/BRAND_GUIDELINES.md)
- [Platform Docs](docs/platform/)

## 🗄️ Database

See [database setup guide](docs/platform/SUPABASE_SETUP.md).

## 🐳 Docker (Local Development)

```bash
cd apps/platform
docker-compose up -d
```

---

*Data Revolt Agency*
