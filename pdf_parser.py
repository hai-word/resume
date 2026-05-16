import pdfplumber
import re

def extract_pdf_text(pdf_path):
    """提取PDF文本"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"PDF解析异常：{str(e)}")

    return clean_text(text)

def clean_text(text):
    """文本清洗"""
    # 多余换行、空格
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r" +", " ", text)
    # 保留中文/英文/数字/空格/常用标点，过滤乱码符号
    keep = (
        r"一-龥"         # 中文
        r"a-zA-Z0-9"              # 英文数字
        r"\s"                     # 空白
        r"@._\-:"                 # 邮箱/日期/链接符号
        r"，。！？；：""''（）【】《》、…—"   # 中文标点
        r",\.!\?;:'\"\(\)\[\]\{\}#%&+\-/|\\"  # 英文标点
    )
    text = re.sub(r"[^" + keep + r"]", "", text)
    return text.strip()
