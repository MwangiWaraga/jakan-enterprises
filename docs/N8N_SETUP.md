# n8n Orchestration Setup

Automate your data refresh workflow with n8n - no more manual CLI commands or button clicking!

## Quick Start

### 1. Start n8n

```bash
docker compose up -d n8n n8n_db
```

Wait for n8n to be ready (check logs):
```bash
docker compose logs -f n8n | grep "n8n is now ready"
```

### 2. Access n8n

Open http://localhost:5678 in your browser

First time setup:
- Create your account and password
- You're in! 🎉

### 3. Import the Workflow

**Option A: Manual Import**
1. Go to **Workflows** (left sidebar)
2. Click **+ New**
3. Click the menu (...) → **Import from file**
4. Select `scripts/n8n_workflow_data_refresh.json`
5. Click **Save** and activate

**Option B: Create Manually** (2 minutes)
1. Click **+ New** workflow
2. Add nodes in this order:
   - **Start** node (already there)
   - **Execute Command** node
   - Configure it with:
     ```
     cd /workspace && python scripts/orchestrate_refresh.py
     ```
   - Connect `Start` → `Execute Command`
   - (Optional) Add **Respondto Webhook** nodes to see results

### 4. Execute the Workflow

You now have two options:

**Option A: Click Execute Button (UI)**
- Open the workflow in n8n
- Click the **Execute Workflow** button (top right)
- Watch the execution in real-time
- Check the **Execution** tab for logs

**Option B: Scheduled Trigger**
- Add a **Cron** node before Execute Command
- Set schedule (e.g., "Every day at 2 AM")
- Workflow runs automatically!

---

## What the Workflow Does

When you execute it:

1. ✅ Loads Kilimall inventory from Excel
2. ✅ Loads Kilimall orders from Excel  
3. ✅ Scrapes latest Oraimo products
4. ✅ Runs dbt to transform all data
5. ✅ Syncs Metabase database schema

**Total time**: ~2-5 minutes (first run slower, subsequent runs ~1-2 min)

---

## Workflow Variables (Optional)

You can add variables to control the workflow. Edit your workflow and add these inputs:

```json
{
  "skip_inventory": false,
  "skip_orders": false,
  "skip_oraimo": false,
  "skip_dbt": false,
  "skip_metabase_sync": false
}
```

Then modify `scripts/orchestrate_refresh.py` to check these env vars.

---

## Troubleshooting

### "Python module not found"
- Make sure you've run `pip install -e .` in your venv
- n8n runs commands with the host environment, so your venv must be set up

### "Docker socket not accessible"
- The n8n container needs access to Docker to run dbt
- This is already configured in docker-compose.yml with `/var/run/docker.sock`

### "Connection refused" errors
- Make sure all services are running: `docker compose ps`
- Check service health: `docker compose logs warehouse`

### Workflow fails midway
- Check the **Execution** logs in n8n for the exact error
- View detailed logs: `docker compose logs n8n`
- Fix the issue and re-run

---

## Viewing Results

After workflow executes:

1. **Check data loaded**:
   ```bash
   docker compose exec warehouse psql -U jakan -d jakan_warehouse -c "SELECT COUNT(*) FROM raw.kilimall_inventory;"
   ```

2. **View transformation status**:
   ```bash
   docker compose logs dbt | tail -20
   ```

3. **Check Metabase**:
   - Go to http://localhost:3000
   - Browse **Data** → You should see all schemas and tables
   - Create queries/dashboards from marts tables

---

## Next: Advanced Usage

### 1. Send Notifications
Add a Slack/Email node after successful execution to notify your team

### 2. Error Handling
Add error handling nodes to send alerts if any step fails

### 3. Conditional Logic
Skip steps based on time of day or data freshness checks

### 4. Webhooks
Trigger the workflow from external systems via HTTP

---

## Useful n8n Nodes for Data Pipelines

- **Execute Command**: Run CLI commands
- **HTTP Request**: Call APIs (Metabase, external services)
- **Cron**: Schedule automatic runs
- **Webhook**: Trigger from external systems
- **Set**: Pass variables between nodes
- **If**: Conditional branching
- **Slack/Email**: Notifications
- **Database**: Query directly (optional)

---

## Stop n8n

```bash
docker compose down n8n n8n_db
```

To stop everything:
```bash
docker compose down
```

---

## Tips

- **Cost savings**: Run expensive operations (Oraimo scrape) only on weekdays
- **Data freshness**: Schedule daily runs at 2 AM to have fresh data every morning
- **Monitoring**: Add notification nodes to track workflow health
- **Testing**: Use "Execute Workflow" button to test changes before scheduling

Enjoy hands-free data pipelines! 🚀
