from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


def create_image_display_group(window):
    container = QWidget()
    layout = QVBoxLayout()

    layout.addWidget(QLabel("Imagem Original:"))
    window.lbl_img_original = QLabel("Carregue uma imagem...")
    window.lbl_img_original.setAlignment(Qt.AlignCenter)
    window.lbl_img_original.setMinimumSize(400, 300)
    window.lbl_img_original.setObjectName("ImageLabel")
    layout.addWidget(window.lbl_img_original, 1)

    layout.addWidget(QLabel("Pixel Art Gerada:"))
    window.lbl_img_pixel_art = QLabel("Aguardando geração...")
    window.lbl_img_pixel_art.setAlignment(Qt.AlignCenter)
    window.lbl_img_pixel_art.setMinimumSize(400, 300)
    window.lbl_img_pixel_art.setObjectName("ImageLabel")
    layout.addWidget(window.lbl_img_pixel_art, 1)

    container.setLayout(layout)
    return container
