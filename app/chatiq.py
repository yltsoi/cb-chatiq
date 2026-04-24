import asyncio
import sys

import uvicorn
import autodynatrace
import oneagent
from oneagent.common import AgentState
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

sys.path.insert(0, "")
from routers.base.admin import router as admin_base
from routers.base.qaflow_base import router as qaflow_base
from routers.v2.admin import router as admin_v2
from routers.v2.qaflow import router as qaflow_v2

app = FastAPI(title="ChatIQ - API")

app.include_router(qaflow_base, prefiex="/base", tags=["Component Endpoints - Version Base"])
app.include_router(admin_base, prefiex="/base", tags=["Admin API - Version Base"])
app.include_router(admin_v2, prefiex="/v2", tags=["Admin API - Version 2"])
app.include_router(qaflow_v2, prefiex="/v2", tags=["Q & A - Version Base"])


if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8080"]

    asyncio.run(server(app,config))

    
