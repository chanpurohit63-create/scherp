import asyncio
import logging
from typing import Optional, Dict, List
from fastapi import WebSocket
from datetime import datetime
from sqlmodel import Session, select

from .database import engine
from .models import Notification, User, Student, Parent, Teacher, Enrollment

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.role_connections: Dict[str, List[int]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        await websocket.accept()
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            if role not in self.role_connections:
                self.role_connections[role] = []
            if user_id not in self.role_connections[role]:
                self.role_connections[role].append(user_id)
        logger.info(f"WebSocket connected: user_id={user_id}, role={role}")
        await self.send_personal_message(user_id, {
            "type": "connected",
            "message": "WebSocket connection established",
            "user_id": user_id,
            "role": role
        })

    async def disconnect(self, websocket: WebSocket, user_id: int, role: str):
        async with self._lock:
            if user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    if role in self.role_connections and user_id in self.role_connections[role]:
                        self.role_connections[role].remove(user_id)
        logger.info(f"WebSocket disconnected: user_id={user_id}, role={role}")

    async def send_personal_message(self, user_id: int, message: dict):
        async with self._lock:
            connections = self.active_connections.get(user_id, [])
            dead = []
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                connections.remove(ws)

    async def broadcast_by_role(self, role: str, message: dict):
        async with self._lock:
            user_ids = self.role_connections.get(role, [])
            for uid in user_ids:
                for ws in self.active_connections.get(uid, []):
                    try:
                        await ws.send_json(message)
                    except Exception:
                        pass

    async def broadcast_to_all(self, message: dict, exclude_user_id: Optional[int] = None):
        async with self._lock:
            for uid, conns in self.active_connections.items():
                if exclude_user_id and uid == exclude_user_id:
                    continue
                for ws in conns:
                    try:
                        await ws.send_json(message)
                    except Exception:
                        pass

    async def send_heartbeat(self, user_id: int):
        await self.send_personal_message(user_id, {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_connected_users(self) -> List[int]:
        return list(self.active_connections.keys())

    def get_connection_count(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())


connection_manager = ConnectionManager()


class NotificationService:

    @staticmethod
    def _get_user_role(user_id: int) -> Optional[str]:
        with Session(engine) as session:
            u = session.get(User, user_id)
            return u.role if u else None

    @staticmethod
    def _get_student_parents(student_id: int) -> List[int]:
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if not s:
                return []
            ids = []
            if s.father_id:
                p = session.get(Parent, s.father_id)
                if p:
                    ids.append(p.user_id)
            if s.mother_id:
                p = session.get(Parent, s.mother_id)
                if p:
                    ids.append(p.user_id)
            return ids

    @staticmethod
    def _get_students_for_class(class_id: int) -> List[int]:
        with Session(engine) as session:
            enrolls = session.exec(select(Enrollment).where(Enrollment.class_id == class_id)).all()
            ids = []
            for e in enrolls:
                s = session.get(Student, e.student_id)
                if s:
                    ids.append(s.user_id)
            return ids

    @staticmethod
    def _get_teacher_user_id(teacher_id: int) -> Optional[int]:
        with Session(engine) as session:
            t = session.get(Teacher, teacher_id)
            return t.user_id if t else None

    @staticmethod
    def _serialize(n: Notification) -> dict:
        return {
            "id": n.id, "user_id": n.user_id,
            "role": n.role, "category": n.category, "title": n.title, "message": n.message,
            "priority": n.priority, "related_module": n.related_module,
            "related_record_id": n.related_record_id, "sender_id": n.sender_id,
            "is_read": n.is_read, "is_archived": n.is_archived,
            "is_pinned": n.is_pinned,
            "created_on": n.created_on.isoformat(),
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }

    @staticmethod
    async def create_and_send(
        user_id: int,
        title: str,
        message: str,
        category: Optional[str] = None,
        priority: Optional[str] = "normal",
        related_module: Optional[str] = None,
        related_record_id: Optional[int] = None,
        sender_id: Optional[int] = None,
    ) -> Notification:
        """Create a notification in DB and send via WebSocket."""
        role = NotificationService._get_user_role(user_id)
        with Session(engine) as session:
            user = session.get(User, user_id)
            school_id = user.school_id if user else None
        n = Notification(
            user_id=user_id, role=role, category=category, title=title,
            message=message, priority=priority, related_module=related_module,
            related_record_id=related_record_id, sender_id=sender_id,
            school_id=school_id,
        )
        with Session(engine) as session:
            session.add(n)
            session.commit()
            session.refresh(n)

        await connection_manager.send_personal_message(user_id, {
            "type": "notification.created",
            "notification": NotificationService._serialize(n)
        })
        return n

    @staticmethod
    async def broadcast_to_role(
        role: str,
        title: str,
        message: str,
        category: Optional[str] = None,
        priority: Optional[str] = "normal",
        sender_id: Optional[int] = None,
    ):
        """Send notification to all users with a specific role."""
        with Session(engine) as session:
            for u in session.exec(select(User).where(User.role == role)).all():
                await NotificationService.create_and_send(
                    user_id=u.id, title=title, message=message,
                    category=category, priority=priority, sender_id=sender_id
                )

    @staticmethod
    async def broadcast_to_class(
        class_id: int,
        title: str,
        message: str,
        category: Optional[str] = None,
        priority: Optional[str] = "normal",
        sender_id: Optional[int] = None,
    ):
        """Send notification to all students in a class and their parents."""
        for uid in NotificationService._get_students_for_class(class_id):
            await NotificationService.create_and_send(
                user_id=uid, title=title, message=message,
                category=category, priority=priority, sender_id=sender_id
            )
            with Session(engine) as session:
                s = session.exec(select(Student).where(Student.user_id == uid)).first()
                if s:
                    for pid in NotificationService._get_student_parents(s.id):
                        await NotificationService.create_and_send(
                            user_id=pid, title=title, message=message,
                            category=category, priority=priority, sender_id=sender_id
                        )

    # ========== EVENT TRIGGERS ==========
    @staticmethod
    async def notify_homework_assigned(homework_id: int, class_id: int, title: str, assigned_by_name: str):
        for uid in NotificationService._get_students_for_class(class_id):
            await NotificationService.create_and_send(
                user_id=uid, title="Homework Assigned",
                message=f"New homework: {title} assigned by {assigned_by_name}",
                category="Homework", related_module="homework", related_record_id=homework_id
            )
            with Session(engine) as session:
                s = session.exec(select(Student).where(Student.user_id == uid)).first()
                if s:
                    for pid in NotificationService._get_student_parents(s.id):
                        await NotificationService.create_and_send(
                            user_id=pid, title="Homework Assigned",
                            message=f"Homework assigned to your child: {title}",
                            category="Homework", related_module="homework", related_record_id=homework_id
                        )

    @staticmethod
    async def notify_homework_submitted(homework_id: int, student_name: str, teacher_id: int):
        tuid = NotificationService._get_teacher_user_id(teacher_id)
        if tuid:
            await NotificationService.create_and_send(
                user_id=tuid, title="Homework Submission Received",
                message=f"{student_name} submitted homework",
                category="Homework", related_module="homework", related_record_id=homework_id
            )

    @staticmethod
    async def notify_homework_graded(homework_id: int, student_id: int, grade: str):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Homework Graded",
                    message=f"Your homework has been graded: {grade}",
                    category="Homework", priority="high",
                    related_module="homework", related_record_id=homework_id
                )
                for pid in NotificationService._get_student_parents(student_id):
                    await NotificationService.create_and_send(
                        user_id=pid, title="Homework Graded",
                        message=f"Your child's homework has been graded: {grade}",
                        category="Homework", related_module="homework", related_record_id=homework_id
                    )

    @staticmethod
    async def notify_attendance_marked(student_id: int, status: str, date_str: str):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Attendance Marked",
                    message=f"Attendance marked as {status} for {date_str}",
                    category="Attendance", related_module="attendance", related_record_id=student_id
                )
                if status == "absent":
                    for pid in NotificationService._get_student_parents(student_id):
                        await NotificationService.create_and_send(
                            user_id=pid, title="Child Absent",
                            message=f"Your child was marked absent on {date_str}",
                            category="Attendance", priority="high",
                            related_module="attendance", related_record_id=student_id
                        )

    @staticmethod
    async def notify_exam_scheduled(exam_id: int, exam_name: str, class_ids: List[int]):
        for cid in class_ids:
            for uid in NotificationService._get_students_for_class(cid):
                await NotificationService.create_and_send(
                    user_id=uid, title="Exam Scheduled",
                    message=f"Exam scheduled: {exam_name}",
                    category="Examinations", related_module="exams", related_record_id=exam_id
                )
                with Session(engine) as session:
                    s = session.exec(select(Student).where(Student.user_id == uid)).first()
                    if s:
                        for pid in NotificationService._get_student_parents(s.id):
                            await NotificationService.create_and_send(
                                user_id=pid, title="Exam Scheduled",
                                message=f"Exam scheduled for your child: {exam_name}",
                                category="Examinations", related_module="exams", related_record_id=exam_id
                            )

    @staticmethod
    async def notify_exam_result_published(exam_id: int, exam_name: str, student_ids: List[int]):
        for sid in student_ids:
            with Session(engine) as session:
                s = session.get(Student, sid)
                if s:
                    await NotificationService.create_and_send(
                        user_id=s.user_id, title="Exam Result Published",
                        message=f"Results for {exam_name} have been published",
                        category="Examinations", priority="high",
                        related_module="exam-results", related_record_id=exam_id
                    )
                    for pid in NotificationService._get_student_parents(sid):
                        await NotificationService.create_and_send(
                            user_id=pid, title="Result Published",
                            message=f"Your child's results for {exam_name} are available",
                            category="Examinations", priority="high",
                            related_module="exam-results", related_record_id=exam_id
                        )

    @staticmethod
    async def notify_fee_payment_received(payment_id: int, student_id: int, amount: float):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Fee Payment Successful",
                    message=f"Payment of ${amount:.2f} received successfully",
                    category="Fees", priority="high",
                    related_module="fees", related_record_id=payment_id
                )
                for pid in NotificationService._get_student_parents(student_id):
                    await NotificationService.create_and_send(
                        user_id=pid, title="Fee Payment Confirmation",
                        message=f"Fee payment of ${amount:.2f} confirmed for your child",
                        category="Fees", related_module="fees", related_record_id=payment_id
                    )
            for a in session.exec(select(User).where(User.role.in_(["Super Admin", "School Admin", "Principal"]))).all():
                await NotificationService.create_and_send(
                    user_id=a.id, title="Fee Payment Received",
                    message=f"Payment of ${amount:.2f} received from student #{student_id}",
                    category="Payments", related_module="payments", related_record_id=payment_id
                )

    @staticmethod
    async def notify_notice_created(notice_id: int, title: str, target_roles: Optional[str]):
        with Session(engine) as session:
            roles = ["Student", "Teacher", "Parent"]
            if target_roles and target_roles != "all":
                roles = [r.strip() for r in target_roles.split(",")]
            for role in roles:
                for u in session.exec(select(User).where(User.role == role)).all():
                    await NotificationService.create_and_send(
                        user_id=u.id, title="New Notice", message=title,
                        category="Announcements", related_module="notices", related_record_id=notice_id
                    )

    @staticmethod
    async def notify_event_created(event_id: int, title: str, target_roles: Optional[str]):
        with Session(engine) as session:
            roles = ["Student", "Teacher", "Parent"]
            if target_roles and target_roles != "all":
                roles = [r.strip() for r in target_roles.split(",")]
            for role in roles:
                for u in session.exec(select(User).where(User.role == role)).all():
                    await NotificationService.create_and_send(
                        user_id=u.id, title="New Event", message=f"New event: {title}",
                        category="Events", related_module="events", related_record_id=event_id
                    )

    @staticmethod
    async def notify_message_received(recipient_id: int, sender_name: str, subject: str, message_id: int):
        await NotificationService.create_and_send(
            user_id=recipient_id, title="Message Received",
            message=f"New message from {sender_name}: {subject}",
            category="Messages", related_module="messages", related_record_id=message_id
        )

    @staticmethod
    async def notify_certificate_generated(student_id: int, certificate_type: str, certificate_id: int):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Certificate Generated",
                    message=f"Your {certificate_type} has been generated",
                    category="Certificates", priority="high",
                    related_module="certificates", related_record_id=certificate_id
                )

    @staticmethod
    async def notify_document_uploaded(student_id: int, document_name: str, document_id: int):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Document Uploaded",
                    message=f"Document uploaded: {document_name}",
                    category="Documents", related_module="documents", related_record_id=document_id
                )

    @staticmethod
    async def notify_new_enrollment(student_id: int, student_name: str):
        with Session(engine) as session:
            for a in session.exec(select(User).where(User.role.in_(["Super Admin", "School Admin", "Principal"]))).all():
                await NotificationService.create_and_send(
                    user_id=a.id, title="New Student Enrolment",
                    message=f"New student enrolled: {student_name}",
                    category="Academic", related_module="enrollments", related_record_id=student_id
                )

    @staticmethod
    async def notify_low_attendance(student_id: int, percentage: float):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Low Attendance Warning",
                    message=f"Your attendance is {percentage:.1f}%. Please improve attendance.",
                    category="Attendance", priority="high",
                    related_module="attendance", related_record_id=student_id
                )

    @staticmethod
    async def notify_fee_reminder(student_id: int, amount: float, due_date: str):
        with Session(engine) as session:
            s = session.get(Student, student_id)
            if s:
                await NotificationService.create_and_send(
                    user_id=s.user_id, title="Fee Reminder",
                    message=f"Fee of ${amount:.2f} is due on {due_date}",
                    category="Fees", priority="normal", related_module="fees"
                )
                for pid in NotificationService._get_student_parents(student_id):
                    await NotificationService.create_and_send(
                        user_id=pid, title="Fee Due Reminder",
                        message=f"Fee of ${amount:.2f} for your child is due on {due_date}",
                        category="Fees", priority="normal", related_module="fees"
                    )

    @staticmethod
    async def notify_teacher_leave_request(teacher_id: int, teacher_name: str):
        with Session(engine) as session:
            for a in session.exec(select(User).where(User.role.in_(["Super Admin", "School Admin", "Principal"]))).all():
                await NotificationService.create_and_send(
                    user_id=a.id, title="Teacher Leave Request",
                    message=f"{teacher_name} has requested leave",
                    category="System", related_module="teachers", related_record_id=teacher_id
                )

    @staticmethod
    async def notify_exam_approaching(exam_name: str, days_left: int, student_ids: List[int]):
        for sid in student_ids:
            with Session(engine) as session:
                s = session.get(Student, sid)
                if s:
                    await NotificationService.create_and_send(
                        user_id=s.user_id, title="Exam Approaching",
                        message=f"{exam_name} starts in {days_left} days",
                        category="Examinations",
                        priority="high" if days_left <= 3 else "normal",
                        related_module="exams"
                    )

    @staticmethod
    async def notify_attendance_pending(teacher_id: int, teacher_name: str, date_str: str):
        tuid = NotificationService._get_teacher_user_id(teacher_id)
        if tuid:
            await NotificationService.create_and_send(
                user_id=tuid, title="Attendance Pending",
                message=f"Please mark attendance for {date_str}",
                category="Attendance", priority="normal"
            )
