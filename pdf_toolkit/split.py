import os
from PyPDF2 import PdfReader, PdfWriter


def split_pdfs(input_path, output_dir, page_ranges=None, pages_per_file=None):
    """
    按页面范围或固定页数拆分PDF

    Args:
        input_path (str): 输入PDF文件路径
        output_dir (str): 输出目录
        page_ranges (list, optional): 页面范围列表，如 [(1, 3), (5, 5)]，页码从1开始
        pages_per_file (int, optional): 每个文件的页数

    Returns:
        list: 生成的PDF文件路径列表
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    if page_ranges is None and pages_per_file is None:
        raise ValueError("必须指定 page_ranges 或 pages_per_file")

    os.makedirs(output_dir, exist_ok=True)

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    output_files = []

    if page_ranges is not None:
        for idx, (start, end) in enumerate(page_ranges):
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"无效的页面范围: {start}-{end}, 总页数: {total_pages}")

            writer = PdfWriter()
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])

            output_path = os.path.join(output_dir, f"split_{idx + 1}_pages_{start}-{end}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
            output_files.append(output_path)
    else:
        if pages_per_file <= 0:
            raise ValueError("pages_per_file 必须大于0")

        file_idx = 0
        for i in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            start_page = i
            end_page = min(i + pages_per_file, total_pages)

            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_path = os.path.join(
                output_dir,
                f"split_{file_idx + 1}_pages_{start_page + 1}-{end_page}.pdf"
            )
            with open(output_path, "wb") as f:
                writer.write(f)
            output_files.append(output_path)
            file_idx += 1

    return output_files
