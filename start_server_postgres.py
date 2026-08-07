#!/usr/bin/env python3
"""
Simple LangGraph API Server

A minimal script to start the LangGraph API server directly using uvicorn.
modified according to cli.py under LangGraph API
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import os
import sys
import json
import asyncio
from pathlib import Path

# Windows 上 psycopg 异步模式不兼容默认的 ProactorEventLoop，必须切到 SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def setup_environment():
    """Setup required environment variables"""
    # Add src and backend to Python path so graph modules can import app.*
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))

    # 先加载 .env，让后续逻辑能读到里面的 POSTGRES_URI / REDIS_URI 等
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Loaded environment from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file")
# type: ignore  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2WjA5aVpBPT06Y2U1YmM0ODQ=

    # Load config from langgraph.json
    config_path = Path(__file__).parent / "langgraph.json"
    graphs = {}
    auth = None

    root_dir = Path(__file__).parent.resolve()

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            graphs = config.get("graphs", {})
            auth = config.get("auth")  # 读取 auth 配置
# pylint: disable  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2WjA5aVpBPT06Y2U1YmM0ODQ=

        # 将 langgraph.json 中的相对路径转换为绝对路径，避免 cwd 影响 graph 加载
        # LangGraph 只认 '/' 作为文件路径分隔符，所以必须把 Windows 反斜杠换成正斜杠
        for key, spec in list(graphs.items()):
            if isinstance(spec, dict) and "path" in spec:
                p = Path(spec["path"])
                if not p.is_absolute():
                    spec["path"] = str(root_dir / p).replace("\\", "/")
            elif isinstance(spec, str):
                p = Path(spec)
                if not p.is_absolute():
                    graphs[key] = {"path": str(root_dir / p).replace("\\", "/")}

    # 从环境变量（来自 .env）读取数据库 / Redis 连接信息
    # 兼容两种命名：POSTGRES_URI / DATABASE_URI
    postgres_uri = os.environ.get("POSTGRES_URI") or os.environ.get("DATABASE_URI")
    redis_uri = os.environ.get("REDIS_URI")
    migrations_path = os.environ.get("MIGRATIONS_PATH", "./storage/migrations")

    missing = []
    if not postgres_uri:
        missing.append("POSTGRES_URI (或 DATABASE_URI)")
    if not redis_uri:
        missing.append("REDIS_URI")
    if missing:
        print(f"❌ 缺少必要的环境变量，请在 .env 中配置: {', '.join(missing)}")
        sys.exit(1)

    # Build environment variables dict
    env_vars = {
        # Database and storage - 从 .env 读取
        "POSTGRES_URI": postgres_uri,
        "REDIS_URI": redis_uri,
        "MIGRATIONS_PATH": migrations_path,
        # 本地 in-memory 无数据库持久化时
        #"DATABASE_URI": ":memory:",
        #"REDIS_URI": "fake",
        #"MIGRATIONS_PATH": "__inmem",

        # Server configuration
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGGRAPH_RUNTIME_EDITION": "postgres",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_API_URL": "http://localhost:2026",

        "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "2000",

        # Graphs configuration
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",

        # Auth configuration - 从 langgraph.json 读取
        "LANGGRAPH_AUTH": json.dumps(auth) if auth else None,

        # Worker configuration
        "N_JOBS_PER_WORKER": "1",
    }

    # 过滤掉 None 值，然后设置环境变量
    os.environ.update({k: v for k, v in env_vars.items() if v is not None})
def monkey_patch():
    # Monkey patch deepagents message reducer to fix TypeError when state is None
    try:
        import deepagents._messages_reducer
        original_reducer = deepagents._messages_reducer._messages_delta_reducer

        def patched_reducer(state, writes):
            if state is None:
                state = []
            return original_reducer(state, writes)

        deepagents._messages_reducer._messages_delta_reducer = patched_reducer
        print("🩹 Successfully applied monkey patch for deepagents message reducer")
    except Exception as e:
        print(f"⚠️ Failed to apply monkey patch: {e}")

def main():
    """Start the server"""
    print("🚀 Starting Simple LangGraph API Server...")
# pylint: disable  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2WjA5aVpBPT06Y2U1YmM0ODQ=

    # Setup environment
    setup_environment()
    monkey_patch()
    # 调试输出：确认 graph 配置已正确写入环境变量
    print(f"📋 LANGSERVE_GRAPHS = {os.environ.get('LANGSERVE_GRAPHS', 'NOT SET')}")
    print(f"📋 LANGGRAPH_RUNTIME_EDITION = {os.environ.get('LANGGRAPH_RUNTIME_EDITION', 'NOT SET')}")

    # Print server information
    print("\n" + "="*60)
    print("📍 Server URL: http://localhost:2026")
    print("📚 API Documentation: http://localhost:2026/docs")
    print("🎨 Studio UI: http://localhost:2026/ui")
    print("💚 Health Check: http://localhost:2026/ok")
    print("="*60)

    try:
        import uvicorn

        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
            "loggers": {
                "uvicorn": {"level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"level": "WARNING"},
            }
        }

        config = uvicorn.Config(
            "langgraph_api.server:app",
            host="0.0.0.0",
            port=2026,
            reload=False,
            access_log=False,
            loop="asyncio",
            log_config=log_config,
        )
        server = uvicorn.Server(config)

        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
# fmt: off  My80OmFIVnBZMlhva2FQbHNJL21tS1U2WjA5aVpBPT06Y2U1YmM0ODQ=

if __name__ == "__main__":
    main()
