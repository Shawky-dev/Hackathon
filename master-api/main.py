from fastapi import FastAPI  
from frontend_api import router as frontend_router  
from data_fetch_api import router as data_router  
from master_orchestrator import router as orchestrator_router  
  
app = FastAPI(title="Unified Air Data Server")  
  
app.include_router(frontend_router, prefix="/frontend", tags=["Frontend"])  
app.include_router(data_router, prefix="/data", tags=["Data"])  
app.include_router(orchestrator_router, prefix="/orchestrator", tags=["Orchestrator"])
