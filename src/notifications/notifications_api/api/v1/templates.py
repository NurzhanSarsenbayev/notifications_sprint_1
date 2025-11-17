from uuid import UUID

from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, Depends, HTTPException, Query, status

from notifications.notifications_api.repositories.templates import TemplateRepository
from notifications.notifications_api.schemas.template import (
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
)
from notifications.notifications_api.utils.dependencies import get_template_repository

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateRead])
async def list_templates(
    repo: TemplateRepository = Depends(get_template_repository),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=1000),
):
    templates = await repo.list(offset=offset, limit=limit)
    return [TemplateRead.from_orm(t) for t in templates]


@router.post(
    "",
    response_model=TemplateRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    data: TemplateCreate,
    repo: TemplateRepository = Depends(get_template_repository),
):
    try:
        tpl = await repo.create(data)
    except IntegrityError:
        # дубликат по (template_code, locale, channel)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Template with this code/locale/channel already exists",
        )
    return TemplateRead.from_attributes(tpl)


@router.get("/{template_id}", response_model=TemplateRead)
async def get_template(
    template_id: UUID,
    repo: TemplateRepository = Depends(get_template_repository),
):
    tpl = await repo.get(template_id)
    if tpl is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return TemplateRead.from_orm(tpl)


@router.put("/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    repo: TemplateRepository = Depends(get_template_repository),
):
    tpl = await repo.get(template_id)
    if tpl is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    tpl = await repo.update(tpl, data)
    return TemplateRead.from_orm(tpl)