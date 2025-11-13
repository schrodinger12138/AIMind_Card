"""Markdown翻译模块 - 基于gpt_academic的翻译功能"""
import os
import re
from typing import List, Optional, Callable
from openai import OpenAI
from ai_reader_cards.config_manager import get_config_manager


class MarkdownTranslator:
    """Markdown翻译器"""
    
    def __init__(self, model: str = None):
        """
        初始化翻译器
        
        Args:
            model: 使用的模型名称
        """
        self.config = get_config_manager()
        openai_config = self.config.get_openai_config()
        
        self.api_key = openai_config["api_key"]
        self.base_url = openai_config["base_url"]
        self.model = model or openai_config["model"]
        
        # 获取代理配置
        proxies = self.config.get_proxies("translate")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=None  # 如果需要代理，可以在这里配置
        )
        
        # 如果使用代理，设置环境变量
        if proxies:
            if "http" in proxies:
                os.environ["HTTP_PROXY"] = proxies["http"]
            if "https" in proxies:
                os.environ["HTTPS_PROXY"] = proxies["https"]
    
    def translate_markdown(
        self,
        markdown_text: str,
        target_language: str = "zh",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> str:
        """
        翻译Markdown文本
        
        Args:
            markdown_text: Markdown文本内容
            target_language: 目标语言 ("zh"中文, "en"英文, 或其他语言)
            progress_callback: 进度回调函数 (current, total, message)
            
        Returns:
            翻译后的Markdown文本
        """
        # 分割文本（如果太长）
        segments = self._split_markdown(markdown_text)
        total_segments = len(segments)
        
        translated_segments = []
        
        for i, segment in enumerate(segments):
            if progress_callback:
                progress_callback(i + 1, total_segments, f"正在翻译第 {i + 1}/{total_segments} 段...")
            
            translated = self._translate_segment(segment, target_language)
            translated_segments.append(translated)
        
        if progress_callback:
            progress_callback(total_segments, total_segments, "翻译完成！")
        
        return "\n\n".join(translated_segments)
    
    def _split_markdown(self, text: str, max_tokens: int = 1024) -> List[str]:
        """
        分割Markdown文本为多个段落
        
        Args:
            text: 原始文本
            max_tokens: 每个段落的最大token数
            
        Returns:
            分割后的文本段落列表
        """
        # 简单的分割策略：按段落分割
        paragraphs = text.split('\n\n')
        segments = []
        current_segment = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())  # 简单估算token数
            if current_length + para_length > max_tokens and current_segment:
                segments.append('\n\n'.join(current_segment))
                current_segment = [para]
                current_length = para_length
            else:
                current_segment.append(para)
                current_length += para_length
        
        if current_segment:
            segments.append('\n\n'.join(current_segment))
        
        return segments if segments else [text]
    
    def _translate_segment(self, segment: str, target_language: str) -> str:
        """
        翻译单个文本段落
        
        Args:
            segment: 文本段落
            target_language: 目标语言
            
        Returns:
            翻译后的文本
        """
        # 构建提示词
        if target_language == "zh" or target_language == "中文":
            prompt = (
                "This is a Markdown file, translate it into Chinese, "
                "do NOT modify any existing Markdown commands, "
                "do NOT use code wrapper (```), "
                "ONLY answer me with translated results:\n\n"
            )
        elif target_language == "en" or target_language == "英文":
            prompt = (
                "This is a Markdown file, translate it into English, "
                "do NOT modify any existing Markdown commands, "
                "do NOT use code wrapper (```), "
                "ONLY answer me with translated results:\n\n"
            )
        else:
            prompt = (
                f"This is a Markdown file, translate it into {target_language}, "
                "do NOT modify any existing Markdown commands, "
                "do NOT use code wrapper (```), "
                "ONLY answer me with translated results:\n\n"
            )
        
        prompt += segment
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional academic paper translator. "
                                 "You translate Markdown files while preserving all formatting, "
                                 "code blocks, mathematical formulas, and structure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            translated = response.choices[0].message.content.strip()
            return translated
            
        except Exception as e:
            raise RuntimeError(f"翻译失败: {str(e)}")
    
    def translate_file(
        self,
        file_path: str,
        target_language: str = "zh",
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> str:
        """
        翻译Markdown文件
        
        Args:
            file_path: 输入文件路径
            target_language: 目标语言
            output_path: 输出文件路径（如果为None，则自动生成）
            progress_callback: 进度回调函数
            
        Returns:
            输出文件路径
        """
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 翻译
        translated = self.translate_markdown(content, target_language, progress_callback)
        
        # 确定输出路径
        if output_path is None:
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_translated_{target_language}{ext}"
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        
        return output_path

