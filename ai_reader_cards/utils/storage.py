"""数据存储模块 - 保存和加载卡片数据"""

import json
from pathlib import Path
from datetime import datetime


class CardStorage:
    """卡片数据存储管理器"""
    
    def __init__(self, storage_dir="data"):
        """初始化存储管理器
        
        Args:
            storage_dir: 数据存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.default_file = self.storage_dir / "cards.json"
    
    def save_cards(self, cards, filepath=None):
        """保存卡片数据到JSON文件
        
        Args:
            cards: 卡片对象列表
            filepath: 保存路径，默认为cards.json
        """
        if filepath is None:
            filepath = self.default_file
        else:
            filepath = Path(filepath)
        
        # 转换卡片为字典列表
        cards_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "cards": [card.to_dict() for card in cards]
        }
        
        # 保存到JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cards_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_cards(self, filepath=None):
        """从JSON文件加载卡片数据
        
        Args:
            filepath: 加载路径，默认为cards.json
            
        Returns:
            list: 卡片数据字典列表
        """
        if filepath is None:
            filepath = self.default_file
        else:
            filepath = Path(filepath)
        
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 返回卡片数据列表
        if isinstance(data, dict) and "cards" in data:
            return data["cards"]
        else:
            # 兼容旧格式
            return data if isinstance(data, list) else []
    
    def export_as_markdown(self, cards, filepath):
        """导出卡片为Markdown格式
        
        Args:
            cards: 卡片对象列表
            filepath: 导出路径
        """
        filepath = Path(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# 知识卡片导出\n\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"卡片总数: {len(cards)}\n\n")
            f.write("---\n\n")
            
            for idx, card in enumerate(cards, 1):
                card_dict = card.to_dict()
                f.write(f"## {idx}. {card_dict['title']}\n\n")
                f.write(f"**问题：** {card_dict['question']}\n\n")
                f.write(f"**答案：** {card_dict['answer']}\n\n")
                
                if card_dict.get('parent_id'):
                    f.write(f"*父卡片ID: {card_dict['parent_id']}*\n\n")
                
                f.write("---\n\n")
        
        return filepath
    
    def get_recent_files(self, limit=10):
        """获取最近保存的文件列表
        
        Args:
            limit: 返回文件数量限制
            
        Returns:
            list: 文件路径列表
        """
        if not self.storage_dir.exists():
            return []
        
        files = list(self.storage_dir.glob("*.json"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return files[:limit]
