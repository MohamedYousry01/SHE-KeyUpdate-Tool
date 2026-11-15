"""Render the application's own widget tree for layout QA; public demo only."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from she_studio.desktop import Studio, STYLE

app = QApplication([])
QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
QFontDatabase.addApplicationFont("C:/Windows/Fonts/consola.ttf")
app.setStyle("Fusion")
app.setStyleSheet(STYLE)
window = Studio()
window.resize(1360,1260)
window.load_demo()
window.show()
app.processEvents()
folder = Path(__file__).resolve().parents[1]/"docs"/"images"
folder.mkdir(parents=True,exist_ok=True)
window.grab().save(str(folder/"workbench.png"))
print(folder/"workbench.png")
window.close()
