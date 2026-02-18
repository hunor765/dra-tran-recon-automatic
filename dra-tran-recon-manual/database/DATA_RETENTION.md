# Data Retention Policy

> **Last Updated**: 2026-02-17  
> **Applies To**: DRA Transaction Reconciliation Platform

---

## Purpose

This document defines data retention policies to:
- Prevent database bloat and performance degradation
- Ensure compliance with data protection regulations (GDPR, CCPA)
- Manage storage costs
- Maintain system performance

---

## Retention Periods

### Job Data

| Data Type | Retention Period | Action After Retention |
|-----------|-----------------|----------------------|
| Job results (detailed) | 90 days | Archive summary, remove detailed missing_ids |
| Job logs | 30 days | Remove or truncate logs |
| Completed jobs | 365 days | Delete entire record |
| Failed jobs | 180 days | Delete after extended period for debugging |

### User Data

| Data Type | Retention Period | Action After Retention |
|-----------|-----------------|----------------------|
| User access logs | 365 days | Delete audit records |
| Inactive user accounts | 2 years | Anonymize or delete |
| Failed login attempts | 90 days | Delete security logs |

### System Data

| Data Type | Retention Period | Action After Retention |
|-----------|-----------------|----------------------|
| API request logs | 30 days | Delete logs |
| Error reports (Sentry) | 90 days | Auto-expire in Sentry |
| Performance metrics | 90 days | Aggregate and archive |

---

## Data Categories

### 1. Reconciliation Results

**Detailed Data** (removed after 90 days):
- Individual missing transaction IDs
- Detailed error logs
- Raw API responses

**Summary Data** (retained for 1 year):
- Match rate percentage
- Total order counts
- Date ranges analyzed
- Aggregated statistics

### 2. Connector Credentials

**Never automatically deleted**:
- Encrypted API credentials
- Configuration settings

**Manual deletion required**:
- When client offboards
- When credentials rotate

### 3. User Activity

**Retained for compliance**:
- User login history (1 year)
- Administrative actions (1 year)
- Data access logs (90 days)

**Can be deleted sooner**:
- Session tokens (on logout)
- Page view analytics (30 days)

---

## Implementation

### Automatic Cleanup

The system runs automatic cleanup daily at 3:00 AM UTC:

```python
# From data_retention.py
from core.data_retention import DataCleanupTask

# Run cleanup
task = DataCleanupTask()
results = await task.run_cleanup(dry_run=False)
```

### Manual Cleanup

Administrators can trigger cleanup manually:

```bash
# Via API (admin only)
curl -X POST "https://api.example.com/api/v1/admin/cleanup" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"dry_run": false}'

# Via Python script
cd dra-tran-recon-manual/backend
python -c "
import asyncio
from core.data_retention import DataCleanupTask

async def main():
    task = DataCleanupTask()
    results = await task.run_cleanup(dry_run=True)  # Preview first
    print(results)

asyncio.run(main())
"
```

---

## Customizing Retention

### Environment Variables

```bash
# .env file
RETENTION_JOB_RESULTS_DAYS=90
RETENTION_JOB_LOGS_DAYS=30
RETENTION_FAILED_JOBS_DAYS=180
RETENTION_AUDIT_LOGS_DAYS=365
RETENTION_OLD_JOBS_DAYS=365
```

### Code Configuration

```python
from core.data_retention import DataRetentionConfig

# Custom retention periods
custom_config = DataRetentionConfig({
    "job_results": 60,      # 60 days instead of 90
    "audit_logs": 730,      # 2 years for compliance
})

task = DataCleanupTask(retention_config=custom_config)
```

---

## GDPR / CCPA Compliance

### Right to be Forgotten

When a user requests data deletion:

```sql
-- Anonymize user data
UPDATE user_clients 
SET email = 'deleted@anonymous.com',
    user_id = NULL,
    status = 'deleted'
WHERE email = 'user@example.com';

-- Delete from auth.users (via Supabase)
-- This must be done through Supabase Auth API
```

### Data Export

Users can export their data:

```bash
# Export client data
curl "https://api.example.com/api/v1/clients/{id}/export?format=json" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Storage Monitoring

### Check Current Usage

```sql
-- Table sizes (PostgreSQL)
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Estimate Cleanup Impact

```python
from core.data_retention import DataCleanupTask

# Dry run to see what would be cleaned
task = DataCleanupTask()
results = await task.run_cleanup(dry_run=True)
print(f"Would clean: {results}")
```

---

## Exceptions

### Legal Holds

If litigation is anticipated:
1. Suspend automatic deletion
2. Preserve relevant records
3. Document preservation scope
4. Notify legal team

```bash
# Disable cleanup temporarily
export DISABLE_CLEANUP=true
```

### Client-Specific Requirements

Some clients may require longer retention:

```python
# Per-client retention override
client_retention = {
    123: DataRetentionConfig({  # Client ID 123
        "job_results": 365,  # Keep for 1 year
        "audit_logs": 2555,  # Keep for 7 years
    })
}
```

---

## Audit Trail

All cleanup operations are logged:

```json
{
  "timestamp": "2024-01-15T03:00:00Z",
  "operation": "data_cleanup",
  "dry_run": false,
  "results": {
    "job_results": {"affected": 150},
    "job_logs": {"affected": 300},
    "old_jobs": {"deleted": 45}
  }
}
```

---

## Review Schedule

| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| Retention policy review | Annual | Data Protection Officer |
| Storage usage review | Monthly | DevOps |
| Compliance audit | Annual | Legal/Compliance |
| Cleanup effectiveness | Quarterly | Engineering |

---

## Related Documents

- [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md) - Backup procedures
- [SECURITY.md](../SECURITY.md) - Security policies
- [PRIVACY_POLICY.md](../PRIVACY_POLICY.md) - Privacy policy

---

## Contact

For questions about data retention:
- **Email**: privacy@datarevolt.agency
- **Slack**: #data-governance
