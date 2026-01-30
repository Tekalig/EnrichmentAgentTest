# Email Open Discord Notifier

Real-time Discord notifications for email opens in Close.io CRM.

## Features

- 🔔 Instant email open alerts via Discord
- 🔄 Dual mode: Webhooks + Polling fallback
- 🚫 Duplicate notification prevention
- 💾 SQLite persistence with analytics
- 📊 Analytics dashboard
- 🐳 Docker containerized
- ☁️ AWS-ready

## Architecture

- **In-memory cache** (24-hour expiry) → Duplicate prevention
- **SQLite database** → Analytics & historical tracking
- **FastAPI** → Webhook receiver & API endpoints
- **Background polling** → Fallback when webhooks unavailable

## Quick Start

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run the service
python main.py

# Service will start on http://localhost:8000
```

### Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

Required environment variables:
- `CLOSEIO_API_KEY` - Get from Close.io Settings → API Keys
- `DISCORD_WEBHOOK_URL` - Create at Discord Server → Integrations → Webhooks

Optional settings:
- `POLLING_ENABLED=true` - Enable polling mode (default: true)
- `POLLING_INTERVAL_SECONDS=300` - Polling interval (default: 5 minutes)
- `CACHE_RETENTION_HOURS=24` - Cache retention (default: 24 hours)
- `HOST=0.0.0.0` - Server host
- `PORT=8000` - Server port

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Webhook Receiver
```bash
# Close.io will POST to this endpoint
POST http://localhost:8000/webhook/closeio
```

### Statistics
```bash
curl http://localhost:8000/stats
```

### Test Notification
```bash
curl -X POST http://localhost:8000/test/notification
```

### Analytics
```bash
# Summary
curl http://localhost:8000/analytics/summary

# Recent opens
curl http://localhost:8000/analytics/recent?limit=10

# By date
curl http://localhost:8000/analytics/by-date?date=2024-01-30

# Top leads
curl http://localhost:8000/analytics/top-leads?limit=10

# By time of day
curl http://localhost:8000/analytics/by-time

# By day of week
curl http://localhost:8000/analytics/by-day

# Engagement metrics
curl http://localhost:8000/analytics/engagement
```

## Modes of Operation

### Webhook Mode (Recommended)

1. Deploy service to a public endpoint (AWS, ngrok, etc.)
2. Configure webhook in Close.io:
   - URL: `https://your-domain.com/webhook/closeio`
   - Events: `activity.email` with `action=updated`
3. Service receives real-time notifications

### Polling Mode (Fallback)

1. Set `POLLING_ENABLED=true` in `.env`
2. Service checks Close.io Event Log API every 5 minutes
3. Detects new email opens and sends Discord notifications
4. Works without public endpoint

**Note:** Both modes can run simultaneously for maximum reliability.

## Discord Webhook Setup

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Configure:
   - Name: "Email Open Notifier"
   - Channel: Select target channel
5. Copy webhook URL
6. Add to `.env` as `DISCORD_WEBHOOK_URL`

## Close.io Setup

### Get API Key
1. Log in to Close.io
2. Go to Settings → API Keys
3. Create new API key
4. Add to `.env` as `CLOSEIO_API_KEY`

### Configure Webhook (Optional)
1. Contact Close.io support to enable webhooks
2. Provide your webhook URL
3. Request `activity.email` events with `action=updated`

## Directory Structure

```
email-open-discord-notifier/
├── main.py             # FastAPI application
├── src/
│   ├── config.py       # Configuration
│   ├── models.py       # Data models
│   ├── closeio.py      # Close.io API client
│   ├── discord_notifier.py  # Discord integration
│   ├── cache.py        # In-memory cache
│   └── database.py     # SQLite persistence
├── data/               # Database storage
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Analytics Features

The service tracks and provides analytics on:

- **Total opens** - Overall email open count
- **Unique emails** - Number of distinct emails tracked
- **Top leads** - Most engaged leads by open count
- **Time patterns** - Opens by hour of day
- **Day patterns** - Opens by day of week
- **Engagement metrics** - Average opens, response rates

Access via API endpoints or query the SQLite database directly.

## Database Schema

SQLite database at `data/email_opens.db`:

```sql
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY,
    email_id TEXT NOT NULL,
    lead_id TEXT,
    lead_name TEXT,
    subject TEXT,
    recipient TEXT,
    opens_count INTEGER,
    opened_at TIMESTAMP,
    notified_at TIMESTAMP,
    UNIQUE(email_id, opened_at)
);
```

## Deployment

### AWS ECS/Fargate

1. Build Docker image
2. Push to ECR
3. Create task definition
4. Deploy to ECS cluster
5. Configure load balancer (if using webhooks)
6. Set environment variables in task definition

### AWS Lambda (Alternative)

1. Use AWS Lambda Web Adapter
2. Package as Lambda function
3. Set up API Gateway
4. Configure environment variables
5. Use DynamoDB instead of SQLite for serverless

## Monitoring

### Logs
```bash
# Docker
docker-compose logs -f

# Check recent activity
curl http://localhost:8000/stats
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Database
```bash
sqlite3 data/email_opens.db "SELECT * FROM notification_log ORDER BY opened_at DESC LIMIT 10;"
```

## Troubleshooting

**No Discord notifications:**
- Verify `DISCORD_WEBHOOK_URL` is correct
- Test: `curl -X POST http://localhost:8000/test/notification`
- Check Discord webhook is active
- Review logs for errors

**Duplicate notifications:**
- Cache working properly? Check `/stats`
- Database unique constraints in place?
- Clear cache: restart service

**Polling not working:**
- Verify `CLOSEIO_API_KEY` is valid
- Check `POLLING_ENABLED=true`
- Review logs for API errors
- Verify Close.io permissions

## Security

- Use HTTPS for webhook endpoints
- Rotate API keys regularly
- Enable webhook signature verification (if available)
- Restrict database file permissions
- Use environment variables for secrets
- Never commit `.env` files

## License

MIT License - See LICENSE file for details
