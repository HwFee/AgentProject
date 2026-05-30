from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from crud.admin import AdminCRUD
from models.user import User
from schemas.responses import ApiResponse, PaginatedResponse
from utils.dependencies import get_db, get_current_user
from utils.exceptions import AppException

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def require_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise AppException(status_code=403, message="需要管理员权限")
    return current_user


@router.get("/stats", response_model=ApiResponse[dict])
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stats = await AdminCRUD.get_stats(db)
    return ApiResponse(status_code=200, message="获取成功", data=stats)


@router.get("/token-trend", response_model=ApiResponse[dict])
async def token_trend(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    data = await AdminCRUD.get_token_trend(db, days)
    return ApiResponse(status_code=200, message="获取成功", data={"data": data})


@router.get("/failed-tasks", response_model=ApiResponse[list[dict]])
async def failed_tasks(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    tasks = await AdminCRUD.get_failed_tasks(db, limit)
    return ApiResponse(
        status_code=200,
        message="获取成功",
        data=[{
            "id": t.id,
            "title": t.title,
            "failed_at": t.updated_at,
            "error_msg": t.error_msg,
        } for t in tasks],
    )


@router.get("/tasks", response_model=ApiResponse[PaginatedResponse[dict]])
async def admin_tasks(
    page: int = 1,
    page_size: int = 10,
    status: str = None,
    mode: str = None,
    user_id: int = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    skip = (page - 1) * page_size
    sd = datetime.fromisoformat(start_date) if start_date else None
    ed = datetime.fromisoformat(end_date) if end_date else None
    rows = await AdminCRUD.get_all_tasks(db, skip, page_size, status, mode, user_id, search, sd, ed)
    total = await AdminCRUD.count_all_tasks(db, status, mode, user_id, search, sd, ed)
    total_pages = (total + page_size - 1) // page_size
    return ApiResponse(
        status_code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[{
                "id": r["task"].id,
                "title": r["task"].title,
                "username": r["username"],
                "status": r["task"].status,
                "mode": r["task"].mode,
                "created_at": r["task"].created_at,
                "updated_at": r["task"].updated_at,
                "error_msg": r["task"].error_msg,
            } for r in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.post("/tasks/{task_id}/stop", response_model=ApiResponse)
async def admin_stop_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from crud.report import ReportCRUD
    task = await ReportCRUD.get_task(db, task_id)
    if not task:
        raise AppException(status_code=404, message="任务不存在")
    if task.status not in ("pending", "planning", "running"):
        raise AppException(status_code=400, message="任务当前状态无法停止")
    await ReportCRUD.update_task_status(db, task_id, "cancelled")
    return ApiResponse(status_code=200, message="任务已停止")


@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def admin_delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    from crud.report import ReportCRUD
    task = await ReportCRUD.get_task(db, task_id)
    if not task:
        raise AppException(status_code=404, message="任务不存在")
    await ReportCRUD.delete_task(db, task_id)
    return ApiResponse(status_code=200, message="删除成功")


@router.get("/users", response_model=ApiResponse[PaginatedResponse[dict]])
async def admin_users(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    skip = (page - 1) * page_size
    users = await AdminCRUD.get_users(db, skip, page_size)
    total = await AdminCRUD.count_users(db)
    total_pages = (total + page_size - 1) // page_size
    return ApiResponse(
        status_code=200,
        message="获取成功",
        data=PaginatedResponse(
            items=[{
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": "admin" if u.is_admin else "user",
                "created_at": u.created_at,
            } for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.put("/users/{user_id}/role", response_model=ApiResponse)
async def admin_update_user_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise AppException(status_code=404, message="用户不存在")
    user.is_admin = (role == "admin")
    await db.commit()
    return ApiResponse(status_code=200, message="更新成功")


@router.delete("/users/{user_id}", response_model=ApiResponse)
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise AppException(status_code=404, message="用户不存在")
    await db.delete(user)
    await db.commit()
    return ApiResponse(status_code=200, message="删除成功")
