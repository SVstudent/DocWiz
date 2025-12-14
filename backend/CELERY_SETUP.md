# Celery Setup for DocWiz

This document describes the Celery async task processing setup for DocWiz.

## Overview

Celery is configured to handle long-running operations asynchronously:
- Surgical visualization generation (AI image processing with Gemini)
- Multi-procedure comparisons
- Comprehensive export report generation
- Cost infographic generation (with Freepik)

## Architecture

- **Broker**: Redis (for task queue)
- **Result Backend**: Redis (for storing task results)
- **Queues**: 
  - `visualizations` - for visualization and comparison tasks
  - `exports` - for export generation tasks
- **Worker Pool**: Solo (for development), Prefork (for production)

## Prerequisites

1. **Redis must be running**:
   ```bash
   # Using Docker Compose
   docker-compose up -d redis
   
   # Or check if already running
   docker ps | grep redis
   ```

2. **Dependencies installed**:
   ```bash
   cd backend
   poetry install
   ```

## Starting Celery Worker

### Development

Start a Celery worker with auto-reload:

```bash
cd backend
celery -A celery_worker worker --loglevel=info --pool=solo
```

For multiple queues:

```bash
celery -A celery_worker worker --loglevel=info --pool=solo -Q visualizations,exports
```

### Production

Start Celery worker with multiple processes:

```bash
celery -A celery_worker worker --loglevel=info --concurrency=4
```

With specific queues:

```bash
# Worker for visualizations
celery -A celery_worker worker --loglevel=info --concurrency=2 -Q visualizations -n worker1@%h

# Worker for exports
celery -A celery_worker worker --loglevel=info --concurrency=2 -Q exports -n worker2@%h
```

## Monitoring

### Flower (Web-based monitoring)

Install Flower:

```bash
pip install flower
```

Start Flower:

```bash
celery -A celery_worker flower --port=5555
```

Access at: http://localhost:5555

### Command-line monitoring

Check active tasks:

```bash
celery -A celery_worker inspect active
```

Check registered tasks:

```bash
celery -A celery_worker inspect registered
```

Check worker stats:

```bash
celery -A celery_worker inspect stats
```

## Task Usage

### From API Endpoints

Endpoints support both sync and async processing via query parameter:

```bash
# Async processing (returns task_id)
POST /api/visualizations?async_processing=true

# Sync processing (waits for completion)
POST /api/visualizations?async_processing=false
```

### Tracking Task Progress

#### REST API

```bash
# Get task status
GET /api/tasks/{task_id}/status

# Get task result (when complete)
GET /api/tasks/{task_id}/result

# Cancel task
POST /api/tasks/{task_id}/cancel
```

#### WebSocket (Real-time updates)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/tasks/{task_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Task update:', data);
  
  if (data.type === 'status') {
    console.log('Progress:', data.data.progress);
    console.log('Status:', data.data.status);
  }
  
  if (data.type === 'complete') {
    console.log('Task completed:', data.data.result);
    ws.close();
  }
};
```

## Task Configuration

Tasks are configured in `app/celery_app.py`:

- **task_time_limit**: 300 seconds (5 minutes) - hard limit
- **task_soft_time_limit**: 240 seconds (4 minutes) - soft limit
- **result_expires**: 3600 seconds (1 hour) - results expire after 1 hour
- **task_acks_late**: True - tasks acknowledged after completion
- **task_reject_on_worker_lost**: True - requeue tasks if worker crashes

## Available Tasks

### Visualization Tasks

1. **generate_visualization_task**
   - Generates surgical preview using Gemini AI
   - Updates progress: 0% → 20% → 80% → 100%
   - Returns visualization result with images and embeddings

2. **generate_comparison_task**
   - Generates multi-procedure comparison
   - Creates visualizations for each procedure
   - Returns comparison with cost/recovery/risk differences

### Export Tasks

1. **generate_export_task**
   - Creates comprehensive patient report
   - Supports PDF, PNG, JPEG, JSON formats
   - Updates progress: 10% → 30% → 90% → 100%

2. **generate_cost_infographic_task**
   - Generates visual cost breakdown
   - Uses Freepik API for infographic creation
   - Returns image in PNG or JPEG format

## Error Handling

Tasks automatically:
- Update state to FAILURE on errors
- Include error message in task metadata
- Log errors for debugging
- Can be retried manually or automatically

## Docker Setup

Add to `docker-compose.yml`:

```yaml
celery-worker:
  build: ./backend
  command: celery -A celery_worker worker --loglevel=info --pool=solo
  volumes:
    - ./backend:/app
  environment:
    - REDIS_URL=redis://redis:6379/0
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/0
  depends_on:
    - redis
    - firestore
    - qdrant
```

## Troubleshooting

### Worker not starting

1. Check Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check environment variables:
   ```bash
   echo $CELERY_BROKER_URL
   echo $CELERY_RESULT_BACKEND
   ```

3. Check for import errors:
   ```bash
   python -c "from app.celery_app import celery_app"
   ```

### Tasks not executing

1. Check worker is registered:
   ```bash
   celery -A celery_worker inspect registered
   ```

2. Check task queue:
   ```bash
   celery -A celery_worker inspect active
   ```

3. Check worker logs for errors

### Tasks timing out

1. Increase time limits in `app/celery_app.py`
2. Check AI service response times
3. Consider breaking task into smaller sub-tasks

## Best Practices

1. **Use async processing for**:
   - AI image generation (>5 seconds)
   - Multi-procedure comparisons (>10 seconds)
   - Large export generation (>5 seconds)

2. **Use sync processing for**:
   - Simple queries
   - Fast operations (<2 seconds)
   - When immediate response needed

3. **Monitor task performance**:
   - Use Flower for visualization
   - Track task execution times
   - Monitor queue lengths

4. **Handle failures gracefully**:
   - Implement retry logic
   - Provide clear error messages
   - Log failures for debugging
