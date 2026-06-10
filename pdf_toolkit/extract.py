import os
import pdfplumber


def extract_text(input_path, output_path=None, pages=None):
    """
    提取PDF中的文本内容

    Args:
        input_path (str): 输入PDF文件路径
        output_path (str, optional): 输出文本文件路径，如果为None则返回文本字符串
        pages (list, optional): 要提取的页码列表（从1开始），默认为全部页面

    Returns:
        str: 如果output_path为None，返回提取的文本内容；否则返回输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    text_parts = []

    with pdfplumber.open(input_path) as pdf:
        total_pages = len(pdf.pages)

        if pages is None:
            page_indices = range(total_pages)
        else:
            page_indices = [p - 1 for p in pages if 1 <= p <= total_pages]

        for idx in page_indices:
            page = pdf.pages[idx]
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- 第 {idx + 1} 页 ---\n{page_text}")

    full_text = "\n\n".join(text_parts)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        return output_path

    return full_text
