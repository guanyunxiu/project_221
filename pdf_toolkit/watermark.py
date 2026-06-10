import os
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image


def _register_cjk_font():
    """注册支持中文的字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("CJKFont", font_path))
                return "CJKFont"
            except Exception:
                continue
    return "Helvetica"


def _create_text_watermark_pdf(
    text,
    page_size=A4,
    font_size=40,
    opacity=0.3,
    rotation=45,
    color=(0.5, 0.5, 0.5),
):
    """创建文字水印PDF页面"""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    width, height = page_size

    font_name = _register_cjk_font()
    c.setFont(font_name, font_size)
    c.setFillColorRGB(*color, alpha=opacity)

    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(rotation)

    text_width = c.stringWidth(text, font_name, font_size)
    x = -text_width / 2
    y = 0

    spacing_x = text_width + 2 * inch
    spacing_y = 2 * inch

    for i in range(-3, 4):
        for j in range(-3, 4):
            c.drawString(x + i * spacing_x, y + j * spacing_y, text)

    c.restoreState()
    c.save()
    packet.seek(0)
    return packet


def _create_image_watermark_pdf(image_path, page_size=A4, opacity=0.3, scale=0.5):
    """创建图片水印PDF页面"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    img = Image.open(image_path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    alpha = img.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    img.putalpha(alpha)

    temp_img_path = "/tmp/_watermark_temp.png"
    img.save(temp_img_path, "PNG")

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    width, height = page_size

    img_width, img_height = img.size
    aspect = img_width / img_height

    target_width = width * scale
    target_height = target_width / aspect

    spacing_x = target_width + 1 * inch
    spacing_y = target_height + 1 * inch

    for i in range(-2, 3):
        for j in range(-2, 3):
            x = width / 2 + i * spacing_x - target_width / 2
            y = height / 2 + j * spacing_y - target_height / 2
            c.drawImage(temp_img_path, x, y, width=target_width, height=target_height, mask="auto")

    c.save()
    packet.seek(0)

    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
    img.close()

    return packet


def add_text_watermark(
    input_path,
    output_path,
    text,
    font_size=40,
    opacity=0.3,
    rotation=45,
    color=(0.5, 0.5, 0.5),
):
    """
    给PDF添加文字水印

    Args:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        text (str): 水印文字
        font_size (int): 字体大小，默认40
        opacity (float): 透明度（0-1），默认0.3
        rotation (int): 旋转角度，默认45度
        color (tuple): RGB颜色，默认灰色(0.5, 0.5, 0.5)

    Returns:
        str: 输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    if not text:
        raise ValueError("水印文字不能为空")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        watermark_packet = _create_text_watermark_pdf(
            text=text,
            page_size=(page_width, page_height),
            font_size=font_size,
            opacity=opacity,
            rotation=rotation,
            color=color,
        )
        watermark_reader = PdfReader(watermark_packet)
        watermark_page = watermark_reader.pages[0]

        page.merge_page(watermark_page)
        writer.add_page(page)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def add_image_watermark(input_path, output_path, image_path, opacity=0.3, scale=0.5):
    """
    给PDF添加图片水印

    Args:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        image_path (str): 水印图片路径
        opacity (float): 透明度（0-1），默认0.3
        scale (float): 缩放比例（相对于页面宽度），默认0.5

    Returns:
        str: 输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        watermark_packet = _create_image_watermark_pdf(
            image_path=image_path,
            page_size=(page_width, page_height),
            opacity=opacity,
            scale=scale,
        )
        watermark_reader = PdfReader(watermark_packet)
        watermark_page = watermark_reader.pages[0]

        page.merge_page(watermark_page)
        writer.add_page(page)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
