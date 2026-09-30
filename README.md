# Academic Drawio Skill

一个帮助 Codex 制作学术技术路线图的 Skill。

你只需要提供论文思路、研究材料，以及一张喜欢的参考图。它会借鉴参考图的版式和视觉风格，重新组织你的研究内容，并生成完整、可编辑的 draw.io XML，而不是一张无法修改的图片。

## 它能做什么

- 根据论文思路生成学术技术路线图
- 参考示例图片的布局、配色和层级
- 读取研究文字或 PDF 材料
- 修改已有的 draw.io 路线图
- 输出原生节点、文字和连接线，方便继续编辑
- 自动检查 XML 结构和常见排版问题

参考图只用于学习版式，不会把参考图里的研究内容复制到你的图中。

## 安装

1. 下载本仓库。
2. 将仓库中的 `academic-drawio` 文件夹复制到 Codex 的个人 Skills 目录：

   ```text
   ~/.codex/skills/academic-drawio
   ```

3. 重新打开 Codex，或开始一个新对话。

Windows 用户的目录通常是：

```text
C:\Users\你的用户名\.codex\skills\academic-drawio
```

## 使用方法

在 Codex 对话中输入 `$academic-drawio`，同时附上参考图和自己的研究材料。例如：

```text
使用 $academic-drawio，参考这张图片的布局，把我上传的论文思路整理成一张学术技术路线图。请直接输出完整的 draw.io XML。
```

如果没有参考图，也可以要求它采用简洁的学术风格：

```text
使用 $academic-drawio，根据下面的研究思路生成一张纵向技术路线图，采用简洁的学术风格。
```

需要改图时，直接说明希望调整的内容：

```text
把第二阶段拆成两个并行模块，其他内容和布局保持不变。
```

## 把结果导入 draw.io

1. 打开 [draw.io](https://app.diagrams.net/) 并新建空白图。
2. 选择 **Extras → Edit Diagram**。
3. 删除编辑框中的原内容。
4. 粘贴 Codex 返回的完整 XML，然后点击应用。
5. 保存为 `.drawio` 文件，即可继续修改文字、模块和连接线。

请不要把 XML 粘贴到普通画布或 Mermaid 输入框中。

## 仓库内容

```text
academic-drawio/
├── SKILL.md                 Skill 的主要说明
├── agents/openai.yaml       Codex 展示信息
├── references/              draw.io 与学术图形规范
├── assets/minimal.xml       最小可编辑示例
└── scripts/validate_drawio.py  XML 校验工具
```

校验工具只依赖 Python 3 标准库。

