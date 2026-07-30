def generate_report_card_pdf(report_card, grades) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Report Card", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Academic Year: {report_card.academic_year_id}", ln=True, align="C")
    pdf.cell(0, 6, f"Student ID: {report_card.student_id} | Class: {report_card.class_id}", ln=True, align="C")
    if report_card.overall_percentage is not None:
        pdf.cell(0, 6, f"Overall: {report_card.overall_percentage}% | Grade: {report_card.overall_grade or '-'} | GPA: {report_card.overall_gpa or '-'}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 8)
    col_widths = [25, 30, 20, 20, 20, 20, 25, 25]
    headers = ["Subject", "Exam Type", "Marks Obtained", "Max Marks", "Percentage", "Grade", "Grade Point", "Remarks"]
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 7, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for grade in grades:
        row_data = [
            str(grade.subject_id),
            str(grade.examination_type_id or "-"),
            str(grade.marks_obtained or "-"),
            str(grade.marks_max or "-"),
            f"{grade.percentage:.1f}%" if grade.percentage else "-",
            grade.grade or "-",
            str(grade.grade_point or "-"),
            grade.remarks or "-",
        ]
        for i, val in enumerate(row_data):
            pdf.cell(col_widths[i], 6, val, border=1, align="C")
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Teacher Remark: {report_card.teacher_remark or '-'}", ln=True)
    pdf.cell(0, 6, f"Principal Remark: {report_card.principal_remark or '-'}", ln=True)
    pdf.cell(0, 6, f"Status: {report_card.status}", ln=True)
    pdf.cell(0, 6, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}", ln=True)

    return pdf.output(dest="S").encode("latin-1")