from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSizePolicy, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

# Robust PIL -> QPixmap converter with multiple fallbacks
def pil_to_qpixmap(pil):
    """Convert a PIL Image to QPixmap reliably.

    Tries PIL.ImageQt first; if not available, falls back to raw bytes -> QImage.
    """
    # ensure PIL image
    try:
        img = pil.convert('RGBA') if hasattr(pil, 'convert') else pil
    except Exception:
        return QPixmap()

    # try ImageQt if available
    try:
        from PIL.ImageQt import ImageQt as _ImageQt
        qim = _ImageQt(img)
        return QPixmap.fromImage(qim)
    except Exception:
        pass

    # fallback: create QImage from raw RGBA / BGRA bytes
    try:
        w, h = img.size
        # try using RGBA8888 format
        data = img.tobytes('raw', 'RGBA')
        try:
            qimg = QImage(data, w, h, QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimg)
        except Exception:
            # convert to BGRA and use ARGB32
            data = img.convert('BGRA').tobytes('raw', 'BGRA')
            qimg = QImage(data, w, h, QImage.Format_ARGB32)
            return QPixmap.fromImage(qimg)
    except Exception:
        return QPixmap()

class PaletteBulkEditorDialog(QDialog):
    def __init__(self, parent, segmentation_maps, initial_texts=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Paletas - Em Massa")
        self.setMinimumSize(900, 600)
        self.parent = parent
        self.segmentation_maps = segmentation_maps or {}
        self.initial_texts = initial_texts or {}

        layout = QVBoxLayout()

        # Scroll area to hold multiple map editors
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.vbox = QVBoxLayout(container)

        # For each subject, create a preview + input
        self.edit_fields = {}  # subject -> QLineEdit

        for subject in sorted(self.segmentation_maps.keys()):
            row = QWidget()
            row_layout = QHBoxLayout(row)

            lbl = QLabel()
            lbl.setFixedSize(200, 150)
            lbl.setAlignment(Qt.AlignCenter)
            try:
                pil = self.segmentation_maps[subject]
                if pil is None:
                    raise ValueError("imagem ausente")
                # force RGBA to avoid ImageQt mode issues
                if hasattr(pil, 'convert'):
                    img = pil.convert('RGBA')
                else:
                    img = pil
                pix = pil_to_qpixmap(img)
                if not pix.isNull():
                    pix = pix.scaled(lbl.width(), lbl.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    lbl.setPixmap(pix)
                else:
                    raise RuntimeError("pixmap vazio")
            except Exception as e:
                # keep readable fallback text and log to console for debugging
                print(f"Warning: não foi possível gerar preview para '{subject}': {e}")
                lbl.setText("(preview não disponível)")

            # input
            le = QLineEdit()
            le.setPlaceholderText("#RRGGBB, #RRGGBB, ...")
            initial = self.initial_texts.get(subject, "")
            le.setText(initial)
            le.setMinimumWidth(400)

            # subject label
            subject_lbl = QLabel(f"{subject}")
            subject_lbl.setFixedWidth(140)

            row_layout.addWidget(lbl)
            row_layout.addWidget(subject_lbl)
            row_layout.addWidget(le)

            self.edit_fields[subject] = le
            self.vbox.addWidget(row)

        self.vbox.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

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
        # Collect texts and call parent to validate/save
        updates = {s: le.text().strip() for s, le in self.edit_fields.items()}
        try:
            # parent will raise Exception on validation error
            self.parent._save_palettes_bulk(updates)
            QMessageBox.information(self, "Sucesso", "Paletas salvas com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Erro ao salvar paletas", str(e))
