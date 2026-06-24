import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

import main


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    # Zeabur sits behind a reverse proxy and sends an external Host header.
    # MCP Python SDK DNS rebinding protection rejects that with 421 unless
    # configured at FastMCP construction time. Rebuild the FastMCP instance
    # with the protection disabled, then re-register the upstream tools.
    old_mcp = main.mcp
    new_mcp = FastMCP(
        "china-stock-mcp",
        host="0.0.0.0",
        port=port,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )

    new_mcp._tool_manager = old_mcp._tool_manager
    new_mcp._resource_manager = old_mcp._resource_manager
    new_mcp._prompt_manager = old_mcp._prompt_manager

    print(f"Starting china-stock-mcp-server on 0.0.0.0:{port} via SSE")
    new_mcp.run(transport="sse")
