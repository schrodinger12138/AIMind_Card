"""文件工具模块 - 处理各种文件格式的读取"""

import os
import tempfile
from pathlib import Path


class FileReader:
    """文件阅读器 - 支持多种文件格式"""

    @staticmethod
    def read_file(filepath):
        """读取文件内容

        Args:
            filepath: 文件路径

        Returns:
            tuple: (成功与否, 内容或错误信息, 文件类型)
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return False, "文件不存在", None

        try:
            if filepath.suffix.lower() == '.pdf':
                return FileReader._read_pdf(filepath)
            elif filepath.suffix.lower() in ['.txt', '.md', '.json', '.py', '.html', '.css', '.js']:
                return FileReader._read_text(filepath)
            else:
                # 尝试作为文本文件读取
                return FileReader._read_text(filepath)

        except Exception as e:
            return False, f"读取文件失败: {str(e)}", None

    @staticmethod
    def _read_text(filepath):
        """读取文本文件"""
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    return True, content, 'text'
                except UnicodeDecodeError:
                    continue
            return False, "无法解码文件内容", None
        except Exception as e:
            return False, f"读取文本文件失败: {str(e)}", None

    @staticmethod
    def _read_pdf(filepath):
        """读取PDF文件"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(filepath)
            text_content = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += f"\n--- 第 {page_num + 1} 页 ---\n"
                text_content += page.get_text()

            doc.close()
            return True, text_content, 'pdf'

        except ImportError:
            return False, "请安装PyMuPDF库: pip install PyMuPDF", None
        except Exception as e:
            return False, f"读取PDF文件失败: {str(e)}", None

    @staticmethod
    def get_supported_formats():
        """获取支持的文件格式"""
        return {
            '文本文件': ['.txt', '.md', '.json', '.xml', '.csv'],
            '代码文件': ['.py', '.java', '.cpp', '.c', '.h', '.js', '.html', '.css'],
            'PDF文件': ['.pdf'],
            '所有文件': ['*']
        }

    @staticmethod
    def create_file_filter():
        """创建文件过滤器"""
        formats = FileReader.get_supported_formats()
        filters = []
        for desc, exts in formats.items():
            if desc != '所有文件':
                filter_str = f"{desc} ({' '.join(f'*{ext}' for ext in exts)})"
                filters.append(filter_str)
        filters.append("所有文件 (*.*)")
        return ";;".join(filters)