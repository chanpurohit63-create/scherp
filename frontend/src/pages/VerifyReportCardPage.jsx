import React, { useState } from 'react'
import { verifyReportCard } from '../api'

export default function VerifyReportCardPage() {
  const [verificationId, setVerificationId] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerify = async (e) => {
    e.preventDefault()
    if (!verificationId.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await verifyReportCard(verificationId.trim())
      setResult(data)
    } catch (err) {
      setError('Verification failed. Please check the ID and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="verify-page">
      <div className="verify-card">
        <div className="verify-icon">✓</div>
        <h1>Report Card Verification</h1>
        <p className="verify-subtitle">Enter the verification ID from your report card to verify its authenticity</p>

        <form onSubmit={handleVerify} className="verify-form">
          <input
            type="text"
            value={verificationId}
            onChange={e => setVerificationId(e.target.value)}
            placeholder="Enter Verification ID"
            className="verify-input"
            required
          />
          <button type="submit" className="verify-btn" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify Report Card'}
          </button>
        </form>

        {error && <div className="verify-error">{error}</div>}

        {result && (
          <div className={`verify-result ${result.valid ? 'valid' : 'invalid'}`}>
            {result.valid ? (
              <>
                <div className="result-icon">✅</div>
                <h2>Verified Report Card</h2>
                <div className="result-details">
                  <div className="detail-row"><span>Student Name:</span> <strong>{result.student_name}</strong></div>
                  <div className="detail-row"><span>School:</span> <strong>{result.school_name}</strong></div>
                  <div className="detail-row"><span>Academic Year:</span> <strong>{result.academic_year}</strong></div>
                  <div className="detail-row"><span>Exam:</span> <strong>{result.exam}</strong></div>
                  <div className="detail-row"><span>Issue Date:</span> <strong>{result.issue_date ? new Date(result.issue_date).toLocaleDateString() : 'N/A'}</strong></div>
                  <div className="detail-row"><span>Result:</span> <strong className={`result-status ${result.result_status === 'PASS' || result.result_status === 'PROMOTED' ? 'pass' : 'fail'}`}>{result.result_status}</strong></div>
                  <div className="detail-row"><span>Percentage:</span> <strong>{result.percentage?.toFixed(2)}%</strong></div>
                  <div className="detail-row"><span>Verification Status:</span> <strong className="verified-badge">{result.verification_status}</strong></div>
                </div>
              </>
            ) : (
              <>
                <div className="result-icon">❌</div>
                <h2>Invalid Report Card</h2>
                <p className="invalid-message">{result.message}</p>
                <p className="invalid-details">{result.details}</p>
              </>
            )}
          </div>
        )}
      </div>

      <style>{`
        .verify-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f5ff; padding: 20px; }
        .verify-card { background: white; border-radius: 16px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 10px 40px rgba(0,0,0,0.1); text-align: center; }
        .verify-icon { width: 60px; height: 60px; background: #1d4ed8; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; margin: 0 auto 20px; }
        .verify-card h1 { font-size: 24px; color: #1a2a3a; margin: 0 0 10px; }
        .verify-subtitle { color: #6b7280; font-size: 14px; margin-bottom: 25px; }
        .verify-form { display: flex; flex-direction: column; gap: 12px; }
        .verify-input { padding: 14px 16px; border: 2px solid #d1d5db; border-radius: 8px; font-size: 16px; text-align: center; letter-spacing: 1px; }
        .verify-input:focus { border-color: #1d4ed8; outline: none; }
        .verify-btn { padding: 14px; background: #1d4ed8; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .verify-btn:hover { background: #1e40af; }
        .verify-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .verify-error { margin-top: 15px; padding: 12px; background: #fee2e2; color: #dc2626; border-radius: 8px; font-size: 14px; }
        .verify-result { margin-top: 25px; padding: 25px; border-radius: 12px; }
        .verify-result.valid { background: #f0fdf4; border: 1px solid #bbf7d0; }
        .verify-result.invalid { background: #fef2f2; border: 1px solid #fecaca; }
        .result-icon { font-size: 40px; margin-bottom: 10px; }
        .verify-result h2 { margin: 0 0 15px; }
        .verify-result.valid h2 { color: #16a34a; }
        .verify-result.invalid h2 { color: #dc2626; }
        .result-details { text-align: left; }
        .detail-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; font-size: 14px; }
        .detail-row:last-child { border-bottom: none; }
        .detail-row span { color: #6b7280; }
        .result-status { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
        .result-status.pass { background: #dcfce7; color: #16a34a; }
        .result-status.fail { background: #fee2e2; color: #dc2626; }
        .verified-badge { color: #16a34a; }
        .invalid-message { font-size: 16px; color: #991b1b; }
        .invalid-details { font-size: 13px; color: #6b7280; margin-top: 10px; }
      `}</style>
    </div>
  )
}