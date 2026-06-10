__all__ = [
    "merge_pdfs",
    "split_pdfs",
    "encrypt_pdf",
    "decrypt_pdf",
    "extract_text",
    "images_to_pdf",
    "add_text_watermark",
    "add_image_watermark",
]


def __getattr__(name):
    if name == "merge_pdfs":
        from .merge import merge_pdfs
        return merge_pdfs
    elif name == "split_pdfs":
        from .split import split_pdfs
        return split_pdfs
    elif name == "encrypt_pdf":
        from .encrypt import encrypt_pdf
        return encrypt_pdf
    elif name == "decrypt_pdf":
        from .encrypt import decrypt_pdf
        return decrypt_pdf
    elif name == "extract_text":
        from .extract import extract_text
        return extract_text
    elif name == "images_to_pdf":
        from .image_to_pdf import images_to_pdf
        return images_to_pdf
    elif name == "add_text_watermark":
        from .watermark import add_text_watermark
        return add_text_watermark
    elif name == "add_image_watermark":
        from .watermark import add_image_watermark
        return add_image_watermark
    raise AttributeError(f"module 'pdf_toolkit' has no attribute '{name}'")
