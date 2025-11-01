import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image


class PixelMakerWindow(QMainWindow):
    """
    Janela principal do aplicativo Pixelmaker.
    (UI + slots) — sem código de startup.
    """
    def __init__(self):
        super().__init__()
        # Armazena os dados do processo
        self.original_image = None
        self.segmentation_map = None
        self.generated_pixel_art = None
        self.color_palettes = {}
        self.required_map_dims = None # <--- ADICIONE ESTA LINHA

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Pixelmaker v1.0 - Segmented Pixel Art')
        self.setGeometry(100, 100, 1400, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()

        left_panel_layout = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel_layout)

        left_panel_layout.addWidget(self._create_file_loader_group())  # Grupo 1: Original
        left_panel_layout.addWidget(self._create_config_group())       # Grupo 2: Escala e Mapa
        left_panel_layout.addWidget(self._create_palette_group())      # Grupo 3: Paletas
        left_panel_layout.addWidget(self._create_controls_group())     # Grupo 4: Gerar
        left_panel_layout.addStretch()

        right_panel_layout = QVBoxLayout()
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)

        right_panel_layout.addWidget(self._create_image_display_group())

        main_layout.addWidget(left_panel_widget, 1)
        main_layout.addWidget(right_panel_widget, 2)

        self.central_widget.setLayout(main_layout)

    def _create_file_loader_group(self):
        group_box = QGroupBox("1. Carregar Imagem Original")
        layout = QVBoxLayout()

        self.btn_load_original = QPushButton("Carregar Imagem Original (JPG, PNG)")
        self.btn_load_original.clicked.connect(self._load_original_image)
        self.lbl_original_path = QLabel("Nenhum arquivo carregado.")
        self.lbl_original_path.setWordWrap(True)
        self.lbl_original_dims = QLabel("Dimensões: N/A")

        # Botão para limpar arquivos carregados
        self.btn_clear = QPushButton("Limpar Arquivos")
        self.btn_clear.clicked.connect(self._clear_loaded_images)
        self.btn_clear.setEnabled(False)

        layout.addWidget(self.btn_load_original)
        layout.addWidget(self.lbl_original_path)
        layout.addWidget(self.lbl_original_dims)
        layout.addWidget(self.btn_clear)

        group_box.setLayout(layout)
        return group_box

    def _create_config_group(self):
        """
        Cria o QGroupBox para definir a escala e carregar o mapa.
        """
        group_box = QGroupBox("2. Definir Escala e Mapa")
        layout = QVBoxLayout()

        # Layout de formulário para o Fator de Escala
        form_layout = QFormLayout()
        self.spin_scale_factor = QSpinBox()
        self.spin_scale_factor.setRange(2, 100)
        self.spin_scale_factor.setValue(10)
        self.spin_scale_factor.setSuffix("x")
        self.spin_scale_factor.setEnabled(False) # Habilitado após carregar img original
        self.spin_scale_factor.valueChanged.connect(self._on_scale_changed)
        form_layout.addRow("Fator de Escala:", self.spin_scale_factor)
        layout.addLayout(form_layout)

        # Label de feedback para as dimensões do mapa
        self.lbl_required_map_dims = QLabel("Dimensões Requeridas do Mapa: N/A")
        self.lbl_required_map_dims.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_required_map_dims)
        layout.addSpacing(10)

        # Carregamento do Mapa de Segmentação
        self.btn_load_map = QPushButton("Carregar Mapa de Segmentação")
        self.btn_load_map.clicked.connect(self._load_segmentation_map)
        self.btn_load_map.setEnabled(False)
        self.lbl_map_path = QLabel("Nenhum arquivo carregado.")
        self.lbl_map_path.setWordWrap(True)
        self.lbl_map_dims = QLabel("Dimensões: N/A")

        layout.addWidget(self.btn_load_map)
        layout.addWidget(self.lbl_map_path)
        layout.addWidget(self.lbl_map_dims)

        group_box.setLayout(layout)
        return group_box

    def _create_palette_group(self):
        group_box = QGroupBox("3. Definir Paletas por Assunto")
        layout = QVBoxLayout()

        self.txt_palettes = QTextEdit()
        self.txt_palettes.setPlaceholderText(
            "Formato:\nAssunto: #Hex1, #Hex2, #Hex3\n"
            "Exemplo:\n"
            "Pele: #FFDAB9, #E0B088\n"
            "Cabelo: #4A2B1B, #301E13"
        )
        self.txt_palettes.setMinimumHeight(150)
        layout.addWidget(self.txt_palettes)

        self.btn_save_palettes = QPushButton("Processar Paletas")
        self.btn_save_palettes.clicked.connect(self._process_palettes)
        layout.addWidget(self.btn_save_palettes)

        group_box.setLayout(layout)
        return group_box

    def _create_controls_group(self):
        """Cria o QGroupBox para os botões de Ação Final.
        (Versão correta, sem o QSpinBox)
        """
        group_box = QGroupBox("4. Gerar Pixel Art")
        layout = QVBoxLayout()
        
        # Botões de Ação
        self.btn_generate = QPushButton("Gerar Pixel Art")
        self.btn_generate.clicked.connect(self._generate_pixel_art)
        # O botão Gerar deve ser habilitado quando tivermos
        # original, mapa e paletas.
        self.btn_generate.setEnabled(False) 
        layout.addWidget(self.btn_generate)
        
        self.btn_save = QPushButton("Salvar Pixel Art")
        self.btn_save.clicked.connect(self._save_pixel_art)
        self.btn_save.setEnabled(False)
        layout.addWidget(self.btn_save)

        group_box.setLayout(layout)
        return group_box

    def _create_image_display_group(self):
        container = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Imagem Original:"))
        self.lbl_img_original = QLabel("Carregue uma imagem...")
        self.lbl_img_original.setAlignment(Qt.AlignCenter)
        self.lbl_img_original.setMinimumSize(400, 300)
        self.lbl_img_original.setObjectName("ImageLabel")
        layout.addWidget(self.lbl_img_original, 1)

        layout.addWidget(QLabel("Pixel Art Gerada:"))
        self.lbl_img_pixel_art = QLabel("Aguardando geração...")
        self.lbl_img_pixel_art.setAlignment(Qt.AlignCenter)
        self.lbl_img_pixel_art.setMinimumSize(400, 300)
        self.lbl_img_pixel_art.setObjectName("ImageLabel")
        layout.addWidget(self.lbl_img_pixel_art, 1)

        container.setLayout(layout)
        return container

    # --- SLOTS (Lógica de interação) ---

    def _load_original_image_file(self):
        """
        Função auxiliar para carregar APENAS a imagem original.
        Retorna True em sucesso, False em cancel/erro.
        """
        file_filter = "Imagens (*.png *.jpg *.jpeg *.bmp)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem Original", "", file_filter)

        if not file_path:
            return False

        try:
            img = Image.open(file_path).convert('RGBA')
            width, height = img.size

            # Armazena a imagem original
            self.original_image = img

            # Atualiza labels
            self.lbl_original_path.setText(f"Carregado: {file_path}")
            self.lbl_original_dims.setText(f"Dimensões: {width} x {height} px")

            # Exibe no label
            pixmap = QPixmap(file_path)
            self.lbl_img_original.setPixmap(
                pixmap.scaled(
                    self.lbl_img_original.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
            print(f"Sucesso ao carregar original: {file_path}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Erro ao Carregar Imagem",
                                 f"Não foi possível carregar o arquivo:\n{file_path}\n\nErro: {e}")
            self.original_image = None
            self.lbl_original_path.setText("Falha ao carregar.")
            self.lbl_original_dims.setText("Dimensões: N/A")
            self.lbl_img_original.setText("Falha ao carregar.")
            return False

    def _clear_generated_art(self):
        self.generated_pixel_art = None
        try:
            self.lbl_img_pixel_art.setText("Aguardando geração...")
        except Exception:
            pass
        try:
            self.btn_save.setEnabled(False)
        except Exception:
            pass

    def _clear_loaded_images(self):
        self.original_image = None
        self.segmentation_map = None
        try:
            self.lbl_original_path.setText("Nenhum arquivo carregado.")
        except Exception:
            pass
        try:
            self.lbl_map_path.setText("Nenhum arquivo carregado.")
        except Exception:
            pass
        try:
            self.lbl_img_original.clear()
            self.lbl_img_original.setText("Carregue uma imagem...")
        except Exception:
            pass
        self._clear_generated_art()
        try:
            self.btn_clear.setEnabled(False)
        except Exception:
            pass

    def _load_original_image(self):
        print("Abrindo diálogo para imagem original...")
        success = self._load_original_image_file()
        if success:
            # Ao carregar uma imagem original, habilitar controle de escala
            self.spin_scale_factor.setEnabled(True)
            # Reseta mapa de segmentação e arte gerada
            self.segmentation_map = None
            self.lbl_map_path.setText("Nenhum mapa carregado.")
            self.lbl_map_dims.setText("Dimensões: N/A")
            try:
                self.lbl_img_pixel_art.clear()
            except Exception:
                pass
            try:
                self.btn_generate.setEnabled(False)
            except Exception:
                pass
        self._clear_generated_art()

    def _load_segmentation_map(self):
        print("Abrindo diálogo para mapa de segmentação...")
        # Exige que a escala (e portanto required_map_dims) já esteja definida
        if not self.required_map_dims:
            QMessageBox.warning(self, "Escala inválida",
                                "Defina o fator de escala válido e carregue a imagem original antes de carregar o mapa.")
            return

        file_filter = "Imagens (*.png *.jpg *.jpeg *.bmp)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Mapa de Segmentação", "", file_filter)
        if not file_path:
            return

        try:
            img = Image.open(file_path).convert('RGBA')
            w, h = img.size

            # Validação estrita: o mapa deve ter as dimensões exigidas
            if (w, h) != self.required_map_dims:
                QMessageBox.warning(self, "Erro de Dimensões",
                                    f"Dimensões inválidas do mapa.\nEsperado: {self.required_map_dims[0]} x {self.required_map_dims[1]} px\n"
                                    f"Encontrado: {w} x {h} px\n\n"
                                    "Por favor, forneça um mapa com as dimensões corretas.")
                return

            # Armazena e atualiza UI
            self.segmentation_map = img
            self.lbl_map_path.setText(f"Carregado: {file_path}")
            self.lbl_map_dims.setText(f"Dimensões: {w} x {h} px")

            pixmap = QPixmap(file_path)
            self.lbl_img_original.setPixmap(
                pixmap.scaled(
                    self.lbl_img_original.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

            # Habilita geração se tivermos paletas também
            try:
                self.btn_generate.setEnabled(bool(self.original_image and self.segmentation_map and self.color_palettes))
            except Exception:
                pass

            try:
                self.btn_clear.setEnabled(True)
            except Exception:
                pass

        except Exception as e:
            QMessageBox.critical(self, "Erro ao Carregar Imagem",
                                 f"Não foi possível carregar o arquivo:\n{file_path}\n\nErro: {e}")
            self.segmentation_map = None
            self.lbl_map_path.setText("Falha ao carregar.")
            self.lbl_map_dims.setText("Dimensões: N/A")
            try:
                self.lbl_img_original.setText("Falha ao carregar.")
            except Exception:
                pass
        self._clear_generated_art()

    def _on_scale_changed(self, value):
        """Calcula e valida as dimensões de mapa requeridas quando o usuário muda a escala."""
        if not self.original_image:
            self.lbl_required_map_dims.setText("Dimensões Requeridas do Mapa: Carregue a imagem original primeiro.")
            self.btn_load_map.setEnabled(False)
            self.required_map_dims = None
            return

        orig_w, orig_h = self.original_image.size
        if orig_w % value != 0 or orig_h % value != 0:
            self.lbl_required_map_dims.setText("Dimensões Requeridas do Mapa: ESCALA INVÁLIDA")
            self.btn_load_map.setEnabled(False)
            self.required_map_dims = None
            return

        req_w = orig_w // value
        req_h = orig_h // value
        self.required_map_dims = (req_w, req_h)
        self.lbl_required_map_dims.setText(f"Dimensões Requeridas do Mapa: {req_w} x {req_h} px")
        self.btn_load_map.setEnabled(True)

    def _process_palettes(self):
        print("Lógica para processar paletas...")
        pass

    def _generate_pixel_art(self):
        print("Lógica para GERAR...")
        pass

    def _save_pixel_art(self):
        print("Lógica para SALVAR...")
        pass
