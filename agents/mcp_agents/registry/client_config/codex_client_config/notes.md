### Codex Client Config

Codex uses TOML instead of the VS Code JSON format.

*C:\Users\<username>\.codex\config.toml*

```
[mcp_servers.task2-server]
enabled = true
url = "http://127.0.0.1:8081/mcp"
```

This is the complete configuration for your unauthenticated local Streamable HTTP server. 

### How to import into Codex
You have two approaches.

`Approach 1: `Through the Codex CLI

Run:

```
bash
codex mcp add customer-support --url http://127.0.0.1:8081/mcp
```

**verify** : `codex mcp list`

`Approach 2:` Through `config.toml`

- Open Codex.

- Open the config.toml file.

- Add the configuration above.

- Save.

Restart the Codex CLI or VS Code Codex extension.
