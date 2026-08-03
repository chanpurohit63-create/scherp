from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select, func, and_, or_

from . import models, schemas
from .database import engine
from .tenant import get_current_school_id
from .audit import log_audit
from .notification_service import NotificationService


DAYS_OF_WEEK = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def _get_school_id() -> Optional[int]:
    return get_current_school_id()


# ========== REPORT CARD TEMPLATES ==========

def create_report_card_template(template_in: schemas.ReportCardTemplateCreate, current_user: models.User) -> models.ReportCardTemplate:
    sid = _get_school_id()
    template = models.ReportCardTemplate(
        school_id=sid,
        name=template_in.name,
        description=template_in.description,
        template_type=template_in.template_type or "standard",
        academic_year_id=template_in.academic_year_id,
        class_id=template_in.class_id,
        exam_id=template_in.exam_id,
        is_default=template_in.is_default or False,
        config=template_in.config,
        header_config=template_in.header_config,
        footer_config=template_in.footer_config,
        body_config=template_in.body_config,
        css_config=template_in.css_config,
        created_by=current_user.id,
    )
    with Session(engine) as session:
        session.add(template)
        session.commit()
        session.refresh(template)

        version = models.ReportCardTemplateVersion(
            template_id=template.id,
            school_id=sid,
            version=1,
            config=template.config,
            header_config=template.header_config,
            footer_config=template.footer_config,
            body_config=template.body_config,
            css_config=template.css_config,
            change_description="Initial version",
            created_by=current_user.id,
        )
        session.add(version)
        session.commit()

    log_audit(
        user_id=current_user.id,
        school_id=sid,
        action="create",
        resource="report_card_template",
        resource_id=template.id,
        details=f"Created report card template: {template.name}",
    )

    return template


def get_report_card_template(template_id: int, school_id: Optional[int] = None) -> Optional[models.ReportCardTemplate]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        template = session.get(models.ReportCardTemplate, template_id)
        if not template:
            return None
        if sid is not None and template.school_id != sid:
            return None
        return template


def list_report_card_templates(
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    exam_id: Optional[int] = None,
    template_type: Optional[str] = None,
    school_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.ReportCardTemplate]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.ReportCardTemplate).where(models.ReportCardTemplate.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.ReportCardTemplate.academic_year_id == academic_year_id)
        if class_id is not None:
            statement = statement.where(models.ReportCardTemplate.class_id == class_id)
        if exam_id is not None:
            statement = statement.where(models.ReportCardTemplate.exam_id == exam_id)
        if template_type is not None:
            statement = statement.where(models.ReportCardTemplate.template_type == template_type)
        statement = statement.order_by(models.ReportCardTemplate.created_on.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()


def update_report_card_template(template_id: int, template_update: schemas.ReportCardTemplateUpdate, current_user: models.User) -> Optional[models.ReportCardTemplate]:
    sid = _get_school_id()
    with Session(engine) as session:
        template = session.get(models.ReportCardTemplate, template_id)
        if not template or (sid is not None and template.school_id != sid):
            return None

        update_data = template_update.dict(exclude_unset=True)
        old_version = template.version

        for k, v in update_data.items():
            setattr(template, k, v)

        template.version = old_version + 1

        version = models.ReportCardTemplateVersion(
            template_id=template.id,
            school_id=sid,
            version=template.version,
            config=template.config,
            header_config=template.header_config,
            footer_config=template.footer_config,
            body_config=template.body_config,
            css_config=template.css_config,
            change_description=f"Version {template.version} update",
            created_by=current_user.id,
        )
        session.add(version)
        session.add(template)
        session.commit()
        session.refresh(template)

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="update",
            resource="report_card_template",
            resource_id=template_id,
            details=f"Updated report card template: {template.name} (version {template.version})",
        )

        return template


def archive_report_card_template(template_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        template = session.get(models.ReportCardTemplate, template_id)
        if not template or (sid is not None and template.school_id != sid):
            return False
        template.is_archived = True
        session.add(template)
        session.commit()

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="archive",
            resource="report_card_template",
            resource_id=template_id,
            details=f"Archived report card template: {template.name}",
        )

        return True


def duplicate_report_card_template(template_id: int, current_user: models.User) -> Optional[models.ReportCardTemplate]:
    sid = _get_school_id()
    with Session(engine) as session:
        original = session.get(models.ReportCardTemplate, template_id)
        if not original or (sid is not None and original.school_id != sid):
            return None

        duplicate = models.ReportCardTemplate(
            school_id=sid,
            name=f"{original.name} (Copy)",
            description=original.description,
            template_type=original.template_type,
            academic_year_id=original.academic_year_id,
            class_id=original.class_id,
            exam_id=original.exam_id,
            is_default=False,
            is_archived=False,
            parent_template_id=original.id,
            config=original.config,
            header_config=original.header_config,
            footer_config=original.footer_config,
            body_config=original.body_config,
            css_config=original.css_config,
            created_by=current_user.id,
        )
        session.add(duplicate)
        session.commit()
        session.refresh(duplicate)

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="duplicate",
            resource="report_card_template",
            resource_id=duplicate.id,
            details=f"Duplicated report card template: {original.name} -> {duplicate.name}",
        )

        return duplicate


# ========== REPORT CARD COMPONENTS ==========

def create_report_card_component(component_in: schemas.ReportCardComponentCreate, current_user: models.User) -> models.ReportCardComponent:
    sid = _get_school_id()
    component = models.ReportCardComponent(
        template_id=component_in.template_id,
        school_id=sid,
        component_type=component_in.component_type,
        label=component_in.label,
        x_position=component_in.x_position or 0.0,
        y_position=component_in.y_position or 0.0,
        width=component_in.width or 100.0,
        height=component_in.height or 50.0,
        font_size=component_in.font_size,
        font_color=component_in.font_color,
        font_family=component_in.font_family,
        font_weight=component_in.font_weight,
        border_radius=component_in.border_radius,
        border_width=component_in.border_width,
        border_color=component_in.border_color,
        background_color=component_in.background_color,
        margin_top=component_in.margin_top,
        margin_bottom=component_in.margin_bottom,
        margin_left=component_in.margin_left,
        margin_right=component_in.margin_right,
        padding=component_in.padding,
        is_visible=component_in.is_visible if component_in.is_visible is not None else True,
        is_editable=component_in.is_editable if component_in.is_editable is not None else True,
        data_source=component_in.data_source,
        default_value=component_in.default_value,
        sort_order=component_in.sort_order or 0,
    )
    with Session(engine) as session:
        session.add(component)
        session.commit()
        session.refresh(component)
    return component


def list_report_card_components(template_id: int, school_id: Optional[int] = None) -> List[models.ReportCardComponent]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.ReportCardComponent).where(
                models.ReportCardComponent.template_id == template_id,
                models.ReportCardComponent.school_id == sid,
            ).order_by(models.ReportCardComponent.sort_order)
        ).all()


def update_report_card_component(component_id: int, component_update: schemas.ReportCardComponentUpdate, current_user: models.User) -> Optional[models.ReportCardComponent]:
    sid = _get_school_id()
    with Session(engine) as session:
        component = session.get(models.ReportCardComponent, component_id)
        if not component or (sid is not None and component.school_id != sid):
            return None
        update_data = component_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(component, k, v)
        session.add(component)
        session.commit()
        session.refresh(component)
        return component


def delete_report_card_component(component_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        component = session.get(models.ReportCardComponent, component_id)
        if not component or (sid is not None and component.school_id != sid):
            return False
        session.delete(component)
        session.commit()
        return True


# ========== EXAMINATION TYPES ==========

def create_examination_type(exam_type_in: schemas.ExaminationTypeCreate, current_user: models.User) -> models.ExaminationType:
    sid = _get_school_id()
    exam_type = models.ExaminationType(
        school_id=sid,
        name=exam_type_in.name,
        code=exam_type_in.code,
        exam_type=exam_type_in.exam_type or "theory",
        weightage=exam_type_in.weightage or 0.0,
        max_marks=exam_type_in.max_marks,
        passing_marks=exam_type_in.passing_marks,
        duration_minutes=exam_type_in.duration_minutes,
        show_in_report_card=exam_type_in.show_in_report_card if exam_type_in.show_in_report_card is not None else True,
        sort_order=exam_type_in.sort_order or 0,
    )
    with Session(engine) as session:
        session.add(exam_type)
        session.commit()
        session.refresh(exam_type)
    return exam_type


def list_examination_types(school_id: Optional[int] = None) -> List[models.ExaminationType]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.ExaminationType).where(models.ExaminationType.school_id == sid).order_by(models.ExaminationType.sort_order)
        ).all()


def get_examination_type(exam_type_id: int, school_id: Optional[int] = None) -> Optional[models.ExaminationType]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        exam_type = session.get(models.ExaminationType, exam_type_id)
        if not exam_type or (sid is not None and exam_type.school_id != sid):
            return None
        return exam_type


def update_examination_type(exam_type_id: int, exam_type_update: schemas.ExaminationTypeUpdate, current_user: models.User) -> Optional[models.ExaminationType]:
    sid = _get_school_id()
    with Session(engine) as session:
        exam_type = session.get(models.ExaminationType, exam_type_id)
        if not exam_type or (sid is not None and exam_type.school_id != sid):
            return None
        update_data = exam_type_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(exam_type, k, v)
        session.add(exam_type)
        session.commit()
        session.refresh(exam_type)
        return exam_type


def delete_examination_type(exam_type_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        exam_type = session.get(models.ExaminationType, exam_type_id)
        if not exam_type or (sid is not None and exam_type.school_id != sid):
            return False
        session.delete(exam_type)
        session.commit()
        return True


# ========== EXAM WEIGHTAGE CONFIG ==========

def create_exam_weightage_config(config_in: schemas.ExamWeightageConfigCreate, current_user: models.User) -> models.ExamWeightageConfig:
    sid = _get_school_id()
    config = models.ExamWeightageConfig(
        school_id=sid,
        academic_year_id=config_in.academic_year_id,
        class_id=config_in.class_id,
        exam_type_id=config_in.exam_type_id,
        weightage=config_in.weightage,
        max_marks=config_in.max_marks,
        passing_marks=config_in.passing_marks,
    )
    with Session(engine) as session:
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


def list_exam_weightage_configs(academic_year_id: Optional[int] = None, class_id: Optional[int] = None, school_id: Optional[int] = None) -> List[models.ExamWeightageConfig]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.ExamWeightageConfig).where(models.ExamWeightageConfig.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.ExamWeightageConfig.academic_year_id == academic_year_id)
        if class_id is not None:
            statement = statement.where(models.ExamWeightageConfig.class_id == class_id)
        return session.exec(statement).all()


# ========== GRADE SCALE ==========

def create_grade_scale(grade_scale_in: schemas.GradeScaleCreate, current_user: models.User) -> models.GradeScale:
    sid = _get_school_id()
    if grade_scale_in.is_default:
        with Session(engine) as session:
            existing = session.exec(
                select(models.GradeScale).where(models.GradeScale.school_id == sid, models.GradeScale.is_default == True)
            ).all()
            for gs in existing:
                gs.is_default = False
                session.add(gs)

    grade_scale = models.GradeScale(
        school_id=sid,
        name=grade_scale_in.name,
        scale_type=grade_scale_in.scale_type or "percentage",
        min_value=grade_scale_in.min_value or 0.0,
        max_value=grade_scale_in.max_value or 100.0,
        passing_value=grade_scale_in.passing_value or 40.0,
        is_default=grade_scale_in.is_default or False,
    )
    with Session(engine) as session:
        session.add(grade_scale)
        session.commit()
        session.refresh(grade_scale)
    return grade_scale


def list_grade_scales(school_id: Optional[int] = None) -> List[models.GradeScale]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.GradeScale).where(models.GradeScale.school_id == sid).order_by(models.GradeScale.created_on)
        ).all()


def get_grade_scale(grade_scale_id: int, school_id: Optional[int] = None) -> Optional[models.GradeScale]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        grade_scale = session.get(models.GradeScale, grade_scale_id)
        if not grade_scale or (sid is not None and grade_scale.school_id != sid):
            return None
        return grade_scale


def update_grade_scale(grade_scale_id: int, grade_scale_update: schemas.GradeScaleUpdate, current_user: models.User) -> Optional[models.GradeScale]:
    sid = _get_school_id()
    with Session(engine) as session:
        grade_scale = session.get(models.GradeScale, grade_scale_id)
        if not grade_scale or (sid is not None and grade_scale.school_id != sid):
            return None
        update_data = grade_scale_update.dict(exclude_unset=True)
        if update_data.get("is_default"):
            existing = session.exec(
                select(models.GradeScale).where(models.GradeScale.school_id == sid, models.GradeScale.id != grade_scale_id, models.GradeScale.is_default == True)
            ).all()
            for gs in existing:
                gs.is_default = False
                session.add(gs)
        for k, v in update_data.items():
            setattr(grade_scale, k, v)
        session.add(grade_scale)
        session.commit()
        session.refresh(grade_scale)
        return grade_scale


# ========== GRADE SCALE RANGES ==========

def create_grade_scale_range(range_in: schemas.GradeScaleRangeCreate, current_user: models.User) -> models.GradeScaleRange:
    sid = _get_school_id()
    grade_range = models.GradeScaleRange(
        grade_scale_id=range_in.grade_scale_id,
        school_id=sid,
        grade=range_in.grade,
        grade_point=range_in.grade_point,
        min_mark=range_in.min_mark,
        max_mark=range_in.max_mark,
        description=range_in.description,
        is_passing=range_in.is_passing if range_in.is_passing is not None else True,
        sort_order=range_in.sort_order or 0,
    )
    with Session(engine) as session:
        session.add(grade_range)
        session.commit()
        session.refresh(grade_range)
    return grade_range


def list_grade_scale_ranges(grade_scale_id: int, school_id: Optional[int] = None) -> List[models.GradeScaleRange]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.GradeScaleRange).where(
                models.GradeScaleRange.grade_scale_id == grade_scale_id,
                models.GradeScaleRange.school_id == sid,
            ).order_by(models.GradeScaleRange.sort_order)
        ).all()


def update_grade_scale_range(range_id: int, range_update: schemas.GradeScaleRangeUpdate, current_user: models.User) -> Optional[models.GradeScaleRange]:
    sid = _get_school_id()
    with Session(engine) as session:
        grade_range = session.get(models.GradeScaleRange, range_id)
        if not grade_range or (sid is not None and grade_range.school_id != sid):
            return None
        update_data = range_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(grade_range, k, v)
        session.add(grade_range)
        session.commit()
        session.refresh(grade_range)
        return grade_range


# ========== GPA ENGINE ==========

def create_gpa_engine_config(gpa_in: schemas.GpaEngineConfigCreate, current_user: models.User) -> models.GpaEngineConfig:
    sid = _get_school_id()
    gpa_config = models.GpaEngineConfig(
        school_id=sid,
        name=gpa_in.name,
        scale_type=gpa_in.scale_type or "4_point",
        max_gpa=gpa_in.max_gpa or 4.0,
        min_gpa=gpa_in.min_gpa or 0.0,
        grade_point_decimals=gpa_in.grade_point_decimals or 2,
        credit_based=gpa_in.credit_based or False,
        weighted=gpa_in.weighted or False,
        formula_config=gpa_in.formula_config,
    )
    with Session(engine) as session:
        session.add(gpa_config)
        session.commit()
        session.refresh(gpa_config)
    return gpa_config


def list_gpa_engine_configs(school_id: Optional[int] = None) -> List[models.GpaEngineConfig]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.GpaEngineConfig).where(models.GpaEngineConfig.school_id == sid).order_by(models.GpaEngineConfig.created_on)
        ).all()


def get_gpa_engine_config(gpa_engine_id: int, school_id: Optional[int] = None) -> Optional[models.GpaEngineConfig]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        gpa_config = session.get(models.GpaEngineConfig, gpa_engine_id)
        if not gpa_config or (sid is not None and gpa_config.school_id != sid):
            return None
        return gpa_config


def update_gpa_engine_config(gpa_engine_id: int, gpa_update: schemas.GpaEngineConfigUpdate, current_user: models.User) -> Optional[models.GpaEngineConfig]:
    sid = _get_school_id()
    with Session(engine) as session:
        gpa_config = session.get(models.GpaEngineConfig, gpa_engine_id)
        if not gpa_config or (sid is not None and gpa_config.school_id != sid):
            return None
        update_data = gpa_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(gpa_config, k, v)
        session.add(gpa_config)
        session.commit()
        session.refresh(gpa_config)
        return gpa_config


# ========== GPA GRADE MAPPING ==========

def create_gpa_grade_mapping(mapping_in: schemas.GpaGradeMappingCreate, current_user: models.User) -> models.GpaGradeMapping:
    sid = _get_school_id()
    mapping = models.GpaGradeMapping(
        gpa_engine_id=mapping_in.gpa_engine_id,
        school_id=sid,
        grade=mapping_in.grade,
        grade_point=mapping_in.grade_point,
        min_percentage=mapping_in.min_percentage,
        max_percentage=mapping_in.max_percentage,
        description=mapping_in.description,
        is_passing=mapping_in.is_passing if mapping_in.is_passing is not None else True,
        sort_order=mapping_in.sort_order or 0,
    )
    with Session(engine) as session:
        session.add(mapping)
        session.commit()
        session.refresh(mapping)
    return mapping


def list_gpa_grade_mappings(gpa_engine_id: int, school_id: Optional[int] = None) -> List[models.GpaGradeMapping]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.GpaGradeMapping).where(
                models.GpaGradeMapping.gpa_engine_id == gpa_engine_id,
                models.GpaGradeMapping.school_id == sid,
            ).order_by(models.GpaGradeMapping.sort_order)
        ).all()


def update_gpa_grade_mapping(mapping_id: int, mapping_update: schemas.GpaGradeMappingUpdate, current_user: models.User) -> Optional[models.GpaGradeMapping]:
    sid = _get_school_id()
    with Session(engine) as session:
        mapping = session.get(models.GpaGradeMapping, mapping_id)
        if not mapping or (sid is not None and mapping.school_id != sid):
            return None
        update_data = mapping_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(mapping, k, v)
        session.add(mapping)
        session.commit()
        session.refresh(mapping)
        return mapping


# ========== SUBJECT CATEGORIES ==========

def create_subject_category(category_in: schemas.SubjectCategoryCreate, current_user: models.User) -> models.SubjectCategory:
    sid = _get_school_id()
    category = models.SubjectCategory(
        school_id=sid,
        name=category_in.name,
        code=category_in.code,
        description=category_in.description,
        color=category_in.color,
        sort_order=category_in.sort_order or 0,
    )
    with Session(engine) as session:
        session.add(category)
        session.commit()
        session.refresh(category)
    return category


def list_subject_categories(school_id: Optional[int] = None) -> List[models.SubjectCategory]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.SubjectCategory).where(models.SubjectCategory.school_id == sid).order_by(models.SubjectCategory.sort_order)
        ).all()


def update_subject_category(category_id: int, category_update: schemas.SubjectCategoryUpdate, current_user: models.User) -> Optional[models.SubjectCategory]:
    sid = _get_school_id()
    with Session(engine) as session:
        category = session.get(models.SubjectCategory, category_id)
        if not category or (sid is not None and category.school_id != sid):
            return None
        update_data = category_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(category, k, v)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category


def delete_subject_category(category_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        category = session.get(models.SubjectCategory, category_id)
        if not category or (sid is not None and category.school_id != sid):
            return False
        session.delete(category)
        session.commit()
        return True


def create_subject_category_mapping(mapping_in: schemas.SubjectCategoryMappingCreate, current_user: models.User) -> models.SubjectCategoryMapping:
    sid = _get_school_id()
    mapping = models.SubjectCategoryMapping(
        school_id=sid,
        subject_id=mapping_in.subject_id,
        category_id=mapping_in.category_id,
        is_primary=mapping_in.is_primary if mapping_in.is_primary is not None else True,
    )
    with Session(engine) as session:
        session.add(mapping)
        session.commit()
        session.refresh(mapping)
    return mapping


def list_subject_category_mappings(school_id: Optional[int] = None) -> List[models.SubjectCategoryMapping]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.SubjectCategoryMapping).where(models.SubjectCategoryMapping.school_id == sid)
        ).all()


# ========== REPORT CARDS ==========

def create_report_card(report_card_in: schemas.ReportCardCreate, current_user: models.User) -> models.ReportCard:
    sid = _get_school_id()
    report_card = models.ReportCard(
        school_id=sid,
        academic_year_id=report_card_in.academic_year_id,
        exam_id=report_card_in.exam_id,
        template_id=report_card_in.template_id,
        student_id=report_card_in.student_id,
        class_id=report_card_in.class_id,
        section_id=report_card_in.section_id,
        template_config=report_card_in.template_config,
        student_data=report_card_in.student_data,
        grades_data=report_card_in.grades_data,
        overall_grade=report_card_in.overall_grade,
        overall_gpa=report_card_in.overall_gpa,
        overall_percentage=report_card_in.overall_percentage,
        total_marks_obtained=report_card_in.total_marks_obtained,
        total_marks_possible=report_card_in.total_marks_possible,
        attendance_data=report_card_in.attendance_data,
        remarks=report_card_in.remarks,
        teacher_remark=report_card_in.teacher_remark,
        principal_remark=report_card_in.principal_remark,
        status="draft",
        generated_by=current_user.id,
        generated_on=datetime.utcnow(),
    )
    with Session(engine) as session:
        session.add(report_card)
        session.commit()
        session.refresh(report_card)
    return report_card


def get_report_card(report_card_id: int, school_id: Optional[int] = None) -> Optional[models.ReportCard]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return None
        return report_card


def list_report_cards(
    academic_year_id: Optional[int] = None,
    exam_id: Optional[int] = None,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    template_id: Optional[int] = None,
    status: Optional[str] = None,
    school_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.ReportCard]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.ReportCard).where(models.ReportCard.school_id == sid)
        if academic_year_id is not None:
            statement = statement.where(models.ReportCard.academic_year_id == academic_year_id)
        if exam_id is not None:
            statement = statement.where(models.ReportCard.exam_id == exam_id)
        if class_id is not None:
            statement = statement.where(models.ReportCard.class_id == class_id)
        if student_id is not None:
            statement = statement.where(models.ReportCard.student_id == student_id)
        if template_id is not None:
            statement = statement.where(models.ReportCard.template_id == template_id)
        if status is not None:
            statement = statement.where(models.ReportCard.status == status)
        statement = statement.order_by(models.ReportCard.created_on.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()


def update_report_card(report_card_id: int, report_card_update: schemas.ReportCardUpdate, current_user: models.User) -> Optional[models.ReportCard]:
    sid = _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return None
        update_data = report_card_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(report_card, k, v)
        session.add(report_card)
        session.commit()
        session.refresh(report_card)
        return report_card


def publish_report_card(report_card_id: int, current_user: models.User) -> Optional[models.ReportCard]:
    sid = _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return None
        report_card.status = "published"
        report_card.published_on = datetime.utcnow()
        session.add(report_card)
        session.commit()
        session.refresh(report_card)

        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="publish",
            resource="report_card",
            resource_id=report_card_id,
            details=f"Published report card for student {report_card.student_id}",
        )

        return report_card


def archive_report_card(report_card_id: int, current_user: models.User) -> Optional[models.ReportCard]:
    sid = _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return None
        report_card.status = "archived"
        session.add(report_card)
        session.commit()
        session.refresh(report_card)
        return report_card


def bulk_generate_report_cards(generate_in: schemas.BulkReportCardGenerate, current_user: models.User) -> Dict[str, Any]:
    sid = _get_school_id()
    generated = 0
    failed = 0
    published = 0
    errors = []

    with Session(engine) as session:
        if generate_in.student_ids:
            student_ids = generate_in.student_ids
        else:
            enrollments = session.exec(
                select(models.Enrollment).where(
                    models.Enrollment.class_id == generate_in.class_id,
                    models.Enrollment.academic_year_id == generate_in.academic_year_id,
                    models.Enrollment.school_id == sid,
                )
            ).all()
            student_ids = [e.student_id for e in enrollments]

        for student_id in student_ids:
            try:
                existing = session.exec(
                    select(models.ReportCard).where(
                        models.ReportCard.school_id == sid,
                        models.ReportCard.student_id == student_id,
                        models.ReportCard.academic_year_id == generate_in.academic_year_id,
                        models.ReportCard.exam_id == generate_in.exam_id,
                    )
                ).first()
                if existing:
                    failed += 1
                    errors.append(f"Report card already exists for student {student_id}")
                    continue

                report_card = models.ReportCard(
                    school_id=sid,
                    academic_year_id=generate_in.academic_year_id,
                    exam_id=generate_in.exam_id,
                    template_id=generate_in.template_id,
                    student_id=student_id,
                    class_id=generate_in.class_id,
                    status="published" if generate_in.publish else "draft",
                    generated_by=current_user.id,
                    generated_on=datetime.utcnow(),
                    published_on=datetime.utcnow() if generate_in.publish else None,
                )
                session.add(report_card)
                generated += 1

                if generate_in.publish:
                    published += 1
            except Exception as e:
                failed += 1
                errors.append(f"Student {student_id}: {str(e)}")

        session.commit()

    log_audit(
        user_id=current_user.id,
        school_id=sid,
        action="bulk_generate",
        resource="report_card",
        details=f"Bulk generated {generated} report cards, {failed} failed, {published} published",
    )

    return {"generated": generated, "failed": failed, "published": published, "errors": errors}


# ========== REPORT CARD GRADES ==========

def create_report_card_subject(grade_in: schemas.ReportCardSubjectCreate, current_user: models.User) -> models.ReportCardSubject:
    sid = _get_school_id()
    grade = models.ReportCardSubject(
        report_card_id=grade_in.report_card_id,
        school_id=sid,
        subject_id=grade_in.subject_id,
        examination_type_id=grade_in.examination_type_id,
        marks_obtained=grade_in.marks_obtained,
        marks_max=grade_in.marks_max,
        percentage=grade_in.percentage,
        grade=grade_in.grade,
        grade_point=grade_in.grade_point,
        grade_scale_range_id=grade_in.grade_scale_range_id,
        remarks=grade_in.remarks,
        teacher_remark=grade_in.teacher_remark,
        is_passing=grade_in.is_passing,
        credit_hours=grade_in.credit_hours,
        weightage=grade_in.weightage,
    )
    with Session(engine) as session:
        session.add(grade)
        session.commit()
        session.refresh(grade)
    return grade


def list_report_card_subjects(report_card_id: int, school_id: Optional[int] = None) -> List[models.ReportCardSubject]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        return session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == report_card_id,
                models.ReportCardSubject.school_id == sid,
            )
        ).all()


def update_report_card_subject(grade_id: int, grade_update: schemas.ReportCardSubjectUpdate, current_user: models.User) -> Optional[models.ReportCardSubject]:
    sid = _get_school_id()
    with Session(engine) as session:
        grade = session.get(models.ReportCardSubject, grade_id)
        if not grade or (sid is not None and grade.school_id != sid):
            return None
        update_data = grade_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(grade, k, v)
        session.add(grade)
        session.commit()
        session.refresh(grade)
        return grade


def calculate_overall_grade(report_card_id: int, school_id: Optional[int] = None) -> Dict[str, Any]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return {}

        grades = session.exec(
            select(models.ReportCardSubject).where(
                models.ReportCardSubject.report_card_id == report_card_id,
                models.ReportCardSubject.school_id == sid,
            )
        ).all()

        total_marks_obtained = sum(g.marks_obtained or 0 for g in grades)
        total_marks_possible = sum(g.marks_max or 0 for g in grades)
        overall_percentage = (total_marks_obtained / total_marks_possible * 100) if total_marks_possible > 0 else 0.0

        grade_scale = None
        if report_card.template_id:
            template = session.get(models.ReportCardTemplate, report_card.template_id)
            if template:
                grade_scale = session.get(models.GradeScale, template.config)

        overall_grade = None
        overall_gpa = None
        if grade_scale:
            grade_ranges = session.exec(
                select(models.GradeScaleRange).where(models.GradeScaleRange.grade_scale_id == grade_scale.id)
            ).all()
            for gr in grade_ranges:
                if gr.min_mark <= overall_percentage <= gr.max_mark:
                    overall_grade = gr.grade
                    overall_gpa = gr.grade_point
                    break

        report_card.overall_grade = overall_grade
        report_card.overall_gpa = overall_gpa
        report_card.overall_percentage = round(overall_percentage, 2)
        report_card.total_marks_obtained = total_marks_obtained
        report_card.total_marks_possible = total_marks_possible
        session.add(report_card)
        session.commit()

        return {
            "overall_percentage": round(overall_percentage, 2),
            "overall_grade": overall_grade,
            "overall_gpa": overall_gpa,
            "total_marks_obtained": total_marks_obtained,
            "total_marks_possible": total_marks_possible,
        }


def delete_report_card(report_card_id: int, current_user: models.User) -> bool:
    sid = _get_school_id()
    with Session(engine) as session:
        report_card = session.get(models.ReportCard, report_card_id)
        if not report_card or (sid is not None and report_card.school_id != sid):
            return False
        session.delete(report_card)
        session.commit()
        log_audit(
            user_id=current_user.id,
            school_id=sid,
            action="delete",
            resource="report_card",
            resource_id=report_card_id,
            details=f"Deleted report card for student {report_card.student_id}",
        )
        return True


def get_report_card_by_verification_id(verification_id: str) -> Optional[models.ReportCard]:
    with Session(engine) as session:
        statement = select(models.ReportCard).where(models.ReportCard.verification_id == verification_id)
        return session.exec(statement).first()


def get_report_card_stats(school_id: Optional[int] = None) -> Dict[str, Any]:
    sid = school_id or _get_school_id()
    with Session(engine) as session:
        statement = select(models.ReportCard).where(models.ReportCard.school_id == sid)
        cards = session.exec(statement).all()
        total = len(cards)
        draft = sum(1 for c in cards if c.status == "draft")
        generated = sum(1 for c in cards if c.status == "generated")
        published = sum(1 for c in cards if c.status == "published")
        archived = sum(1 for c in cards if c.status == "archived")
        pass_count = sum(1 for c in cards if c.result_status == "PASS")
        fail_count = sum(1 for c in cards if c.result_status == "FAIL")
        return {
            "total": total,
            "draft": draft,
            "generated": generated,
            "published": published,
            "archived": archived,
            "pass_count": pass_count,
            "fail_count": fail_count,
        }