"""Seed script to create initial school, roles, and a super admin user."""
from app import database, models, auth
from sqlmodel import Session, select
from datetime import date, timedelta


def seed():
    database.init_db()
    with Session(database.engine) as session:
        # Create default school if not exists
        default_school = session.exec(
            select(models.School).where(models.School.school_code == "DEFAULT")
        ).first()
        if not default_school:
            default_school = models.School(
                school_name="Default School",
                school_code="DEFAULT",
                email="admin@default.school",
                phone="000-000-0000",
                address="Default Address",
                city="Default City",
                state="Default State",
                country="Default Country",
                principal_name="Default Principal",
                subscription_plan="premium",
                subscription_start=date.today(),
                subscription_end=date.today() + timedelta(days=365),
                status="active",
                timezone="UTC",
                currency="USD",
                student_limit=2000,
                teacher_limit=200,
            )
            session.add(default_school)
            session.commit()
            session.refresh(default_school)
            print(f"Created default school: {default_school.school_name} (ID: {default_school.id})")
        else:
            print(f"Default school already exists (ID: {default_school.id})")

        # Create roles
        existing = session.exec(select(models.Role).where(models.Role.name == "Super Admin")).first()
        if not existing:
            sa = models.Role(name="Super Admin", description="Full system access", school_id=default_school.id)
            session.add(sa)
        for rname in ["School Admin", "Principal", "Teacher", "Student", "Parent"]:
            if not session.exec(select(models.Role).where(models.Role.name == rname)).first():
                session.add(models.Role(name=rname, school_id=default_school.id))
        session.commit()

        # Create super admin user (platform owner)
        admin_email = "admin@school.local"
        if not session.exec(select(models.User).where(models.User.email == admin_email)).first():
            hashed = auth.get_password_hash("admin123")
            admin = models.User(
                email=admin_email,
                full_name="Super Admin",
                hashed_password=hashed,
                role="Super Admin",
                school_id=default_school.id,
            )
            session.add(admin)
            session.commit()
            print(f"Created super admin user: {admin_email} (password: admin123)")
        else:
            print("Super admin user already exists")

        # Create a demo school admin for the default school
        school_admin_email = "schooladmin@default.school"
        if not session.exec(select(models.User).where(models.User.email == school_admin_email)).first():
            hashed = auth.get_password_hash("admin123")
            school_admin = models.User(
                email=school_admin_email,
                full_name="School Admin",
                hashed_password=hashed,
                role="School Admin",
                school_id=default_school.id,
            )
            session.add(school_admin)
            session.commit()
            print(f"Created school admin user: {school_admin_email} (password: admin123)")
        else:
            print("School admin user already exists")


if __name__ == "__main__":
    seed()