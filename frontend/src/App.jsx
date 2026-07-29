import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsersPage from './pages/UsersPage'
import StudentsPage from './pages/StudentsPage'
import TeachersPage from './pages/TeachersPage'
import ParentsPage from './pages/ParentsPage'
import AttendancePage from './pages/AttendancePage'
import ExamsPage from './pages/ExamsPage'
import ExamResultsPage from './pages/ExamResultsPage'
import FeesPage from './pages/FeesPage'
import PaymentsPage from './pages/PaymentsPage'
import NoticesPage from './pages/NoticesPage'
import CertificatesPage from './pages/CertificatesPage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'
import AcademicYearsPage from './pages/AcademicYearsPage'
import ClassesPage from './pages/ClassesPage'
import SectionsPage from './pages/SectionsPage'
import SubjectsPage from './pages/SubjectsPage'
import SubjectAllocationsPage from './pages/SubjectAllocationsPage'
import EnrollmentsPage from './pages/EnrollmentsPage'
import HomeworkPage from './pages/HomeworkPage'
import EventsPage from './pages/EventsPage'
// Student Portal
import StudentDashboardPage from './pages/StudentDashboardPage'
import StudentProfilePage from './pages/StudentProfilePage'
import StudentAttendancePage from './pages/StudentAttendancePage'
import StudentHomeworkPage from './pages/StudentHomeworkPage'
import StudentExamsPage from './pages/StudentExamsPage'
import StudentFeesPage from './pages/StudentFeesPage'
import StudentNoticesPage from './pages/StudentNoticesPage'
import StudentCalendarPage from './pages/StudentCalendarPage'
import StudentDocumentsPage from './pages/StudentDocumentsPage'
import StudentMessagesPage from './pages/StudentMessagesPage'
// Parent Portal
import ParentDashboardPage from './pages/ParentDashboardPage'
import ParentChildrenPage from './pages/ParentChildrenPage'
import ParentAttendancePage from './pages/ParentAttendancePage'
import ParentHomeworkPage from './pages/ParentHomeworkPage'
import ParentExamsPage from './pages/ParentExamsPage'
import ParentFeesPage from './pages/ParentFeesPage'
import ParentNoticesPage from './pages/ParentNoticesPage'
import ParentCalendarPage from './pages/ParentCalendarPage'
import ParentMessagesPage from './pages/ParentMessagesPage'
import ParentProfilePage from './pages/ParentProfilePage'
import ParentProgressPage from './pages/ParentProgressPage'
// Teacher Portal
import TeacherDashboardPage from './pages/TeacherDashboardPage'
import TeacherClassesPage from './pages/TeacherClassesPage'
import TeacherAttendancePage from './pages/TeacherAttendancePage'
import TeacherHomeworkPage from './pages/TeacherHomeworkPage'
import TeacherExamsPage from './pages/TeacherExamsPage'
import TeacherStudentsPage from './pages/TeacherStudentsPage'
import TeacherNoticesPage from './pages/TeacherNoticesPage'
import TeacherCalendarPage from './pages/TeacherCalendarPage'
import TeacherMessagesPage from './pages/TeacherMessagesPage'
import TeacherProfilePage from './pages/TeacherProfilePage'
// Notification Pages
import NotificationCenterPage from './pages/NotificationCenterPage'
import NotificationSettingsPage from './pages/NotificationSettings'
// Notification Providers
import { NotificationProvider } from './components/NotificationProvider'
import { WebSocketProvider } from './components/WebSocketProvider'
import './styles.css'

function RequireAuth({ children }) {
  const auth = useAuth()
  if (!auth.isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return children
}

function DashboardRedirect() {
  const auth = useAuth()
  if (!auth.profile) return null
  const role = auth.profile.role
  if (role === 'Student') return <Navigate to="/student/dashboard" replace />
  if (role === 'Parent') return <Navigate to="/parent/dashboard" replace />
  if (role === 'Teacher') return <Navigate to="/teacher/dashboard" replace />
  return <DashboardPage />
}

function AppContent() {
  return (
    <WebSocketProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <Routes>
                {/* Admin Routes */}
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="users" element={<UsersPage />} />
                <Route path="students" element={<StudentsPage />} />
                <Route path="teachers" element={<TeachersPage />} />
                <Route path="parents" element={<ParentsPage />} />
                <Route path="academic-years" element={<AcademicYearsPage />} />
                <Route path="classes" element={<ClassesPage />} />
                <Route path="sections" element={<SectionsPage />} />
                <Route path="subjects" element={<SubjectsPage />} />
                <Route path="subject-allocations" element={<SubjectAllocationsPage />} />
                <Route path="enrollments" element={<EnrollmentsPage />} />
                <Route path="attendance" element={<AttendancePage />} />
                <Route path="homework" element={<HomeworkPage />} />
                <Route path="exams" element={<ExamsPage />} />
                <Route path="exam-results" element={<ExamResultsPage />} />
                <Route path="fees" element={<FeesPage />} />
                <Route path="payments" element={<PaymentsPage />} />
                <Route path="notices" element={<NoticesPage />} />
                <Route path="events" element={<EventsPage />} />
                <Route path="certificates" element={<CertificatesPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="settings" element={<SettingsPage />} />
                {/* Notification Routes */}
                <Route path="notifications" element={<NotificationCenterPage />} />
                <Route path="notifications/settings" element={<NotificationSettingsPage />} />
                {/* Student Portal */}
                <Route path="student/dashboard" element={<StudentDashboardPage />} />
                <Route path="student/profile" element={<StudentProfilePage />} />
                <Route path="student/attendance" element={<StudentAttendancePage />} />
                <Route path="student/homework" element={<StudentHomeworkPage />} />
                <Route path="student/exams" element={<StudentExamsPage />} />
                <Route path="student/fees" element={<StudentFeesPage />} />
                <Route path="student/notices" element={<StudentNoticesPage />} />
                <Route path="student/calendar" element={<StudentCalendarPage />} />
                <Route path="student/documents" element={<StudentDocumentsPage />} />
                <Route path="student/messages" element={<StudentMessagesPage />} />
                {/* Parent Portal */}
                <Route path="parent/dashboard" element={<ParentDashboardPage />} />
                <Route path="parent/children" element={<ParentChildrenPage />} />
                <Route path="parent/children/:studentId/attendance" element={<ParentAttendancePage />} />
                <Route path="parent/children/:studentId/homework" element={<ParentHomeworkPage />} />
                <Route path="parent/children/:studentId/exams" element={<ParentExamsPage />} />
                <Route path="parent/children/:studentId/fees" element={<ParentFeesPage />} />
                <Route path="parent/children/:studentId/progress" element={<ParentProgressPage />} />
                <Route path="parent/notices" element={<ParentNoticesPage />} />
                <Route path="parent/calendar" element={<ParentCalendarPage />} />
                <Route path="parent/messages" element={<ParentMessagesPage />} />
                <Route path="parent/profile" element={<ParentProfilePage />} />
                {/* Teacher Portal */}
                <Route path="teacher/dashboard" element={<TeacherDashboardPage />} />
                <Route path="teacher/classes" element={<TeacherClassesPage />} />
                <Route path="teacher/attendance" element={<TeacherAttendancePage />} />
                <Route path="teacher/homework" element={<TeacherHomeworkPage />} />
                <Route path="teacher/exams" element={<TeacherExamsPage />} />
                <Route path="teacher/students" element={<TeacherStudentsPage />} />
                <Route path="teacher/notices" element={<TeacherNoticesPage />} />
                <Route path="teacher/calendar" element={<TeacherCalendarPage />} />
                <Route path="teacher/messages" element={<TeacherMessagesPage />} />
                <Route path="teacher/profile" element={<TeacherProfilePage />} />
                <Route path="*" element={<DashboardRedirect />} />
              </Routes>
            </RequireAuth>
          }
        />
      </Routes>
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
    </WebSocketProvider>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NotificationProvider>
          <AppContent />
        </NotificationProvider>
      </BrowserRouter>
    </AuthProvider>
  )
}
