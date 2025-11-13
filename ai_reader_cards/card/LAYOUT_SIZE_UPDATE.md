# 自动布局动态节点大小更新说明

## 更新内容

### 1. 动态节点大小计算 ✅

**文件**: `ai_reader_cards/card/madmap_based_nodes.py`

**新增方法**:
- `get_actual_size()` - 获取节点的实际大小（考虑形状、内容等）
- `get_bounding_rect()` - 获取节点的边界矩形

**计算因素**:
- 基础大小（WIDTH × HEIGHT）
- 标签（在底部，可能增加高度）
- 图片（根据位置增加高度或宽度）
- 形状（圆形使用较大的边）

### 2. 布局引擎更新 ✅

**文件**: `ai_reader_cards/card/madmap_based_layout.py`

**更新的布局方法**:
- `mind_map()` - 思维导图布局，支持动态大小
- `logical()` - 逻辑结构布局，支持动态大小
- `timeline()` - 时间轴布局，支持动态大小
- `fishbone()` - 鱼骨图布局，支持动态大小
- `auto_arrange()` - 自动排列，支持动态大小

**改进**:
- 所有布局方法现在使用 `get_actual_size()` 获取节点实际大小
- 根据实际大小计算间距，避免节点重叠
- 支持不同形状和内容的节点

### 3. 连线管理器更新 ✅

**文件**: `ai_reader_cards/card/madmap_based_connections.py`

**改进**:
- `get_connection_points()` 方法现在使用 `get_actual_size()` 获取节点大小
- 连线连接点计算更准确，适应不同大小的节点

### 4. 连线样式增强 ✅

**文件**: `ai_reader_cards/card/enhanced_connections.py`

**新增连线样式**:
- `HandDrawnConnection` - 手绘风格连线（随机抖动效果）
- `RainbowConnection` - 彩虹线条（渐变颜色）
- `AnimatedConnection` - 流动动画连线（虚线流动效果）

**使用方法**:
```python
# 在场景中设置连线样式
scene.set_connection_style("hand_drawn")  # 手绘风格
scene.set_connection_style("rainbow")     # 彩虹线条
scene.set_connection_style("animated")     # 流动动画
```

## 使用示例

### 动态大小计算

```python
# 节点会根据内容自动调整大小
node = CardVisualNode(tree_node)

# 获取实际大小
width, height = node.get_actual_size()

# 获取边界矩形
bounding_rect = node.get_bounding_rect()
```

### 布局应用

```python
# 应用布局（自动使用动态大小）
scene.apply_layout()

# 布局会自动考虑：
# - 节点的实际大小
# - 标签占用的空间
# - 图片占用的空间
# - 不同形状的节点
```

### 连线样式切换

```python
# 切换连线样式
scene.set_connection_style("bezier")      # 贝塞尔曲线（默认）
scene.set_connection_style("hand_drawn")  # 手绘风格
scene.set_connection_style("rainbow")     # 彩虹线条
scene.set_connection_style("animated")     # 流动动画
```

## 技术细节

### 大小计算逻辑

1. **基础大小**: 使用 `WIDTH` 和 `HEIGHT` 常量
2. **标签影响**: 如果标签多行，增加相应高度
3. **图片影响**: 
   - 图片在上下：增加高度
   - 图片在左右：增加宽度
4. **形状影响**: 圆形使用较大的边作为直径

### 布局算法改进

- **思维导图布局**: 根据子节点实际高度计算垂直间距
- **逻辑结构布局**: 根据子节点实际宽度计算水平间距
- **时间轴布局**: 根据节点实际宽度和高度计算位置
- **鱼骨图布局**: 根据节点实际高度调整垂直间距
- **自动排列**: 使用实际大小检测重叠

## 向后兼容

- 所有更改向后兼容
- 旧节点默认使用基础大小（280 × 180）
- 如果节点没有实现 `get_actual_size()`，使用默认大小

## 性能考虑

- 大小计算是轻量级的，不会影响性能
- 布局算法在计算时缓存节点大小
- 动画连线使用定时器，可随时停止

