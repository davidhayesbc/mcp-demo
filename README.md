# Prerequisites

## Install `uv` (Python Package Manager)

Run the following command in PowerShell to install `uv`:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more details, refer to the [uv installation guide](https://astral.sh/uv/).

## Clone the Repository

Clone the repository using the following command:

```bash
git clone https://github.com/davidhayesbc/mcp-demo.git
```

## Open the Project in VS Code

Navigate to the project directory and open it in Visual Studio Code:

```bash
cd mcp-demo
code .
```

If you don't have Visual Studio Code installed, download it from the [official website](https://code.visualstudio.com/).

## Synchronize Dependencies

Run the following command to synchronize dependencies:

```bash
uv sync
```

Refer to the [uv documentation](https://astral.sh/uv/docs/) for more details on dependency management.

## Update Configuration

Edit the `.vscode/mcp.json` file and update the path to point to the location of `main.py`. For guidance, see the [MCP configuration documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server).

---

## Run the MCP Server

1. Use `Ctrl+Shift+P` to open the Command Palette in Visual Studio Code.
2. Search for `MCP: List Servers` and select it.
3. Choose the `my-weather` server.
4. Select `Start Server`.

You can now enable Copilot's Agent Mode and ask it:

> "Tell me about the weather this weekend."

It will ask you to confirm this is ok if this is the first time you've run the server

For more information, visit the [MCP server documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers).
