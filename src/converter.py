import os
import subprocess
import tempfile
from PyQt6.QtCore import QThread, pyqtSignal
from utils import find_pdf_engine

class ConversionWorker(QThread):
    # Signals to communicate with the GUI thread
    # Emits: (input_file, output_file, success, status_message)
    started = pyqtSignal(str)
    finished = pyqtSignal(str, str, bool, str)

    def __init__(self, pandoc_path, input_file, target_format, output_dir=None):
        super().__init__()
        self.pandoc_path = pandoc_path
        self.input_file = os.path.abspath(input_file)
        self.target_format = target_format.lower().strip(".")
        self.output_dir = output_dir

    def run(self):
        self.started.emit(self.input_file)

        # 1. Check if input file exists
        if not os.path.exists(self.input_file):
            self.finished.emit(self.input_file, "", False, "输入文件不存在")
            return

        # 2. Determine output path
        file_dir, file_name = os.path.split(self.input_file)
        base_name, _ = os.path.splitext(file_name)
        
        target_dir = self.output_dir if self.output_dir else file_dir
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                self.finished.emit(self.input_file, "", False, f"无法创建输出目录: {str(e)}")
                return

        output_file = os.path.join(target_dir, f"{base_name}.{self.target_format}")

        # If input and output are the same, reject to avoid overwriting source
        if self.input_file.lower() == output_file.lower():
            self.finished.emit(self.input_file, output_file, False, "输入和输出文件格式相同，已跳过")
            return

        # Never overwrite an existing document silently.
        if os.path.exists(output_file):
            index = 1
            while True:
                candidate = os.path.join(
                    target_dir, f"{base_name}_转换_{index}.{self.target_format}"
                )
                if not os.path.exists(candidate):
                    output_file = candidate
                    break
                index += 1

        # 3. PDF needs a two-step pipeline. Pandoc's direct DOCX -> Typst output
        # can contain absolute Windows image paths, which Typst rejects.
        pdf_engine = None
        if self.target_format == "pdf":
            pdf_engine = find_pdf_engine()
            if not pdf_engine:
                self.finished.emit(
                    self.input_file,
                    output_file,
                    False,
                    "PDF 转换失败：程序未找到 PDF 引擎。请使用包含 Typst 的最新版程序，或安装 Typst 后重启程序。"
                )
                return
            if os.path.basename(pdf_engine).lower() == "typst.exe":
                self.convert_pdf_with_typst(pdf_engine, output_file)
                return

        # Other formats use Pandoc's direct output path.
        cmd = [self.pandoc_path, self.input_file, "-o", output_file]

        # 4. Execute Subprocess
        try:
            # Hide the cmd window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0 # SW_HIDE

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                timeout=600
            )

            if process.returncode == 0 and os.path.isfile(output_file) and os.path.getsize(output_file) > 0:
                self.finished.emit(self.input_file, output_file, True, "转换成功")
            else:
                stderr_text = process.stderr.strip()
                error_msg = stderr_text if stderr_text else "Pandoc 发生未知错误"
                
                # Check for PDF engine missing error and make it friendly
                if self.target_format == "pdf":
                    error_msg = f"PDF 转换失败（引擎：{pdf_engine or '未检测到'}）：{error_msg}"
                elif process.returncode == 0 and not os.path.isfile(output_file):
                    error_msg = "转换失败：Pandoc 未生成输出文件，请检查目标格式和输出目录权限。"

                self.finished.emit(self.input_file, output_file, False, error_msg)

        except subprocess.TimeoutExpired:
            self.finished.emit(self.input_file, output_file, False, "转换超时（限时10分钟）")
        except Exception as e:
            self.finished.emit(self.input_file, output_file, False, f"执行异常: {str(e)}")

    def convert_pdf_with_typst(self, typst_path, output_file):
        """Generate Typst in a local temp tree so extracted images stay relative."""
        try:
            with tempfile.TemporaryDirectory(prefix="pandocflow-") as work_dir:
                typ_file = os.path.join(work_dir, "document.typ")
                media_dir = os.path.join(work_dir, "media")
                pandoc_process = subprocess.run(
                    [self.pandoc_path, self.input_file, "--to=typst", "--extract-media", "media", "-o", "document.typ"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=self.windows_startupinfo(),
                    timeout=600,
                    cwd=work_dir,
                )
                if pandoc_process.returncode != 0 or not os.path.isfile(typ_file):
                    detail = pandoc_process.stderr.strip() or "Pandoc 未生成 Typst 中间文件"
                    self.finished.emit(self.input_file, output_file, False, f"PDF 转换失败（生成 Typst 失败）：{detail}")
                    return

                typst_process = subprocess.run(
                    [typst_path, "compile", "document.typ", output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    startupinfo=self.windows_startupinfo(),
                    timeout=600,
                    cwd=work_dir,
                )
                if typst_process.returncode == 0 and os.path.isfile(output_file) and os.path.getsize(output_file) > 0:
                    self.finished.emit(self.input_file, output_file, True, "转换成功")
                else:
                    detail = typst_process.stderr.strip() or "Typst 未生成 PDF 文件"
                    self.finished.emit(self.input_file, output_file, False, f"PDF 转换失败（Typst）：{detail}")
        except subprocess.TimeoutExpired:
            self.finished.emit(self.input_file, output_file, False, "PDF 转换超时（限时10分钟）")
        except Exception as error:
            self.finished.emit(self.input_file, output_file, False, f"PDF 转换异常：{error}")

    @staticmethod
    def windows_startupinfo():
        if os.name != "nt":
            return None
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        return startupinfo
