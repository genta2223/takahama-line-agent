from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def page_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/policies")
async def page_policies(request: Request):
    return templates.TemplateResponse(request=request, name="policies.html")

@router.get("/issues")
async def page_issues(request: Request):
    return templates.TemplateResponse(request=request, name="issues.html")

@router.get("/profile")
async def page_profile(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")

@router.get("/supporters")
async def page_supporters(request: Request):
    return templates.TemplateResponse(request=request, name="supporters.html")
