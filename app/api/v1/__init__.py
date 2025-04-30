from fastapi import APIRouter
import importlib
import pkgutil

router = APIRouter()

# 自動遍歷所有 route_*.py
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith("route_"):
        module = importlib.import_module(f"{__name__}.{module_name}")
        router.include_router(module.router)