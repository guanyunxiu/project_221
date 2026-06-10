import argparse
import sys
import os

from .merge import merge_pdfs
from .split import split_pdfs
from .encrypt import encrypt_pdf, decrypt_pdf
from .extract import extract_text
from .image_to_pdf import images_to_pdf
from .watermark import add_text_watermark, add_image_watermark


def _parse_page_ranges(ranges_str):
    """解析页面范围字符串，如 '1-3,5,7-9'"""
    if not ranges_str:
        return None
    ranges = []
    for part in ranges_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ranges.append((int(start.strip()), int(end.strip())))
        else:
            page = int(part.strip())
            ranges.append((page, page))
    return ranges


def _parse_pages(pages_str):
    """解析页码列表字符串，如 '1,3,5'"""
    if not pages_str:
        return None
    return [int(p.strip()) for p in pages_str.split(",") if p.strip()]


def _parse_color(color_str):
    """解析颜色字符串，如 '0.5,0.5,0.5'"""
    if not color_str:
        return (0.5, 0.5, 0.5)
    parts = [float(c.strip()) for c in color_str.split(",")]
    if len(parts) != 3:
        raise ValueError("颜色必须是三个数值，用逗号分隔")
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(
        description="PDF处理工具集 - 合并、拆分、加密、解密、文本提取、图片转PDF、添加水印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s merge -i input1.pdf input2.pdf -o merged.pdf
  %(prog)s split -i input.pdf -o output_dir --pages-per-file 5
  %(prog)s split -i input.pdf -o output_dir --ranges "1-3,5,7-9"
  %(prog)s encrypt -i input.pdf -o encrypted.pdf -p user123
  %(prog)s decrypt -i encrypted.pdf -o decrypted.pdf -p user123
  %(prog)s extract -i input.pdf -o output.txt
  %(prog)s extract -i input.pdf --pages "1,3,5"
  %(prog)s img2pdf -i img1.jpg img2.png -o output.pdf
  %(prog)s watermark-text -i input.pdf -o watermarked.pdf -t "机密"
  %(prog)s watermark-image -i input.pdf -o watermarked.pdf -w logo.png
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    merge_parser = subparsers.add_parser("merge", help="合并多个PDF文件")
    merge_parser.add_argument("-i", "--inputs", nargs="+", required=True, help="输入PDF文件路径列表")
    merge_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")

    split_parser = subparsers.add_parser("split", help="按页面范围或固定页数拆分PDF")
    split_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    split_parser.add_argument("-o", "--output-dir", required=True, help="输出目录")
    split_group = split_parser.add_mutually_exclusive_group(required=True)
    split_group.add_argument("--ranges", help='页面范围，如 "1-3,5,7-9"')
    split_group.add_argument("--pages-per-file", type=int, help="每个文件的页数")

    encrypt_parser = subparsers.add_parser("encrypt", help="给PDF设置密码保护")
    encrypt_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    encrypt_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")
    encrypt_parser.add_argument("-p", "--password", required=True, help="用户密码")
    encrypt_parser.add_argument("--owner-password", help="所有者密码（默认为用户密码）")

    decrypt_parser = subparsers.add_parser("decrypt", help="移除PDF的密码保护")
    decrypt_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    decrypt_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")
    decrypt_parser.add_argument("-p", "--password", required=True, help="密码")

    extract_parser = subparsers.add_parser("extract", help="提取PDF中的文本内容")
    extract_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    extract_parser.add_argument("-o", "--output", help="输出文本文件路径（不指定则打印到控制台）")
    extract_parser.add_argument("--pages", help='指定页码，如 "1,3,5"（默认提取全部）')

    img2pdf_parser = subparsers.add_parser("img2pdf", help="将图片转换为PDF")
    img2pdf_parser.add_argument("-i", "--inputs", nargs="+", required=True, help="输入图片文件路径列表（支持JPG/PNG）")
    img2pdf_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")

    wm_text_parser = subparsers.add_parser("watermark-text", help="给PDF添加文字水印")
    wm_text_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    wm_text_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")
    wm_text_parser.add_argument("-t", "--text", required=True, help="水印文字")
    wm_text_parser.add_argument("--font-size", type=int, default=40, help="字体大小（默认40）")
    wm_text_parser.add_argument("--opacity", type=float, default=0.3, help="透明度0-1（默认0.3）")
    wm_text_parser.add_argument("--rotation", type=int, default=45, help="旋转角度（默认45度）")
    wm_text_parser.add_argument("--color", default="0.5,0.5,0.5", help='RGB颜色，如 "0.5,0.5,0.5"（默认灰色）')

    wm_image_parser = subparsers.add_parser("watermark-image", help="给PDF添加图片水印")
    wm_image_parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    wm_image_parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")
    wm_image_parser.add_argument("-w", "--watermark", required=True, help="水印图片路径")
    wm_image_parser.add_argument("--opacity", type=float, default=0.3, help="透明度0-1（默认0.3）")
    wm_image_parser.add_argument("--scale", type=float, default=0.5, help="缩放比例，相对于页面宽度（默认0.5）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "merge":
            result = merge_pdfs(args.inputs, args.output)
            print(f"合并成功: {result}")

        elif args.command == "split":
            ranges = _parse_page_ranges(args.ranges) if args.ranges else None
            result = split_pdfs(
                args.input,
                args.output_dir,
                page_ranges=ranges,
                pages_per_file=args.pages_per_file,
            )
            print(f"拆分成功，生成文件:")
            for f in result:
                print(f"  {f}")

        elif args.command == "encrypt":
            result = encrypt_pdf(
                args.input,
                args.output,
                args.password,
                args.owner_password,
            )
            print(f"加密成功: {result}")

        elif args.command == "decrypt":
            result = decrypt_pdf(args.input, args.output, args.password)
            print(f"解密成功: {result}")

        elif args.command == "extract":
            pages = _parse_pages(args.pages)
            result = extract_text(args.input, args.output, pages)
            if args.output:
                print(f"文本提取成功: {result}")
            else:
                print(result)

        elif args.command == "img2pdf":
            result = images_to_pdf(args.inputs, args.output)
            print(f"图片转PDF成功: {result}")

        elif args.command == "watermark-text":
            color = _parse_color(args.color)
            result = add_text_watermark(
                args.input,
                args.output,
                args.text,
                font_size=args.font_size,
                opacity=args.opacity,
                rotation=args.rotation,
                color=color,
            )
            print(f"文字水印添加成功: {result}")

        elif args.command == "watermark-image":
            result = add_image_watermark(
                args.input,
                args.output,
                args.watermark,
                opacity=args.opacity,
                scale=args.scale,
            )
            print(f"图片水印添加成功: {result}")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
