"""Seed script to create initial roles and an admin user."""
from app import database, models, auth
from sqlmodel import Session, select


def seed():
    database.init_db()
    with Session(database.engine) as session:
        # roles
        existing = session.exec(select(models.Role).where(models.Role.name == "Super Admin")).first()
        if not existing:
            sa = models.Role(name="Super Admin", description="Full system access")
            session.add(sa)
        for rname in ["School Admin", "Principal", "Teacher", "Student", "Parent"]:
            if not session.exec(select(models.Role).where(models.Role.name == rname)).first():
                session.add(models.Role(name=rname))
        session.commit()

        # admin user
        admin_email = "admin@school.local"
        if not session.exec(select(models.User).where(models.User.email == admin_email)).first():
            hashed = auth.get_password_hash("admin123")
            admin = models.User(email=admin_email, full_name="Super Admin", hashed_password=hashed, role="Super Admin")
            session.add(admin)
            session.commit()
            print("Created admin user: admin@school.local (password: admin123)")
        else:
            print("Admin user already exists")


if __name__ == "__main__":
    seed()
