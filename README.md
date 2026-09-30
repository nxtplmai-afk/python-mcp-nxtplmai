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

By default the server listens on Streamable HTTP on all interfaces (`0.0.0.0:8000`),
so it is reachable at `http://<host>:8000/mcp`. Set `MCP_HOST=127.0.0.1` to allow
local connections only, or `MCP_TRANSPORT=stdio` to run over stdio instead.
`GET /health` returns `{"status": "ok"}` when the server is up.

## Develop with the MCP Inspector

```bash
.venv\Scripts\fastmcp dev inspector app.py
```

If it fails with `PORT IS IN USE`, another Inspector is still running: close it, or
pick other ports with `--ui-port 6284 --server-port 6287`.
