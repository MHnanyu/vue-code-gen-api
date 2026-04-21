"""
Agent 模式联调测试脚本。

用法:
    python scripts/test_agent.py                    # 纯文本需求（简单场景）
    python scripts/test_agent.py --prompt "做一个登录页" --lib ElementUI
    python scripts/test_agent.py --prompt "做一个Dashboard" --lib CcUI --image uploads/test.jpg
    python scripts/test_agent.py --mock              # Mock 模式测试 SSE 事件格式
"""
import argparse
import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "http://localhost:8000"


async def test_agent_stream(prompt: str, component_lib: str = "ElementUI", image_path: str | None = None):
    """测试 Agent 流式接口"""
    print(f"\n{'='*60}")
    print(f"[测试] Agent Stream - componentLib={component_lib}")
    print(f"[测试] Prompt: {prompt[:100]}...")
    print(f"{'='*60}\n")

    payload = {
        "prompt": prompt,
        "componentLib": component_lib,
    }

    if image_path:
        if os.path.exists(image_path):
            print(f"[测试] 上传图片: {image_path}")
            import httpx
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=60.0, write=120.0, pool=30.0)) as upload_client:
                with open(image_path, "rb") as f:
                    resp = await upload_client.post(
                        f"{BASE_URL}/api/upload",
                        files={"files": (os.path.basename(image_path), f)},
                    )
                if resp.status_code != 200:
                    print(f"[错误] 图片上传失败: HTTP {resp.status_code} {resp.text}")
                    return
                upload_data = resp.json().get("data", {})
                uploaded_files = upload_data.get("files", [])
                if not uploaded_files:
                    print("[错误] 上传返回无文件信息")
                    return
                payload["attachments"] = [uploaded_files[0]]
                print(f"[测试] 上传成功: {uploaded_files[0].get('url')}")
        else:
            print(f"[警告] 图片文件不存在: {image_path}，将跳过图片上传")

    import httpx
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=1200.0, write=30.0, pool=30.0)) as client:
        start_time = time.time()
        event_counts: dict[str, int] = {}
        total_events = 0

        try:
            async with client.stream(
                "POST",
                f"{BASE_URL}/api/generate/agent/stream",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    print(f"[错误] HTTP {response.status_code}: {body.decode()}")
                    return

                print("[SSE] 连接建立，等待事件...\n")

                current_event_type = ""
                current_data = ""

                async for line in response.aiter_lines():
                    if line.startswith("event: "):
                        current_event_type = line[7:].strip()
                    elif line.startswith("data: "):
                        current_data = line[6:].strip()
                    elif line == "" and current_event_type and current_data:
                        event_counts[current_event_type] = event_counts.get(current_event_type, 0) + 1
                        total_events += 1

                        try:
                            data = json.loads(current_data)
                        except json.JSONDecodeError:
                            data = current_data

                        if current_event_type == "agent_thinking":
                            content = data.get("content", "") if isinstance(data, dict) else str(data)
                            step = data.get("step", "?") if isinstance(data, dict) else "?"
                            if len(content) > 200:
                                print(f"[Step {step}] 💭 Thinking: {content[:200]}...\n         (已截断，共 {len(content)} 字符)")
                            else:
                                print(f"[Step {step}] 💭 Thinking: {content}")
                        elif current_event_type == "tool_call_start":
                            tool = data.get("toolName", "?") if isinstance(data, dict) else "?"
                            step = data.get("step", "?") if isinstance(data, dict) else "?"
                            args_raw = data.get("arguments", "{}") if isinstance(data, dict) else "{}"
                            try:
                                args = json.loads(args_raw)
                                args_preview = json.dumps(args, ensure_ascii=False)[:100]
                            except Exception:
                                args_preview = args_raw[:100]
                            print(f"[Step {step}] 🔧 Tool Call: {tool}({args_preview})")
                        elif current_event_type == "tool_call_result":
                            tool = data.get("toolName", "?") if isinstance(data, dict) else "?"
                            result = data.get("result", {}) if isinstance(data, dict) else {}
                            if isinstance(result, dict):
                                status = result.get("status", "N/A")
                                file_count = result.get("file_count", "N/A")
                                error = result.get("error")
                                if error:
                                    print(f"         ⚠️ Result: ERROR - {error}")
                                elif file_count != "N/A":
                                    print(f"         ✅ Result: {status}, files={file_count}")
                                else:
                                    result_str = json.dumps(result, ensure_ascii=False)
                                    if len(result_str) > 200:
                                        print(f"         ✅ Result: {result_str[:200]}...")
                                        print(f"                   (已截断，共 {len(result_str)} 字符)")
                                    else:
                                        print(f"         ✅ Result: {result_str}")
                            else:
                                result_str = str(result)
                                if len(result_str) > 200:
                                    print(f"         ✅ Result: {result_str[:200]}...")
                                    print(f"                   (已截断，共 {len(result_str)} 字符)")
                                else:
                                    print(f"         ✅ Result: {result_str}")
                        elif current_event_type == "agent_done":
                            files = data.get("files", []) if isinstance(data, dict) else []
                            print(f"\n{'='*60}")
                            print(f"[完成] Agent Done")
                            print(f"  文件数: {len(files)}")
                            for f in files[:5]:
                                print(f"  - {f.get('name', '?')} ({f.get('lines', '?')} 行, {f.get('size_bytes', '?')} bytes)")
                            if len(files) > 5:
                                print(f"  ... 还有 {len(files) - 5} 个文件")
                        elif current_event_type == "agent_cancelled":
                            step = data.get("cancelledAtStep", "?") if isinstance(data, dict) else "?"
                            print(f"\n[取消] Agent Cancelled at step {step}")
                        elif current_event_type == "error":
                            msg = data.get("message", "") if isinstance(data, dict) else str(data)
                            print(f"\n[错误] {msg}")
                        else:
                            print(f"[{current_event_type}] {str(data)[:100]}")

                        current_event_type = ""
                        current_data = ""

        except httpx.ConnectError:
            print("[错误] 无法连接服务器，请确保服务已启动: http://localhost:8000")
            return
        except Exception as e:
            print(f"[错误] {type(e).__name__}: {e}")

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"[统计] 耗时: {elapsed:.1f}s, 事件总数: {total_events}")
        print(f"[统计] 事件分布: {json.dumps(event_counts, ensure_ascii=False)}")
        print(f"{'='*60}")


async def test_health():
    """测试服务是否在线"""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{BASE_URL}/docs")
            if resp.status_code == 200:
                print("[OK] 服务在线")
                return True
    except Exception:
        print("[错误] 服务未启动，请先运行: uvicorn app.main:app --reload")
        return False
    return False


async def test_import_chain():
    """测试 import 链路是否正常"""
    print("\n[测试] Import 链路检查...")
    try:
        from app.agent.core import AgentCore
        from app.agent.tools import ToolRegistry, ToolDefinition, create_tool_registry
        from app.agent.prompts import build_agent_system_prompt
        from app.utils.sse import (
            emit_agent_thinking, emit_tool_call_start,
            emit_tool_call_result, emit_agent_done, emit_agent_cancelled,
        )
        print("[OK] app.agent.core - AgentCore")
        print("[OK] app.agent.tools - ToolRegistry, ToolDefinition, create_tool_registry")
        print("[OK] app.agent.prompts - build_agent_system_prompt")
        print("[OK] app.utils.sse - Agent SSE events")

        registry = ToolRegistry()
        registry.register(ToolDefinition(
            name="test_tool",
            description="测试工具",
            parameters={"type": "object", "properties": {}},
            execute=lambda args: {"ok": True},
        ))
        tools = registry.get_openai_tools()
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "test_tool"
        print("[OK] ToolRegistry 功能正常")

        prompt = build_agent_system_prompt("ElementUI", "- test_tool: 测试工具", ["normalize_requirement"])
        assert "ElementUI" in prompt
        assert "normalize_requirement" in prompt
        print("[OK] System Prompt 生成正常")

        thinking_event = emit_agent_thinking("测试思考", 0)
        assert "agent_thinking" in thinking_event
        print("[OK] SSE 事件格式正常")

        print("\n[通过] 所有 import 和基本功能检查通过！\n")
        return True
    except Exception as e:
        print(f"\n[失败] Import 检查失败: {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Agent 模式联调测试")
    parser.add_argument("--prompt", default="做一个简单的登录页面，包含用户名、密码输入框和登录按钮", help="测试 prompt")
    parser.add_argument("--lib", default="ElementUI", choices=["ElementUI", "CcUI", "aui"], help="组件库")
    parser.add_argument("--image", default=None, help="附件图片路径")
    parser.add_argument("--check", action="store_true", help="仅检查 import 链路")
    parser.add_argument("--health", action="store_true", help="仅检查服务健康")
    args = parser.parse_args()

    if args.check:
        asyncio.run(test_import_chain())
    elif args.health:
        asyncio.run(test_health())
    else:
        asyncio.run(test_agent_stream(args.prompt, args.lib, args.image))


if __name__ == "__main__":
    main()
