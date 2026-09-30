# 学术图形规范（用户提供，v1.1）

本文件落实用户的《DrawIO 图形规范指南（完整版）》，优先于参考图中的细线、小字、左对齐等样式。后续明确覆盖某项时遵循用户要求。

## A4、字体与布局

- 单页 A4：纵向 pageWidth=827、pageHeight=1169，横向交换宽高；page=1、pageScale=1、grid=1、gridSize=10、math=0。
- 依布局选纸张方向，不扩大画布再缩印而声称文字可读。放不下时先换行和重排，仍不能清晰表达才请求分图或精简。
- 所有文本 fontStyle=1、align=center、verticalAlign=middle，HTML 不能用 font-weight:normal 覆盖。正文从 16–18、分区 20–22、标题 24–28 起调，标题明显大于正文。字号是编辑器单位，打印大小需 A4 预览确认。
- 同级模块间距优先 30–50（默认 40），网格对齐；相关模块放入容器或组。组件尺寸按内容调整并留内边距，不能裁剪或隐藏溢出。

## 边框与连接线

统一 strokeWidth=3，对应 draw.io 默认 pt 界面的 3。官方源码中 pt 输入直接映射此值，不做 CSS 4px 换算。缩放、导出及打印会影响实际物理线宽；如需精确的物理 3pt，应额外检查导出的 PDF，不能将界面数字视为测量结果。

所有线条与边框显式写 jumpStyle=arc、jumpSize=5；跳线效果只对连线路径有意义。属性大小写不能写成 jumpstyle/jumpsize。

连接线统一：

```text
edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=classic;startArrow=none;endFill=1;strokeWidth=3;jumpStyle=arc;jumpSize=5;
```

节点圆角可随模板，但所有连接线的拐角必须 rounded=1。

## 浮动连接和复杂场景

- 绑定 source/target 节点，但不设固定 entry/exit 坐标、偏移、sourcePort/targetPort，不能使用 portConstraint=fixed。
- 多线汇入通过相对位置和末端航点引导从不同方向进入；同源分支通过首段航点分散。可限制连接到哪条边，不锁定边上的比例位置。
- 长线使用航点；必要时以无业务语义的中间连接点或分段组织，不能虚构研究模块。
- 跳线不能解决文字遮挡：路径不得穿越正文、组件标签或分区标题。
- 平行连线间距一致，复杂图按层级和区域组织以减少交叉。
- 双向关系使用两条独立单向边，不使用双向箭头。

## 文本与公式

全部 html=1、fontStyle=1。上下标用 HTML sup/sub，不使用 LaTeX 或 MathJax，math=0。
点乘在 HTML 中写 &odot;，在 XML 属性中写 &amp;odot;；完整例子见绘图规则。公式可使用数学字体，但仍加粗居中。节点需容纳加粗后的正文、公式和上下标。

## 文件与命名

使用完整单页未压缩 mxfile，diagram name 表达主题，不能用 Page-1/Untitled。节点 ID 反映功能，连接线 ID 反映 source→target；按分区组织相关元素。

## 用户上传图片的借鉴方式

图片包含四条横向数据流，使用绿、橙、黄、粉色标题条划分区域，主体由左向右，含分支汇合；节点用淡绿、淡橙、淡蓝等功能色。

这是“分区横向流程”的布局参考，不硬编码四条数据流，不把语音交互、腾讯服务、英雄或赛事等业务自动带入其他研究。长行可在分区内分层重排，同时满足 A4 和阅读性要求。

## 人工检查清单

- A4 预览中正文可读，全体加粗、居中，标题突出。
- 文字不截断，组件不意外重叠，连线不穿文字或标题。
- 线宽、箭头、圆角与跳线一致，分支出入口分散。
- 移动节点后浮动连接保持合理，长路径航点不引入遮挡。
- 上下标和点乘正确显示，不露出 HTML/LaTeX。
- 文件能打开、独立编辑、保存后重新打开。

## 官方依据

- [A4 设置](https://www.drawio.com/docs/manual/editor/panels/page-size-scale-orientation/)
- [A4 尺寸](https://github.com/jgraph/drawio-mcp/blob/main/shared/mxfile.xsd)
- [样式与 HTML](https://www.drawio.com/docs/reference/diagram-generation/style-reference/)
- [pt 与线宽输入映射](https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/grapheditor/Format.js)

