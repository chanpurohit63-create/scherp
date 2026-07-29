from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlmodel import Session, select, func
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import or_, extract

from .. import models, schemas, crud, auth
from ..database import engine

router = APIRouter()


# ========== AUDIT LOG HELPER ==========

def log_audit(
    user_id: Optional[int],
    school_id: Optional[int],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    before_values: Optional[str] = None,
    after_values: Optional[str] = None,
    ip_address: Optional[str] = None,
):
    """Create an audit log entry."""
    audit = models.AuditLog(
        user_id=user_id,
        school_id=school_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        before_values=before_values,
        after_values=after_values,
        ip_address=ip_address,
    )
    crud.create_item(audit)


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP from request."""
    if request.client:
        return request.client.host
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return None


# ========== SCHOOL MANAGEMENT ==========

@router.post("/schools", response_model=schemas.SchoolRead, status_code=status.HTTP_201_CREATED)
def create_school(
    school_in: schemas.SchoolCreate,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    existing = crud.get_school_by_code(school_in.school_code)
    if existing:
        raise HTTPException(status_code=400, detail="School code already exists")
    school = models.School(**school_in.dict())
    if school.subscription_plan and school.subscription_plan != "free":
        school.subscription_start = date.today()
        school.subscription_end = date.today() + timedelta(days=365)
    created = crud.create_school(school)
    log_audit(
        user_id=current_user.id,
        school_id=created.id,
        action="school.created",
        resource="school",
        resource_id=created.id,
        details=f"Created school: {created.school_name} ({created.school_code})",
        after_values=created.json(),
        ip_address=get_client_ip(request),
    )
    return created


@router.get("/schools", response_model=List[schemas.SchoolRead])
def list_schools(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    current_user=Depends(auth.require_super_admin),
):
    return crud.list_schools(skip=skip, limit=limit, status=status_filter, search=search)


@router.get("/schools/count")
def count_schools_endpoint(
    status_filter: Optional[str] = None,
    current_user=Depends(auth.require_super_admin),
):
    return {"count": crud.count_schools(status=status_filter)}


@router.get("/schools/{school_id}", response_model=schemas.SchoolRead)
def get_school(school_id: int, current_user=Depends(auth.require_super_admin)):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.put("/schools/{school_id}", response_model=schemas.SchoolRead)
def update_school(
    school_id: int,
    school_update: schemas.SchoolUpdate,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    before = school.json()
    updated = crud.update_school(school_id, school_update.dict(exclude_unset=True))
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="school.updated",
        resource="school",
        resource_id=school_id,
        details=f"Updated school: {updated.school_name}",
        before_values=before,
        after_values=updated.json(),
        ip_address=get_client_ip(request),
    )
    return updated


@router.delete("/schools/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    school_id: int,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    crud.update_school(school_id, {"status": "deleted"})
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="school.deleted",
        resource="school",
        resource_id=school_id,
        details=f"Deleted school: {school.school_name}",
        before_values=school.json(),
        ip_address=get_client_ip(request),
    )
    return {}


@router.post("/schools/{school_id}/activate", response_model=schemas.SchoolRead)
def activate_school(
    school_id: int,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    before = school.json()
    updated = crud.update_school(school_id, {"status": "active"})
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="school.activated",
        resource="school",
        resource_id=school_id,
        details=f"Activated school: {school.school_name}",
        before_values=before,
        after_values=updated.json(),
        ip_address=get_client_ip(request),
    )
    return updated


@router.post("/schools/{school_id}/suspend", response_model=schemas.SchoolRead)
def suspend_school(
    school_id: int,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    before = school.json()
    updated = crud.update_school(school_id, {"status": "suspended"})
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="school.suspended",
        resource="school",
        resource_id=school_id,
        details=f"Suspended school: {school.school_name}",
        before_values=before,
        after_values=updated.json(),
        ip_address=get_client_ip(request),
    )
    return updated


# ========== SUBSCRIPTION MANAGEMENT ==========

@router.get("/subscriptions/plans", response_model=List[schemas.SubscriptionPlan])
def list_subscription_plans(current_user=Depends(auth.get_current_user)):
    return list(schemas.SUBSCRIPTION_PLANS.values())


@router.put("/schools/{school_id}/subscription", response_model=schemas.SchoolRead)
def update_subscription(
    school_id: int,
    plan: str,
    subscription_start: Optional[date] = None,
    subscription_end: Optional[date] = None,
    request: Request = None,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    if plan not in schemas.SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Available: {list(schemas.SUBSCRIPTION_PLANS.keys())}")
    plan_obj = schemas.SUBSCRIPTION_PLANS[plan]
    before = school.json()
    values = {
        "subscription_plan": plan,
        "student_limit": plan_obj.max_students,
        "teacher_limit": plan_obj.max_teachers,
    }
    if subscription_start:
        values["subscription_start"] = subscription_start
    elif not school.subscription_start:
        values["subscription_start"] = date.today()
    if subscription_end:
        values["subscription_end"] = subscription_end
    elif plan != "free":
        values["subscription_end"] = (values.get("subscription_start", date.today())) + timedelta(days=365)
    updated = crud.update_school(school_id, values)
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="subscription.changed",
        resource="school",
        resource_id=school_id,
        details=f"Changed subscription to {plan}",
        before_values=before,
        after_values=updated.json(),
        ip_address=get_client_ip(request) if request else None,
    )
    return updated


# ========== SCHOOL STATISTICS ==========

@router.get("/schools/{school_id}/statistics", response_model=schemas.SchoolStatisticsRead)
def school_statistics(school_id: int, current_user=Depends(auth.require_super_admin)):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    with Session(engine) as session:
        total_students = session.exec(
            select(func.count(models.Student.id)).where(models.Student.school_id == school_id)
        ).one()
        total_teachers = session.exec(
            select(func.count(models.Teacher.id)).where(models.Teacher.school_id == school_id)
        ).one()
        total_parents = session.exec(
            select(func.count(models.Parent.id)).where(models.Parent.school_id == school_id)
        ).one()
        total_classes = session.exec(
            select(func.count(models.SchoolClass.id)).where(models.SchoolClass.school_id == school_id)
        ).one()
        total_revenue = session.exec(
            select(func.sum(models.Payment.amount)).where(models.Payment.school_id == school_id)
        ).one() or 0
        return schemas.SchoolStatisticsRead(
            school_id=school_id,
            school_name=school.school_name,
            total_students=total_students,
            total_teachers=total_teachers,
            total_parents=total_parents,
            total_classes=total_classes,
            total_revenue=float(total_revenue),
            subscription_plan=school.subscription_plan,
            status=school.status,
        )


# ========== PLATFORM DASHBOARD ==========

@router.get("/platform/dashboard", response_model=schemas.PlatformDashboardRead)
def platform_dashboard(current_user=Depends(auth.require_super_admin)):
    with Session(engine) as session:
        total_schools = session.exec(select(func.count(models.School.id))).one()
        active_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "active")
        ).one()
        inactive_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "inactive")
        ).one()
        suspended_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "suspended")
        ).one()
        expired_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "expired")
        ).one()

        total_students = session.exec(select(func.count(models.Student.id))).one()
        total_teachers = session.exec(select(func.count(models.Teacher.id))).one()
        total_parents = session.exec(select(func.count(models.Parent.id))).one()

        total_revenue = session.exec(select(func.sum(models.Payment.amount))).one() or 0
        now = datetime.utcnow()
        monthly_revenue = session.exec(
            select(func.sum(models.Payment.amount)).where(
                extract("year", models.Payment.paid_on) == now.year,
                extract("month", models.Payment.paid_on) == now.month,
            )
        ).one() or 0

        new_schools_this_month = session.exec(
            select(func.count(models.School.id)).where(
                extract("year", models.School.created_on) == now.year,
                extract("month", models.School.created_on) == now.month,
            )
        ).one()

        active_users_today = session.exec(
            select(func.count(func.distinct(models.Notification.user_id))).where(
                func.date(models.Notification.created_on) == date.today()
            )
        ).one()

        sub_dist_rows = session.exec(
            select(models.School.subscription_plan, func.count(models.School.id))
            .group_by(models.School.subscription_plan)
        ).all()
        subscription_distribution = [
            {"plan": plan or "free", "count": count} for plan, count in sub_dist_rows
        ]

        school_growth = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            count = session.exec(
                select(func.count(models.School.id)).where(
                    extract("year", models.School.created_on) == month_date.year,
                    extract("month", models.School.created_on) == month_date.month,
                )
            ).one()
            school_growth.append({"month": month_date.strftime("%b %Y"), "count": count})

        revenue_trend = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            rev = session.exec(
                select(func.sum(models.Payment.amount)).where(
                    extract("year", models.Payment.paid_on) == month_date.year,
                    extract("month", models.Payment.paid_on) == month_date.month,
                )
            ).one() or 0
            revenue_trend.append({"month": month_date.strftime("%b %Y"), "revenue": float(rev)})

        return schemas.PlatformDashboardRead(
            total_schools=total_schools,
            active_schools=active_schools,
            inactive_schools=inactive_schools,
            suspended_schools=suspended_schools,
            expired_schools=expired_schools,
            total_students=total_students,
            total_teachers=total_teachers,
            total_parents=total_parents,
            total_staff=total_teachers,
            total_revenue=float(total_revenue),
            monthly_revenue=float(monthly_revenue),
            new_schools_this_month=new_schools_this_month,
            active_users_today=active_users_today,
            subscription_distribution=subscription_distribution,
            school_growth=school_growth,
            revenue_trend=revenue_trend,
            monthly_registrations=school_growth,
        )


@router.get("/platform/analytics", response_model=schemas.PlatformAnalyticsRead)
def platform_analytics(current_user=Depends(auth.require_super_admin)):
    with Session(engine) as session:
        total_schools = session.exec(select(func.count(models.School.id))).one()
        active_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "active")
        ).one()
        suspended_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "suspended")
        ).one()
        expired_schools = session.exec(
            select(func.count(models.School.id)).where(models.School.status == "expired")
        ).one()
        total_students = session.exec(select(func.count(models.Student.id))).one()
        total_teachers = session.exec(select(func.count(models.Teacher.id))).one()
        total_revenue = session.exec(select(func.sum(models.Payment.amount))).one() or 0
        schools = session.exec(select(models.School).limit(100)).all()
        return schemas.PlatformAnalyticsRead(
            total_schools=total_schools,
            active_schools=active_schools,
            suspended_schools=suspended_schools,
            expired_schools=expired_schools,
            total_students=total_students,
            total_teachers=total_teachers,
            total_revenue=float(total_revenue),
            schools=schools,
        )


# ========== AUDIT LOGS ==========

@router.get("/audit-logs", response_model=List[schemas.AuditLogRead])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    action: Optional[str] = None,
    current_user=Depends(auth.require_super_admin),
):
    with Session(engine) as session:
        statement = select(models.AuditLog)
        if school_id is not None:
            statement = statement.where(models.AuditLog.school_id == school_id)
        if action:
            statement = statement.where(models.AuditLog.action == action)
        statement = statement.order_by(models.AuditLog.created_on.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()


# ========== SCHOOL ADMIN PASSWORD RESET ==========

@router.post("/schools/{school_id}/reset-admin-password")
def reset_school_admin_password(
    school_id: int,
    new_password: str,
    request: Request,
    current_user=Depends(auth.require_super_admin),
):
    school = crud.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    with Session(engine) as session:
        admin_user = session.exec(
            select(models.User).where(
                models.User.school_id == school_id,
                models.User.role.in_(["School Admin", "Principal"]),
            )
        ).first()
        if not admin_user:
            raise HTTPException(status_code=404, detail="No school admin found for this school")
        hashed = auth.get_password_hash(new_password)
        admin_user.hashed_password = hashed
        session.add(admin_user)
        session.commit()
    log_audit(
        user_id=current_user.id,
        school_id=school_id,
        action="password.reset",
        resource="user",
        resource_id=admin_user.id,
        details=f"Reset password for school admin of {school.school_name}",
        ip_address=get_client_ip(request),
    )
    return {"msg": "Password reset successfully"}