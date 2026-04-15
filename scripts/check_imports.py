import sys
sys.path.insert(0, ".")

print(f"Python: {sys.version}")
print(f"CWD: {sys.path[0]}")

try:
    from app.agent.core import AgentCore
    print("[OK] app.agent.core - AgentCore")
except Exception as e:
    print(f"[FAIL] app.agent.core: {e}")

try:
    from app.agent.tools import ToolRegistry, ToolDefinition, create_tool_registry
    print("[OK] app.agent.tools - ToolRegistry, ToolDefinition, create_tool_registry")
except Exception as e:
    print(f"[FAIL] app.agent.tools: {e}")

try:
    from app.agent.prompts import build_agent_system_prompt, build_review_prompt
    print("[OK] app.agent.prompts - build_agent_system_prompt, build_review_prompt")
except Exception as e:
    print(f"[FAIL] app.agent.prompts: {e}")

try:
    from app.agent.review import review_generated_code
    print("[OK] app.agent.review - review_generated_code")
except Exception as e:
    print(f"[FAIL] app.agent.review: {e}")

try:
    from app.utils.sse import (
        emit_agent_thinking, emit_tool_call_start,
        emit_tool_call_result, emit_agent_done, emit_agent_cancelled,
    )
    print("[OK] app.utils.sse - Agent SSE events")
except Exception as e:
    print(f"[FAIL] app.utils.sse: {e}")

try:
    from app.routers.generate import router
    routes = [r.path for r in router.routes]
    agent_route = "/api/generate/agent/stream"
    if agent_route in routes:
        print(f"[OK] app.routers.generate - Agent route registered ({len(routes)} routes total)")
    else:
        print(f"[FAIL] app.routers.generate - Agent route NOT found. Routes: {routes}")
except Exception as e:
    print(f"[FAIL] app.routers.generate: {e}")

try:
    from app.schemas.generate import (
        AgentThinkingEvent, ToolCallStartEvent,
        ToolCallResultEvent, AgentDoneEvent, AgentCancelledEvent,
    )
    print("[OK] app.schemas.generate - Agent event schemas")
except Exception as e:
    print(f"[FAIL] app.schemas.generate: {e}")

try:
    from app.config import settings
    print(f"[OK] app.config - AGENT_MAX_STEPS={settings.AGENT_MAX_STEPS}, AGENT_ENABLE_REVIEW={settings.AGENT_ENABLE_REVIEW}")
except Exception as e:
    print(f"[FAIL] app.config: {e}")

print("\n[DONE] Import chain check complete.")
