# Third-party components

Application source is MIT licensed. Dependencies retain their own licenses.
The repository does not reproduce standards documents or vendor logos.

| Component | Purpose | License / source |
|---|---|---|
| PySide6 / Shiboken 6.11.2 and Qt 6 | Desktop interface; dynamically loaded Qt libraries | LGPL v3 option; [Qt for Python source](https://code.qt.io/cgit/pyside/pyside-setup.git/), [Qt source](https://code.qt.io/cgit/qt/), [license information](https://doc.qt.io/qtforpython-6/licenses.html) |
| PyCryptodome 3.23.0 | AES and CMAC | BSD/public-domain components; [source](https://github.com/Legrandin/pycryptodome/tree/v3.23.0); bundled license in `licenses/` |
| Python 3.14 | Bundled interpreter | PSF license; [source and license](https://www.python.org/downloads/source/) |
| PyInstaller 6.22.2 | Executable bootloader | GPL with bootloader exception; [source](https://github.com/pyinstaller/pyinstaller); bundled license in `licenses/` |

No dependency source is modified. Full application source, pinned requirements,
and the build script are provided so recipients can rebuild with compatible
replacement libraries. PyInstaller extracts dynamic libraries into a temporary
directory when the one-file executable runs. Users may inspect, debug, and
modify LGPL components under their licenses; the application imposes no
additional restriction on that use. LGPL and GPL license texts are in `licenses/`.
Font files are not redistributed; Windows supplies fonts at runtime.
