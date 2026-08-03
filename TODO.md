# API Connectivity Verification - TODO

## Step 1: Register missing `report_card.py` router in main.py
- [ ] Add import for `report_cards as enterprise_report_cards` from `report_card.py`
- [ ] Add router include statement (prefix `/api`) - AFTER the plural report_cards to avoid route conflicts

## Step 2: Verify schemas exist for enterprise endpoints
- [x] Added new schema classes in schemas.py (ReportCardTemplate*, ReportCardComponent*, ExaminationType*, GradeScale*, GpaEngine*, SubjectCategory*, ExamWeightageConfig*)

## Step 3: Run comprehensive API connectivity verification
- [ ] Start backend server
- [ ] Run verify_api_connectivity.py or create new verification
- [ ] Check all endpoints respond correctly
- [ ] Verify database connections work

## Step 4: Fix any discovered connectivity issues
- [ ] Address any 404/500 errors from missing routes
- [ ] Fix any schema mismatches between frontend and backend

## Step 5: Generate final connectivity report
- [ ] List all modules and their connection status
- [ ] Document any remaining issues or warnings

