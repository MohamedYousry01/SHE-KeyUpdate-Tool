"""Build standalone Windows executables and a portable release archive."""
import hashlib
import importlib.metadata
import os
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != "win32":
        raise SystemExit("Build on 64-bit Windows.")
    os.chdir(ROOT)
    # Avoid collecting unrelated native DLLs from other applications on PATH.
    build_env = os.environ.copy()
    windows = Path(os.environ.get("SystemRoot", "C:/Windows"))
    build_env["PATH"] = os.pathsep.join((sys.base_prefix, str(Path(sys.executable).parent),
                                        str(windows/"System32"), str(windows)))
    output = ROOT/"downloads"
    output.mkdir(exist_ok=True)
    work = ROOT/"build"
    work.mkdir(exist_ok=True)
    image = Image.new("RGBA",(256,256),"#101a2b")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18,18,238,238),radius=52,fill="#60dfb6")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf",160)
    draw.text((128,120),"S",font=font,anchor="mm",fill="#101a2b")
    ico = work/"studio.ico"
    image.save(ico,sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    subprocess.run([sys.executable,"-m","pytest","-q","-p","no:cacheprovider","--basetemp",str(work/"test-temp")],check=True)
    for name, launcher, gui in (("SHE-Key-Studio","launch.py",True),("she-key","cli_launch.py",False)):
        args = [sys.executable,"-m","PyInstaller","--noconfirm","--clean","--onefile",
                "--name",name,"--distpath",str(output),"--workpath",str(work/"freeze"),
                "--specpath",str(work),"--icon",str(ico)]
        if gui:
            args += ["--windowed", "--exclude-module","PySide6.QtWebEngineCore",
                     "--exclude-module","PySide6.QtQml","--exclude-module","PySide6.QtQuick"]
        args += [launcher]
        subprocess.run(args,check=True,env=build_env)
    smoke_env = build_env.copy()
    smoke_env["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run([str(output/"SHE-Key-Studio.exe"),"--self-check"],
                   check=True,timeout=60,env=smoke_env)
    print("Frozen desktop Qt/generation/inspection/proof self-check passed.")
    license_dir = ROOT/"licenses"
    license_dir.mkdir(exist_ok=True)
    for package in ("pycryptodome", "pyinstaller"):
        distribution = importlib.metadata.distribution(package)
        for file in distribution.files or []:
            if file.name.lower().startswith(("license", "copying")) and file.locate().is_file():
                shutil.copyfile(file.locate(),license_dir/(package+"-"+file.name))
    sums = []
    for file in sorted(output.glob("*.exe")):
        sums.append(f"{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}")
    (output/"SHA256SUMS.txt").write_text("\n".join(sums)+"\n",encoding="utf-8")
    staging = work/"portable"
    staging.mkdir(exist_ok=True)
    for file in (*output.glob("*.exe"),output/"SHA256SUMS.txt",ROOT/"LICENSE",ROOT/"THIRD_PARTY_NOTICES.md"):
        shutil.copy2(file,staging/file.name)
    shutil.copytree(ROOT/"licenses",staging/"licenses",dirs_exist_ok=True)
    shutil.copytree(ROOT/"docs",staging/"docs",dirs_exist_ok=True)
    shutil.copytree(ROOT/"examples",staging/"examples",dirs_exist_ok=True)
    shutil.copyfile(ROOT/"docs"/"USER_GUIDE.md",staging/"START_HERE.md")
    release = ROOT/"release"
    release.mkdir(exist_ok=True)
    archive = shutil.make_archive(str(release/"SHE-Key-Studio-1.0.0-Windows-x64"),"zip",staging)
    print(f"Portable release: {archive}")
    print("\n".join(sums))


if __name__ == "__main__":
    main()
