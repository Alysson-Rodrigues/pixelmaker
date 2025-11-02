from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QScrollArea, QWidget, QLineEdit, QLabel, QPushButton


def create_palette_group(window):
    group_box = QGroupBox("3. Definir Paletas por Mapa")
    outer_layout = QVBoxLayout()

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_content = QWidget()
    window.palettes_layout = QVBoxLayout(scroll_content)
    window.palettes_layout.addStretch()
    scroll_area.setWidget(scroll_content)

    outer_layout.addWidget(scroll_area, 1)

    window.btn_process_palettes = QPushButton("Processar Paletas")
    window.btn_process_palettes.clicked.connect(window._process_palettes)
    window.btn_process_palettes.setEnabled(False)
    # Botão para abrir editor grande de paletas (preview + inputs)
    window.btn_edit_palettes = QPushButton("Editar Paletas")
    window.btn_edit_palettes.clicked.connect(window._open_palette_bulk_editor)
    window.btn_edit_palettes.setEnabled(False)
    outer_layout.addWidget(window.btn_edit_palettes)
    outer_layout.addWidget(window.btn_process_palettes)

    group_box.setLayout(outer_layout)
    return group_box
