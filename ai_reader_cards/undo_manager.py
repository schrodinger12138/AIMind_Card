"""撤销/重做管理器"""
from typing import List, Dict, Any


class UndoManager:
    """撤销/重做管理器"""
    
    def __init__(self, max_history=50):
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.is_undoing = False
    
    def save_state(self, cards_data: List[Dict[str, Any]], action_name: str = ""):
        """保存状态到撤销栈"""
        if self.is_undoing:
            return
        
        # 保存当前状态
        state = {
            'action': action_name,
            'cards': [card.copy() for card in cards_data],
            'timestamp': self._get_timestamp()
        }
        
        self.undo_stack.append(state)
        
        # 限制历史记录数量
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        # 执行新操作时清空重做栈
        self.redo_stack.clear()
    
    def undo(self) -> List[Dict[str, Any]]:
        """撤销操作"""
        if not self.undo_stack:
            return None
        
        # 保存当前状态到重做栈
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        
        # 获取上一个状态
        if self.undo_stack:
            previous_state = self.undo_stack[-1]
            self.is_undoing = True
            return previous_state['cards'].copy()
        else:
            # 如果没有更多历史，返回空列表
            self.is_undoing = True
            return []
    
    def redo(self) -> List[Dict[str, Any]]:
        """重做操作"""
        if not self.redo_stack:
            return None
        
        # 从重做栈恢复状态
        state = self.redo_stack.pop()
        self.undo_stack.append(state)
        self.is_undoing = True
        return state['cards'].copy()
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return len(self.undo_stack) > 1  # 至少需要2个状态才能撤销
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return len(self.redo_stack) > 0
    
    def clear(self):
        """清空历史记录"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

