# Simple Mind Map 功能分析与优化建议文档

## 一、Simple Mind Map 完整功能清单

### 1. 核心架构特性

#### 1.1 插件化架构
- ✅ 核心功能与插件分离
- ✅ 按需加载，减小打包体积
- ✅ 支持自定义插件扩展
- ✅ 插件列表：
  - RichText（节点富文本插件）
  - Select（鼠标多选节点插件）
  - Drag（节点拖拽插件）
  - AssociativeLine（关联线插件）
  - Export（导出插件）
  - KeyboardNavigation（键盘导航插件）
  - MiniMap（小地图插件）
  - Watermark（水印插件）
  - TouchEvent（移动端触摸事件支持插件）
  - NodeImgAdjust（拖拽调整节点图片大小插件）
  - Search（搜索插件）
  - Painter（节点格式刷插件）
  - Scrollbar（滚动条插件）
  - Formula（数学公式插件）
  - Cooperate（协同编辑插件）
  - RainbowLines（彩虹线条插件）
  - Demonstrate（演示模式插件）
  - OuterFrame（外框插件）
  - MindMapLayoutPro（思维导图布局插件）

#### 1.2 布局系统
- ✅ 逻辑结构图（向左、向右）
- ✅ 思维导图
- ✅ 组织结构图
- ✅ 目录组织图
- ✅ 时间轴（横向、竖向，多种变体）
- ✅ 鱼骨图（多种变体）

### 2. 节点功能特性

#### 2.1 节点内容支持
- ✅ **文本**：
  - 普通文本
  - 富文本（RichText，支持格式化）
  - 数学公式（LaTeX/MathJax）
  - 文本自动换行
  - 自定义文本宽度
- ✅ **图片**：
  - 支持图片插入
  - 图片位置：left/top/right/bottom
  - 图片大小调整（拖拽调整）
  - 图片标题
  - Base64图片存储
  - 图片加载失败处理
- ✅ **图标**：
  - 内置图标库（商务、教育、节日、食物、医疗、工具、旅行等）
  - 支持多个图标
  - SVG图标和图片图标
  - 图标点击事件
- ✅ **超链接**：
  - 支持超链接
  - 点击跳转
- ✅ **备注**：
  - 节点备注功能
  - 备注显示（tooltip/侧边栏）
  - 备注编辑
  - Markdown格式备注
- ✅ **标签**：
  - 多标签支持
  - 标签位置：right/bottom
  - 标签样式自定义
  - 标签圆角、颜色、字体
- ✅ **概要**：
  - 概要节点功能
  - 概要节点样式
  - 概要节点布局

#### 2.2 节点形状
- ✅ 矩形（rectangle）
- ✅ 菱形（diamond）
- ✅ 平行四边形（parallelogram）
- ✅ 圆角矩形（roundedRectangle）
- ✅ 八角矩形（octagonalRectangle）
- ✅ 外三角矩形（outerTriangularRectangle）
- ✅ 内三角矩形（innerTriangularRectangle）
- ✅ 椭圆（ellipse）
- ✅ 圆形（circle）
- ✅ 支持扩展自定义形状

#### 2.3 节点样式
- ✅ **颜色**：
  - 填充颜色
  - 边框颜色
  - 文字颜色
  - 渐变填充（线性渐变）
  - 渐变方向自定义
- ✅ **边框**：
  - 边框宽度
  - 边框样式（实线/虚线）
  - 边框圆角
  - 虚线样式自定义
- ✅ **字体**：
  - 字体族
  - 字体大小
  - 字体粗细
  - 字体样式（正常/斜体）
  - 文字对齐方式
  - 文字装饰（下划线等）
- ✅ **内边距**：
  - 水平内边距（paddingX）
  - 垂直内边距（paddingY）
- ✅ **层级样式**：
  - 根节点样式
  - 二级节点样式
  - 三级及以下节点样式
  - 概要节点样式
  - 每层可独立配置

#### 2.4 节点操作
- ✅ **创建**：
  - 双击空白处创建
  - Enter键创建子节点
  - Tab键创建同级节点
  - 快捷创建子节点按钮
- ✅ **编辑**：
  - 双击节点编辑文本
  - 富文本编辑
  - 实时渲染
  - 自动进入编辑模式
- ✅ **删除**：
  - 右键双击删除
  - Delete键删除
  - 批量删除
- ✅ **移动**：
  - 拖拽移动节点
  - 自定义位置
  - 位置锁定
- ✅ **选择**：
  - 单击选择
  - Ctrl+左键多选
  - 鼠标拖拽框选
  - 全选（Ctrl+A）
- ✅ **展开/收起**：
  - 展开收起按钮
  - 展开收起动画
  - 展开按钮占位
- ✅ **复制粘贴**：
  - 复制节点
  - 粘贴节点
  - 剪贴板处理
  - 跨画布粘贴
- ✅ **其他**：
  - 节点宽度调整（拖拽）
  - 节点格式刷
  - 节点外框
  - 节点标记

### 3. 连线功能特性

#### 3.1 结构连线（父子节点连线）
- ✅ **连线样式**：
  - 直线
  - 曲线（贝塞尔曲线）
  - 手绘风格
  - 彩虹线条
- ✅ **连线属性**：
  - 连线宽度
  - 连线颜色
  - 连线样式（实线/虚线）
  - 连线流动动画
  - 连线箭头
  - 连线方向（单向/双向）
- ✅ **连线布局**：
  - 根据布局自动计算连线路径
  - 不同布局有不同的连线方式
  - 连线避让算法

#### 3.2 关联线（AssociativeLine）
- ✅ **创建关联线**：
  - 从激活节点创建
  - 鼠标拖拽创建
  - 自动检测目标节点
  - 防止重复连线
- ✅ **关联线样式**：
  - 虚线样式
  - 线条宽度
  - 线条颜色
  - 激活状态颜色
  - 激活状态宽度
  - 箭头样式
- ✅ **关联线控制**：
  - 控制点（2个控制点）
  - 拖拽调整控制点
  - 控制点可视化
  - 控制点连线显示
  - 控制点保存（相对位置）
- ✅ **关联线文字**：
  - 支持在关联线上添加文字
  - 文字位置自动调整
  - 文字编辑（双击）
  - 文字样式（颜色、字体、大小）
  - 文字跟随路径
- ✅ **关联线交互**：
  - 点击激活关联线
  - 双击编辑文字
  - 删除关联线
  - 关联线置顶
  - 关联线事件（click、dblclick）

#### 3.3 连线优化
- ✅ 连线缓存
- ✅ 连线批量更新
- ✅ 连线性能优化
- ✅ 连线碰撞检测

### 4. 画布功能

#### 4.1 画布操作
- ✅ **拖动**：
  - 鼠标拖动画布
  - 触摸拖动
  - 右键拖动模式
  - 左键选择右键拖动模式
- ✅ **缩放**：
  - 鼠标滚轮缩放
  - 触摸缩放
  - 缩放限制
  - 缩放中心点
- ✅ **视图**：
  - 小地图（MiniMap）
  - 滚动条（Scrollbar）
  - 视图居中
  - 视图适应
  - 视图数据保存/恢复

#### 4.2 画布辅助
- ✅ 水印
- ✅ 网格（可选）
- ✅ 标尺（可选）

### 5. 交互功能

#### 5.1 快捷键
- ✅ 完整的快捷键系统
- ✅ 快捷键自定义
- ✅ 快捷键冲突检测
- ✅ 键盘导航

#### 5.2 搜索替换
- ✅ 搜索节点
- ✅ 搜索高亮
- ✅ 搜索结果导航
- ✅ 替换功能

#### 5.3 前进后退
- ✅ 操作历史记录
- ✅ 撤销（Undo）
- ✅ 重做（Redo）
- ✅ 历史记录限制

### 6. 导入导出

#### 6.1 导出格式
- ✅ JSON
- ✅ PNG（图片）
- ✅ SVG（矢量图）
- ✅ PDF
- ✅ Markdown
- ✅ XMind
- ✅ TXT

#### 6.2 导入格式
- ✅ JSON
- ✅ XMind
- ✅ Markdown

### 7. 高级功能

#### 7.1 协同编辑
- ✅ 多用户协同
- ✅ 用户头像显示
- ✅ 操作同步
- ✅ 冲突处理

#### 7.2 演示模式
- ✅ 演示模式
- ✅ 节点聚焦
- ✅ 节点高亮
- ✅ 空白模式

#### 7.3 其他
- ✅ 节点格式刷
- ✅ 节点外框
- ✅ 节点标记
- ✅ 主题系统
- ✅ 主题注册
- ✅ 主题切换

---

## 二、当前实现（Card部分）功能对比

### 2.1 节点（Card）功能现状

#### ✅ 已实现功能
1. **基础节点**：
   - 节点创建（双击空白处、Enter/Tab键）
   - 节点删除（右键双击、Delete键）
   - 节点移动（拖拽）
   - 节点选择
   - 节点编辑（双击编辑对话框）

2. **节点内容**：
   - 标题显示
   - 问题显示
   - 答案显示
   - 笔记图标显示
   - 文本截断

3. **节点样式**：
   - 层级样式（4级）
   - 渐变填充
   - 边框样式
   - 文字颜色自适应

4. **节点操作**：
   - 跳转到源文本
   - 跳转到笔记
   - 编辑卡片（标题、问题、答案、笔记）

#### ❌ 缺失功能（对比Simple Mind Map）

1. **节点内容**：
   - ❌ 富文本支持（仅支持纯文本）
   - ❌ 图片支持
   - ❌ 图标支持
   - ❌ 超链接支持
   - ❌ 标签支持
   - ❌ 数学公式支持
   - ❌ 概要节点

2. **节点形状**：
   - ❌ 仅支持矩形
   - ❌ 无其他形状选项

3. **节点样式**：
   - ❌ 无边框样式选项（虚线等）
   - ❌ 无渐变方向控制
   - ❌ 无字体样式选项（粗体、斜体等）
   - ❌ 无文字对齐选项
   - ❌ 无内边距自定义

4. **节点操作**：
   - ❌ 无节点宽度调整
   - ❌ 无节点格式刷
   - ❌ 无节点外框
   - ❌ 无节点标记
   - ❌ 无展开/收起功能
   - ❌ 无快捷创建子节点按钮
   - ❌ 无节点复制粘贴

5. **节点交互**：
   - ❌ 无节点hover效果
   - ❌ 无节点激活状态样式
   - ❌ 无节点拖拽调整大小

### 2.2 连线功能现状

#### ✅ 已实现功能
1. **基础连线**：
   - 父子节点连线
   - 贝塞尔曲线连线
   - 智能连线（自动避让）
   - 渐变连线
   - 连线箭头

2. **连线样式**：
   - 连线宽度
   - 连线颜色（根据层级）
   - 连线样式（实线/虚线）

#### ❌ 缺失功能（对比Simple Mind Map）

1. **结构连线**：
   - ❌ 无手绘风格连线
   - ❌ 无彩虹线条
   - ❌ 无连线流动动画
   - ❌ 无连线方向控制（单向/双向）
   - ❌ 无连线避让算法优化

2. **关联线（AssociativeLine）**：
   - ❌ **完全缺失** - 这是最大的功能缺失
   - ❌ 无跨节点关联线
   - ❌ 无关联线控制点
   - ❌ 无关联线文字
   - ❌ 无关联线编辑
   - ❌ 无关联线删除

3. **连线交互**：
   - ❌ 无连线点击事件
   - ❌ 无连线激活状态
   - ❌ 无连线编辑

4. **连线优化**：
   - ❌ 无连线缓存
   - ❌ 无连线批量更新优化
   - ❌ 无连线性能优化

---

## 三、优化建议（按优先级排序）

### 🔴 高优先级优化

#### 1. 关联线功能实现（最重要）
**现状**：完全缺失  
**建议**：参考 `AssociativeLine.js` 实现完整的关联线系统

**实现要点**：
```python
# 需要实现的功能
1. 关联线创建：
   - 从激活节点开始创建
   - 鼠标拖拽创建关联线
   - 自动检测目标节点
   - 防止重复连线

2. 关联线控制点：
   - 2个控制点（贝塞尔曲线）
   - 控制点可视化
   - 控制点拖拽调整
   - 控制点位置保存（相对位置）

3. 关联线文字：
   - 在关联线上添加文字
   - 文字位置自动调整
   - 文字编辑（双击）
   - 文字样式配置

4. 关联线交互：
   - 点击激活关联线
   - 双击编辑文字
   - 删除关联线
   - 关联线样式更新
```

**代码结构建议**：
```python
# ai_reader_cards/card/associative_line.py
class AssociativeLineManager:
    """关联线管理器"""
    - line_list: 所有关联线列表
    - active_line: 当前激活的关联线
    - is_creating_line: 是否正在创建关联线
    - creating_start_node: 创建起始节点
    - control_points: 控制点管理
    
    def create_line(from_node, to_node)
    def remove_line(line)
    def set_active_line(line)
    def update_control_points(line, point1, point2)
    def add_text_to_line(line, text)
    def edit_line_text(line, text)
```

#### 2. 节点内容增强
**现状**：仅支持标题、问题、答案  
**建议**：逐步添加更多内容类型

**优先级排序**：
1. **图片支持**（高优先级）
   - 图片插入
   - 图片位置（top/bottom/left/right）
   - 图片大小调整
   
2. **图标支持**（中优先级）
   - 内置图标库
   - 图标选择器
   
3. **标签支持**（中优先级）
   - 多标签
   - 标签样式
   
4. **富文本支持**（低优先级，复杂）
   - 富文本编辑器集成
   - 格式化支持

#### 3. 节点形状扩展
**现状**：仅支持矩形  
**建议**：添加常用形状

**实现建议**：
```python
# ai_reader_cards/card/shapes.py
class NodeShape:
    """节点形状基类"""
    
class RectangleShape(NodeShape):
    """矩形"""
    
class RoundedRectangleShape(NodeShape):
    """圆角矩形"""
    
class EllipseShape(NodeShape):
    """椭圆"""
    
class DiamondShape(NodeShape):
    """菱形"""
```

#### 4. 连线样式增强
**现状**：基础连线样式  
**建议**：添加更多样式选项

**实现要点**：
- 手绘风格连线
- 彩虹线条
- 连线流动动画
- 连线避让算法优化

### 🟡 中优先级优化

#### 5. 节点操作增强
- 节点宽度调整（拖拽边缘）
- 节点格式刷
- 节点外框
- 节点标记
- 展开/收起功能
- 快捷创建子节点按钮

#### 6. 节点样式增强
- 边框样式选项（虚线等）
- 字体样式（粗体、斜体）
- 文字对齐方式
- 内边距自定义
- 节点hover效果
- 节点激活状态样式

#### 7. 连线性能优化
- 连线缓存机制
- 连线批量更新
- 连线渲染优化
- 大量节点时的性能优化

### 🟢 低优先级优化

#### 8. 高级功能
- 节点复制粘贴
- 节点格式刷
- 节点外框
- 节点标记
- 小地图
- 水印
- 搜索替换增强

---

## 四、具体实现建议

### 4.1 关联线功能实现（详细设计）

#### 数据结构
```python
# 在 CardTreeNode 中添加
class CardTreeNode:
    # 关联线目标节点ID列表
    associative_line_targets: List[str] = []
    
    # 关联线控制点偏移（相对位置）
    associative_line_control_offsets: Dict[str, List[QPointF]] = {}
    
    # 关联线文字
    associative_line_text: Dict[str, str] = {}
    
    # 关联线样式
    associative_line_style: Dict[str, dict] = {}
```

#### 关联线管理器
```python
class AssociativeLineManager:
    """关联线管理器"""
    
    def __init__(self, scene):
        self.scene = scene
        self.line_list = []  # 所有关联线
        self.active_line = None  # 当前激活的关联线
        self.is_creating_line = False
        self.creating_start_node = None
        self.creating_line_path = None
        self.control_points = {}  # 控制点管理
    
    def create_line(self, from_node, to_node):
        """创建关联线"""
        # 1. 检查是否已存在
        # 2. 计算控制点
        # 3. 创建连线路径
        # 4. 添加到列表
        pass
    
    def remove_line(self, line):
        """删除关联线"""
        pass
    
    def set_active_line(self, line):
        """设置激活的关联线"""
        # 1. 显示控制点
        # 2. 高亮连线
        # 3. 显示文字编辑
        pass
    
    def update_control_points(self, line, point1, point2):
        """更新控制点"""
        # 保存相对位置
        pass
    
    def add_text_to_line(self, line, text):
        """在关联线上添加文字"""
        pass
```

#### 关联线绘制
```python
class AssociativeLine(QGraphicsPathItem):
    """关联线图形项"""
    
    def __init__(self, from_node, to_node):
        # 计算贝塞尔曲线路径
        # 绘制虚线
        # 绘制箭头
        # 绘制文字
        pass
    
    def update_path(self):
        """更新路径"""
        # 根据控制点更新贝塞尔曲线
        pass
    
    def draw_control_points(self, painter):
        """绘制控制点"""
        pass
```

### 4.2 节点内容增强实现

#### 图片支持
```python
class CardVisualNode:
    def add_image(self, image_path, placement='top'):
        """添加图片"""
        # 创建 QGraphicsPixmapItem
        # 根据placement调整位置
        pass
    
    def adjust_image_size(self, image_item, new_size):
        """调整图片大小"""
        pass
```

#### 图标支持
```python
class IconManager:
    """图标管理器"""
    ICON_LIBRARIES = {
        'business': [...],
        'education': [...],
        'tools': [...],
        # ...
    }
    
    def get_icon(self, category, name):
        """获取图标"""
        pass
```

### 4.3 节点形状扩展实现

```python
class NodeShapeFactory:
    """节点形状工厂"""
    
    @staticmethod
    def create_shape(shape_type, rect):
        """创建形状"""
        if shape_type == 'rectangle':
            return QGraphicsRectItem(rect)
        elif shape_type == 'rounded_rectangle':
            return RoundedRectangleItem(rect)
        elif shape_type == 'ellipse':
            return QGraphicsEllipseItem(rect)
        # ...
```

### 4.4 连线样式增强实现

#### 手绘风格连线
```python
class HandDrawnConnection(ProfessionalConnection):
    """手绘风格连线"""
    
    def update_path(self):
        # 添加随机抖动
        # 使用多个控制点
        pass
```

#### 彩虹线条
```python
class RainbowConnection(ProfessionalConnection):
    """彩虹线条"""
    
    def draw(self, painter):
        # 使用渐变画笔
        # 根据路径长度分段着色
        pass
```

#### 连线流动动画
```python
class AnimatedConnection(ProfessionalConnection):
    """带动画的连线"""
    
    def __init__(self):
        self.animation = QPropertyAnimation()
        self.animation.setPropertyName(b"dashOffset")
        # ...
```

---

## 五、性能优化建议

### 5.1 连线渲染优化
1. **连线缓存**：
   - 缓存已计算的连线路径
   - 节点位置变化时仅更新相关连线
   
2. **批量更新**：
   - 批量更新连线，避免频繁重绘
   - 使用定时器延迟更新

3. **可见区域优化**：
   - 仅渲染可见区域的连线
   - 使用视图裁剪

### 5.2 节点渲染优化
1. **虚拟化**：
   - 大量节点时使用虚拟化渲染
   - 仅渲染可见节点

2. **缓存**：
   - 缓存节点渲染结果
   - 节点内容变化时局部更新

### 5.3 布局优化
1. **增量布局**：
   - 节点变化时增量更新布局
   - 避免全量重新布局

2. **异步布局**：
   - 复杂布局异步计算
   - 使用后台线程

---

## 六、代码质量改进建议

### 6.1 架构优化
1. **插件化**：
   - 参考Simple Mind Map的插件化架构
   - 将功能模块化
   - 支持按需加载

2. **事件系统**：
   - 完善事件系统
   - 支持事件订阅/发布
   - 解耦组件

3. **配置系统**：
   - 统一的配置管理
   - 支持主题配置
   - 支持用户自定义

### 6.2 代码组织
1. **模块分离**：
   - 节点渲染与逻辑分离
   - 连线管理与绘制分离
   - 布局算法独立

2. **接口设计**：
   - 定义清晰的接口
   - 支持扩展
   - 向后兼容

---

## 七、总结

### 7.1 功能对比总结

| 功能类别 | Simple Mind Map | 当前实现 | 缺失程度 |
|---------|----------------|---------|---------|
| 节点内容 | 10+种 | 3种（标题/问题/答案） | 🔴 严重缺失 |
| 节点形状 | 9种 | 1种（矩形） | 🔴 严重缺失 |
| 节点样式 | 完整 | 基础 | 🟡 部分缺失 |
| 结构连线 | 完整 | 基础 | 🟡 部分缺失 |
| 关联线 | ✅ 完整 | ❌ 完全缺失 | 🔴 严重缺失 |
| 节点操作 | 完整 | 基础 | 🟡 部分缺失 |
| 画布功能 | 完整 | 基础 | 🟡 部分缺失 |

### 7.2 优化优先级

**第一优先级（必须实现）**：
1. ✅ **关联线功能** - 这是最核心的缺失功能
2. ✅ **节点图片支持** - 提升实用性
3. ✅ **节点形状扩展** - 提升视觉效果

**第二优先级（建议实现）**：
4. ✅ 节点图标支持
5. ✅ 节点标签支持
6. ✅ 连线样式增强（手绘、彩虹）
7. ✅ 节点操作增强（格式刷、外框等）

**第三优先级（可选实现）**：
8. ✅ 富文本支持
9. ✅ 数学公式支持
10. ✅ 高级画布功能（小地图、水印等）

### 7.3 实现路线图

**阶段一（核心功能）**：
- 实现关联线系统
- 添加节点图片支持
- 扩展节点形状（圆角矩形、椭圆）

**阶段二（增强功能）**：
- 节点图标支持
- 节点标签支持
- 连线样式增强

**阶段三（完善功能）**：
- 节点操作增强
- 性能优化
- 高级功能

---

## 八、参考实现代码位置

### Simple Mind Map 关键文件

1. **关联线实现**：
   - `simple-mind-map/src/plugins/AssociativeLine.js`
   - `simple-mind-map/src/plugins/associativeLine/associativeLineUtils.js`
   - `simple-mind-map/src/plugins/associativeLine/associativeLineControls.js`
   - `simple-mind-map/src/plugins/associativeLine/associativeLineText.js`

2. **节点内容创建**：
   - `simple-mind-map/src/core/render/node/nodeCreateContents.js`

3. **节点形状**：
   - `simple-mind-map/src/core/render/node/Shape.js`

4. **节点样式**：
   - `simple-mind-map/src/core/render/node/Style.js`

5. **连线渲染**：
   - `simple-mind-map/src/layouts/MindMap.js` (renderLine方法)
   - `simple-mind-map/src/layouts/LogicalStructure.js` (renderLine方法)

### 当前实现文件

1. **节点实现**：
   - `ai_reader_cards/card/madmap_based_nodes.py`
   - `ai_reader_cards/card/madmap_based_models.py`

2. **连线实现**：
   - `ai_reader_cards/card/madmap_based_connections.py`
   - `ai_reader_cards/card/madmap_based_scene.py`

---

## 九、具体优化代码示例

### 示例1：关联线管理器基础结构

```python
# ai_reader_cards/card/associative_line_manager.py
from PyQt6.QtCore import QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
import math

class AssociativeLineItem(QGraphicsPathItem):
    """关联线图形项"""
    
    def __init__(self, from_node, to_node, control_points=None):
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self.control_points = control_points or []
        self.line_text = ""
        self.is_active = False
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)  # 在节点下方
        
        self.update_path()
    
    def update_path(self):
        """更新贝塞尔曲线路径"""
        start_point = self.get_connection_point(self.from_node, self.to_node)
        end_point = self.get_connection_point(self.to_node, self.from_node)
        
        # 计算控制点
        if not self.control_points:
            self.control_points = self.compute_default_control_points(
                start_point, end_point
            )
        
        # 创建贝塞尔曲线
        path = QPainterPath()
        path.moveTo(start_point)
        path.cubicTo(
            self.control_points[0],
            self.control_points[1],
            end_point
        )
        
        self.setPath(path)
    
    def compute_default_control_points(self, start, end):
        """计算默认控制点"""
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # 控制点偏移
        offset_x = abs(dx) * 0.5
        offset_y = abs(dy) * 0.5
        
        cp1 = QPointF(start.x() + offset_x, start.y())
        cp2 = QPointF(end.x() - offset_x, end.y())
        
        return [cp1, cp2]
    
    def get_connection_point(self, node, target_node):
        """获取节点连接点"""
        # 计算节点边缘连接点
        node_center = node.center_pos()
        target_center = target_node.center_pos()
        
        # 计算方向
        dx = target_center.x() - node_center.x()
        dy = target_center.y() - node_center.y()
        
        # 获取节点边界
        node_rect = node.boundingRect()
        node_pos = node.pos()
        
        # 计算连接点（在节点边缘）
        if abs(dx) > abs(dy):
            # 水平方向
            if dx > 0:
                # 右侧
                return QPointF(
                    node_pos.x() + node_rect.width(),
                    node_center.y()
                )
            else:
                # 左侧
                return QPointF(node_pos.x(), node_center.y())
        else:
            # 垂直方向
            if dy > 0:
                # 下方
                return QPointF(
                    node_center.x(),
                    node_pos.y() + node_rect.height()
                )
            else:
                # 上方
                return QPointF(node_center.x(), node_pos.y())
    
    def paint(self, painter, option, widget):
        """绘制关联线"""
        # 虚线样式
        pen = QPen(QColor(100, 100, 100), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([6, 4])
        
        if self.is_active:
            pen.setColor(QColor(70, 130, 180))
            pen.setWidth(3)
        
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
        
        # 绘制箭头
        self.draw_arrow(painter)
        
        # 绘制文字（如果有）
        if self.line_text:
            self.draw_text(painter)
    
    def draw_arrow(self, painter):
        """绘制箭头"""
        path = self.path()
        if path.elementCount() < 2:
            return
        
        # 获取路径终点
        end_point = path.pointAtPercent(1.0)
        
        # 计算方向
        t = 0.95
        point_before_end = path.pointAtPercent(t)
        direction = end_point - point_before_end
        
        if direction.manhattanLength() == 0:
            return
        
        angle = math.atan2(direction.y(), direction.x())
        
        # 绘制箭头
        arrow_size = 10
        arrow_p1 = QPointF(
            end_point.x() - arrow_size * math.cos(angle - math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = QPointF(
            end_point.x() - arrow_size * math.cos(angle + math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle + math.pi / 6)
        )
        
        arrow_path = QPainterPath()
        arrow_path.moveTo(end_point)
        arrow_path.lineTo(arrow_p1)
        arrow_path.lineTo(arrow_p2)
        arrow_path.closeSubpath()
        
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPath(arrow_path)
    
    def draw_text(self, painter):
        """在连线上绘制文字"""
        path = self.path()
        if path.elementCount() < 2:
            return
        
        # 在路径中点绘制文字
        mid_point = path.pointAtPercent(0.5)
        
        # 计算文字位置（垂直于路径）
        t = 0.5
        point_before = path.pointAtPercent(t - 0.01)
        point_after = path.pointAtPercent(t + 0.01)
        direction = point_after - point_before
        
        # 垂直方向
        perp_angle = math.atan2(direction.y(), direction.x()) + math.pi / 2
        
        # 文字偏移
        text_offset = 15
        text_pos = QPointF(
            mid_point.x() + text_offset * math.cos(perp_angle),
            mid_point.y() + text_offset * math.sin(perp_angle)
        )
        
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(text_pos, self.line_text)


class AssociativeLineManager:
    """关联线管理器"""
    
    def __init__(self, scene):
        self.scene = scene
        self.line_list = []  # [(line_item, from_node, to_node), ...]
        self.active_line = None
        self.is_creating_line = False
        self.creating_start_node = None
        self.creating_line_item = None
    
    def create_line(self, from_node, to_node):
        """创建关联线"""
        # 检查是否已存在
        for line_item, fn, tn in self.line_list:
            if (fn == from_node and tn == to_node) or \
               (fn == to_node and tn == from_node):
                return None
        
        # 创建关联线
        line_item = AssociativeLineItem(from_node, to_node)
        self.scene.addItem(line_item)
        
        # 保存到列表
        self.line_list.append((line_item, from_node, to_node))
        
        # 更新节点数据
        self._update_node_data(from_node, to_node)
        
        return line_item
    
    def remove_line(self, line_item):
        """删除关联线"""
        for i, (item, fn, tn) in enumerate(self.line_list):
            if item == line_item:
                self.scene.removeItem(item)
                self.line_list.pop(i)
                self._remove_from_node_data(fn, tn)
                break
    
    def set_active_line(self, line_item):
        """设置激活的关联线"""
        # 取消之前的激活
        if self.active_line:
            self.active_line.is_active = False
            self.active_line.update()
        
        # 设置新的激活
        self.active_line = line_item
        if line_item:
            line_item.is_active = True
            line_item.update()
    
    def start_creating_line(self, from_node):
        """开始创建关联线"""
        self.is_creating_line = True
        self.creating_start_node = from_node
        # 创建临时连线（跟随鼠标）
        # ...
    
    def complete_creating_line(self, to_node):
        """完成创建关联线"""
        if not self.is_creating_line or not self.creating_start_node:
            return
        
        if self.creating_start_node == to_node:
            # 不能连接到自身
            self.cancel_creating_line()
            return
        
        # 创建关联线
        self.create_line(self.creating_start_node, to_node)
        self.cancel_creating_line()
    
    def cancel_creating_line(self):
        """取消创建关联线"""
        if self.creating_line_item:
            self.scene.removeItem(self.creating_line_item)
            self.creating_line_item = None
        self.is_creating_line = False
        self.creating_start_node = None
    
    def _update_node_data(self, from_node, to_node):
        """更新节点数据"""
        # 在CardTreeNode中保存关联线目标
        if hasattr(from_node, 'tree_node'):
            if not hasattr(from_node.tree_node, 'associative_line_targets'):
                from_node.tree_node.associative_line_targets = []
            
            target_id = to_node.tree_node.id
            if target_id not in from_node.tree_node.associative_line_targets:
                from_node.tree_node.associative_line_targets.append(target_id)
    
    def _remove_from_node_data(self, from_node, to_node):
        """从节点数据中移除关联线"""
        if hasattr(from_node, 'tree_node'):
            if hasattr(from_node.tree_node, 'associative_line_targets'):
                target_id = to_node.tree_node.id
                if target_id in from_node.tree_node.associative_line_targets:
                    from_node.tree_node.associative_line_targets.remove(target_id)
    
    def render_all_lines(self):
        """渲染所有关联线"""
        # 清除现有连线
        for line_item, _, _ in self.line_list:
            self.scene.removeItem(line_item)
        self.line_list.clear()
        
        # 重新创建所有关联线
        for vn in self.scene.visual_nodes:
            if hasattr(vn.tree_node, 'associative_line_targets'):
                for target_id in vn.tree_node.associative_line_targets:
                    target_vn = self.scene.find_node_by_id(target_id)
                    if target_vn:
                        self.create_line(vn, target_vn)
```

### 示例2：节点图片支持

```python
# 在 CardVisualNode 中添加
class CardVisualNode:
    def add_image(self, image_path, placement='top'):
        """添加图片"""
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QGraphicsPixmapItem
        
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return None
        
        # 调整图片大小以适应节点
        max_width = self.WIDTH - 20
        max_height = 100
        
        scaled_pixmap = pixmap.scaled(
            max_width, max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        image_item = QGraphicsPixmapItem(scaled_pixmap, self)
        
        # 根据placement设置位置
        if placement == 'top':
            image_item.setPos(10, 5)
        elif placement == 'bottom':
            image_item.setPos(10, self.HEIGHT - scaled_pixmap.height() - 5)
        elif placement == 'left':
            image_item.setPos(5, 10)
        elif placement == 'right':
            image_item.setPos(self.WIDTH - scaled_pixmap.width() - 5, 10)
        
        return image_item
```

### 示例3：节点形状扩展

```python
# ai_reader_cards/card/shapes.py
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainterPath

class NodeShapeFactory:
    """节点形状工厂"""
    
    @staticmethod
    def create_shape(shape_type, rect: QRectF, parent=None):
        """创建形状"""
        if shape_type == 'rectangle':
            return QGraphicsRectItem(rect, parent)
        elif shape_type == 'rounded_rectangle':
            return RoundedRectangleItem(rect, parent)
        elif shape_type == 'ellipse':
            return QGraphicsEllipseItem(rect, parent)
        elif shape_type == 'diamond':
            return DiamondItem(rect, parent)
        else:
            return QGraphicsRectItem(rect, parent)


class RoundedRectangleItem(QGraphicsRectItem):
    """圆角矩形"""
    
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.radius = 10
    
    def paint(self, painter, option, widget):
        """绘制圆角矩形"""
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        painter.fillPath(path, self.brush())
        painter.strokePath(path, self.pen())


class DiamondItem(QGraphicsRectItem):
    """菱形"""
    
    def paint(self, painter, option, widget):
        """绘制菱形"""
        rect = self.rect()
        center_x = rect.center().x()
        center_y = rect.center().y()
        half_width = rect.width() / 2
        half_height = rect.height() / 2
        
        path = QPainterPath()
        path.moveTo(center_x, rect.top())
        path.lineTo(rect.right(), center_y)
        path.lineTo(center_x, rect.bottom())
        path.lineTo(rect.left(), center_y)
        path.closeSubpath()
        
        painter.fillPath(path, self.brush())
        painter.strokePath(path, self.pen())
```

---

## 十、实施计划

### 阶段一：核心功能（1-2周）
1. ✅ 实现关联线管理器基础框架
2. ✅ 实现关联线创建和删除
3. ✅ 实现关联线控制点
4. ✅ 实现关联线文字

### 阶段二：内容增强（1周）
1. ✅ 节点图片支持
2. ✅ 节点形状扩展（圆角矩形、椭圆、菱形）
3. ✅ 节点图标支持

### 阶段三：样式增强（1周）
1. ✅ 连线样式增强（手绘、彩虹）
2. ✅ 节点样式选项扩展
3. ✅ 节点操作增强

### 阶段四：优化完善（持续）
1. ✅ 性能优化
2. ✅ 代码重构
3. ✅ 测试和bug修复

---

## 十一、注意事项

1. **向后兼容**：所有新功能需要保持向后兼容
2. **性能考虑**：大量节点时的性能优化
3. **用户体验**：交互要流畅，反馈要及时
4. **代码质量**：保持代码清晰，注释完整
5. **测试**：新功能需要充分测试

---

**文档生成时间**：2024年
**版本**：v1.0





