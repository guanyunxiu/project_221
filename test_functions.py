from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import io
import os


def main():
    print("1. 测试PDF创建...")
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.drawString(100, 750, "Hello World - Test PDF 1")
    c.drawString(100, 700, "This is page 1")
    c.showPage()
    c.drawString(100, 750, "Hello World - Test PDF 2")
    c.drawString(100, 700, "This is page 2")
    c.showPage()
    c.drawString(100, 750, "Hello World - Test PDF 3")
    c.drawString(100, 700, "This is page 3")
    c.showPage()
    c.save()
    packet.seek(0)

    os.makedirs("test_output", exist_ok=True)

    with open("test_output/test1.pdf", "wb") as f:
        f.write(packet.getvalue())

    packet2 = io.BytesIO()
    c2 = canvas.Canvas(packet2, pagesize=A4)
    c2.drawString(100, 750, "Second PDF Document")
    c2.drawString(100, 700, "Additional content")
    c2.showPage()
    c2.save()
    packet2.seek(0)

    with open("test_output/test2.pdf", "wb") as f:
        f.write(packet2.getvalue())

    print("   测试PDF创建成功!")

    print("2. 测试PDF合并...")
    from pdf_toolkit.merge import merge_pdfs
    result = merge_pdfs(["test_output/test1.pdf", "test_output/test2.pdf"], "test_output/merged.pdf")
    reader = PdfReader(result)
    print(f"   合并成功! 总页数: {len(reader.pages)}")

    print("3. 测试PDF拆分...")
    from pdf_toolkit.split import split_pdfs
    files = split_pdfs("test_output/test1.pdf", "test_output/split", pages_per_file=1)
    print(f"   拆分成功! 生成文件数: {len(files)}")

    print("4. 测试PDF加密...")
    from pdf_toolkit.encrypt import encrypt_pdf, decrypt_pdf
    encrypt_pdf("test_output/test1.pdf", "test_output/encrypted.pdf", "test123")
    print("   加密成功!")

    print("5. 测试PDF解密...")
    decrypt_pdf("test_output/encrypted.pdf", "test_output/decrypted.pdf", "test123")
    print("   解密成功!")

    print("6. 测试图片转PDF...")
    from pdf_toolkit.image_to_pdf import images_to_pdf
    img = Image.new("RGB", (800, 600), color="lightblue")
    img.save("test_output/test_image.jpg")
    img2 = Image.new("RGB", (600, 400), color="lightgreen")
    img2.save("test_output/test_image2.png")
    images_to_pdf(["test_output/test_image.jpg", "test_output/test_image2.png"], "test_output/images.pdf")
    print("   图片转PDF成功!")

    print("7. 测试文字水印...")
    from pdf_toolkit.watermark import add_text_watermark
    add_text_watermark("test_output/test1.pdf", "test_output/text_watermarked.pdf", "CONFIDENTIAL", font_size=50, opacity=0.3)
    print("   文字水印添加成功!")

    print("8. 测试图片水印...")
    from pdf_toolkit.watermark import add_image_watermark
    add_image_watermark("test_output/test1.pdf", "test_output/image_watermarked.pdf", "test_output/test_image.jpg", opacity=0.2, scale=0.3)
    print("   图片水印添加成功!")

    print()
    print("所有已安装依赖的功能测试通过!")
    print("生成的测试文件在 test_output/ 目录下")


if __name__ == "__main__":
    main()
