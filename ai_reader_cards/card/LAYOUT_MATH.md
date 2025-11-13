# 逻辑布局数学计算

## 布局规则：从左到右，父节点 → 子节点

### 基本定义

- **父节点 a**：左上角位置 `(ax, ay)`，大小 `(aw, ah)`
- **子节点 b**：左上角位置 `(bx, by)`，大小 `(bw, bh)`
- **固定水平间距**：`h_spacing = 200`
- **垂直间距**：`v_spacing = 120`

### 水平方向（x）计算

**目标**：父节点 a 的右边 → 固定间距 → 子节点 b 的左边

```
[父节点 a] ----h_spacing----> [子节点 b]
(ax, ay)    (ax+aw)    (bx)    (bx+bw)
```

**公式**：
- a 的右边缘：`ax + aw`
- b 的左边缘：`bx`
- 间距：`bx - (ax + aw) = h_spacing`
- **因此：`bx = ax + aw + h_spacing`**

### 垂直方向（y）计算

#### 情况1：单个子节点
- 可以居中：`by = ay + (ah - bh) / 2`
- 或者顶部对齐：`by = ay`

#### 情况2：多个子节点（垂直分布）
- 第一个子节点：`by1 = ay + ah + v_spacing`
- 第二个子节点：`by2 = by1 + bh1 + v_spacing`
- 第 i 个子节点：`by_i = by_{i-1} + bh_{i-1} + v_spacing`

### 逻辑布局算法（修正后）

```python
def logical(root, h_spacing=200, v_spacing=120):
    """自上而下逻辑结构布局 - 从左到右"""
    
    def layout(node, parent_x=None, parent_y=None, parent_w=None, parent_h=None):
        # 获取节点实际大小
        node_w, node_h = get_node_size(node)
        
        if parent_x is None:
            # 根节点：左上角在 (0, 0)
            node.x = 0
            node.y = 0
        else:
            # 子节点：在父节点右侧
            # 水平：父节点右边缘 + 间距
            node.x = parent_x + parent_w + h_spacing
            
            # 垂直：如果有多个子节点，需要垂直分布
            # 这里先简化：第一个子节点与父节点顶部对齐
            node.y = parent_y
        
        # 递归布局子节点
        if node.children:
            for i, child in enumerate(node.children):
                child_w, child_h = get_node_size(child)
                
                # 子节点的 x：父节点右边缘 + 间距
                child_x = node.x + node_w + h_spacing
                
                # 子节点的 y：垂直分布
                if i == 0:
                    # 第一个子节点：与父节点顶部对齐
                    child_y = node.y
                else:
                    # 后续子节点：在前一个子节点下方
                    prev_child = node.children[i-1]
                    prev_child_w, prev_child_h = get_node_size(prev_child)
                    # 需要知道前一个子节点的实际位置
                    # 这里需要先布局前一个子节点
                    child_y = prev_child.y + prev_child_h + v_spacing
                
                layout(child, child_x, child_y, child_w, child_h)
    
    layout(root)
```

### 问题分析

当前代码的问题：
1. 使用中心点计算，导致位置不准确
2. 子节点垂直分布计算复杂且容易出错
3. `add_child_node` 使用固定值，没有考虑实际节点大小

### 解决方案

1. **统一使用左上角坐标**：所有位置计算基于左上角
2. **简化垂直分布**：第一个子节点与父节点顶部对齐，后续子节点依次向下
3. **修复 add_child_node**：使用正确的公式计算新节点位置

