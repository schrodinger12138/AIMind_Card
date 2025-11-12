"""PDF转Markdown工具 - 基于OCR"""
import fitz  # PyMuPDF
from PIL import Image
import requests
from tqdm import tqdm
import io
import os


class PDFToMarkdownConverter:
    """PDF转Markdown转换器"""
    
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
    
    def convert_pdf_to_images(self, pdf_binary, dpi=100):
        """将PDF转换为图像列表"""
        doc = fitz.open("pdf", pdf_binary)
        images = []
        for i in range(doc.page_count):
            page = doc[i]
            pixmap = page.get_pixmap(dpi=dpi)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            images.append(image)
        doc.close()
        return images
    
    def pdf_ocr(self, image):
        """对图像进行OCR识别"""
        header = {"token": self.uat_token}
        img_file = {"file": self.pillow_image_to_file_binary(image)}
        try:
            res = requests.post(self.api_url, files=img_file, data={}, headers=header, timeout=30).json()
            if 'res' in res and 'content' in res['res']:
                return res['res']['content']
            else:
                print("OCR API 返回错误: ", res)
                return ""
        except Exception as e:
            print(f"OCR请求发生错误: {e}")
            return ""
    
    def convert_pdf_to_markdown(self, pdf_path, progress_callback=None):
        """
        将PDF文件转换为Markdown
        
        Args:
            pdf_path: PDF文件路径
            progress_callback: 进度回调函数 (current, total, message)
        
        Returns:
            str: Markdown内容
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if progress_callback:
            progress_callback(0, 1, "正在读取PDF文件...")
        
        # 读取PDF文件
        with open(pdf_path, 'rb') as pdf_file:
            file_binary = pdf_file.read()
        
        if progress_callback:
            progress_callback(0, 1, "正在将PDF转换为图像...")
        
        # 转换为图像
        images = self.convert_pdf_to_images(file_binary)
        total_pages = len(images)
        
        if progress_callback:
            progress_callback(0, total_pages, f"开始OCR识别，共{total_pages}页...")
        
        # OCR识别
        final_markdown_content = ""
        for i, image in enumerate(images):
            if progress_callback:
                progress_callback(i + 1, total_pages, f"正在识别第 {i + 1}/{total_pages} 页...")
            
            content = self.pdf_ocr(image)
            if content:
                final_markdown_content += content + "\n\n"
        
        if progress_callback:
            progress_callback(total_pages, total_pages, "转换完成！")
        
        return final_markdown_content
    
    def convert_pdf_to_markdown_simple(self, pdf_path):
        """简化版转换（不使用进度回调）"""
        return self.convert_pdf_to_markdown(pdf_path, progress_callback=None)

