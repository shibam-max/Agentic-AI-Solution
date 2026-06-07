# API Examples

## Health Check

```powershell
curl http://127.0.0.1:8000/health
```

## Review Logs

PowerShell example:

```powershell
$logs = Get-Content data\sample_logs\payment_incident.jsonl -Raw
$body = @{ raw_logs = $logs } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/review/logs -Method Post -Body $body -ContentType "application/json"
```

Expected output includes:

- incident count
- severity
- risk score
- confidence
- timeline
- runbook matches
- recommended actions
