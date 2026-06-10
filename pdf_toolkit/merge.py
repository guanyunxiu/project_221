import os
from PyPDF2 import PdfWriter, PdfReader


def merge_pdfs(input_paths, output_path):
    """
    合并多个PDF文件为一个PDF

    Args:
        input_paths (list): PDF文件路径列表
        output_path (str): 输出PDF文件路径

    Returns:
        str: 输出文件路径
    """
    if not input_paths:
        raise ValueError("输入PDF文件列表不能为空")

    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在: {path}")

    writer = PdfWriter()

    for path in input_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
