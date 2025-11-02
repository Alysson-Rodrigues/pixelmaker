from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QFormLayout, QSpinBox, QPushButton, QLabel, QListWidget


def create_config_group(window):
    group_box = QGroupBox("2. Definir Escala e Mapas")
    layout = QVBoxLayout()

    form_layout = QFormLayout()
    window.spin_scale_factor = QSpinBox()
    window.spin_scale_factor.setRange(2, 100)
    window.spin_scale_factor.setValue(10)
    window.spin_scale_factor.setSuffix("x")
    window.spin_scale_factor.setEnabled(False)
    window.spin_scale_factor.valueChanged.connect(window._on_scale_changed)
    form_layout.addRow("Fator de Escala:", window.spin_scale_factor)
    layout.addLayout(form_layout)

    window.lbl_required_map_dims = QLabel("Dimensões Requeridas do Mapa: N/A")
    window.lbl_required_map_dims.setStyleSheet("font-weight: bold;")
    layout.addWidget(window.lbl_required_map_dims)
    layout.addSpacing(10)

    window.btn_add_maps = QPushButton("Adicionar Mapas de Segmentação")
    window.btn_add_maps.clicked.connect(window._load_segmentation_maps)
    window.btn_add_maps.setEnabled(False)

    window.lst_maps = QListWidget()
    window.lst_maps.setSelectionMode(QListWidget.MultiSelection)
    window.lst_maps.itemDoubleClicked.connect(window._open_palette_editor)

    window.btn_remove_maps = QPushButton("Remover Selecionados")
    window.btn_remove_maps.clicked.connect(window._remove_selected_maps)
    window.btn_remove_maps.setEnabled(False)

    window.lbl_maps_loaded = QLabel("Nenhum mapa carregado.")
    window.lbl_maps_loaded.setWordWrap(True)

    layout.addWidget(window.btn_add_maps)
    layout.addWidget(window.lst_maps)
    layout.addWidget(window.btn_remove_maps)
    layout.addWidget(window.lbl_maps_loaded)

    group_box.setLayout(layout)
    return group_box
