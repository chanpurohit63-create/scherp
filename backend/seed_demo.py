"""Comprehensive demo seed script for school ERP demonstration."""
import uuid as uuid_mod
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from app import database, models, auth
from app.database import engine

def seed():
    database.init_db()
    with Session(engine) as session:
        # === 1. SCHOOL (Springfield Greenfield Academy) ===
        school = models.School(
            school_name="Springfield Greenfield Academy",
            school_code="SGA001",
            email="info@springfield.edu",
            phone="+1-555-0100",
            address="123 Greenfield Avenue, Springfield",
            city="Springfield",
            state="IL",
            country="USA",
            postal_code="62701",
            principal_name="Dr. Jane Smith",
            subscription_plan="premium",
            subscription_start=date.today(),
            subscription_end=date.today() + timedelta(days=365),
            status="active",
            timezone="UTC",
            currency="USD",
            student_limit=2000,
            teacher_limit=200,
        )
        session.add(school)
        session.commit()
        session.refresh(school)
        sid = school.id
        print(f"  School: {school.school_name} (ID: {sid})")

        # === 2. ROLES ===
        for rname in ["Super Admin", "School Admin", "Principal", "Teacher", "Student", "Parent"]:
            if not session.exec(select(models.Role).where(models.Role.name == rname, models.Role.school_id == sid)).first():
                session.add(models.Role(name=rname, school_id=sid))
        session.commit()

        # === 3. USERS (Super Admin, School Admin, Teachers, Student Users, Parent Users) ===
        def create_user(email, full_name, role):
            existing = session.exec(select(models.User).where(models.User.email == email)).first()
            if existing:
                return existing
            u = models.User(
                email=email,
                full_name=full_name,
                hashed_password=auth.get_password_hash("admin123"),
                role=role,
                school_id=sid,
                is_active=True,
            )
            session.add(u)
            session.commit()
            session.refresh(u)
            return u

        super_admin = create_user("superadmin@springfield.edu", "Platform Owner", "Super Admin")
        school_admin = create_user("admin@springfield.edu", "Alice Johnson", "School Admin")

        # === 4. SCHOOL SETTINGS ===
        settings = models.SchoolSettings(
            school_id=sid,
            school_name=school.school_name,
            address=school.address,
            phone=school.phone,
            email=school.email,
            principal_name=school.principal_name,
            theme_color="#4f46e5",
        )
        session.add(settings)
        session.commit()

        # === 5. ACADEMIC YEAR ===
        ay = models.AcademicYear(
            school_id=sid,
            name="2025-2026",
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
            is_active=True,
        )
        session.add(ay)
        session.commit()
        session.refresh(ay)

        # === 6. CLASSES ===
        classes = []
        for cname, glevel in [("Class 9", "9"), ("Class 10", "10"), ("Class 11", "11")]:
            c = models.SchoolClass(name=cname, grade_level=glevel, school_id=sid)
            session.add(c)
            session.commit()
            session.refresh(c)
            classes.append(c)

        # === 7. SECTIONS ===
        sections = []
        for ci, c in enumerate(classes):
            for sname in ["A", "B"]:
                s = models.Section(name=sname, class_id=c.id, school_id=sid)
                session.add(s)
                session.commit()
                session.refresh(s)
                sections.append(s)

        # === 8. SUBJECTS ===
        subjects = []
        for sname, scode in [("Mathematics", "MATH"), ("Science", "SCI"), ("English", "ENG"), ("Social Studies", "SST")]:
            s = models.Subject(name=sname, code=scode, school_id=sid)
            session.add(s)
            session.commit()
            session.refresh(s)
            subjects.append(s)

        # === 9. TEACHERS ===
        teachers = []
        teacher_data = [
            ("Ms. Sarah Wilson", "TCH001", "Mathematics"),
            ("Mr. Robert Chen", "TCH002", "Science"),
            ("Mrs. Emily Davis", "TCH003", "English"),
            ("Mr. James Brown", "TCH004", "Social Studies"),
        ]
        for tname, emp_no, subject_name in teacher_data:
            user = create_user(f"teacher{len(teachers)+1}@springfield.edu", tname, "Teacher")
            t = models.Teacher(user_id=user.id, employee_no=emp_no, hire_date=date.today(), school_id=sid)
            session.add(t)
            session.commit()
            session.refresh(t)
            teachers.append(t)

        # === 10. SUBJECT ALLOCATIONS ===
        for c_idx, c in enumerate(classes):
            for s in subjects:
                t_idx = min(c_idx + subjects.index(s), len(teachers) - 1)
                alloc = models.SubjectAllocation(
                    subject_id=s.id,
                    teacher_id=teachers[t_idx].id,
                    class_id=c.id,
                    school_id=sid,
                )
                session.add(alloc)
        session.commit()

        # === 11. PARENTS ===
        parents = []
        parent_names = ["Mr. John Smith", "Mrs. Mary Johnson", "Mr. David Williams", "Mrs. Lisa Brown", "Mr. Robert Davis"]
        for pname in parent_names:
            user = create_user(f"parent{len(parents)+1}@springfield.edu", pname, "Parent")
            p = models.Parent(user_id=user.id, phone=f"555-01{len(parents)+1:02d}", address="Springfield", school_id=sid)
            session.add(p)
            session.commit()
            session.refresh(p)
            parents.append(p)

        # === 12. STUDENTS ===
        students = []
        student_data = [
            ("Alice Anderson", "STU001", "A", 0, 0),
            ("Bob Barker", "STU002", "A", 0, 0),
            ("Carol Clark", "STU003", "B", 0, 0),
            ("David Doe", "STU004", "A", 0, 0),
            ("Eve Evans", "STU005", "B", 0, 0),
            ("Frank Foster", "STU006", "A", 1, 2),
            ("Grace Green", "STU007", "B", 1, 2),
            ("Henry Hill", "STU008", "A", 1, 1),
            ("Ivy Irwin", "STU009", "B", 1, 3),
            ("Jack Jones", "STU010", "A", 2, 0),
            ("Karen King", "STU011", "B", 2, 1),
            ("Leo Lewis", "STU012", "A", 2, 2),
            ("Mia Miller", "STU013", "B", 2, 3),
            ("Noah Nelson", "STU014", "A", 2, 0),
            ("Olivia Owens", "STU015", "B", 2, 1),
        ]
        for sname, adm_no, section_name, class_idx, parent_idx in student_data:
            user = create_user(f"student_{adm_no.lower()}@springfield.edu", sname, "Student")
            c = classes[class_idx]
            sec = None
            for s in sections:
                if s.name == section_name and s.class_id == c.id:
                    sec = s
                    break
            st = models.Student(
                user_id=user.id,
                admission_no=adm_no,
                admission_date=date.today() - timedelta(days=365),
                status="active",
                father_id=parents[parent_idx].id if parent_idx < len(parents) else None,
                school_id=sid,
            )
            session.add(st)
            session.commit()
            session.refresh(st)
            students.append(st)

            # Enrollment
            enrollment = models.Enrollment(
                student_id=st.id,
                academic_year_id=ay.id,
                class_id=c.id,
                section_id=sec.id if sec else None,
                school_id=sid,
            )
            session.add(enrollment)
            session.commit()

        # === 13. PERIOD MASTER ===
        periods = []
        for i, (pname, start, end) in enumerate([
            ("Period 1", "08:00", "08:50"),
            ("Period 2", "09:00", "09:50"),
            ("Period 3", "10:00", "10:50"),
            ("Lunch", "11:00", "11:50"),
            ("Period 4", "12:00", "12:50"),
            ("Period 5", "13:00", "13:50"),
        ]):
            pm = models.PeriodMaster(
                school_id=sid,
                period_name=pname,
                period_number=i + 1,
                start_time=start,
                end_time=end,
            )
            session.add(pm)
            session.commit()
            session.refresh(pm)
            periods.append(pm)

        # === 14. ROOMS ===
        rooms = []
        for rname, rtype in [("Room 101", "Classroom"), ("Room 201", "Classroom"), ("Lab 1", "Lab"), ("Library", "Library")]:
            r = models.Room(
                school_id=sid,
                room_name=rname,
                room_number=rname.split()[-1],
                building="Main Block",
                capacity=40,
                room_type=rtype,
                color="#4f46e5",
                is_active=True,
            )
            session.add(r)
            session.commit()
            session.refresh(r)
            rooms.append(r)

        # === 15. TIMETABLE ENTRIES (sample, Class 10-A) ===
        timetable_entries = []
        for day in range(5):  # Monday-Friday (0-4)
            for period_idx in range(4):  # 4 periods per day
                subject = subjects[period_idx % len(subjects)]
                teacher = teachers[period_idx % len(teachers)]
                room = rooms[0]
                section = sections[1] if periods else None  # Class 10-A
                for s in sections:
                    if s.name == "A" and s.class_id == classes[1].id:
                        section = s
                        break
                tt = models.Timetable(
                    school_id=sid,
                    academic_year_id=ay.id,
                    class_id=classes[1].id,
                    section_id=section.id if section else None,
                    subject_id=subject.id,
                    teacher_id=teacher.id,
                    room_id=room.id,
                    day_of_week=day,
                    period=period_idx + 1,
                    start_time=periods[period_idx].start_time,
                    end_time=periods[period_idx].end_time,
                    status="active",
                    created_by=super_admin.id,
                )
                session.add(tt)
                session.commit()
                session.refresh(tt)
                timetable_entries.append(tt)

        # === 16. ATTENDANCE RECORDS ===
        attendance_date = date.today() - timedelta(days=1)
        for st in students[:5]:
            att = models.Attendance(
                student_id=st.id,
                date=attendance_date,
                status="present" if st.id % 3 != 0 else "absent",
                school_id=sid,
            )
            session.add(att)
        session.commit()

        # === 17. EXAMS ===
        exams = []
        for ename, start_d in [("Midterm Exam 2025", date(2025, 10, 15)), ("Final Exam 2025", date(2026, 3, 10))]:
            e = models.Exam(
                school_id=sid,
                name=ename,
                academic_year_id=ay.id,
                start_date=start_d,
                end_date=start_d + timedelta(days=5),
            )
            session.add(e)
            session.commit()
            session.refresh(e)
            exams.append(e)

        # === 18. EXAM RESULTS ===
        for st in students:
            for subj in subjects:
                max_marks = 100
                obtained = 85 if st.id % 3 == 0 else (72 if st.id % 3 == 1 else 94)
                er = models.ExamResult(
                    exam_id=exams[0].id,
                    student_id=st.id,
                    subject_id=subj.id,
                    marks_obtained=obtained,
                    max_marks=max_marks,
                    school_id=sid,
                )
                session.add(er)
        session.commit()

        # === 19. NOTICES ===
        for i, ntitle in enumerate(["Welcome to Springfield Greenfield Academy", "Parent-Teacher Meeting - Oct 20", "Exam Schedule Released"]):
            n = models.Notice(
                school_id=sid,
                title=ntitle,
                content=f"This is notice {i+1} content for demonstration purposes.",
                target_roles="all",
                created_by=school_admin.id,
                created_on=datetime.utcnow(),
                scheduled_for=None,
            )
            session.add(n)
        session.commit()

        # === 20. HOMEWORK ===
        hw = models.Homework(
            school_id=sid,
            title="Math Assignment - Chapter 5",
            description="Solve problems 1-20 from Chapter 5",
            assigned_by=teachers[0].id,
            class_id=classes[1].id,
            section_id=sections[0].id if sections else None,
            due_date=date.today() + timedelta(days=3),
        )
        session.add(hw)
        session.commit()

        # === 21. FEE STRUCTURES ===
        for fname, famount, fcat in [("Tuition Fee", 5000, "Academic"), ("Lab Fee", 500, "Academic"), ("Transport Fee", 1000, "Other")]:
            fs = models.FeeStructure(
                school_id=sid,
                name=fname,
                description=fcat,
                amount=famount,
                category=fcat,
                due_date=date.today() + timedelta(days=15),
            )
            session.add(fs)
            session.commit()
            session.refresh(fs)

            # Fee assignments for all students
            for st in students:
                fa = models.FeeAssignment(
                    fee_structure_id=fs.id,
                    student_id=st.id,
                    amount=famount,
                    due_date=date.today() + timedelta(days=15),
                    is_paid=(fs.name == "Tuition Fee" and st.id % 3 == 0),
                    school_id=sid,
                )
                session.add(fa)
            session.commit()

        # === 22. REPORT CARD TEMPLATE ===
        template = models.ReportCardTemplate(
            school_id=sid,
            name="Standard Report Card",
            template_type="standard",
            is_active=True,
            created_by=school_admin.id,
        )
        session.add(template)
        session.commit()
        session.refresh(template)

        # === 23. GRADING RULES ===
        rule = models.GradingRule(
            school_id=sid,
            grading_scale="10_point",
            rules_json='{"A+": 90, "A": 80, "B": 70, "C": 60, "D": 50, "F": 0}',
            pass_percentage=33.0,
            is_active=True,
            created_by=school_admin.id,
        )
        session.add(rule)
        session.commit()

        # === 24. SAMPLE REPORT CARD ===
        import hashlib
        verification_id = hashlib.sha256(f"rc-{students[0].id}-{exams[0].id}".encode()).hexdigest()[:12]
        rc = models.ReportCard(
            school_id=sid,
            student_id=students[0].id,
            exam_id=exams[0].id,
            class_id=classes[1].id,
            academic_year_id=ay.id,
            template_id=template.id,
            total_marks=400.0,
            obtained_marks=342.0,
            percentage=85.5,
            overall_grade="A",
            gpa=3.7,
            attendance_percentage=92.5,
            working_days=20,
            present_days=18,
            result_status="PASS",
            promotion_status="PROMOTED",
            rank=2,
            verification_id=verification_id,
            is_regenerated=False,
            status="published",
            generated_by=school_admin.id,
            generated_on=datetime.utcnow(),
            published_on=datetime.utcnow(),
            created_on=datetime.utcnow(),
        )
        session.add(rc)
        session.commit()
        session.refresh(rc)

        # Report Card Subjects
        for subj in subjects:
            obtained = 85 if rc.student_id % 3 == 0 else 72
            rc_subject = models.ReportCardSubject(
                report_card_id=rc.id,
                subject_id=subj.id,
                subject_name=subj.name,
                maximum_marks=100.0,
                obtained_marks=obtained,
                percentage=obtained,
                grade="A" if obtained >= 80 else "B",
                grade_point=3.7 if obtained >= 80 else 2.7,
                remarks="Good",
                school_id=sid,
            )
            session.add(rc_subject)
        session.commit()

        print(f"\n  Demo data seeded:")
        print(f"  - 3 Classes, {len(sections)} Sections")
        print(f"  - {len(teachers)} Teachers")
        print(f"  - {len(students)} Students")
        print(f"  - {len(parents)} Parents")
        print(f"  - {len(subjects)} Subjects")
        print(f"  - {len(exams)} Exams with results")
        print(f"  - {len(timetable_entries)} Timetable entries")
        print(f"  - {len(rooms)} Rooms")
        print(f"  - 3 Fee structures with assignments")
        print(f"  - Report Card Template + 1 published report card")
        print(f"\n  Login credentials:")
        print(f"  Super Admin: superadmin@springfield.edu / admin123")
        print(f"  School Admin: admin@springfield.edu / admin123")


if __name__ == "__main__":
    seed()
