import os
import shutil
import subprocess
import sys

def executable_candidates(name):
    """Return bundled, portable, PATH and common Windows locations."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.extend([
            os.path.join(sys._MEIPASS, name),
            os.path.join(sys._MEIPASS, "engines", name),
        ])
    base = os.path.dirname(os.path.abspath(__file__))
    candidates.extend([
        os.path.join(base, os.pardir, "vendor", name),
        os.path.join(base, os.pardir, "engines", name),
    ])
    found = shutil.which(name)
    if found:
        candidates.append(found)
    for root in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("APPDATA", ""), r"C:\Program Files", r"C:\Program Files (x86)"):
        if root:
            candidates.extend([
                os.path.join(root, "Typst", name),
                os.path.join(root, "wkhtmltopdf", "bin", name),
                os.path.join(root, "MiKTeX", "miktex", "bin", name),
            ])
    return list(dict.fromkeys(os.path.abspath(path) for path in candidates if path))

def find_executable(name):
    for path in executable_candidates(name):
        if os.path.isfile(path):
            return path
    return None

def find_pdf_engine():
    """Find a PDF engine supported by the bundled/current Pandoc."""
    for name in ("typst.exe", "wkhtmltopdf.exe", "pdflatex.exe"):
        path = find_executable(name)
        if path:
            return path
    return None

def find_pandoc():
    """
    Search for pandoc executable in system PATH and common installation directories on Windows.
    Returns:
        tuple: (executable_path, version_string) or (None, None)
    """
    # 1. Prefer the Pandoc bundled by PyInstaller so the EXE works offline.
    bundled_path = find_executable("pandoc.exe")
    if bundled_path:
        version = get_pandoc_version(bundled_path)
        if version:
            return bundled_path, version

    # 2. Search beside the source tree for portable/development runs.
    portable_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "vendor", "pandoc.exe")
    )
    if os.path.exists(portable_path):
        version = get_pandoc_version(portable_path)
        if version:
            return portable_path, version

    # 3. Search in PATH
    pandoc_path = shutil.which("pandoc")
    if pandoc_path:
        version = get_pandoc_version(pandoc_path)
        if version:
            return pandoc_path, version

    # 4. Check common Windows install paths
    possible_paths = [
        r"C:\Program Files\Pandoc\pandoc.exe",
        r"C:\Program Files (x86)\Pandoc\pandoc.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Pandoc\pandoc.exe"),
        os.path.join(os.environ.get("APPDATA", ""), r"Pandoc\pandoc.exe"),
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            version = get_pandoc_version(path)
            if version:
                return path, version

    return None, None

def get_pandoc_version(executable_path):
    """
    Run pandoc --version to get its version details.
    """
    try:
        # Use subprocess.run and hide window on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0 # SW_HIDE

        result = subprocess.run(
            [executable_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            startupinfo=startupinfo,
            timeout=2
        )
        if result.returncode == 0:
            # First line is usually "pandoc x.y.z..."
            lines = result.stdout.strip().split('\n')
            if lines:
                return lines[0].strip()
    except Exception:
        pass
    return None
