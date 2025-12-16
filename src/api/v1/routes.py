"""API Router - Version 1"""
from fastapi import APIRouter

from src.services.api_governance.router import router as governance_router
#from src.services.graphql_validator.router import router as graphql_router
#from src.services.log_classifier.router import router as logs_router

api_router = APIRouter()

# Include service routers
api_router.include_router(
    governance_router,
    prefix="/governance",
    tags=["API Governance"]
)

# TODO: Add other routers as we build them
# api_router.include_router(
#     graphql_router,
#     prefix="/graphql",
#     tags=["GraphQL Validator"]
# )
# 
# api_router.include_router(
#     logs_router,
#     prefix="/logs",
#     tags=["Log Classifier"]
# )
