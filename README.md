# Teamcenter MCP (Python / FastMCP)

MCP server exposing Teamcenter search, dataset and workflow operations. It proxies a
Teamcenter REST backend configured via `TEAMCENTER_API_URL`.

## Tools

| Tool | Backend endpoint |
|---|---|
| `searchItems` | `POST /api/search` (`Item...`) |
| `searchItemRevisions` | `POST /api/search` (`Item Revision...`) |
| `searchDatasets` | `POST /api/search` (`Dataset...`) |
| `getDatasetByItemId` | `GET /api/datasets/item/{itemId}` |
| `readDataset` | `GET /api/datasets/{uid}/content` |
| `initiateWorkflow` | `POST /api/workflow/create` |

## Run

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env      # then set TEAMCENTER_API_URL
.venv\Scripts\python app.py
```

By default the server listens on streamable HTTP at `http://127.0.0.1:8000/mcp`.
Set `MCP_TRANSPORT=stdio` to run over stdio instead.
