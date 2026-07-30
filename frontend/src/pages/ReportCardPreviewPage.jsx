import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { getReportCard, downloadReportCardPDF } from '../api'
import toast from 'react-hot-toast'

export default function ReportCardPreviewPage() {
  const { id } = useParams()
  const { token } = useAuth()
  const [rc, setRc] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getReportCard(token, id)
        setRc(data)
      } catch (err) {
        toast.error('Failed to load report card')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [token, id])

  const handleDownload = async () => {
    try {
      await downloadReportCardPDF(token, id)
      toast.success('PDF downloaded')
    } catch (err) {
      toast.error('Download failed')
    }
  }

  if (loading) return <div className="loading">Loading report card...</div>
  if (!rc) return <div className="loading">Report card not found</div>

  return (
    <div className="preview-container">
      <div className="preview-header">
        <h1>Report Card Preview</h1>
        <div className="preview-actions">
          <button className="btn btn-primary" onClick={handleDownload}>Download PDF</button>
          <button className="btn btn-secondary" onClick={() => window.print()}>Print</button>
          <a href="/report-cards" className="btn btn-outline">Back</a>
        </div>
      </div>

      <div className="report-card" id="report-card">
        {/* School Header */}
        <div className="school-header">
          <div className="school-logo-placeholder">🏫</div>
          <div className="school-info">
            <h2>School Name</h2>
            <p className="school-address">School Address</p>
            <p className="school-contact">Phone | Email | Website</p>
          </div>
        </div>

        <div className="divider"></div>

        {/* Title */}
        <div className="title-section">
          <h1 className="report-title">REPORT CARD</h1>
          <p className="exam-info">Exam: #{rc.exam_id} | Academic Year: #{rc.academic_year_id}</p>
        </div>

        {/* Student Info */}
        <div className="section">
          <div className="section-title">STUDENT INFORMATION</div>
          <div className="student-info-grid">
            <div className="info-col">
              <div className="info-row"><span className="label">Student ID:</span><span className="value">#{rc.student_id}</span></div>
              <div className="info-row"><span className="label">Admission No:</span><span className="value">{rc.admission_no || 'N/A'}</span></div>
              <div className="info-row"><span className="label">Roll Number:</span><span className="value">{rc.roll_number || 'N/A'}</span></div>
              <div className="info-row"><span className="label">Class:</span><span className="value">{rc.class_name || 'N/A'}</span></div>
            </div>
            <div className="info-col">
              <div className="info-row"><span className="label">Section:</span><span className="value">{rc.section_name || 'N/A'}</span></div>
              <div className="info-row"><span className="label">Gender:</span><span className="value">{rc.gender || 'N/A'}</span></div>
              <div className="info-row"><span className="label">DOB:</span><span className="value">{rc.dob || 'N/A'}</span></div>
              <div className="info-row"><span className="label">Parent:</span><span className="value">{rc.parent_name || 'N/A'}</span></div>
            </div>
            <div className="photo-col">
              <div className="student-photo-placeholder">📷</div>
            </div>
          </div>
        </div>

        {/* Attendance */}
        <div className="section">
          <div className="section-title">ATTENDANCE</div>
          <div className="attendance-info">
            Working Days: {rc.working_days} | Present Days: {rc.present_days} | Attendance: {rc.attendance_percentage?.toFixed(1)}%
          </div>
        </div>

        {/* Subject Table */}
        <div className="section">
          <div className="section-title">ACADEMIC PERFORMANCE</div>
          <table className="subject-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Max Marks</th>
                <th>Obtained</th>
                <th>Grade</th>
                <th>GP</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {rc.subjects?.map((subj, idx) => (
                <tr key={subj.id} className={idx % 2 === 0 ? 'even' : 'odd'}>
                  <td>{subj.subject_name || `Subject #${subj.subject_id}`}</td>
                  <td className="text-center">{subj.maximum_marks}</td>
                  <td className="text-center">{subj.obtained_marks}</td>
                  <td className="text-center"><span className="grade-badge">{subj.grade || 'N/A'}</span></td>
                  <td className="text-center">{subj.grade_point}</td>
                  <td>{subj.remarks || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary */}
        <div className="summary-box">
          <div className="summary-title">SUMMARY</div>
          <div className="summary-grid">
            <div className="summary-item"><span>Total Max Marks:</span> {rc.total_marks?.toFixed(0)}</div>
            <div className="summary-item"><span>Total Obtained:</span> {rc.obtained_marks?.toFixed(0)}</div>
            <div className="summary-item"><span>Percentage:</span> {rc.percentage?.toFixed(2)}%</div>
            <div className="summary-item"><span>Overall Grade:</span> {rc.overall_grade || 'N/A'}</div>
            <div className="summary-item"><span>GPA:</span> {rc.gpa?.toFixed(2)}</div>
            <div className="summary-item"><span>Result:</span> 
              <span className={`result-badge ${rc.result_status === 'PASS' || rc.result_status === 'PROMOTED' ? 'pass' : rc.result_status === 'FAIL' ? 'fail' : 'other'}`}>
                {rc.result_status || 'N/A'}
              </span>
            </div>
            <div className="summary-item"><span>Promotion:</span> {rc.promotion_status || 'N/A'}</div>
            {rc.rank && <div className="summary-item"><span>Rank:</span> {rc.rank}</div>}
          </div>
        </div>

        {/* Remarks */}
        {(rc.teacher_remarks || rc.principal_remarks) && (
          <div className="section">
            <div className="section-title">REMARKS</div>
            {rc.teacher_remarks && (
              <div className="remark-block">
                <strong>Teacher's Remark:</strong>
                <p>{rc.teacher_remarks}</p>
              </div>
            )}
            {rc.principal_remarks && (
              <div className="remark-block">
                <strong>Principal's Remark:</strong>
                <p>{rc.principal_remarks}</p>
              </div>
            )}
          </div>
        )}

        {/* QR & Signatures */}
        <div className="footer-section">
          <div className="qr-placeholder">
            <div className="qr-code">🔲</div>
            <span className="qr-label">Scan to Verify</span>
            <span className="verification-id">ID: {rc.verification_id}</span>
          </div>
          <div className="signatures">
            <div className="signature-line">_________________________</div>
            <div className="signature-label">Principal</div>
            <div className="signature-line" style={{ marginTop: 20 }}>_________________________</div>
            <div className="signature-label">School Stamp</div>
          </div>
        </div>

        <div className="generated-date">
          Generated: {rc.generated_on ? new Date(rc.generated_on).toLocaleString() : 'N/A'}
        </div>
      </div>

      <style>{`
        .preview-container { padding: 20px; max-width: 900px; margin: 0 auto; }
        .preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .preview-header h1 { margin: 0; font-size: 24px; color: #1a2a3a; }
        .preview-actions { display: flex; gap: 10px; }
        .loading { text-align: center; padding: 60px; color: #6b7280; font-size: 16px; }
        .report-card { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); font-family: Arial, sans-serif; }
        .school-header { display: flex; align-items: center; gap: 20px; margin-bottom: 10px; }
        .school-logo-placeholder { width: 60px; height: 60px; background: #f3f4f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 30px; }
        .school-info h2 { margin: 0; font-size: 22px; color: #1e3a5f; }
        .school-address, .school-contact { margin: 2px 0; font-size: 12px; color: #6b7280; }
        .divider { height: 2px; background: linear-gradient(to right, #1e3a5f, #3b82f6); margin: 15px 0; }
        .title-section { text-align: center; margin-bottom: 20px; }
        .report-title { font-size: 20px; color: #1e3a5f; margin: 0; letter-spacing: 2px; }
        .exam-info { font-size: 12px; color: #6b7280; margin: 5px 0 0; }
        .section { margin-bottom: 15px; }
        .section-title { background: #1e3a5f; color: white; padding: 6px 12px; font-size: 12px; font-weight: 600; border-radius: 4px; margin-bottom: 10px; letter-spacing: 1px; }
        .student-info-grid { display: grid; grid-template-columns: 1fr 1fr 80px; gap: 15px; }
        .info-row { margin-bottom: 4px; font-size: 13px; }
        .info-row .label { color: #6b7280; font-weight: 600; margin-right: 5px; }
        .info-row .value { color: #1a2a3a; }
        .photo-col { display: flex; align-items: flex-start; justify-content: center; }
        .student-photo-placeholder { width: 70px; height: 70px; background: #f3f4f6; border: 2px dashed #d1d5db; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 30px; }
        .attendance-info { font-size: 13px; color: #374151; padding: 8px 12px; background: #f8fafc; border-radius: 6px; }
        .subject-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .subject-table th { background: #f8fafc; padding: 8px 12px; text-align: left; font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; border-bottom: 2px solid #e5e7eb; }
        .subject-table td { padding: 8px 12px; border-bottom: 1px solid #f0f0f0; }
        .subject-table .even { background: #fafbfc; }
        .text-center { text-align: center; }
        .grade-badge { display: inline-block; background: #dbeafe; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
        .summary-box { background: #f0f5ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .summary-title { font-size: 13px; font-weight: 700; color: #1e3a5f; margin-bottom: 10px; }
        .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        .summary-item { font-size: 13px; color: #374151; }
        .summary-item span { color: #6b7280; }
        .result-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
        .result-badge.pass { background: #dcfce7; color: #16a34a; }
        .result-badge.fail { background: #fee2e2; color: #dc2626; }
        .result-badge.other { background: #fef3c7; color: #d97706; }
        .remark-block { margin-bottom: 8px; }
        .remark-block strong { font-size: 12px; color: #374151; }
        .remark-block p { margin: 4px 0; font-size: 13px; color: #4b5563; font-style: italic; }
        .footer-section { display: flex; justify-content: space-between; align-items: flex-start; margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb; }
        .qr-placeholder { text-align: center; }
        .qr-code { width: 60px; height: 60px; background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin: 0 auto 4px; }
        .qr-label { display: block; font-size: 9px; color: #9ca3af; }
        .verification-id { display: block; font-size: 8px; color: #6b7280; margin-top: 2px; }
        .signatures { text-align: center; }
        .signature-line { font-size: 12px; color: #374151; letter-spacing: 2px; }
        .signature-label { font-size: 11px; color: #6b7280; margin-top: 2px; }
        .generated-date { text-align: center; font-size: 10px; color: #9ca3af; margin-top: 15px; }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; }
        .btn-primary { background: #1d4ed8; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-outline { background: transparent; border: 1px solid #d1d5db; color: #374151; }
        @media print { .preview-header, .preview-actions { display: none; } .report-card { box-shadow: none; padding: 20px; } }
      `}</style>
    </div>
  )
}