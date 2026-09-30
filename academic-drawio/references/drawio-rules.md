# XML 构建与交付规则

## 文件与原生对象

默认单个 XML 代码块，完整未压缩 `mxfile/diagram/mxGraphModel/root`，diagram 有有意义的名称和 ID。根层包含 `mxCell id="0"`、`mxCell id="1" parent="0"`。节点和连接线的唯一 ID 表达功能与关系，如 `query-network`、`edge-query-to-database`。相关元素按分区归拢。

节点 `vertex="1"`，具有 value/style/parent 和 mxGeometry 的 x/y/width/height/as="geometry"，宽高正数、数值有限。组或 swimlane 是原生节点，子节点坐标相对父容器，标题带不能被子节点遮挡。

连接线 `edge="1"`，通过 source/target 绑定节点，几何 relative="1"。绑定节点不等于固定连接点：省略 entry/exit 坐标、偏移和 sourcePort/targetPort。跨容器连线采用共同祖先父级，航点坐标也相对此父级。航点放入 `mxGeometry/Array as="points"/mxPoint`。

通过航点、相对位置和允许的边方向分散出入口。双向关系使用两个独立的单向边。具体格式见 [图形规范](figure-standard.md)。

## HTML 与 XML 两层转义

所有文本使用 html=1、fontStyle=1，换行使用 HTML 的 br。
先构造 HTML，再交给 XML 序列化器写入 value，避免漏转义或多转义。

希望显示 h 的上标 v 与下标 inter 的点乘时，XML 属性为：

```xml
value="h&lt;sup&gt;v&lt;/sup&gt; &amp;odot; h&lt;sub&gt;inter&lt;/sub&gt;"
```

普通文字“误差 < 阈值”的 HTML 是 `误差 &lt; 阈值`，在 XML 属性中为 `误差 &amp;lt; 阈值`。裸 `&odot;` 不是 XML 预定义实体，会导致解析失败。不把 LaTeX 当成可渲染 HTML，也不让标签原样显示。

## 校验与边界

```text
python scripts/validate_drawio.py candidate.xml --profile academic
```

structural 兼容裸页面或完整单页未压缩文件；academic 检查完整文件及新学术规范。两者都只读，不支持压缩、多页或用户对象包装。
academic 覆盖 A4、网格、页面名、字体、线宽、箭头、跳线、浮动连接、HTML 及几何边界。它不计算实际字体渲染、自动路由与交叉跳线效果，不能代替人工视觉检查。

## 使用入口

在空白图中打开 **Extras → Edit Diagram**，粘贴完整代码并应用；或保存为 .drawio 打开。此操作会替换当前页，不默认覆盖用户原图。若旧版编辑器只接受裸页面，优先用 .drawio 文件打开。
用户明确要求裸页面源码时才交付 mxGraphModel；该格式没有 diagram name 的位置，不能捏造非标准属性。

官方依据（2026-09-30 核对）：
- [页面源码编辑](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/)
- [完整 mxfile 的编辑器处理分支](https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/grapheditor/Dialogs.js)
- [文件结构](https://www.drawio.com/docs/reference/diagram-generation/)

