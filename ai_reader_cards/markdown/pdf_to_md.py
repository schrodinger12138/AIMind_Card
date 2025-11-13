"""PDF转Markdown工具 - 基于OCR（单线程版本）"""
import fitz  # PyMuPDF
from PIL import Image
import requests
from tqdm import tqdm
import io
import os
import time
import datetime


class PDFToMarkdownConverter:
    """PDF转Markdown转换器（单线程版本）"""

    def __init__(self, uat_token=None):
        """
        初始化转换器
        Args:
            uat_token: SimpleTex OCR API的用户授权令牌
        """
        self.uat_token = uat_token or "qOwHOIifkexohLHWi7x4UNDHEtIiZjdhJUDqBWc11MvKY28XWY0Z54dB8nYvPhDA"
        self.api_url = "https://server.simpletex.cn/api/doc_ocr/"

    def pillow_image_to_file_binary(self, image):
        """将PIL图像转换为二进制数据"""
        bytes_io = io.BytesIO()
        image.save(bytes_io, format='PNG')
        return bytes_io.getvalue()

    def convert_pdf_to_images(self, pdf_path, dpi=100):
        """将PDF转换为图像列表"""
        doc = fitz.open(pdf_path)
        images = []
        for i in range(doc.page_count):
            page = doc[i]
            pixmap = page.get_pixmap(dpi=dpi)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            images.append((i, image))  # 返回(页码, 图像)元组
        doc.close()
        return images

    def pdf_ocr(self, image):
        """对图像进行OCR识别"""
        header = {"token": self.uat_token}
        img_file = {"file": self.pillow_image_to_file_binary(image)}
        try:
            res = requests.post(self.api_url, files=img_file, headers=header, timeout=60).json()
            if "res" in res and "content" in res["res"]:
                return res["res"]["content"], None
            else:
                error_msg = f"OCR API返回异常: {res}"
                return "", error_msg
        except Exception as e:
            error_msg = f"OCR请求发生错误: {e}"
            return "", error_msg

    def convert_pdf_to_markdown(self, pdf_path, progress_callback=None, delay=1.5):
        """
        将PDF文件转换为Markdown（单线程版本）

        Args:
            pdf_path: PDF文件路径
            progress_callback: 进度回调函数 (current, total, message)
            delay: 每页之间的延迟秒数，避免API限制

        Returns:
            tuple: (markdown内容, 错误列表)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        if progress_callback:
            progress_callback(0, 1, "正在读取PDF文件...")

        # 转换为图像
        page_images = self.convert_pdf_to_images(pdf_path)
        total_pages = len(page_images)

        if progress_callback:
            progress_callback(0, total_pages, f"开始OCR识别，共{total_pages}页...")

        # 单线程OCR识别
        markdown_contents = [""] * total_pages  # 预分配列表，按页码存储结果
        errors = []

        # 使用tqdm显示进度
        with tqdm(total=total_pages, desc="OCR识别进度") as pbar:
            for page_num, image in page_images:
                if progress_callback:
                    progress_callback(page_num, total_pages, f"正在识别第 {page_num+1}/{total_pages} 页...")

                content, error = self.pdf_ocr(image)
                if error:
                    errors.append(f"第{page_num+1}页: {error}")
                    markdown_contents[page_num] = f"\n\n## 第 {page_num+1} 页\n\n*OCR识别失败: {error}*\n\n"
                else:
                    markdown_contents[page_num] = f"\n\n## 第 {page_num+1} 页\n\n{content}\n\n"

                pbar.update(1)

                # 添加延迟，避免API限制
                if page_num < total_pages - 1:  # 最后一页不需要延迟
                    time.sleep(delay)

        # 合并所有页面的内容
        final_markdown_content = "".join(markdown_contents)

        # 添加文件头信息
        header = f"""# PDF转换结果\n\n
- **源文件**: {os.path.basename(pdf_path)}
- **转换时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总页数**: {total_pages}
- **成功页数**: {total_pages - len(errors)}
- **失败页数**: {len(errors)}\n\n
"""

        if errors:
            header += "## 错误信息\n\n" + "\n".join(f"- {error}" for error in errors) + "\n\n---\n\n"

        final_markdown_content = header + final_markdown_content

        if progress_callback:
            progress_callback(total_pages, total_pages,
                            f"转换完成！成功{total_pages - len(errors)}页，失败{len(errors)}页")

        return final_markdown_content, errors

    def convert_pdf_to_markdown_simple(self, pdf_path):
        """简化版转换（不使用进度回调）"""
        markdown_content, errors = self.convert_pdf_to_markdown(pdf_path, progress_callback=None)
        return markdown_content