import os
from PyPDF2 import PdfReader, PdfWriter


def encrypt_pdf(input_path, output_path, user_password, owner_password=None):
    """
    给PDF文件设置密码保护

    Args:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        user_password (str): 用户密码（打开文件需要）
        owner_password (str, optional): 所有者密码（权限控制），默认为用户密码

    Returns:
        str: 输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    if not user_password:
        raise ValueError("用户密码不能为空")

    if owner_password is None:
        owner_password = user_password

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(user_password=user_password, owner_password=owner_password)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def decrypt_pdf(input_path, output_path, password):
    """
    移除PDF文件的密码保护

    Args:
        input_path (str): 输入PDF文件路径
        output_path (str): 输出PDF文件路径
        password (str): 密码

    Returns:
        str: 输出文件路径
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    reader = PdfReader(input_path)

    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("密码错误，无法解密PDF文件")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
