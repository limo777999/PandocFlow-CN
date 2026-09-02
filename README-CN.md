# PandocFlow 中文独立版

这是基于开源项目 [Fireooout/PandocFlow](https://github.com/Fireooout/PandocFlow)
制作的 Windows 中文独立版。发布的 EXE 内置 Pandoc 和 Typst，目标电脑无需安装
Python、Pandoc 或 Typst。

## 许可证

本项目采用 [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html) 许可证。
Pandoc、PyQt6/Qt、PyInstaller 和 Typst 保留各自的上游许可证与版权，详见
`THIRD_PARTY_NOTICES.txt`。发布修改版时请保留本许可证和第三方声明。

## 使用

1. 双击 `PandocFlow-CN.exe`。
2. 拖入文件或文件夹，选择目标格式与输出目录。
3. 点击“开始批量转换”。已有同名文件不会被覆盖，程序会自动添加序号。

常用转换如 Markdown、Word、HTML、EPUB、ODT、RTF、纯文本和 reStructuredText
均由内置 Pandoc 完成。最新版程序同时内置 Typst，可直接转换 PDF，无需现场
安装 LaTeX、wkhtmltopdf 或 WeasyPrint。

## 构建

```powershell
# 源码构建需要本机提供 Pandoc；Typst 未设置时使用仓库内 engines\typst.exe
$env:PANDOC_EXE='C:\tools\pandoc.exe'
# 可选：$env:TYPST_EXE='C:\tools\typst.exe'
python -m pip install -r requirements.txt
python build_exe.py
```

产物位于 `dist/PandocFlow-CN.exe`，构建脚本同时复制一份到项目根目录。
第三方版权与许可证见 `THIRD_PARTY_NOTICES.txt` 和 `LICENSE`。

## 发布说明

源码仓库不提交 `build/`、`dist/` 和本机配置。Windows 单文件 EXE 建议作为
GitHub Release 附件发布，并同时提供源码和第三方声明。
