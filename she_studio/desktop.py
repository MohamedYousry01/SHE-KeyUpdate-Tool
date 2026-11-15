"""Windows desktop workbench built with Qt."""
import json
import secrets
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QIcon, QPainter, QColor, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QGridLayout, QFrame,
    QStackedWidget, QPlainTextEdit, QFileDialog, QMessageBox, QScrollArea, QTextBrowser, QSizePolicy)
from .engine import Provisioning, SLOTS, FLAG_NAMES, hex_bytes, integer, generate, inspect_update, verify_proof
from .exchange import render

PORTFOLIO = "https://mohamedyousry01.github.io/Mohamed-Yousry-Portfolio/"
STYLE = """
QWidget { background: #0c1220; color: #e4eaf4; font-family: 'Segoe UI'; font-size: 13px; }
QLabel { background: transparent; }
QFrame#sidebar { background: #101a2b; border-right: 1px solid #243149; }
QLabel#brand { font-size: 21px; font-weight: 700; color: #f2f7ff; }
QLabel#eyebrow { color: #58d9b0; font-size: 11px; font-weight: 700; }
QLabel#title { font-size: 29px; font-weight: 700; }
QLabel#muted { color: #99aac3; }
QLabel#section { font-size: 15px; font-weight: 600; }
QLabel#status { background: #15263a; color: #a7c6e9; border-radius: 8px; padding: 12px; }
QFrame#card { background: #131e30; border: 1px solid #273650; border-radius: 12px; }
QFrame#card QLabel, QFrame#card QCheckBox { background: transparent; }
QPushButton { background: #1c2c43; border: 1px solid #30435f; padding: 10px 15px; border-radius: 7px; font-weight: 600; }
QPushButton:hover { background: #293e59; border-color: #6885a7; }
QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 1px solid #58d9b0; }
QPushButton:disabled { color: #65758b; background: #182334; border-color: #263246; }
QPushButton#primary { background: #60dfb6; border: none; color: #0c2421; }
QPushButton#primary:hover { background: #91f0d1; }
QPushButton#nav { text-align: left; border: none; background: transparent; padding: 13px; color: #a2b1c6; }
QPushButton#nav:checked { background: #20374a; color: #77e7c4; }
QLineEdit, QComboBox, QPlainTextEdit, QTextBrowser { background: #0d1625; border: 1px solid #31415a; border-radius: 7px; padding: 9px; selection-background-color: #326a76; }
QComboBox QAbstractItemView { background: #152237; selection-background-color: #28544e; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QCheckBox::indicator:unchecked { background: #0c1625; border: 1px solid #58708e; border-radius: 3px; }
QCheckBox::indicator:checked { background: #60dfb6; border: 1px solid #60dfb6; border-radius: 3px; }
QCheckBox::indicator:disabled { background: #172236; border: 1px solid #2b3a50; }
QLineEdit { font-family: 'Consolas'; font-size: 12px; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #101a2b; width: 9px; }
QScrollBar::handle:vertical { background: #354861; border-radius: 4px; min-height: 30px; }
QToolTip { color: #e4eaf4; background: #263952; border: 1px solid #54708c; }
"""


def label(text, name=None):
    widget = QLabel(text)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(True)
    return widget


def button(text, action, primary=False):
    widget = QPushButton(text)
    widget.clicked.connect(action)
    if primary:
        widget.setObjectName("primary")
    return widget


def card():
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(12)
    return frame, layout


def entry(placeholder="", secret=False):
    widget = QLineEdit()
    widget.setPlaceholderText(placeholder)
    widget.setFont(QFont("Consolas", 10))
    widget.setMinimumHeight(38)
    widget.setMinimumWidth(0)
    widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
    if secret:
        widget.setEchoMode(QLineEdit.EchoMode.Password)
    return widget


def icon():
    pixmap = QPixmap(64,64)
    pixmap.fill(QColor("#101a2b"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("#60dfb6"))
    painter.setFont(QFont("Segoe UI",28,QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
    painter.end()
    return QIcon(pixmap)


class Studio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHE Key Studio")
        self.setWindowIcon(icon())
        self.resize(1360, 920)
        self.setMinimumSize(1080, 760)
        self.result = None
        self.clipboard_value = None
        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0,0,0,0)
        shell.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(21,30,21,22)
        side.addWidget(label("S / STUDIO", "brand"))
        side.addWidget(label("SHE PROVISIONING", "eyebrow"))
        side.addSpacing(35)
        self.nav = []
        self.pages = QStackedWidget()
        for index, title in enumerate(("01   Generate update", "02   Inspect messages", "03   Verify ECU proof", "04   Developer guide")):
            nav = button(title, lambda checked=False, i=index: self.navigate(i))
            nav.setObjectName("nav")
            nav.setCheckable(True)
            self.nav.append(nav)
            side.addWidget(nav)
        side.addStretch()
        side.addWidget(label("LOCAL BY DESIGN", "eyebrow"))
        side.addWidget(label("No accounts. No telemetry.\nKeys stay in this session.", "muted"))
        side.addSpacing(18)
        side.addWidget(button("Mohamed Yousry  ↗", lambda: QDesktopServices.openUrl(QUrl(PORTFOLIO))))
        side.addWidget(label("v1.0.0  /  Windows", "muted"))
        shell.addWidget(sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(30,26,30,20)
        content.addWidget(self.pages)
        self.status = label("Ready. Start with the public demo vector or enter your device parameters.", "status")
        self.status.setAccessibleName("Operation status")
        content.addWidget(self.status)
        shell.addLayout(content,1)
        self.build_generate()
        self.build_inspect()
        self.build_verify()
        self.build_guide()
        self.navigate(0)

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        for i, nav in enumerate(self.nav):
            nav.setChecked(i == index)

    def page(self, eyebrow, title, description):
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0,0,10,0)
        layout.setSpacing(16)
        layout.addWidget(label(eyebrow,"eyebrow"))
        layout.addWidget(label(title,"title"))
        layout.addWidget(label(description,"muted"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        self.pages.addWidget(scroll)
        return layout

    def build_generate(self):
        layout = self.page("WORKBENCH / GENERATE", "Build a secure key update",
            "Create M1–M3 for your device and M4–M5 as the expected proof of an update.")
        toolbar = QHBoxLayout()
        toolbar.addWidget(button("Load public demo", self.load_demo))
        toolbar.addWidget(button("Clear session", self.clear_session))
        toolbar.addStretch()
        self.show_keys = QCheckBox("Reveal keys")
        self.show_keys.toggled.connect(self.reveal)
        toolbar.addWidget(self.show_keys)
        layout.addLayout(toolbar)
        columns = QHBoxLayout()
        left, form = card()
        form.addWidget(label("01 / Device & key material", "section"))
        self.fields = {}
        for key, title, hint in (("uid","Device UID · 15 bytes","30 hex characters; all zero means wildcard"),
                                 ("auth_key","Authentication key · 16 bytes","Current key in the authorization slot"),
                                 ("new_key","New key · 16 bytes","32 hex characters")):
            form.addWidget(label(title))
            row = QHBoxLayout()
            control = entry(hint, key != "uid")
            control.setAccessibleName(title)
            self.fields[key] = control
            row.addWidget(control,1)
            if key == "new_key":
                row.addWidget(button("Random", lambda: self.fields["new_key"].setText(secrets.token_hex(16).upper())))
            form.addLayout(row)
        grid = QGridLayout()
        self.slot = QComboBox()
        for number, title in SLOTS.items():
            self.slot.addItem(f"0x{number:X}  {title}", number)
        self.slot.setCurrentIndex(3)
        self.auth = QComboBox()
        self.counter = entry("Decimal or 0x-prefixed")
        self.counter.setText("1")
        self.bank = QComboBox()
        self.bank.addItem("Bank 1 · standard",1)
        self.bank.addItem("Bank 2 · device extension",2)
        for n, (title, widget) in enumerate((("Target wire slot",self.slot),("Authorization slot",self.auth),
                                            ("New counter · 28 bits",self.counter),("Key bank",self.bank))):
            grid.addWidget(label(title),n//2*2,n%2)
            grid.addWidget(widget,n//2*2+1,n%2)
        form.addLayout(grid)
        form.addWidget(label("Counter must exceed the device’s stored value. RAM_KEY uses zero. Bank 2 maps wire slots 4–13 to KEY_11–KEY_20.","muted"))
        form.addStretch()
        right, settings = card()
        settings.addWidget(label("02 / Protocol & protection", "section"))
        self.profile = QComboBox()
        self.profile.addItem("SHE · 5 flags (published specification)","she5")
        self.profile.addItem("Extended · 6 flags (VERIFY_ONLY)","extended6")
        settings.addWidget(self.profile)
        settings.addWidget(label("Select the layout required by your target firmware. The profile is not encoded in M1.","muted"))
        self.flags = []
        descriptions = ("Irreversible on hardware: prevent future updates", "Require successful secure boot",
            "Disable key use while a debugger is active", "Use key for CMAC instead of encryption",
            "Reject future wildcard UID updates", "Restrict CMAC usage to verification")
        for name, description in zip(FLAG_NAMES,descriptions):
            check = QCheckBox(name)
            check.setToolTip(description)
            settings.addWidget(check)
            settings.addWidget(label(description,"muted"))
            self.flags.append(check)
        settings.addStretch()
        columns.addWidget(left, 6)
        columns.addWidget(right, 5)
        layout.addLayout(columns)
        layout.addWidget(button("Generate M1–M5  →", self.calculate, True))
        output, results = card()
        results.addWidget(label("03 / Message output", "section"))
        results.addWidget(label("M1–M3 → device    /    M4–M5 → expected response. Generating messages does not provision hardware.","muted"))
        self.outputs = {}
        for name, size in (("M1",16),("M2",32),("M3",16),("M4",32),("M5",16)):
            row = QHBoxLayout()
            row.addWidget(label(f"{name}  /  {size} B"))
            box = entry("Generate an update to see bytes")
            box.setReadOnly(True)
            box.setAccessibleName(name + " output")
            self.outputs[name] = box
            row.addWidget(box,1)
            row.addWidget(button("Copy", lambda checked=False,n=name: self.copy_message(n)))
            results.addLayout(row)
        exports = QHBoxLayout()
        self.export_buttons = []
        for kind, title in (("json","Export JSON"),("c","Export C header"),("text","Export text")):
            control = button(title,lambda checked=False,k=kind: self.export(k))
            control.setEnabled(False)
            exports.addWidget(control)
            self.export_buttons.append(control)
        results.addLayout(exports)
        layout.addWidget(output)
        self.slot.currentIndexChanged.connect(self.slot_changed)
        self.profile.currentIndexChanged.connect(self.profile_changed)
        for widget in (*self.fields.values(),self.counter):
            widget.textChanged.connect(self.invalidate)
        for widget in (self.auth,self.bank):
            widget.currentIndexChanged.connect(self.invalidate)
        for flag in self.flags:
            flag.toggled.connect(self.invalidate)
        self.slot_changed()
        self.profile_changed()

    def slot_changed(self):
        target = self.slot.currentData()
        allowed = {1,target} if target != 3 else {1,2}
        if target == 14:
            allowed = set(range(15)) - {3}
        self.auth.clear()
        for n in sorted(allowed):
            self.auth.addItem(f"0x{n:X}  {SLOTS.get(n,'SECRET_KEY')}",n)
        if target == 14:
            self.counter.setText("0")
            for flag in self.flags:
                flag.setChecked(False)
        elif self.counter.text() == "0":
            self.counter.setText("1")
        self.invalidate()

    def profile_changed(self):
        enabled = self.profile.currentData() == "extended6"
        self.flags[-1].setEnabled(enabled)
        if not enabled:
            self.flags[-1].setChecked(False)
        self.invalidate()

    def reveal(self, checked):
        for key in ("auth_key","new_key"):
            self.fields[key].setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)

    def invalidate(self, *_):
        self.result = None
        for output in self.outputs.values():
            output.clear()
        for control in self.export_buttons:
            control.setEnabled(False)
        self.status.setText("Parameters changed. Generate again to refresh the messages.")

    def request(self):
        width = 6 if self.profile.currentData() == "extended6" else 5
        fid = sum(int(flag.isChecked()) << (width-1-i) for i,flag in enumerate(self.flags[:width]))
        return Provisioning.from_dict({**{k:v.text() for k,v in self.fields.items()},
            "slot":self.slot.currentData(), "auth_slot":self.auth.currentData(),
            "counter":self.counter.text(), "flags":fid, "profile":self.profile.currentData(),
            "bank":self.bank.currentData()})

    def calculate(self):
        self.invalidate()
        try:
            request = self.request()
            messages = generate(request)
            self.result = (request,messages)
            for name, value in messages.items():
                self.outputs[name].setText(value.hex().upper())
            for control in self.export_buttons:
                control.setEnabled(True)
            notes = ["Generated 112 bytes. No hardware was changed."]
            if not any(request.uid):
                notes.append("Wildcard UID: acceptance depends on the device’s stored policy.")
            if request.flags & (1 << ((6 if request.profile == 'extended6' else 5)-1)):
                notes.append("WRITE_PROTECTION will permanently lock the slot if applied.")
            self.status.setText(" ".join(notes))
        except ValueError as exc:
            self.status.setText(str(exc))

    def load_demo(self):
        self.profile.setCurrentIndex(0)
        self.bank.setCurrentIndex(0)
        self.slot.setCurrentIndex(3)
        self.auth.setCurrentIndex(0)
        self.counter.setText("1")
        for flag in self.flags:
            flag.setChecked(False)
        self.fields["uid"].setText("00"*14+"01")
        self.fields["auth_key"].setText(bytes(range(16)).hex().upper())
        self.fields["new_key"].setText(bytes(reversed(range(16))).hex().upper())
        self.calculate()
        self.status.setText("PUBLIC DEMO ONLY · Known test keys loaded. Replace both keys before real provisioning.")

    def clear_session(self):
        for widget in self.fields.values():
            widget.clear()
        self.show_keys.setChecked(False)
        self.inspect_input.clear()
        self.inspect_key.clear()
        self.inspected = None
        self.inspected_key.clear()
        self.inspect_reveal.setChecked(False)
        self.inspect_output.clear()
        self.proof4.clear()
        self.proof5.clear()
        self.invalidate()
        self.clear_clipboard()
        self.status.setText("Session fields cleared. Python/Qt cannot guarantee erasure of memory copies.")

    def copy_message(self,name):
        if not self.result:
            self.status.setText("Generate messages before copying.")
            return
        self.clipboard_value = self.result[1][name].hex().upper()
        QApplication.clipboard().setText(self.clipboard_value)
        QTimer.singleShot(30000,self.clear_clipboard)
        self.status.setText(f"{name} copied. Clipboard clears after 30 seconds if it still contains this value.")

    def clear_clipboard(self):
        if self.clipboard_value and QApplication.clipboard().text() == self.clipboard_value:
            QApplication.clipboard().clear()
        self.clipboard_value = None

    def export(self,kind):
        if not self.result:
            return
        suffix = {"json":"json","c":"h","text":"txt"}[kind]
        path,_ = QFileDialog.getSaveFileName(self,"Export message bundle",f"she_update.{suffix}",f"Message export (*.{suffix})")
        if not path:
            return
        try:
            Path(path).write_text(render(*self.result,kind),encoding="utf-8")
            self.status.setText("Exported message bundle. Plaintext keys and derived keys are excluded.")
        except OSError as exc:
            self.status.setText(f"Export failed: {exc}")

    def build_inspect(self):
        layout = self.page("WORKBENCH / INSPECT", "Understand an update bundle",
            "Authenticate M3 before decrypting M2. The JSON profile and bank must match your firmware.")
        panel, body = card()
        body.addWidget(label("Authentication key · 16 bytes"))
        self.inspect_key = entry("32 hex characters",True)
        body.addWidget(self.inspect_key)
        body.addWidget(label("Paste exported JSON with profile, bank, and messages M1–M3"))
        self.inspect_input = QPlainTextEdit()
        self.inspect_input.setPlaceholderText('{"profile":"she5", "bank":1, "messages":{"M1":"…", "M2":"…", "M3":"…"}}')
        self.inspect_input.setMinimumHeight(170)
        body.addWidget(self.inspect_input)
        actions = QHBoxLayout()
        actions.addWidget(button("Import JSON",self.import_bundle))
        actions.addWidget(button("Use generated bundle",self.use_generated))
        actions.addWidget(button("Authenticate & inspect",self.inspect_messages,True))
        body.addLayout(actions)
        self.inspect_output = QPlainTextEdit()
        self.inspect_output.setReadOnly(True)
        self.inspect_output.setMinimumHeight(170)
        body.addWidget(self.inspect_output)
        self.inspected = None
        self.inspect_reveal = QCheckBox("Reveal authenticated new key in this session")
        self.inspected_key = entry("Authenticated key remains hidden",True)
        self.inspected_key.setReadOnly(True)
        self.inspect_reveal.toggled.connect(self.reveal_inspected)
        body.addWidget(self.inspect_reveal)
        body.addWidget(self.inspected_key)
        self.inspect_key.textChanged.connect(self.invalidate_inspection)
        self.inspect_input.textChanged.connect(self.invalidate_inspection)
        layout.addWidget(panel)
        layout.addStretch()

    def invalidate_inspection(self):
        self.inspected = None
        self.inspected_key.clear()
        self.inspect_reveal.setChecked(False)
        self.inspect_output.clear()

    def reveal_inspected(self, checked):
        self.inspected_key.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        self.inspected_key.setText(self.inspected.new_key.hex().upper() if self.inspected and checked else "")

    def import_bundle(self):
        path,_ = QFileDialog.getOpenFileName(self,"Open message bundle","","JSON (*.json)")
        if path:
            try:
                self.inspect_input.setPlainText(Path(path).read_text(encoding="utf-8-sig"))
            except OSError as exc:
                self.status.setText(str(exc))

    def use_generated(self):
        if self.result:
            self.inspect_input.setPlainText(render(*self.result))
        else:
            self.status.setText("Generate a bundle first.")

    def inspect_messages(self):
        self.invalidate_inspection()
        try:
            data = json.loads(self.inspect_input.toPlainText())
            messages = data["messages"]
            req = inspect_update(hex_bytes(self.inspect_key.text(),16,"Authentication key"),
                *(hex_bytes(messages[k],n,k) for k,n in (("M1",16),("M2",32),("M3",16))),
                data["profile"],integer(data["bank"],"bank"))
            self.inspected = req
            self.inspect_output.setPlainText(f"M3 AUTHENTICATED\nUID: {req.uid.hex().upper()}\nTarget: 0x{req.slot:X}\nAuthorization: 0x{req.auth_slot:X}\nCounter: {req.counter}\nFlags: {req.flags}\nProfile: {req.profile}\nBank: {req.bank}\nNew key: hidden")
            self.status.setText("Message integrity verified. This does not prove the device accepted the update.")
        except (ValueError,KeyError,TypeError) as exc:
            self.status.setText(f"Inspection rejected: {exc}")

    def build_verify(self):
        layout = self.page("WORKBENCH / VERIFY", "Check the device’s response",
            "Generate the exact update first, then paste the M4 and M5 returned by your ECU.")
        panel, body = card()
        body.addWidget(label("Received M4 · 32 bytes"))
        self.proof4 = entry("64 hex characters")
        body.addWidget(self.proof4)
        body.addWidget(label("Received M5 · 16 bytes"))
        self.proof5 = entry("32 hex characters")
        body.addWidget(self.proof5)
        body.addWidget(button("Verify received proof", self.check_proof,True))
        body.addWidget(label("Both messages must match the current request. A pasted expected proof is only a local self-check; it is not evidence of a hardware update.","muted"))
        layout.addWidget(panel)
        layout.addStretch()

    def check_proof(self):
        try:
            if not self.result:
                raise ValueError("Generate the matching update first.")
            valid = verify_proof(self.result[0],hex_bytes(self.proof4.text(),32,"M4"),hex_bytes(self.proof5.text(),16,"M5"))
            self.status.setText("PROOF MATCHED · Received M4 and M5 match this update." if valid else "PROOF FAILED · Response does not match this update.")
        except ValueError as exc:
            self.status.setText(str(exc))

    def build_guide(self):
        layout = self.page("REFERENCE / QUICK START", "From key material to device proof",
            "A practical offline workflow for embedded software developers.")
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml('''<h2>1. Start with a public demo</h2><p>Choose Generate update → Load public demo. The known vector produces all five messages. These public keys are only for learning.</p>
<h2>2. Set the target</h2><p>Read your device’s 120-bit UID and current slot counter using your approved tooling. Select the target wire ID and a valid authorization slot. Supply the current authentication key and a fresh 128-bit new key. Random uses the operating system’s cryptographic generator.</p>
<h2>3. Match your firmware</h2><p><b>she5:</b> WRITE, BOOT, DEBUG, USAGE, WILDCARD (95 reserved zero bits). <b>extended6:</b> the same flags followed by VERIFY_ONLY (94 reserved zero bits). Confirm the latter extension in your device manual. Bank 2 uses extension constants 0181 / 0182 and maps KEY_11–20 to wire IDs 4–13.</p>
<h2>4. Generate and integrate</h2><p>Transfer M1 (16 bytes), M2 (32 bytes), and M3 (16 bytes) through your firmware’s CMD_LOAD_KEY interface. C headers use standard uint8_t arrays. JSON/text exports exclude plaintext keys. No transport, UDS service, driver, or ECU access is built in.</p>
<h2>5. Verify the ECU</h2><p>Paste the actual response into Verify ECU proof. Compare both M4 (32 bytes) and M5 (16 bytes). Record a new counter only after the device confirms success.</p>
<h2>Protection flags matter</h2><p>WRITE_PROTECTION can permanently lock a physical slot. WILDCARD=1 disables future wildcard updates; it does not enable them. RAM_KEY requires zero flags and counter. The application cannot see stored flags, counter, boot state, or memory failures.</p>
<h2>Session privacy</h2><p>No network calls, automatic saves, logs, or key history. Key fields are masked. Explicit exports contain encrypted provisioning material and should still be protected. Clear session clears fields; Python and Qt cannot promise memory zeroization. Clipboard managers may retain copied bytes.</p>
<h2>About</h2><p>SHE Key Studio 1.0.0 · Mohamed Yousry<br><a href="'''+PORTFOLIO+'''">Portfolio ↗</a></p>
<p>See the repository documentation for the protocol, CLI, tests, build process, and GitHub releases.</p>''')
        layout.addWidget(browser,1)

    def closeEvent(self,event):
        self.clear_clipboard()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = Studio()
    if "--self-check" in sys.argv:
        # Exercise the frozen Qt runtime without opening a window or writing secrets.
        window.load_demo()
        assert window.result is not None
        assert window.outputs["M3"].text() == "B9D745E5ACE7D41860BC63C2B9F5BB46"
        request, messages = window.result
        assert inspect_update(request.auth_key, messages["M1"], messages["M2"], messages["M3"]) == request
        assert verify_proof(request, messages["M4"], messages["M5"])
        window.clear_session()
        window.close()
        sys.exit(0)
    window.show()
    sys.exit(app.exec())
