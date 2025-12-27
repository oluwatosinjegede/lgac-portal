# apps/core/utils.py
import io
import os
import hashlib
import requests
import qrcode
from datetime import datetime

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

from django.core.files.storage import default_storage
from reportlab.lib.colors import green
from io import BytesIO


def draw_image_safe(pdf, file_field, x, y, width, height):
    """
    Safely draw an ImageField stored in cloud storage (R2/S3) into a ReportLab PDF.
    """
    try:
        with default_storage.open(file_field.name, "rb") as f:
            image_bytes = BytesIO(f.read())
    except Exception as e:
        print(f"[PDF IMAGE ERROR] {file_field.name}: {e}")
        return

    try:
        image = ImageReader(image_bytes)
        pdf.drawImage(
            image,
            x,
            y,
            width=width,
            height=height,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"[PDF IMAGE ERROR] {file_field.name}: {e}")


# =====================================================
# GLOBAL CONSTANTS
# =====================================================
STATE_NAME = getattr(settings, "STATE_NAME", "ONDO")
COUNTRY_NAME = "FEDERAL REPUBLIC OF NIGERIA"
MINISTRY_NAME = "MINISTRY OF LOCAL GOVERNMENT & CHIEFTAINCY AFFAIRS"
SITE_URL = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")


# =====================================================
# VERIFY NIN (VERIFYME)
# =====================================================
def verify_nin_with_verifyme(nin):
    api_key = getattr(settings, "VERIFYME_API_KEY", None)
    if not api_key:
        return False, {"error": "Missing API key"}

    url = f"https://api.verifyme.ng/v1/verify/nin/{nin}"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.status_code == 200, resp.json()
    except requests.RequestException as e:
        return False, {"error": str(e)}


# =====================================================
# HEADER (FEDERAL + STATE)
# =====================================================
def draw_certificate_header(pdf, width, height):
    LOGO_WIDTH = 110
    LOGO_HEIGHT = 110
    TOP_MARGIN = 25
    SIDE_MARGIN = 30

    y = height - TOP_MARGIN - LOGO_HEIGHT

    # Federal Coat of Arms (Left)
    coa_path = os.path.join(settings.BASE_DIR, "static/img/coat_of_arms.png")
    if os.path.exists(coa_path):
        pdf.drawImage(
            coa_path,
            SIDE_MARGIN,
            y,
            width=LOGO_WIDTH,
            height=LOGO_HEIGHT,
            preserveAspectRatio=True,
            mask="auto",
        )

    # State Logo (Right)
    state_logo_path = os.path.join(settings.BASE_DIR, "static/img/ondo_logo.png")
    if os.path.exists(state_logo_path):
        pdf.drawImage(
            state_logo_path,
            width - SIDE_MARGIN - LOGO_WIDTH,
            y,
            width=LOGO_WIDTH,
            height=LOGO_HEIGHT,
            preserveAspectRatio=True,
            mask="auto",
        )


# =====================================================
# CERTIFICATE PDF GENERATION
# =====================================================
def generate_certificate_pdf(application):
    """
    Generates a government-grade LGAC certificate.
    Returns (relative_pdf_path, verification_hash)
    """

    # -------------------------------------------------
    # CERTIFICATE NUMBER + HASH
    # -------------------------------------------------
    if not application.certificate_number:
        application.certificate_number = (
            f"LGAC/{application.lga.slug.upper()}/{application.created_at.year}/{application.id:06d}"
        )

    payload = f"{application.id}|{application.certificate_number}|{application.applicant_id}"
    cert_hash = hashlib.sha256(payload.encode()).hexdigest()

    # -------------------------------------------------
    # PDF SETUP
    # -------------------------------------------------
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    green = HexColor("#1B5E20")
    margin_x = 40

    # -------------------------------------------------
    # WATERMARK
    # -------------------------------------------------
    pdf.saveState()
    pdf.setFillColor(HexColor("#EAEAEA"))
    pdf.setFont("Helvetica-Bold", 60)
    pdf.translate(width / 2, height / 2)
    pdf.rotate(45)
    pdf.drawCentredString(0, 0, "ORIGINAL COPY")
    pdf.restoreState()

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    draw_certificate_header(pdf, width, height)

    # -------------------------------------------------
    # GOVERNMENT TITLES
    # -------------------------------------------------
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 45, COUNTRY_NAME)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 70, f"{STATE_NAME.upper()} STATE GOVERNMENT")

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, height - 90, MINISTRY_NAME)

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(
        width / 2,
        height - 115,
        f"{application.lga.name.upper()} LOCAL GOVERNMENT COUNCIL",
    )

    pdf.setStrokeColor(green)
    pdf.line(margin_x, height - 125, width - margin_x, height - 125)

    # -------------------------------------------------
    # TITLE
    # -------------------------------------------------
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawCentredString(
        width / 2,
        height - 160,
        "LOCAL GOVERNMENT ATTESTATION CERTIFICATE",
    )

    # -------------------------------------------------
    # META
    # -------------------------------------------------
    issued_at = application.approved_at or datetime.now()
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin_x, height - 190, f"Certificate No: {application.certificate_number}")
    pdf.drawString(margin_x, height - 205, f"Issue Date: {issued_at:%d %B %Y}")

    # ============================
    # PASSPORT PHOTO (TOP RIGHT)
    # ============================

    pdf.setStrokeColor(green)
    pdf.rect(width - 160, height - 330, 120, 140)

    if application.passport_photo:
    	draw_image_safe(
        	pdf,
        	application.passport_photo,   # pass ImageField, NOT bytes, NOT .path
        	width - 155,
        	height - 325,
        	110,
        	130,
    	)
    # -------------------------------------------------
    # APPLICANT DETAILS
    # -------------------------------------------------
    y = height - 240
    line_gap = 18

    pdf.setFont("Helvetica", 11)
    for label, value in [
        ("Full Name", application.full_name),
        ("Date of Birth", application.date_of_birth.strftime("%d %B %Y")),
        ("Place of Birth", application.place_of_birth),
        ("NIN", application.nin),
        ("Home Town", application.home_town),
        ("Family Compound", application.family_compound),
        ("Father’s Name", application.father_name),
        ("Mother’s Name", application.mother_name),
    ]:
        pdf.drawString(margin_x, y, f"{label}:")
        pdf.drawString(200, y, str(value))
        y -= line_gap

    # -------------------------------------------------
    # DECLARATION
    # -------------------------------------------------
    y -= 30
    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        margin_x,
        y,
        "This certificate is issued following due verification of records and is valid for official use only.",
    )

    # -------------------------------------------------
    # SIGNATURES & LOCAL GOVERNMENT SEAL (STACKED)
    # -------------------------------------------------

    sig_left_x = margin_x
    sig_center_x = (width / 2) - 75  # center align
    sig_img_width = 150
    sig_img_height = 50
    line_gap = 14
    block_gap = 45  # vertical spacing between blocks

    # Base Y position (start signatures here)
    sig_top_y = y - 70


    # ============================
    # HLGA SIGNATURE (TOP BLOCK)
    # ============================

    if application.lga and application.lga.hlga_signature:
    	draw_image_safe(
        	pdf,
        	application.lga.hlga_signature,  # correct file
        	sig_left_x,
        	sig_top_y,
        	sig_img_width,
        	sig_img_height,
    	)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
    	sig_left_x,
    	sig_top_y - line_gap,
    	"_______________________________",
    )
    pdf.drawString(
    	sig_left_x,
    	sig_top_y - (2 * line_gap),
    	"Head of Local Government Administration",
    )
    pdf.drawString(
    	sig_left_x,
    	sig_top_y - (3 * line_gap),
    	f"{application.lga.name} Local Government",
    )

    # ============================
    # CHAIRMAN SIGNATURE (BELOW HLGA)
    # ============================

    chairman_y = sig_top_y - block_gap - sig_img_height

    if application.lga and application.lga.chairman_signature:
    	draw_image_safe(
        	pdf,
        	application.lga.chairman_signature,  # correct ImageField
        	sig_left_x,
        	chairman_y,
        	sig_img_width,
        	sig_img_height,
    	)

    pdf.drawString(
    	sig_left_x,
    	chairman_y - line_gap,
    	"_______________________________",
    )
    pdf.drawString(
    	sig_left_x,
    	chairman_y - (2 * line_gap),
    	"Executive Chairman",
    )
    pdf.drawString(
    	sig_left_x,
    	chairman_y - (3 * line_gap),
    	f"{application.lga.name} Local Government",
    )

    # ============================
    # OFFICIAL LGA SEAL (RIGHT SIDE)
    # ============================

    seal_size = 110
    seal_x = width - margin_x - seal_size
    seal_y = chairman_y - 10

    if application.lga and application.lga.seal:
    	draw_image_safe(
        	pdf,
        	application.lga.seal,   # pass ImageField, NOT .path
        	seal_x,
        	seal_y,
        	seal_size,
        	seal_size,
    	)

    	pdf.setFont("Helvetica-Bold", 8)
    	pdf.drawCentredString(
        	seal_x + seal_size / 2,
        	seal_y - 10,
        	"OFFICIAL SEAL",
    	)



    # -------------------------------------------------
    # QR CODE
    # -------------------------------------------------
    verify_url = f"{SITE_URL}/verify/{cert_hash}"
    qr_img = qrcode.make(verify_url)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf.drawImage(ImageReader(qr_buffer), width - 160, 60, width=120, height=120)

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------
    pdf.setFont("Helvetica", 6)
    pdf.setFillColor(HexColor("#666666"))
    pdf.drawString(
        margin_x,
        25,
        f"Verification Hash: {cert_hash} | Generated electronically by LGAC Portal.",
    )

    # -------------------------------------------------
    # FINALIZE
    # -------------------------------------------------
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    relative_path = f"certificates/lgac_{application.id}_{cert_hash[:12]}.pdf"
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(buffer.read())

    application.certificate_hash = cert_hash
    application.save(update_fields=["certificate_number", "certificate_hash"])

    #return relative_path, cert_hash
    return relative_path, cert_hash
