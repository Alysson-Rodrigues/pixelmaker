from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

def pil_to_qpixmap(pil):
    """Convert a PIL Image to QPixmap reliably.

    Tries PIL.ImageQt first; if not available, falls back to raw bytes -> QImage.
    """
    try:
        img = pil.convert('RGBA') if hasattr(pil, 'convert') else pil
    except Exception:
        return QPixmap()

    try:
        from PIL.ImageQt import ImageQt as _ImageQt
        qim = _ImageQt(img)
        return QPixmap.fromImage(qim)
    except Exception:
        pass

    try:
        w, h = img.size
        data = img.tobytes('raw', 'RGBA')
        try:
            qimg = QImage(data, w, h, QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimg)
        except Exception:
            data = img.convert('BGRA').tobytes('raw', 'BGRA')
            qimg = QImage(data, w, h, QImage.Format_ARGB32)
            return QPixmap.fromImage(qimg)
    except Exception:
        return QPixmap()


class PaletteEditorDialog(QDialog):
    def __init__(self, parent, subject_name, pil_image, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Paleta - {subject_name}")
        self.setMinimumSize(500, 400)
        self.subject_name = subject_name
        self.parent = parent

        layout = QVBoxLayout()

        # Preview (scaled)
        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if pil_image is not None:
            try:
                # ensure RGBA to avoid ImageQt mode issues
                if hasattr(pil_image, 'convert'):
                    img = pil_image.convert('RGBA')
                else:
                    img = pil_image
                pix = pil_to_qpixmap(img)
                if not pix.isNull():
                    self.lbl_preview.setPixmap(pix.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                print(f"Warning: não foi possível gerar preview no editor simples para '{subject_name}': {e}")
                # fallback: no pixmap
                pass

        # Scroll area for preview in case of large content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        v = QVBoxLayout(content)
        v.addWidget(self.lbl_preview)
        scroll.setWidget(content)

        layout.addWidget(scroll)

        # Input for palette
        self.input_palette = QLineEdit()
        self.input_palette.setPlaceholderText("Ex: #FFDAB9, #E0B088, #C18866")
        self.input_palette.setText(initial_text)
        layout.addWidget(QLabel("Paleta (separar por vírgula):"))
        layout.addWidget(self.input_palette)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Salvar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_save(self):
        text = self.input_palette.text().strip()
        # let the parent handle validation/parse
        try:
            self.parent._save_palette_for_subject(self.subject_name, text)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Erro ao Salvar", str(e))
