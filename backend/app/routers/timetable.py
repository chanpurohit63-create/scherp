from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session, select

from .. import models, schemas, crud, auth
from ..database import engine
from ..tenant import get_current_school_id
from ..audit import log_audit
from ..timetable_service import (
    create_timetable_entry,
    get_timetable_entry,
    list_timetable_entries,
    update_timetable_entry,
    delete_timetable_entry,
    duplicate_timetable,
    copy_timetable_between_sections,
    bulk_generate_timetable,
    validate_timetable_conflicts,
    get_conflicts,
    resolve_conflict,
    get_teacher_timetable,
    get_class_timetable,
    get_room_timetable,
    get_student_timetable,
    get_teacher_availability,
    set_teacher_availability,
    get_timetable_dashboard,
    get_period_master,
    create_period_master,
    update_period_master,
    delete_period_master,
    get_room_allocation,
    bulk_import_timetable,
    bulk_update_timetable,
    bulk_delete_timetable,
    publish_timetable,
    unpublish_timetable,
    regenerate_timetable,
    get_teacher_workload_report,
    get_room_occupancy_report,
    get_class_timetable_report,
    get_subject_distribution_report,
    get_period_analysis_report,
)

router = APIRouter()

ADMIN_ROLES = ("Super Admin", "School Admin", "Principal")
ALL_ADMIN_ROLES = ("Super Admin", "School Admin", "Principal", "Teacher")


def _session():
    return Session(engine)


# ========== TIMETABLE CRUD ==========

@router.post("/timetable", response_model=schemas.TimetableRead, status_code=status.HTTP_201_CREATED)
def create_timetable(timetable_in: schemas.TimetableCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    try:
        entry = create_timetable_entry(timetable_in, current_user)
        return entry
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/timetable", response_model=List[schemas.TimetableRead])
def list_timetable(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    section_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    room_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    day_of_week: Optional[int] = None,
    period: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return list_timetable_entries(
        skip=skip,
        limit=limit,
        academic_year_id=academic_year_id,
        class_id=class_id,
        section_id=section_id,
        teacher_id=teacher_id,
        room_id=room_id,
        subject_id=subject_id,
        day_of_week=day_of_week,
        period=period,
    )


# ========== TIMETABLE DUPLICATE & COPY ==========

@router.post("/timetable/duplicate", response_model=dict)
def duplicate_timetable_endpoint(
    source_academic_year_id: int,
    target_academic_year_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    count = duplicate_timetable(source_academic_year_id, target_academic_year_id, current_user)
    return {"duplicated": count, "source": source_academic_year_id, "target": target_academic_year_id}


@router.post("/timetable/copy-section", response_model=dict)
def copy_timetable_section(
    source_academic_year_id: int,
    source_section_id: int,
    target_section_id: int,
    target_class_id: int,
    target_academic_year_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    count = copy_timetable_between_sections(
        source_academic_year_id,
        source_section_id,
        target_section_id,
        target_class_id,
        target_academic_year_id,
        current_user,
    )
    return {"copied": count}


# ========== TIMETABLE GENERATOR ==========

@router.post("/timetable/generate", response_model=dict)
def generate_timetable(
    config: schemas.TimetableGenerateRequest,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    try:
        result = bulk_generate_timetable(config, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== CONFLICT DETECTION ==========

@router.post("/timetable/check-conflicts", response_model=schemas.TimetableConflictResult)
def check_conflicts(conflict_check: schemas.TimetableConflictCheck, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    sid = get_current_school_id()
    with Session(engine) as session:
        temp_entry = models.Timetable(
            school_id=sid,
            academic_year_id=0,
            class_id=conflict_check.class_id,
            section_id=conflict_check.section_id,
            subject_id=conflict_check.subject_id or 0,
            teacher_id=conflict_check.teacher_id,
            room_id=conflict_check.room_id,
            day_of_week=conflict_check.day_of_week,
            period=conflict_check.period,
            start_time=conflict_check.start_time,
            end_time=conflict_check.end_time,
        )
        conflicts = validate_timetable_conflicts(session, temp_entry, sid, exclude_id=conflict_check.exclude_timetable_id)
        messages = [c["description"] for c in conflicts]
        return schemas.TimetableConflictResult(has_conflict=len(conflicts) > 0, conflicts=conflicts, messages=messages)


@router.get("/timetable/conflicts", response_model=List[schemas.TimetableConflictLogRead])
def list_conflicts(
    academic_year_id: Optional[int] = None,
    resolved: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return get_conflicts(
        academic_year_id=academic_year_id,
        resolved=resolved,
        skip=skip,
        limit=limit,
    )


@router.put("/timetable/conflicts/{conflict_id}/resolve", response_model=dict)
def resolve_timetable_conflict(conflict_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = resolve_conflict(conflict_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"resolved": True, "conflict_id": conflict_id}


# ========== TIMETABLE BY PERSONNEL ==========

@router.get("/teachers/{teacher_id}/timetable", response_model=List[schemas.TimetableRead])
def get_teacher_timetable_endpoint(
    teacher_id: int,
    academic_year_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return get_teacher_timetable(teacher_id, academic_year_id)


@router.get("/students/{student_id}/timetable", response_model=List[schemas.TimetableRead])
def get_student_timetable_endpoint(
    student_id: int,
    academic_year_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES, "Student", "Parent")),
):
    return get_student_timetable(student_id, academic_year_id)


@router.get("/classes/{class_id}/timetable", response_model=List[schemas.TimetableRead])
def get_class_timetable_endpoint(
    class_id: int,
    academic_year_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return get_class_timetable(class_id, academic_year_id)


@router.get("/rooms/{room_id}/timetable", response_model=List[schemas.TimetableRead])
def get_room_timetable_endpoint(
    room_id: int,
    academic_year_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return get_room_timetable(room_id, academic_year_id)


# ========== TIMETABLE DASHBOARD ==========

@router.get("/timetable/dashboard", response_model=schemas.TimetableDashboardRead)
def timetable_dashboard(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return get_timetable_dashboard()


# ========== PERIOD MASTER ==========

@router.post("/periods", response_model=schemas.PeriodMasterRead, status_code=status.HTTP_201_CREATED)
def create_period(period_in: schemas.PeriodMasterCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_period_master(period_in, current_user)


@router.get("/periods", response_model=List[schemas.PeriodMasterRead])
def list_periods(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return get_period_master()


@router.put("/periods/{period_id}", response_model=schemas.PeriodMasterRead)
def update_period(period_id: int, period_update: schemas.PeriodMasterUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    period = update_period_master(period_id, period_update, current_user)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period


@router.delete("/periods/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_period(period_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = delete_period_master(period_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Period not found")
    return {}


# ========== TEACHER AVAILABILITY ==========

@router.get("/teachers/{teacher_id}/availability", response_model=List[schemas.TeacherAvailabilityRead])
def get_teacher_availability_endpoint(
    teacher_id: int,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return get_teacher_availability(teacher_id)


@router.put("/teachers/{teacher_id}/availability", response_model=List[schemas.TeacherAvailabilityRead])
def set_teacher_availability_endpoint(
    teacher_id: int,
    availability_in: List[schemas.TeacherAvailabilityCreate],
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return set_teacher_availability(teacher_id, availability_in, current_user)


# ========== ROOM ALLOCATION ==========

@router.get("/rooms/allocation", response_model=List[dict])
def get_room_allocation_endpoint(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return get_room_allocation()


# ========== EXPORT ENDPOINTS ==========

@router.get("/timetable/export/pdf")
def export_timetable_pdf(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    from ..export_service import generate_timetable_pdf
    entries = list_timetable_entries(
        academic_year_id=academic_year_id,
        class_id=class_id,
        teacher_id=teacher_id,
        limit=500,
    )
    pdf_bytes = generate_timetable_pdf(entries)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="timetable.pdf"'},
    )


@router.get("/timetable/export/excel")
def export_timetable_excel(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    from ..export_service import generate_timetable_excel
    entries = list_timetable_entries(
        academic_year_id=academic_year_id,
        class_id=class_id,
        teacher_id=teacher_id,
        limit=500,
    )
    excel_bytes = generate_timetable_excel(entries)
    return StreamingResponse(
        iter([excel_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="timetable.xlsx"'},
    )


@router.get("/timetable/export/csv")
def export_timetable_csv(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    from ..export_service import generate_timetable_csv
    entries = list_timetable_entries(
        academic_year_id=academic_year_id,
        class_id=class_id,
        teacher_id=teacher_id,
        limit=500,
    )
    csv_content = generate_timetable_csv(entries)
    return StreamingResponse(
        iter([csv_content.encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="timetable.csv"'},
    )


# ========== PRINT ==========

@router.get("/timetable/print")
def print_timetable(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    view: str = Query("weekly", enum=["weekly", "daily", "teacher", "class", "room"]),
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    entries = list_timetable_entries(
        academic_year_id=academic_year_id,
        class_id=class_id,
        teacher_id=teacher_id,
        limit=500,
    )
    return JSONResponse(content={"view": view, "entries": len(entries), "data": [e.__dict__ for e in entries]})


# ========== BULK OPERATIONS ==========

@router.post("/timetable/bulk-import", response_model=dict)
def bulk_import_timetable_endpoint(
    entries_in: List[schemas.TimetableCreate],
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    result = bulk_import_timetable(entries_in, current_user)
    return result


@router.put("/timetable/bulk-update", response_model=dict)
def bulk_update_timetable_endpoint(
    entry_ids: List[int],
    updates: dict,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    result = bulk_update_timetable(entry_ids, updates, current_user)
    return result


@router.delete("/timetable/bulk-delete", response_model=dict)
def bulk_delete_timetable_endpoint(
    entry_ids: List[int],
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    result = bulk_delete_timetable(entry_ids, current_user)
    return result


# ========== PUBLISH / DRAFT ==========

@router.post("/timetable/publish", response_model=dict)
def publish_timetable_endpoint(
    academic_year_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    count = publish_timetable(academic_year_id, current_user)
    return {"published": count, "academic_year_id": academic_year_id}


@router.post("/timetable/unpublish", response_model=dict)
def unpublish_timetable_endpoint(
    academic_year_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    count = unpublish_timetable(academic_year_id, current_user)
    return {"unpublished": count, "academic_year_id": academic_year_id}


# ========== REGENERATE ==========

@router.post("/timetable/regenerate", response_model=dict)
def regenerate_timetable_endpoint(
    academic_year_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    result = regenerate_timetable(academic_year_id, current_user)
    return result


# ========== REPORTS ==========

@router.get("/timetable/reports/teacher-workload", response_model=List[dict])
def teacher_workload_report(
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return get_teacher_workload_report()


@router.get("/timetable/reports/room-occupancy", response_model=List[dict])
def room_occupancy_report(
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return get_room_occupancy_report()


@router.get("/timetable/reports/class/{class_id}", response_model=List[dict])
def class_timetable_report(
    class_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return get_class_timetable_report(class_id)


@router.get("/timetable/reports/subject-distribution", response_model=List[dict])
def subject_distribution_report(
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return get_subject_distribution_report()


@router.get("/timetable/reports/period-analysis", response_model=List[dict])
def period_analysis_report(
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return get_period_analysis_report()


# ========== TIMETABLE NOTIFICATIONS ==========

@router.post("/timetable/notify/published")
async def notify_timetable_published_endpoint(
    academic_year_id: int,
    class_ids: List[int],
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    from ..timetable_service import notify_timetable_published
    await notify_timetable_published(academic_year_id, class_ids)
    return {"notified": True, "academic_year_id": academic_year_id, "class_ids": class_ids}


@router.post("/timetable/notify/changed")
async def notify_timetable_changed_endpoint(
    entry_id: int,
    change_type: str = Query("updated"),
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    from ..timetable_service import notify_timetable_changed
    await notify_timetable_changed(entry_id, change_type)
    return {"notified": True, "entry_id": entry_id, "change_type": change_type}


@router.post("/timetable/notify/room-changed")
async def notify_room_changed_endpoint(
    room_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    from ..timetable_service import notify_room_changed
    await notify_room_changed(room_id)
    return {"notified": True, "room_id": room_id}


@router.post("/timetable/notify/emergency")
async def notify_emergency_endpoint(
    class_id: int,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    from ..timetable_service import notify_emergency_schedule_update
    await notify_emergency_schedule_update(class_id)
    return {"notified": True, "class_id": class_id}


@router.get("/timetable/{entry_id}", response_model=schemas.TimetableRead)
def get_timetable(entry_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    entry = get_timetable_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return entry


@router.put("/timetable/{entry_id}", response_model=schemas.TimetableRead)
def update_timetable(entry_id: int, timetable_update: schemas.TimetableUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    try:
        entry = update_timetable_entry(entry_id, timetable_update, current_user)
        if not entry:
            raise HTTPException(status_code=404, detail="Timetable entry not found")
        return entry
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/timetable/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable(entry_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = delete_timetable_entry(entry_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    return {}