"""Professional A4 PDF Report Card Generator.

Generates print-ready, high-resolution report cards with:
- School branding (logo, name, address, contact)
- Student information and photo
- Subject-wise marks table
- GPA, grades, percentages
- Attendance information
- QR code for verification
- Digital signatures
- Teacher and principal remarks
"""
import os
import io
import base64
from typing import Optional, List, Dict
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import qrcode


class ReportCardPDF(FPDF):
    """Custom PDF class for generating professional report cards."""

    def __init__(self, school_name: str = ""):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.school_name = school_name
        self.add_font("DejaVu", "", "c:/Windows/Fonts/arial.ttf", uni=True)
        self.add_font("DejaVu", "B", "c:/Windows/Fonts/arialbd.ttf", uni=True)
        self.add_font("DejaVu", "I", "c:/Windows/Fonts/ariali.ttf", uni=True)

    def header(self):
        pass  # Custom header handled in generation

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M')} | Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def add_school_header(self, school_name: str, address: Optional[str], logo_path: Optional[str],
                          phone: Optional[str], email: Optional[str], website: Optional[str]):
        """Add school branding header."""
        self.set_font("DejaVu", "B", 18)
        self.set_text_color(25, 50, 100)

        # Logo on the left
        if logo_path and os.path.exists(logo_path):
            try:
                self.image(logo_path, x=15, y=10, w=25, h=25)
            except Exception:
                pass

        # School name centered
        self.set_xy(15, 12)
        self.cell(0, 10, school_name, 0, 1, "C")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(80, 80, 80)

        if address:
            self.cell(0, 5, address, 0, 1, "C")

        contact_parts = []
        if phone:
            contact_parts.append(f"Phone: {phone}")
        if email:
            contact_parts.append(f"Email: {email}")
        if website:
            contact_parts.append(f"Web: {website}")

        if contact_parts:
            self.cell(0, 5, " | ".join(contact_parts), 0, 1, "C")

        # Horizontal line
        self.set_draw_color(25, 50, 100)
        self.set_line_width(0.5)
        self.line(15, self.get_y() + 3, 195, self.get_y() + 3)
        self.ln(6)

    def add_section_title(self, title: str):
        """Add a section title with background."""
        self.set_fill_color(25, 50, 100)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 7, f"  {title}", 0, 1, "L", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def add_info_row(self, label: str, value: str, x: float = 15, width: float = 85):
        """Add a label: value row."""
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(50, 50, 50)
        self.cell(width, 5, f"{label}:", 0, 0, "L")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(width, 5, str(value or "N/A"), 0, 1, "L")

    def add_student_photo(self, photo_path: Optional[str], x: float = 160, y: float = 35, size: int = 30):
        """Add student photo or default avatar placeholder."""
        if photo_path and os.path.exists(photo_path):
            try:
                self.image(photo_path, x=x, y=y, w=size, h=size)
                return
            except Exception:
                pass
        # Draw default avatar placeholder
        self.set_draw_color(180, 180, 180)
        self.set_fill_color(240, 240, 240)
        self.rect(x, y, size, size, "DF")
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.set_xy(x, y + size / 2 - 4)
        self.cell(size, 8, "No Photo", 0, 0, "C")

    def add_subject_table(self, subjects: List[Dict], col_widths: List[float] = None):
        """Add subject marks table."""
        if col_widths is None:
            col_widths = [50, 25, 25, 20, 20, 40]

        headers = ["Subject", "Max Marks", "Obtained", "Grade", "GP", "Remarks"]
        table_width = sum(col_widths)

        # Table header
        self.set_fill_color(25, 50, 100)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 8)
        x_start = 15
        x = x_start
        for i, h in enumerate(headers):
            self.set_xy(x, self.get_y())
            self.cell(col_widths[i], 7, h, 1, 0, "C", fill=True)
            x += col_widths[i]
        self.ln(7)

        # Table rows
        self.set_text_color(0, 0, 0)
        for idx, subj in enumerate(subjects):
            if idx % 2 == 0:
                self.set_fill_color(245, 247, 250)
            else:
                self.set_fill_color(255, 255, 255)

            x = x_start
            row_data = [
                subj.get("subject_name", ""),
                str(subj.get("maximum_marks", 0)),
                str(subj.get("obtained_marks", 0)),
                subj.get("grade", ""),
                str(subj.get("grade_point", 0)),
                subj.get("remarks", "") or "",
            ]

            self.set_font("DejaVu", "", 8)
            for i, val in enumerate(row_data):
                self.set_xy(x, self.get_y())
                align = "L" if i == 0 or i == 5 else "C"
                self.cell(col_widths[i], 6, val, 1, 0, align, fill=True)
                x += col_widths[i]
            self.ln(6)

    def add_totals_section(self, total_marks: float, obtained_marks: float, percentage: float,
                           overall_grade: Optional[str], gpa: float, result_status: Optional[str],
                           promotion_status: Optional[str], rank: Optional[int]):
        """Add totals and summary section."""
        self.ln(2)
        self.set_fill_color(240, 245, 250)
        self.set_draw_color(25, 50, 100)

        # Summary box
        y_start = self.get_y()
        self.rect(15, y_start, 180, 35, "DF")

        self.set_xy(20, y_start + 2)
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(25, 50, 100)
        self.cell(80, 5, "SUMMARY", 0, 1, "L")

        self.set_text_color(0, 0, 0)
        self.set_font("DejaVu", "", 8)

        col1_x = 20
        col2_x = 100

        self.set_xy(col1_x, y_start + 9)
        self.cell(70, 5, f"Total Max Marks: {total_marks:.0f}", 0, 1)
        self.set_xy(col1_x, y_start + 15)
        self.cell(70, 5, f"Total Obtained: {obtained_marks:.0f}", 0, 1)
        self.set_xy(col1_x, y_start + 21)
        self.cell(70, 5, f"Percentage: {percentage:.2f}%", 0, 1)
        self.set_xy(col1_x, y_start + 27)
        self.cell(70, 5, f"Overall Grade: {overall_grade or 'N/A'}", 0, 1)

        self.set_xy(col2_x, y_start + 9)
        self.cell(70, 5, f"GPA: {gpa:.2f}", 0, 1)
        self.set_xy(col2_x, y_start + 15)
        self.cell(70, 5, f"Result: {result_status or 'N/A'}", 0, 1)
        self.set_xy(col2_x, y_start + 21)
        self.cell(70, 5, f"Promotion: {promotion_status or 'N/A'}", 0, 1)
        if rank is not None:
            self.set_xy(col2_x, y_start + 27)
            self.cell(70, 5, f"Rank: {rank}", 0, 1)

        self.set_y(y_start + 38)

    def add_remarks_section(self, teacher_remarks: Optional[str], principal_remarks: Optional[str]):
        """Add teacher and principal remarks."""
        if teacher_remarks or principal_remarks:
            self.add_section_title("REMARKS")

            if teacher_remarks:
                self.set_font("DejaVu", "B", 9)
                self.set_text_color(50, 50, 50)
                self.cell(0, 5, "Teacher's Remark:", 0, 1)
                self.set_font("DejaVu", "I", 9)
                self.set_text_color(0, 0, 0)
                self.multi_cell(0, 5, teacher_remarks)
                self.ln(2)

            if principal_remarks:
                self.set_font("DejaVu", "B", 9)
                self.set_text_color(50, 50, 50)
                self.cell(0, 5, "Principal's Remark:", 0, 1)
                self.set_font("DejaVu", "I", 9)
                self.set_text_color(0, 0, 0)
                self.multi_cell(0, 5, principal_remarks)
                self.ln(2)

    def add_attendance_section(self, working_days: int, present_days: int, attendance_pct: float):
        """Add attendance information."""
        self.add_section_title("ATTENDANCE")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f"Working Days: {working_days}  |  Present Days: {present_days}  |  Attendance: {attendance_pct:.1f}%", 0, 1)
        self.ln(2)

    def add_qr_code(self, verification_id: str, base_url: str = ""):
        """Generate and embed QR code for verification."""
        verification_url = f"{base_url}/verify/report-card/{verification_id}" if base_url else f"https://verify.school.com/{verification_id}"

        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(verification_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Save to temp buffer
            temp_path = f"/tmp/qr_{verification_id}.png"
            qr_img.save(temp_path)

            self.image(temp_path, x=160, y=self.get_y(), w=25, h=25)

            # Clean up
            try:
                os.remove(temp_path)
            except Exception:
                pass

            self.set_xy(160, self.get_y() + 26)
            self.set_font("DejaVu", "", 6)
            self.set_text_color(100, 100, 100)
            self.cell(25, 4, "Scan to Verify", 0, 1, "C")
        except Exception:
            # If QR generation fails, show verification ID
            self.set_xy(155, self.get_y())
            self.set_font("DejaVu", "", 7)
            self.set_text_color(100, 100, 100)
            self.cell(35, 5, f"Verify ID: {verification_id}", 0, 1, "C")

    def add_digital_signatures(self, principal_name: Optional[str], signature_path: Optional[str] = None,
                                stamp_path: Optional[str] = None):
        """Add digital signature area with principal signature and school stamp."""
        self.ln(5)
        y = self.get_y()

        # Principal signature
        self.set_xy(15, y)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(50, 50, 50)

        if signature_path and os.path.exists(signature_path):
            try:
                self.image(signature_path, x=15, y=y, w=30, h=10)
            except Exception:
                self.cell(50, 5, "_________________________", 0, 0, "C")
        else:
            self.cell(50, 5, "_________________________", 0, 0, "C")

        self.set_xy(15, y + 6)
        self.set_font("DejaVu", "B", 8)
        self.cell(50, 5, f"Principal ({principal_name or 'N/A'})", 0, 0, "C")

        # School stamp (render actual image if available)
        self.set_xy(130, y)
        self.set_font("DejaVu", "", 8)
        if stamp_path and os.path.exists(stamp_path):
            try:
                self.image(stamp_path, x=130, y=y, w=30, h=15)
            except Exception:
                self.cell(50, 5, "_________________________", 0, 0, "C")
        else:
            self.cell(50, 5, "_________________________", 0, 0, "C")
        self.set_xy(130, y + 8)
        self.set_font("DejaVu", "B", 8)
        self.cell(50, 5, "School Stamp", 0, 0, "C")

    def generate_report_card(self, data: Dict) -> bytes:
        """Generate complete report card PDF from data dict.
        
        Args:
            data: Dictionary containing all report card data
        
        Returns:
            PDF bytes
        """
        self.alias_nb_pages()
        self.add_page()

        # School Header
        self.add_school_header(
            school_name=data.get("school_name", "School Name"),
            address=data.get("school_address"),
            logo_path=data.get("school_logo"),
            phone=data.get("school_phone"),
            email=data.get("school_email"),
            website=data.get("school_website"),
        )

        # Report Card Title
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(25, 50, 100)
        self.cell(0, 8, "REPORT CARD", 0, 1, "C")
        self.ln(2)

        # Exam & Academic Year
        self.set_font("DejaVu", "", 9)
        self.set_text_color(80, 80, 80)
        exam_name = data.get("exam_name", "")
        ac_year = data.get("academic_year_name", "")
        self.cell(0, 5, f"{exam_name}  |  Academic Year: {ac_year}", 0, 1, "C")
        self.ln(3)

        # Student Information Section
        self.add_section_title("STUDENT INFORMATION")

        # Student photo
        self.add_student_photo(data.get("photo_path"))

        # Student details in two columns
        col1 = [
            ("Student Name", data.get("student_name", "")),
            ("Admission No", data.get("admission_no")),
            ("Roll Number", data.get("roll_number")),
            ("Class", data.get("class_name", "")),
        ]
        col2 = [
            ("Section", data.get("section_name")),
            ("Gender", data.get("gender")),
            ("Date of Birth", str(data.get("dob", "")) if data.get("dob") else "N/A"),
            ("Parent Name", data.get("parent_name")),
        ]

        y_start = self.get_y()
        for i, (label, value) in enumerate(col1):
            self.set_xy(15, y_start + i * 5)
            self.add_info_row(label, value, 15, 70)

        for i, (label, value) in enumerate(col2):
            self.set_xy(95, y_start + i * 5)
            self.add_info_row(label, value, 95, 60)

        self.set_y(y_start + len(col1) * 5 + 3)

        # Attendance
        self.add_attendance_section(
            data.get("working_days", 0),
            data.get("present_days", 0),
            data.get("attendance_percentage", 0),
        )

        # Subject Marks Table
        self.add_section_title("ACADEMIC PERFORMANCE")
        subjects = data.get("subjects", [])
        self.add_subject_table(subjects)

        # Totals
        self.add_totals_section(
            total_marks=data.get("total_marks", 0),
            obtained_marks=data.get("obtained_marks", 0),
            percentage=data.get("percentage", 0),
            overall_grade=data.get("overall_grade"),
            gpa=data.get("gpa", 0),
            result_status=data.get("result_status"),
            promotion_status=data.get("promotion_status"),
            rank=data.get("rank"),
        )

        # Remarks
        self.add_remarks_section(
            teacher_remarks=data.get("teacher_remarks"),
            principal_remarks=data.get("principal_remarks"),
        )

        # QR Code and Signatures
        y_before = self.get_y()
        self.add_qr_code(
            verification_id=data.get("verification_id", ""),
            base_url=data.get("verification_base_url", ""),
        )

        self.set_y(max(y_before, self.get_y()))
        self.add_digital_signatures(
            principal_name=data.get("principal_name"),
            signature_path=data.get("signature_path"),
            stamp_path=data.get("stamp_path"),
        )

        # Return PDF bytes
        return bytes(self.output(dest="S"))


def generate_report_card_pdf(data: Dict) -> bytes:
    """Convenience function to generate report card PDF."""
    pdf = ReportCardPDF(school_name=data.get("school_name", ""))
    return pdf.generate_report_card(data)