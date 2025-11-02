from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton


def create_controls_group(window):
    group_box = QGroupBox("4. Gerar Pixel Art")
    layout = QVBoxLayout()

    window.btn_generate = QPushButton("Gerar Pixel Art")
    window.btn_generate.clicked.connect(window._generate_pixel_art)
    window.btn_generate.setEnabled(False)
    layout.addWidget(window.btn_generate)

    window.btn_save = QPushButton("Salvar Pixel Art")
    window.btn_save.clicked.connect(window._save_pixel_art)
    window.btn_save.setEnabled(False)
    layout.addWidget(window.btn_save)

    group_box.setLayout(layout)
    return group_box
