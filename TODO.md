# Multi-Tenant Hardening - TODO

## Phase 1: Core CRUD & Auth Hardening
- [ ] 1. Add tenant check to `crud.py` - get_user(), update_user(), delete_user()
- [ ] 2. Add tenant override protection in `auth.py`

## Phase 2: Fix Dashboard & Analytics
- [ ] 3. Fix `/dashboard/summary` - add tenant filters to ALL queries
- [ ] 4. Fix `/analytics/overview` - add tenant filters

## Phase 3: Fix ALL Report Endpoints
- [ ] 5. Fix `/reports/students` - add school_id filter
- [ ] 6. Fix `/reports/attendance` - add school_id filter
- [ ] 7. Fix `/reports/teachers` - add school_id filter
- [ ] 8. Fix `/reports/fees` - add school_id filter
- [ ] 9. Fix `/reports/exams` - add school_id filter

## Phase 4: Fix Portal Endpoints
- [ ] 10. Fix Student Portal (dashboard, exams, calendar, notices, messages)
- [ ] 11. Fix Parent Portal (child endpoints, calendar, notices, messages)
- [ ] 12. Fix Teacher Portal (dashboard, classes, attendance, exams, students, calendar, messages)

## Phase 5: Fix Notification Service
- [ ] 13. Fix notify_notice_created - filter by school_id
- [ ] 14. Fix notify_event_created - filter by school_id
- [ ] 15. Fix notify_fee_payment_received - filter by school_id for admins

## Phase 6: File Storage Isolation
- [ ] 16. Update all upload handlers to use school_id subdirectories

## Phase 7: School Settings & Timetable Fixes
- [ ] 17. Fix School Settings - remove hardcoded `id=1`
- [ ] 18. Fix Timetable list - add tenant filter

## Phase 8: Cross-Tenant Security Tests
- [ ] 19. Create comprehensive pytest suite

## Phase 9: School Status Enforcement
- [ ] 20. Add subscription expiry auto-check on every request

