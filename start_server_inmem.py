#!/usr/bin/env python3
"""
Simple LangGraph API Server

A minimal script to start the LangGraph API server directly using uvicorn.
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
from pathlib import Path

def setup_environment():
    """Setup required environment variables"""
    # Add src to Python path
# fmt: off  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2U3pOTU1RPT06ZTQzNDhjYmI=

    src_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(src_path))

    # Load graphs from langgraph.json
    config_path = Path(__file__).parent / "langgraph.json"
    graphs = {}
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            graphs = config.get("graphs", {})
    
    # Set environment variables
    os.environ.update({
        # Database and storage - 使用自定义 PostgreSQL checkpointer
        # "POSTGRES_URI": "postgresql://postgres:postgres@localhost:5432/langgraph_checkpointer_db?sslmode=disable",
        # "REDIS_URI": "redis://localhost:6379",
        "DATABASE_URI": ":memory:",
        "REDIS_URI": "fake",
        # "MIGRATIONS_PATH": "/storage/migrations",
        "MIGRATIONS_PATH": "__inmem",
        # Server configuration
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGGRAPH_RUNTIME_EDITION": "inmem",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_API_URL": "http://localhost:2025",

        # "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "1000",
        
        # Graphs configuration
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        
        # Worker configuration
        "N_JOBS_PER_WORKER": "1",
    })
# noqa  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2U3pOTU1RPT06ZTQzNDhjYmI=
    
    # Load .env file if exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Loaded environment from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file")
def monkey_patch():
    # Monkey patch deepagents message reducer to fix TypeError when state is None
    try:
        import deepagents._messages_reducer
        original_reducer = deepagents._messages_reducer._messages_delta_reducer

        def patched_reducer(state, writes):
            if state is None:
                state = []
            return original_reducer(state, writes)
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2U3pOTU1RPT06ZTQzNDhjYmI=

        deepagents._messages_reducer._messages_delta_reducer = patched_reducer
        print("🩹 Successfully applied monkey patch for deepagents message reducer")
    except Exception as e:
        print(f"⚠️ Failed to apply monkey patch: {e}")
def main():
    """Start the server"""
    print("🚀 Starting Simple LangGraph API Server...")
    
    # Setup environment
    setup_environment()
    monkey_patch()
    # Print server information
    print("\n" + "="*60)
    print("📍 Server URL: http://localhost:2026")
    print("📚 API Documentation: http://localhost:2026/docs")
    print("🎨 Studio UI: http://localhost:2026/ui")
    print("💚 Health Check: http://localhost:2026/ok")
    print("="*60)
    
    try:
        # Import uvicorn after environment setup
        import uvicorn
        
        # Start the server directly
        uvicorn.run(
            "langgraph_api.server:app",
            host="0.0.0.0",
            port=2026,
            reload=False,
            access_log=False,
            log_config={
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
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
# pragma: no cover  My80OmFIVnBZMlhva2FQbHNJL21tS1U2U3pOTU1RPT06ZTQzNDhjYmI=
