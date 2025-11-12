"""AI API模块 - 调用OpenAI API生成问题/答案卡片"""

import os
import json
import re
from openai import OpenAI




API_BASE = "https://api.chatanywhere.tech/v1"
OPENAI_API_KEY = "sk-lwkQzJYwYdJwbQ4DaAlM3Ti6pgMCzEgztBjREyOlYFPLPDQP"


class AICardGenerator:
    """AI卡片生成器"""

    def __init__(self, model="gpt-3.5-turbo"):  # ✅ 改成 gpt-3.5-turbo
        api_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
        if not api_key:
            raise RuntimeError("未检测到 OPENAI_API_KEY 环境变量，请先设置API密钥")

        self.client = OpenAI(
            api_key=api_key,
            base_url=API_BASE  # ✅ 加上自定义代理
        )
        self.model = model
    
    def generate_card(self, text_content):
        """从文本内容生成学习卡片
        
        Args:
            text_content: 要转换为卡片的文本内容
            
        Returns:
            dict: 包含title, question, answer的字典
        """
        prompt = f"""请把下面的文本提炼成一个学习卡片，返回JSON格式，包含以下字段：
        - title: 一句精简的标题（6-20字）
        - question: 一个考察该片段核心概念的问题
        - answer: 对问题的简洁回答（不超过150字）
        
        返回内容必须是严格的JSON对象，不要添加任何额外说明。
        
        文本内容：
        {text_content}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识卡片生成助手，擅长将复杂内容转换为结构化的学习卡片。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = (response.choices[0].message.content or "").strip()
            
            # 解析JSON响应
            card_data = self._parse_json_response(result_text)
            
            # 确保所有必需字段都存在
            card = {
                "title": card_data.get("title", "")[:100],
                "question": card_data.get("question", "")[:200],
                "answer": card_data.get("answer", "")[:500],
                "source_text": text_content[:500]
            }
            
            return card
            
        except Exception as e:
            raise RuntimeError(f"AI卡片生成失败: {str(e)}")
    
    def _parse_json_response(self, response_text):
        """解析AI返回的JSON响应
        
        Args:
            response_text: AI返回的文本
            
        Returns:
            dict: 解析后的JSON对象
        """
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 解析失败，返回默认结构
                return {
                    "title": "解析失败",
                    "question": "AI返回内容无法解析",
                    "answer": response_text[:200]
                }
    
    def set_model(self, model):
        """设置使用的模型
        
        Args:
            model: 模型名称
        """
        self.model = model
