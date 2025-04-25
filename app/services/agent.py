from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from agents.mcp import MCPServerSse
from agents import gen_trace_id, trace
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ToolMapper:
    @staticmethod
    def to_openai_format(tool: dict) -> dict[str, dict]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            }
        }


@asynccontextmanager
async def mcp_session():
    """Reusable MCP session context."""
    async with sse_client(url="http://mcp-server:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def load_tools() -> list[dict[str, dict]]:
    async with MCPServerSse(
        name="Activities Server",
        params={"url": "http://mcp-server:8001/sse"},
    ) as mcp_server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Activities Server", trace_id=trace_id):
            logger.info(f"Tracing tools load: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            tools = await mcp_server.list_tools()
            logger.info(f"Loaded {len(tools)} tools from MCP")
            return [ToolMapper.to_openai_format(tool) for tool in tools]


async def load_csv_resources() -> str:
    async with mcp_session() as session:
        resources_result = await session.list_resources()
        logger.info(f"Found {len(resources_result.resources)} resources")
        first_uri = resources_result.resources[0].uri
        read_result = await session.read_resource(uri=first_uri)
        return read_result.contents[0].text


async def get_prompts() -> list[str]:
    async with mcp_session() as session:
        prompt_results = await session.list_prompts()
        logger.info(f"Found {len(prompt_results.prompts)} prompts")
        return [
            (await session.get_prompt(prompt.name)).messages[0].content.text
            for prompt in prompt_results.prompts
        ]