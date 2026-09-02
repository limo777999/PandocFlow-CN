import os
import shutil
import PyInstaller.__main__
from src.utils import find_executable

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def configured_executable(env_name, filename):
    """Use a valid explicit path, otherwise fall back to bundled/local discovery."""
    configured = os.environ.get(env_name, "").strip().strip('"')
    if configured:
        # The documentation uses ... as a placeholder; never treat it as a path.
        if "..." in configured:
            print(f"警告：忽略无效的 {env_name}：{configured}")
        elif os.path.isfile(configured):
            return os.path.abspath(configured)
        else:
            raise FileNotFoundError(f"环境变量 {env_name} 指向的文件不存在：{configured}")

    local_candidates = [
        os.path.join(PROJECT_DIR, "engines", filename),
        os.path.join(PROJECT_DIR, "vendor", filename),
    ]
    for path in local_candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)
    return find_executable(filename)

def build():
    print("=== 开始打包 PandocFlow 中文独立版 ===")
    os.chdir(PROJECT_DIR)
    
    # Target entry point
    entry_point = os.path.join("src", "main.py")
    if not os.path.exists(entry_point):
        print(f"错误: 找不到入口文件 {entry_point}")
        return

    pandoc_path = configured_executable("PANDOC_EXE", "pandoc.exe")
    if not pandoc_path or not os.path.isfile(pandoc_path):
        raise FileNotFoundError(
            "未找到 pandoc.exe。请设置 PANDOC_EXE，或将 Pandoc 加入 PATH。"
        )

    # Define build parameters
    args = [
        entry_point,
        "--name=PandocFlow-CN",
        "--onefile",
        "--noconsole",
        "--clean",
        "--paths=src",
        "--icon=src/default.ico",
        "--add-data=src/default.ico;src",
        f"--add-binary={pandoc_path};.",
        "--add-data=THIRD_PARTY_NOTICES.txt;.",
    ]

    # Bundle Typst when available so PDF conversion works on a clean machine.
    typst_path = configured_executable("TYPST_EXE", "typst.exe")
    if typst_path:
        args.append(f"--add-binary={typst_path};.")
        print(f"已内置 PDF 引擎 Typst: {typst_path}")
    else:
        print("警告：未找到 Typst，生成的 exe 仍不能离线转换 PDF。请设置 TYPST_EXE 后重新打包。")

    print(f"正在运行 PyInstaller，参数: {args}")
    try:
        PyInstaller.__main__.run(args)
        print("\n=== 打包完成 ===")
        
        # Verify the file is generated
        exe_path = os.path.join("dist", "PandocFlow-CN.exe")
        if os.path.exists(exe_path):
            print(f"可执行文件成功输出至: {os.path.abspath(exe_path)}")
            # Also copy it to the root of the project workspace for easier user access
            dest_root_path = os.path.join(".", "PandocFlow-CN.exe")
            shutil.copy2(exe_path, dest_root_path)
            print(f"已将可执行文件复制到当前根目录: {os.path.abspath(dest_root_path)}")
        else:
            print("打包失败: 未在 dist/ 目录中检测到生成的 exe 文件。")
            
    except Exception as e:
        print(f"打包过程中遇到异常: {str(e)}")

if __name__ == "__main__":
    build()
