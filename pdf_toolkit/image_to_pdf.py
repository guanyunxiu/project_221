import os
from PIL import Image


def images_to_pdf(image_paths, output_path):
    """
    将多张图片转换为一个PDF文件

    Args:
        image_paths (list): 图片文件路径列表，支持 JPG/PNG 等格式
        output_path (str): 输出PDF文件路径

    Returns:
        str: 输出文件路径
    """
    if not image_paths:
        raise ValueError("图片文件列表不能为空")

    for path in image_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在: {path}")

    images = []
    for path in image_paths:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    if not images:
        raise ValueError("没有有效的图片可转换")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    first_image = images[0]
    other_images = images[1:] if len(images) > 1 else None

    first_image.save(output_path, "PDF", resolution=100.0, save_all=True, append_images=other_images)

    for img in images:
        img.close()

    return output_path
