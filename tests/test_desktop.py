import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from PySide6.QtWidgets import QApplication
from she_studio.desktop import Studio, STYLE


def test_desktop_workflow():
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = Studio()
    window.show()
    app.processEvents()
    window.load_demo()
    assert window.outputs["M1"].text().endswith("0141")
    assert window.result is not None
    window.use_generated()
    window.inspect_key.setText(bytes(range(16)).hex())
    window.inspect_messages()
    assert window.inspected.counter == 1
    window.inspect_reveal.setChecked(True)
    assert window.inspected_key.text() == bytes(reversed(range(16))).hex().upper()
    messages = window.result[1]
    window.proof4.setText(messages["M4"].hex())
    window.proof5.setText(messages["M5"].hex())
    window.check_proof()
    assert "PROOF MATCHED" in window.status.text()
    window.counter.setText("2")
    assert window.result is None
    assert all(not widget.text() for widget in window.outputs.values())
    window.load_demo()
    window.clear_session()
    assert not window.fields["new_key"].text()
    assert not window.inspected_key.text()
    window.close()
