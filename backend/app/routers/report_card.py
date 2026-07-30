from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, JSONResponse

from .. import models, schemas, auth
from ..database import engine
from ..tenant import get_current_school_id
from ..report_card_service import (
    create_report_card_template,
    get_report_card_template,
    list_report_card_templates,
    update_report_card_template,
    archive_report_card_template,
    duplicate_report_card_template,
    create_report_card_component,
    list_report_card_components,
    update_report_card_component,
    delete_report_card_component,
    create_examination_type,
    list_examination_types,
    get_examination_type,
    update_examination_type,
    delete_examination_type,
    create_exam_weightage_config,
    list_exam_weightage_configs,
    create_grade_scale,
    list_grade_scales,
    get_grade_scale,
    update_grade_scale,
    create_grade_scale_range,
    list_grade_scale_ranges,
    create_gpa_engine_config,
    list_gpa_engine_configs,
    get_gpa_engine_config,
    update_gpa_engine_config,
    create_gpa_grade_mapping,
    list_gpa_grade_mappings,
    create_subject_category,
    list_subject_categories,
    update_subject_category,
    delete_subject_category,
    create_subject_category_mapping,
    list_subject_category_mappings,
    create_report_card,
    get_report_card,
    list_report_cards,
    update_report_card,
    publish_report_card,
    archive_report_card,
    bulk_generate_report_cards,
    create_report_card_subject,
    list_report_card_subjects,
    update_report_card_subject,
    calculate_overall_grade,
)

router = APIRouter()

ADMIN_ROLES = ("Super Admin", "School Admin", "Principal")
ALL_ADMIN_ROLES = ("Super Admin", "School Admin", "Principal", "Teacher")


# ========== REPORT CARD TEMPLATES ==========

@router.post("/report-card/templates", response_model=schemas.ReportCardTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(template_in: schemas.ReportCardTemplateCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_report_card_template(template_in, current_user)


@router.get("/report-card/templates", response_model=List[schemas.ReportCardTemplateRead])
def list_templates(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    exam_id: Optional[int] = None,
    template_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return list_report_card_templates(
        academic_year_id=academic_year_id,
        class_id=class_id,
        exam_id=exam_id,
        template_type=template_type,
        skip=skip,
        limit=limit,
    )


@router.get("/report-card/templates/{template_id}", response_model=schemas.ReportCardTemplateRead)
def get_template(template_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    template = get_report_card_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/report-card/templates/{template_id}", response_model=schemas.ReportCardTemplateRead)
def update_template(template_id: int, template_update: schemas.ReportCardTemplateUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    template = update_report_card_template(template_id, template_update, current_user)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/report-card/templates/{template_id}/archive", response_model=dict)
def archive_template(template_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = archive_report_card_template(template_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"archived": True, "template_id": template_id}


@router.post("/report-card/templates/{template_id}/duplicate", response_model=schemas.ReportCardTemplateRead)
def duplicate_template(template_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    template = duplicate_report_card_template(template_id, current_user)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# ========== REPORT CARD COMPONENTS ==========

@router.post("/report-card/components", response_model=schemas.ReportCardComponentRead, status_code=status.HTTP_201_CREATED)
def create_component(component_in: schemas.ReportCardComponentCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_report_card_component(component_in, current_user)


@router.get("/report-card/components/template/{template_id}", response_model=List[schemas.ReportCardComponentRead])
def list_components(template_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_report_card_components(template_id)


@router.put("/report-card/components/{component_id}", response_model=schemas.ReportCardComponentRead)
def update_component(component_id: int, component_update: schemas.ReportCardComponentUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    component = update_report_card_component(component_id, component_update, current_user)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


@router.delete("/report-card/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(component_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = delete_report_card_component(component_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Component not found")
    return {}


# ========== EXAMINATION TYPES ==========

@router.post("/examination-types", response_model=schemas.ExaminationTypeRead, status_code=status.HTTP_201_CREATED)
def create_exam_type(exam_type_in: schemas.ExaminationTypeCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_examination_type(exam_type_in, current_user)


@router.get("/examination-types", response_model=List[schemas.ExaminationTypeRead])
def list_exam_types(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_examination_types()


@router.get("/examination-types/{exam_type_id}", response_model=schemas.ExaminationTypeRead)
def get_exam_type(exam_type_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    exam_type = get_examination_type(exam_type_id)
    if not exam_type:
        raise HTTPException(status_code=404, detail="Examination type not found")
    return exam_type


@router.put("/examination-types/{exam_type_id}", response_model=schemas.ExaminationTypeRead)
def update_exam_type(exam_type_id: int, exam_type_update: schemas.ExaminationTypeUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    exam_type = update_examination_type(exam_type_id, exam_type_update, current_user)
    if not exam_type:
        raise HTTPException(status_code=404, detail="Examination type not found")
    return exam_type


@router.delete("/examination-types/{exam_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_type(exam_type_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = delete_examination_type(exam_type_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Examination type not found")
    return {}


# ========== EXAM WEIGHTAGE CONFIG ==========

@router.post("/exam-weightage", response_model=schemas.ExamWeightageConfigRead, status_code=status.HTTP_201_CREATED)
def create_exam_weightage(config_in: schemas.ExamWeightageConfigCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_exam_weightage_config(config_in, current_user)


@router.get("/exam-weightage", response_model=List[schemas.ExamWeightageConfigRead])
def list_exam_weightage(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return list_exam_weightage_configs(academic_year_id=academic_year_id, class_id=class_id)


# ========== GRADE SCALES ==========

@router.post("/grade-scales", response_model=schemas.GradeScaleRead, status_code=status.HTTP_201_CREATED)
def create_grade_scale(grade_scale_in: schemas.GradeScaleCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_grade_scale(grade_scale_in, current_user)


@router.get("/grade-scales", response_model=List[schemas.GradeScaleRead])
def list_grade_scales(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_grade_scales()


@router.put("/grade-scales/{grade_scale_id}", response_model=schemas.GradeScaleRead)
def update_grade_scale(grade_scale_id: int, grade_scale_update: schemas.GradeScaleUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    grade_scale = update_grade_scale(grade_scale_id, grade_scale_update, current_user)
    if not grade_scale:
        raise HTTPException(status_code=404, detail="Grade scale not found")
    return grade_scale


# ========== GRADE SCALE RANGES ==========

@router.post("/grade-scales/{grade_scale_id}/ranges", response_model=schemas.GradeScaleRangeRead, status_code=status.HTTP_201_CREATED)
def create_grade_scale_range(grade_scale_id: int, range_in: schemas.GradeScaleRangeCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_grade_scale_range(range_in, current_user)


@router.get("/grade-scales/{grade_scale_id}/ranges", response_model=List[schemas.GradeScaleRangeRead])
def list_grade_scale_ranges(grade_scale_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_grade_scale_ranges(grade_scale_id)


@router.put("/grade-scale-ranges/{range_id}", response_model=schemas.GradeScaleRangeRead)
def update_grade_scale_range(range_id: int, range_update: schemas.GradeScaleRangeUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    grade_range = update_grade_scale_range(range_id, range_update, current_user)
    if not grade_range:
        raise HTTPException(status_code=404, detail="Grade range not found")
    return grade_range


# ========== GPA ENGINE ==========

@router.post("/gpa-engines", response_model=schemas.GpaEngineConfigRead, status_code=status.HTTP_201_CREATED)
def create_gpa_engine(gpa_in: schemas.GpaEngineConfigCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_gpa_engine_config(gpa_in, current_user)


@router.get("/gpa-engines", response_model=List[schemas.GpaEngineConfigRead])
def list_gpa_engines(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_gpa_engine_configs()


@router.put("/gpa-engines/{gpa_engine_id}", response_model=schemas.GpaEngineConfigRead)
def update_gpa_engine(gpa_engine_id: int, gpa_update: schemas.GpaEngineConfigUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    gpa_engine = update_gpa_engine_config(gpa_engine_id, gpa_update, current_user)
    if not gpa_engine:
        raise HTTPException(status_code=404, detail="GPA engine not found")
    return gpa_engine


# ========== GPA GRADE MAPPINGS ==========

@router.post("/gpa-engines/{gpa_engine_id}/mappings", response_model=schemas.GpaGradeMappingRead, status_code=status.HTTP_201_CREATED)
def create_gpa_mapping(gpa_engine_id: int, mapping_in: schemas.GpaGradeMappingCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_gpa_grade_mapping(mapping_in, current_user)


@router.get("/gpa-engines/{gpa_engine_id}/mappings", response_model=List[schemas.GpaGradeMappingRead])
def list_gpa_mappings(gpa_engine_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_gpa_grade_mappings(gpa_engine_id)


@router.put("/gpa-mappings/{mapping_id}", response_model=schemas.GpaGradeMappingRead)
def update_gpa_mapping(mapping_id: int, mapping_update: schemas.GpaGradeMappingUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    mapping = update_gpa_grade_mapping(mapping_id, mapping_update, current_user)
    if not mapping:
        raise HTTPException(status_code=404, detail="GPA mapping not found")
    return mapping


# ========== SUBJECT CATEGORIES ==========

@router.post("/subject-categories", response_model=schemas.SubjectCategoryRead, status_code=status.HTTP_201_CREATED)
def create_subject_cat(category_in: schemas.SubjectCategoryCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_subject_category(category_in, current_user)


@router.get("/subject-categories", response_model=List[schemas.SubjectCategoryRead])
def list_subject_cats(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_subject_categories()


@router.put("/subject-categories/{category_id}", response_model=schemas.SubjectCategoryRead)
def update_subject_cat(category_id: int, category_update: schemas.SubjectCategoryUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    category = update_subject_category(category_id, category_update, current_user)
    if not category:
        raise HTTPException(status_code=404, detail="Subject category not found")
    return category


@router.delete("/subject-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject_cat(category_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    success = delete_subject_category(category_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Subject category not found")
    return {}


@router.post("/subject-category-mappings", response_model=schemas.SubjectCategoryMappingRead, status_code=status.HTTP_201_CREATED)
def create_subject_cat_mapping(mapping_in: schemas.SubjectCategoryMappingCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_subject_category_mapping(mapping_in, current_user)


@router.get("/subject-category-mappings", response_model=List[schemas.SubjectCategoryMappingRead])
def list_subject_cat_mappings(current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_subject_category_mappings()


# ========== REPORT CARDS ==========

@router.post("/report-cards", response_model=schemas.ReportCardRead, status_code=status.HTTP_201_CREATED)
def create_report_card_endpoint(report_card_in: schemas.ReportCardCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_report_card(report_card_in, current_user)


@router.get("/report-cards", response_model=List[schemas.ReportCardRead])
def list_report_cards_endpoint(
    academic_year_id: Optional[int] = None,
    exam_id: Optional[int] = None,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES)),
):
    return list_report_cards(
        academic_year_id=academic_year_id,
        exam_id=exam_id,
        class_id=class_id,
        student_id=student_id,
        template_id=template_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/report-cards/{report_card_id}", response_model=schemas.ReportCardRead)
def get_report_card_endpoint(report_card_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    report_card = get_report_card(report_card_id)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    return report_card


@router.put("/report-cards/{report_card_id}", response_model=schemas.ReportCardRead)
def update_report_card_endpoint(report_card_id: int, report_card_update: schemas.ReportCardUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    report_card = update_report_card(report_card_id, report_card_update, current_user)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    return report_card


@router.post("/report-cards/{report_card_id}/publish", response_model=schemas.ReportCardRead)
def publish_report_card_endpoint(report_card_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    report_card = publish_report_card(report_card_id, current_user)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    return report_card


@router.post("/report-cards/{report_card_id}/archive", response_model=schemas.ReportCardRead)
def archive_report_card_endpoint(report_card_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    report_card = archive_report_card(report_card_id, current_user)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    return report_card


@router.post("/report-cards/bulk-generate", response_model=dict)
def bulk_generate_report_cards_endpoint(
    generate_in: schemas.BulkReportCardGenerate,
    current_user=Depends(auth.require_roles(*ADMIN_ROLES)),
):
    return bulk_generate_report_cards(generate_in, current_user)


# ========== REPORT CARD GRADES ==========

@router.post("/report-cards/{report_card_id}/grades", response_model=schemas.ReportCardSubjectRead, status_code=status.HTTP_201_CREATED)
def create_report_card_subject_endpoint(report_card_id: int, grade_in: schemas.ReportCardSubjectCreate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    return create_report_card_subject(grade_in, current_user)


@router.get("/report-cards/{report_card_id}/grades", response_model=List[schemas.ReportCardSubjectRead])
def list_report_card_subjects_endpoint(report_card_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    return list_report_card_subjects(report_card_id)


@router.put("/report-card-grades/{grade_id}", response_model=schemas.ReportCardSubjectRead)
def update_report_card_subject_endpoint(grade_id: int, grade_update: schemas.ReportCardSubjectUpdate, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    grade = update_report_card_subject(grade_id, grade_update, current_user)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.post("/report-cards/{report_card_id}/calculate-overall", response_model=dict)
def calculate_overall_grade_endpoint(report_card_id: int, current_user=Depends(auth.require_roles(*ADMIN_ROLES))):
    result = calculate_overall_grade(report_card_id)
    return result


# ========== PRINT / EXPORT ==========

@router.get("/report-cards/{report_card_id}/print")
def print_report_card(report_card_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    report_card = get_report_card(report_card_id)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    return JSONResponse(content={"report_card": report_card.__dict__})


@router.get("/report-cards/{report_card_id}/export/pdf")
def export_report_card_pdf(report_card_id: int, current_user=Depends(auth.require_roles(*ALL_ADMIN_ROLES))):
    from ..report_card_export import generate_report_card_pdf
    report_card = get_report_card(report_card_id)
    if not report_card:
        raise HTTPException(status_code=404, detail="Report card not found")
    grades = list_report_card_subjects(report_card_id)
    pdf_bytes = generate_report_card_pdf(report_card, grades)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_card_{report_card_id}.pdf"'},
    )