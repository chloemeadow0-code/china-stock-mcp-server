import os

from main import mcp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    # Zeabur provides the public port through the PORT environment variable.
    # The upstream project only defines MCP tools; it does not start a long-running server.
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.settings.debug = False

    print(f"Starting china-stock-mcp-server on 0.0.0.0:{port} via SSE")
    mcp.run(transport="sse")
