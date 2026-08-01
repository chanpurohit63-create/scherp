export const BACKEND_URL = 'http://127.0.0.1:8001'

export function getBackendUrl() {
  return BACKEND_URL
}

function getAuthHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function login(email, password) {
  const response = await fetch(`${BACKEND_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!response.ok) throw new Error('Invalid credentials')
  return response.json()
}

export async function fetchProfile(token) {
  const response = await fetch(`${BACKEND_URL}/users/me`, {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Unable to load profile')
  return response.json()
}

export async function createResource(token, path, body) {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Create failed')
  }
  return response.json()
}

export async function listResources(token, path, query = '') {
  const url = new URL(`${BACKEND_URL}/api/${path}`)
  if (query) url.search = query
  const response = await fetch(url.toString(), { headers: { ...getAuthHeaders(token) } })
  if (!response.ok) throw new Error('List failed')
  return response.json()
}

export async function getResource(token, path, id) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, { headers: { ...getAuthHeaders(token) } })
  if (!response.ok) throw new Error('Fetch failed')
  return response.json()
}

export async function updateResource(token, path, id, body) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Update failed')
  }
  return response.json()
}

export async function deleteResource(token, path, id) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Delete failed')
  return null
}

export async function uploadFile(token, path, file, fieldName = 'file') {
  const formData = new FormData()
  formData.append(fieldName, file)
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    method: 'POST',
    headers: { ...getAuthHeaders(token) },
    body: formData,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Upload failed')
  }
  return response.json()
}

export async function downloadFile(token, path, filename = 'download') {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Download failed')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
  return true
}

export async function fetchText(token, path) {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Fetch failed')
  return response.text()
}
// ========== REPORT CARD TEMPLATES ==========

export async function listReportCardTemplates(token, params = {}) {
  const query = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') query.append(k, v)
  }
  const url = query.toString() ? `report-card/templates?${query.toString()}` : 'report-card/templates'
  return listResources(token, url)
}

export async function createReportCardTemplate(token, data) {
  return createResource(token, 'report-card/templates', data)
}

export async function getReportCardTemplate(token, id) {
  return getResource(token, 'report-card/templates', id)
}

export async function updateReportCardTemplate(token, id, data) {
  return updateResource(token, 'report-card/templates', id, data)
}

export async function archiveReportCardTemplate(token, id) {
  return postResource(token, `report-card/templates/${id}/archive`, {})
}

export async function duplicateReportCardTemplate(token, id) {
  return postResource(token, `report-card/templates/${id}/duplicate`, {})
}

// ========== REPORT CARD COMPONENTS ==========

export async function listReportCardComponents(token, templateId) {
  return listResources(token, `report-card/components/template/${templateId}`)
}

export async function createReportCardComponent(token, data) {
  return createResource(token, 'report-card/components', data)
}

export async function updateReportCardComponent(token, id, data) {
  return updateResource(token, 'report-card/components', id, data)
}

export async function deleteReportCardComponent(token, id) {
  return deleteResource(token, 'report-card/components', id)
}

// ========== EXAMINATION TYPES ==========

export async function listExaminationTypes(token) {
  return listResources(token, 'examination-types')
}

export async function createExaminationType(token, data) {
  return createResource(token, 'examination-types', data)
}

export async function updateExaminationType(token, id, data) {
  return updateResource(token, 'examination-types', id, data)
}

export async function deleteExaminationType(token, id) {
  return deleteResource(token, 'examination-types', id)
}

// ========== EXAM WEIGHTAGE ==========

export async function listExamWeightage(token, params = {}) {
  const query = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') query.append(k, v)
  }
  const url = query.toString() ? `exam-weightage?${query.toString()}` : 'exam-weightage'
  return listResources(token, url)
}

export async function createExamWeightage(token, data) {
  return createResource(token, 'exam-weightage', data)
}

// ========== GRADE SCALES ==========

export async function listGradeScales(token) {
  return listResources(token, 'grade-scales')
}

export async function createGradeScale(token, data) {
  return createResource(token, 'grade-scales', data)
}

export async function updateGradeScale(token, id, data) {
  return updateResource(token, 'grade-scales', id, data)
}

export async function deleteGradeScale(token, id) {
  return deleteResource(token, 'grade-scales', id)
}

export async function listGradeScaleRanges(token, gradeScaleId) {
  return listResources(token, `grade-scales/${gradeScaleId}/ranges`)
}

export async function createGradeScaleRange(token, gradeScaleId, data) {
  return createResource(token, `grade-scales/${gradeScaleId}/ranges`, data)
}

export async function updateGradeScaleRange(token, rangeId, data) {
  return updateResource(token, 'grade-scale-ranges', rangeId, data)
}

// ========== GPA ENGINES ==========

export async function listGpaEngines(token) {
  return listResources(token, 'gpa-engines')
}

export async function createGpaEngine(token, data) {
  return createResource(token, 'gpa-engines', data)
}

export async function updateGpaEngine(token, id, data) {
  return updateResource(token, 'gpa-engines', id, data)
}

export async function deleteGpaEngine(token, id) {
  return deleteResource(token, 'gpa-engines', id)
}

export async function listGpaGradeMappings(token, gpaEngineId) {
  return listResources(token, `gpa-engines/${gpaEngineId}/mappings`)
}

export async function createGpaGradeMapping(token, gpaEngineId, data) {
  return createResource(token, `gpa-engines/${gpaEngineId}/mappings`, data)
}

export async function updateGpaGradeMapping(token, mappingId, data) {
  return updateResource(token, 'gpa-mappings', mappingId, data)
}

// ========== SUBJECT CATEGORIES ==========

export async function listSubjectCategories(token) {
  return listResources(token, 'subject-categories')
}

export async function createSubjectCategory(token, data) {
  return createResource(token, 'subject-categories', data)
}

export async function updateSubjectCategory(token, id, data) {
  return updateResource(token, 'subject-categories', id, data)
}

export async function deleteSubjectCategory(token, id) {
  return deleteResource(token, 'subject-categories', id)
}

export async function listSubjectCategoryMappings(token) {
  return listResources(token, 'subject-category-mappings')
}

export async function createSubjectCategoryMapping(token, data) {
  return createResource(token, 'subject-category-mappings', data)
}
// ========== REPORT CARDS (CRUD) ==========

export async function listReportCards(token, params = {}) {
  const query = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') query.append(k, v)
  }
  const url = query.toString() ? `report-cards?${query.toString()}` : 'report-cards'
  return listResources(token, url)
}

export async function getReportCard(token, id) {
  return getResource(token, 'report-cards', id)
}

export async function generateReportCard(token, data) {
  return createResource(token, 'report-cards', data)
}

export async function updateReportCard(token, id, data) {
  return updateResource(token, 'report-cards', id, data)
}

export async function publishReportCard(token, id) {
  return postResource(token, `report-cards/${id}/publish`, {})
}

export async function archiveReportCard(token, id) {
  return postResource(token, `report-cards/${id}/archive`, {})
}

export async function bulkGenerateReportCards(token, data) {
  return createResource(token, 'report-cards/bulk-generate', data)
}

export async function deleteReportCard(token, id) {
  return deleteResource(token, 'report-cards', id)
}

export async function verifyReportCard(verificationId) {
  const res = await fetch(`${BACKEND_URL}/api/report-cards/verify/${verificationId}`)
  return res.json()
}

export async function getReportCardStats(token) {
  return listResources(token, 'report-cards/stats/summary')
}

export async function downloadReportCardPDF(token, id) {
  return downloadFile(token, `report-cards/${id}/export/pdf`, `report_card_${id}.pdf`)
}

export async function bulkDownloadReportCardsPDF(token, ids) {
  return downloadFile(token, `report-cards/bulk/download?report_card_ids=${ids.join(',')}`, 'report_cards.zip')
}

// ========== GRADING RULES ==========

export async function listGradingRules(token) {
  return listResources(token, 'grading-rules')
}

export async function createGradingRule(token, data) {
  return createResource(token, 'grading-rules', data)
}

export async function updateGradingRule(token, id, data) {
  return updateResource(token, 'grading-rules', id, data)
}

export async function deleteGradingRule(token, id) {
  return deleteResource(token, 'grading-rules', id)
}
