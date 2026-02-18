# Database Backup Strategy

> **Last Updated**: 2026-02-17

This document outlines the backup strategy for the DRA Transaction Reconciliation Platform.

---

## Overview

The platform uses PostgreSQL as its primary database. Backups are essential for:
- Disaster recovery
- Point-in-time restoration
- Data migration
- Compliance requirements

---

## Automated Backups (Supabase)

If using Supabase (recommended for production):

### Daily Backups
- **Frequency**: Daily at 00:00 UTC
- **Retention**: 7 days (free tier) / 30 days (pro tier)
- **Location**: Supabase managed storage
- **Access**: Supabase Dashboard → Database → Backups

### Point-in-Time Recovery (Pro Tier)
- Available with Supabase Pro ($25/month)
- Restore to any point in the last 7 days
- Automatic WAL archiving

### Setup
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to Database → Backups
4. Verify daily backups are enabled

---

## Manual Backups

### Using pg_dump (Recommended)

```bash
# Full database backup
pg_dump \
  --host=db.your-project.supabase.co \
  --port=5432 \
  --username=postgres \
  --dbname=postgres \
  --format=custom \
  --file=backup_$(date +%Y%m%d_%H%M%S).dump

# Compressed backup with data only (faster)
pg_dump \
  --host=db.your-project.supabase.co \
  --port=5432 \
  --username=postgres \
  --dbname=postgres \
  --data-only \
  --format=plain \
  | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Using Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Create backup
supabase db dump --data-only > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Docker/Local Backups

For local development or self-hosted PostgreSQL:

```bash
# Backup
# Run from project root
docker-compose exec -T postgres pg_dump -U postgres dra_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T postgres psql -U postgres dra_platform < backup_file.sql
```

---

## Automated Backup Script

Use the provided backup script:

```bash
# Set environment variables
export DATABASE_URL="postgresql://postgres:password@host:5432/dbname"
export BACKUP_BUCKET="s3://your-backup-bucket"  # Optional: for S3 storage

# Run backup
chmod +x scripts/backup.sh
./scripts/backup.sh
```

### Cron Setup (Daily at 2 AM)

```bash
# Edit crontab
crontab -e

# Add line:
0 2 * * * /path/to/project/scripts/backup.sh >> /var/log/dra-backup.log 2>&1
```

---

## Backup Retention Policy

| Backup Type | Frequency | Retention | Storage Location |
|-------------|-----------|-----------|------------------|
| Automated (Supabase) | Daily | 7-30 days | Supabase Cloud |
| Manual Full | Weekly | 90 days | S3 / Local |
| Pre-deployment | On-demand | 1 year | S3 |
| Disaster Recovery | Monthly | 1 year | Offsite S3 |

---

## Restoration Procedures

### From pg_dump Custom Format

```bash
# Restore full database
pg_restore \
  --host=db.your-project.supabase.co \
  --port=5432 \
  --username=postgres \
  --dbname=postgres \
  --clean \
  --if-exists \
  backup_file.dump

# Restore specific tables
pg_restore \
  --host=db.your-project.supabase.co \
  --dbname=postgres \
  --table=jobs \
  --table=clients \
  backup_file.dump
```

### From SQL Dump

```bash
# Restore plain SQL
psql \
  --host=db.your-project.supabase.co \
  --username=postgres \
  --dbname=postgres \
  --file=backup_file.sql
```

### From Supabase Dashboard

1. Go to Database → Backups
2. Select the backup date
3. Click "Restore"
4. Confirm the restoration

⚠️ **Warning**: Restoration will overwrite current data!

---

## Testing Backups

Test your backups regularly:

```bash
# Create test restore
docker run -d --name test-postgres -e POSTGRES_PASSWORD=test postgres:15
docker exec -i test-postgres psql -U postgres < backup_file.sql

# Verify
docker exec test-postgres psql -U postgres -c "SELECT COUNT(*) FROM jobs;"

# Cleanup
docker stop test-postgres && docker rm test-postgres
```

---

## Critical Data Checklist

Ensure these are backed up:

- [ ] `clients` table
- [ ] `connectors` table (encrypted credentials)
- [ ] `jobs` table (reconciliation history)
- [ ] `user_clients` table (RBAC data)
- [ ] `schedules` table (automation configs)
- [ ] `auth.users` (via Supabase Auth backup)

---

## Encryption

- Database credentials are encrypted at rest (Fernet)
- Backup files should be encrypted for sensitive environments
- Use AWS S3 SSE or GCS encryption for cloud backups

---

## Monitoring

Set up alerts for:
- Backup failures
- Backup size anomalies
- Storage capacity warnings

```bash
# Check backup size
ls -lh /backups/
du -sh /backups/
```

---

## Emergency Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| Database Admin | admin@datarevolt.agency | Restore operations |
| DevOps | devops@datarevolt.agency | Infrastructure |
| On-Call | +1-XXX-XXX-XXXX | After-hours emergencies |

---

## Related Documents

- [DATA_RETENTION.md](DATA_RETENTION.md) - Data cleanup policies
- [SUPABASE_SETUP.md](../SUPABASE_SETUP.md) - Database configuration
- [IMPLEMENTATION_PLAN.md](../docs/IMPLEMENTATION_PLAN.md) - Architecture overview
