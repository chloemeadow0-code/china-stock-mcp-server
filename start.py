import os
import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import main
import urllib.request


def fetch_eastmoney_trends(symbol: str) -> dict:
    """拉东财trends2分时数据（原生HTTP，不依赖AKShare）"""
    url = (
        f"https://push2delay.eastmoney.com/api/qt/stock/trends2/get"
        f"?secid=0.{symbol}"
        f"&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
        f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
        f"&iscr=0&iscca=0"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_trends(data: dict) -> list:
    """解析东财分时数据"""
    trends = data.get("data", {}).get("trends", [])
    result = []
    for t in trends:
        parts = t.split(",")
        result.append({
            "time": parts[0],
            "open": float(parts[1]),
            "close": float(parts[2]),
            "high": float(parts[3]),
            "low": float(parts[4]),
            "volume": int(parts[5]),
            "amount": float(parts[6]),
        })
    return result


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

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

    # ── 新增：东财原生分时工具 ──
    @new_mcp.tool()
    def get_trends(symbol: str = "159995") -> str:
        """获取A股/ETF当天分钟分时走势（东财原生接口，不依赖AKShare）

        Args:
            symbol: 股票代码，如 159995
        Returns:
            当天每分钟的分时数据：时间、开盘、收盘、最高、最低、成交量、成交额
        """
        try:
            raw = fetch_eastmoney_trends(symbol)
            trends = parse_trends(raw)
            return json.dumps({"data": trends, "total": len(trends)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @new_mcp.tool()
    def find_price_times(symbol: str = "159995", price_list: str = "[]") -> str:
        """按成交价在当天分时中反推时间点（东财原生接口）

        Args:
            symbol: 股票代码，如 159995
            price_list: JSON数组字符串，要查找的价格，如 "[2.948, 2.974, 3.001]"
        Returns:
            每个价格对应的成交时间（分钟级）
        """
        try:
            prices = json.loads(price_list)
            raw = fetch_eastmoney_trends(symbol)
            trends = parse_trends(raw)

            results = []
            for target in prices:
                times = []
                for t in trends:
                    if abs(t["close"] - target) < 0.001:
                        times.append(t["time"])
                results.append({"price": target, "times": times})

            return json.dumps({"symbol": symbol, "data": results}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    print(f"Starting china-stock-mcp-server on 0.0.0.0:{port} via SSE")
    new_mcp.run(transport="sse")
