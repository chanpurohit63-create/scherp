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
import TimetableDashboardPage from './pages/TimetableDashboardPage'
import WeeklyTimetablePage from './pages/WeeklyTimetablePage'
import DailyTimetablePage from './pages/DailyTimetablePage'
import TeacherTimetablePage from './pages/TeacherTimetablePage'
import StudentTimetablePage from './pages/StudentTimetablePage'
import ClassTimetablePage from './pages/ClassTimetablePage'
import RoomManagementPage from './pages/RoomManagementPage'
import ConflictMonitorPage from './pages/ConflictMonitorPage'
import TimetableGeneratorPage from './pages/TimetableGeneratorPage'
import PeriodMasterPage from './pages/PeriodMasterPage'
import TeacherAvailabilityPage from './pages/TeacherAvailabilityPage'
import ReportCardDashboardPage from './pages/ReportCardDashboardPage'
import GenerateReportCardPage from './pages/GenerateReportCardPage'
import BulkGenerateReportCardsPage from './pages/BulkGenerateReportCardsPage'
import ReportCardPreviewPage from './pages/ReportCardPreviewPage'
import VerifyReportCardPage from './pages/VerifyReportCardPage'
import ReportCardTemplatesPage from './pages/ReportCardTemplatesPage'
import ReportCardDesignerPage from './pages/ReportCardDesignerPage'
import ReportCardPrintPreviewPage from './pages/ReportCardPrintPreviewPage'
import GradeScalePage from './pages/GradeScalePage'
import GradeScaleRangePage from './pages/GradeScaleRangePage'
import GpaEnginePage from './pages/GpaEnginePage'
import GpaGradeMappingPage from './pages/GpaGradeMappingPage'
import SubjectCategoryPage from './pages/SubjectCategoryPage'
import ExaminationTypePage from './pages/ExaminationTypePage'
import ExamWeightagePage from './pages/ExamWeightagePage'
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
import ParentCertificatesPage from './pages/ParentCertificatesPage'
import ParentDocumentsPage from './pages/ParentDocumentsPage'
import ParentPaymentHistoryPage from './pages/ParentPaymentHistoryPage'
import ParentChangePasswordPage from './pages/ParentChangePasswordPage'
import ParentEventsPage from './pages/ParentEventsPage'
import { ParentChildProvider } from './components/ParentChildContext'
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
        <Route path="/verify/report-card/:verificationId" element={<VerifyReportCardPage />} />
        <Route path="/verify" element={<VerifyReportCardPage />} />
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
                {/* ========== TIMETABLE ========== */}
                <Route path="timetable" element={<TimetableDashboardPage />} />
                <Route path="timetable/weekly" element={<WeeklyTimetablePage />} />
                <Route path="timetable/daily" element={<DailyTimetablePage />} />
                <Route path="timetable/teacher" element={<TeacherTimetablePage />} />
                <Route path="timetable/student" element={<StudentTimetablePage />} />
                <Route path="timetable/class" element={<ClassTimetablePage />} />
                <Route path="timetable/rooms" element={<RoomManagementPage />} />
                <Route path="timetable/conflicts" element={<ConflictMonitorPage />} />
                <Route path="timetable/generator" element={<TimetableGeneratorPage />} />
                <Route path="timetable/periods" element={<PeriodMasterPage />} />
                <Route path="timetable/teacher-availability" element={<TeacherAvailabilityPage />} />
                {/* ========== REPORT CARDS ========== */}
                <Route path="report-cards" element={<ReportCardDashboardPage />} />
                <Route path="report-cards/generate" element={<GenerateReportCardPage />} />
                <Route path="report-cards/bulk-generate" element={<BulkGenerateReportCardsPage />} />
                <Route path="report-cards/:id/preview" element={<ReportCardPreviewPage />} />
                <Route path="report-cards/templates" element={<ReportCardTemplatesPage />} />
                <Route path="report-cards/templates/:id/designer" element={<ReportCardDesignerPage />} />
                <Route path="report-cards/templates/:id/preview" element={<ReportCardPrintPreviewPage />} />
                <Route path="report-cards/grade-scales" element={<GradeScalePage />} />
                <Route path="report-cards/grade-scales/:id/ranges" element={<GradeScaleRangePage />} />
                <Route path="report-cards/gpa-engines" element={<GpaEnginePage />} />
                <Route path="report-cards/gpa-engines/:id/mappings" element={<GpaGradeMappingPage />} />
                <Route path="report-cards/subject-categories" element={<SubjectCategoryPage />} />
                <Route path="report-cards/examination-types" element={<ExaminationTypePage />} />
                <Route path="report-cards/exam-weightage" element={<ExamWeightagePage />} />
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
                <Route path="parent/*" element={
                  <ParentChildProvider>
                    <Routes>
                      <Route path="dashboard" element={<ParentDashboardPage />} />
                      <Route path="children" element={<ParentChildrenPage />} />
                      <Route path="children/:studentId/attendance" element={<ParentAttendancePage />} />
                      <Route path="children/:studentId/homework" element={<ParentHomeworkPage />} />
                      <Route path="children/:studentId/exams" element={<ParentExamsPage />} />
                      <Route path="children/:studentId/fees" element={<ParentFeesPage />} />
                      <Route path="children/:studentId/progress" element={<ParentProgressPage />} />
                      <Route path="notices" element={<ParentNoticesPage />} />
                      <Route path="calendar" element={<ParentCalendarPage />} />
                      <Route path="messages" element={<ParentMessagesPage />} />
                      <Route path="profile" element={<ParentProfilePage />} />
                      <Route path="attendance" element={<ParentAttendancePage />} />
                      <Route path="homework" element={<ParentHomeworkPage />} />
                      <Route path="exams" element={<ParentExamsPage />} />
                      <Route path="fees" element={<ParentFeesPage />} />
                      <Route path="certificates" element={<ParentCertificatesPage />} />
                      <Route path="documents" element={<ParentDocumentsPage />} />
                      <Route path="payment-history" element={<ParentPaymentHistoryPage />} />
                      <Route path="change-password" element={<ParentChangePasswordPage />} />
                      <Route path="events" element={<ParentEventsPage />} />
                    </Routes>
                  </ParentChildProvider>
                } />
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