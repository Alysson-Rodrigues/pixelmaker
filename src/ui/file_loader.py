from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image


def create_file_loader_group(window):
    group_box = QGroupBox("1. Carregar Imagem Original")
    layout = QVBoxLayout()

    window.btn_load_original = QPushButton("Carregar Imagem Original (JPG, PNG)")
    window.btn_load_original.clicked.connect(window._load_original_image)
    window.lbl_original_path = QLabel("Nenhum arquivo carregado.")
    window.lbl_original_path.setWordWrap(True)
    window.lbl_original_dims = QLabel("Dimensões: N/A")

    window.btn_clear = QPushButton("Limpar Arquivos")
    window.btn_clear.clicked.connect(window._clear_loaded_images)
    window.btn_clear.setEnabled(False)

    layout.addWidget(window.btn_load_original)
    layout.addWidget(window.lbl_original_path)
    layout.addWidget(window.lbl_original_dims)
    layout.addWidget(window.btn_clear)

    group_box.setLayout(layout)
    return group_box
