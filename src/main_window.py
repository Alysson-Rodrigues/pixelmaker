"""Main window UI for PixelMaker (PyQt5).

Moved into `src` package to improve project structure.
This module exposes `PixelMakerWindow` class only (no top-level execution).
"""

import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

from src.palette_processor import parse_palette_line
from src.ui import (
    create_file_loader_group,
    create_config_group,
    create_palette_group,
    create_controls_group,
    create_image_display_group,
)
# import the processing algorithm
from src.art_processor import generate_pixel_art


# helper: convert PIL image to QPixmap (robust fallback)
def pil_to_qpixmap(pil):
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
        qimg = QImage(data, w, h, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimg)
    except Exception:
        try:
            data = img.convert('BGRA').tobytes('raw', 'BGRA')
            qimg = QImage(data, w, h, QImage.Format_ARGB32)
            return QPixmap.fromImage(qimg)
        except Exception:
            return QPixmap()


class PixelMakerWindow(QMainWindow):
    """Janela principal do aplicativo Pixelmaker.

    Implementação consolidada: múltiplos mapas de segmentação e paletas dinâmicas.
    """

    def __init__(self):
        super().__init__()

        # Dados do processo
        self.original_image = None  # PIL.Image
        self.segmentation_maps = {}  # {subject_name: PIL.Image}
        self.palette_inputs = {}  # {subject_name: QLineEdit}
        self.color_palettes = {}  # {subject_name: ["#RRGGBB", ...]}
        self.generated_pixel_art = None
        self.required_map_dims = None  # (w, h) in pixels

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

        left_panel_layout.addWidget(create_file_loader_group(self))
        left_panel_layout.addWidget(create_config_group(self))
        left_panel_layout.addWidget(create_palette_group(self))
        left_panel_layout.addWidget(create_controls_group(self))
        left_panel_layout.addStretch()

        right_panel_layout = QVBoxLayout()
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)

        right_panel_layout.addWidget(create_image_display_group(self))

        main_layout.addWidget(left_panel_widget, 1)
        main_layout.addWidget(right_panel_widget, 2)

        self.central_widget.setLayout(main_layout)

    

    # --- Helpers / slots ---
    def _clear_palette_widgets(self):
        # Remove widgets added to palettes_layout except the final stretch
        while self.palettes_layout.count() > 0:
            item = self.palettes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.palettes_layout.addStretch()
        self.palette_inputs.clear()

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
        self.segmentation_maps.clear()
        self._clear_palette_widgets()
        try:
            self.lbl_original_path.setText("Nenhum arquivo carregado.")
        except Exception:
            pass
        try:
            self.lbl_maps_loaded.setText("Nenhum mapa carregado.")
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

    def _load_original_image_file(self):
        file_filter = "Imagens (*.png *.jpg *.jpeg *.bmp)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem Original", "", file_filter)
        if not file_path:
            return None
        try:
            img = Image.open(file_path).convert('RGBA')
            return file_path, img
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Carregar Imagem",
                                 f"Não foi possível carregar o arquivo:\n{file_path}\n\nErro: {e}")
            return None

    def _load_original_image(self):
        print("Abrindo diálogo para imagem original...")
        res = self._load_original_image_file()
        if not res:
            return
        file_path, img = res
        width, height = img.size
        self.original_image = img
        self.lbl_original_path.setText(f"Carregado: {file_path}")
        self.lbl_original_dims.setText(f"Dimensões: {width} x {height} px")

        pixmap = QPixmap(file_path)
        self.lbl_img_original.setPixmap(
            pixmap.scaled(self.lbl_img_original.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        self.spin_scale_factor.setEnabled(True)
        self.required_map_dims = None
        self.btn_clear.setEnabled(True)
        self._clear_generated_art()

    def _load_segmentation_maps(self):
        print("Abrindo diálogo para múltiplos mapas de segmentação...")
        if not self.required_map_dims:
            QMessageBox.warning(self, "Escala inválida",
                                "Defina o fator de escala válido e carregue a imagem original antes de carregar os mapas.")
            return

        file_filter = "Imagens (*.png *.jpg *.jpeg *.bmp)"
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar Mapas de Segmentação", "", file_filter)
        if not file_paths:
            return

    # Não limpar mapas existentes: vamos adicionar incrementalmente
    # A arte gerada será limpa mais abaixo se houver mudanças

        errors = []
        loaded = {}
        req_w, req_h = self.required_map_dims

        for file_path in file_paths:
            try:
                img = Image.open(file_path).convert('RGBA')
                w, h = img.size
                if (w, h) != (req_w, req_h):
                    errors.append(f"{os.path.basename(file_path)}: Dimensões erradas (Esperado {req_w}x{req_h}, Encontrado {w}x{h})")
                    continue
                subject_name = os.path.splitext(os.path.basename(file_path))[0]
                if subject_name in self.segmentation_maps or subject_name in loaded:
                    errors.append(f"{os.path.basename(file_path)}: Nome duplicado ('{subject_name}'). Renomeie o arquivo ou remova o já existente.")
                    continue
                loaded[subject_name] = img
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: Erro ao ler ({e})")

        if errors:
            QMessageBox.warning(self, "Erros ao Carregar Mapas",
                                "Alguns mapas não puderam ser carregados:\n\n" + "\n".join(errors))

        if not loaded:
            # nada novo carregado
            if not self.segmentation_maps:
                self.lbl_maps_loaded.setText("Nenhum mapa carregado.")
            return

        # Adiciona os novos mapas ao dicionário existente
        self.segmentation_maps.update(loaded)
        self.lbl_maps_loaded.setText(f"{len(self.segmentation_maps)} mapas carregados.")
        self.btn_clear.setEnabled(True)
        self.btn_process_palettes.setEnabled(True)
        self._update_palette_widgets()
        # Limpa arte gerada pois a seleção mudou
        self._clear_generated_art()

    def _update_palette_widgets(self):
        # Clear existing small palette widgets; we now use a single bulk editor dialog
        self._clear_palette_widgets()

        # Show a short instruction in the palettes area
        try:
            instr = QLabel("Use 'Editar Paletas' para definir/editar as paletas dos mapas carregados.")
            self.palettes_layout.insertWidget(self.palettes_layout.count() - 1, instr)
        except Exception:
            pass
        # Atualiza a lista de mapas (se o widget existir)
        try:
            self.lst_maps.clear()
            for subject_name in sorted(self.segmentation_maps.keys()):
                self.lst_maps.addItem(subject_name)
            # Habilitar botão de remover e o editor de paletas se houver mapas
            self.btn_remove_maps.setEnabled(len(self.segmentation_maps) > 0)
            try:
                self.btn_edit_palettes.setEnabled(len(self.segmentation_maps) > 0)
            except Exception:
                pass
        except Exception:
            pass

    def _open_palette_editor(self, item):
        """Abre o diálogo de edição de paleta para o mapa selecionado (duplo-clique)."""
        try:
            subject_name = item.text()
        except Exception:
            return

        img = self.segmentation_maps.get(subject_name)
        # Preenche texto inicial a partir da paleta já processada ou do QLineEdit existente
        initial = ""
        if subject_name in self.color_palettes:
            initial = ", ".join(self.color_palettes[subject_name])
        else:
            # check if there's a QLineEdit present
            le = self.palette_inputs.get(subject_name)
            if le:
                initial = le.text()

        from src.ui.palette_editor import PaletteEditorDialog
        dlg = PaletteEditorDialog(self, subject_name, img, initial_text=initial)
        dlg.exec_()

    def _save_palette_for_subject(self, subject_name, text):
        """Save palette text for a subject, update inputs and parsed palettes.

        Raises Exception on invalid palette format.
        """
        # validate/parse using existing parser
        try:
            colors = parse_palette_line(text)
        except Exception as e:
            raise Exception(f"Formato inválido: {e}")

        if not colors:
            raise Exception("A paleta está vazia ou em formato inválido.")

        # Update stored palettes and the visible QLineEdit if exists
        self.color_palettes[subject_name] = colors
        le = self.palette_inputs.get(subject_name)
        if le:
            le.setText(", ".join(colors))

        # enable generate button if all conditions met
        try:
            self.btn_generate.setEnabled(bool(self.original_image and self.segmentation_maps and self.color_palettes))
        except Exception:
            pass

    def _open_palette_bulk_editor(self):
        """Abre o editor em massa para todas as paletas dos mapas carregados."""
        # Prepare initial texts from either processed palettes or current QLineEdits
        initial = {}
        for subject in sorted(self.segmentation_maps.keys()):
            if subject in self.color_palettes:
                initial[subject] = ", ".join(self.color_palettes[subject])
            else:
                le = self.palette_inputs.get(subject)
                initial[subject] = le.text() if le else ""

        from src.ui.palette_bulk_editor import PaletteBulkEditorDialog
        dlg = PaletteBulkEditorDialog(self, self.segmentation_maps, initial_texts=initial)
        dlg.exec_()

    def _save_palettes_bulk(self, updates: dict):
        """Validates and saves multiple palette texts at once.

        updates: dict mapping subject_name -> palette_text
        Raises Exception on first validation error (message includes subject).
        """
        errors = []
        parsed = {}
        for subject, text in updates.items():
            try:
                colors = parse_palette_line(text)
                if not colors:
                    errors.append(f"{subject}: paleta vazia ou inválida.")
                else:
                    parsed[subject] = colors
            except Exception as e:
                errors.append(f"{subject}: {e}")

        if errors:
            # raise a single exception with details
            raise Exception("\n".join(errors))

        # Apply parsed palettes
        for subject, colors in parsed.items():
            self.color_palettes[subject] = colors
            le = self.palette_inputs.get(subject)
            if le:
                le.setText(", ".join(colors))

        # update generate button status
        try:
            self.btn_generate.setEnabled(bool(self.original_image and self.segmentation_maps and self.color_palettes))
        except Exception:
            pass

    def _on_scale_changed(self, value):
        # Try to compute original dims; fall back to label parsing
        if not self.original_image:
            import re
            txt = self.lbl_original_dims.text() if hasattr(self, 'lbl_original_dims') else ''
            m = re.search(r"(\d+)\s*x\s*(\d+)", txt)
            if not m:
                self.lbl_required_map_dims.setText("Dimensões Requeridas do Mapa: Carregue a imagem original primeiro.")
                try:
                    self.btn_add_maps.setEnabled(False)
                except Exception:
                    pass
                self.required_map_dims = None
                return
            orig_w, orig_h = int(m.group(1)), int(m.group(2))
        else:
            orig_w, orig_h = self.original_image.size

        if orig_w % value != 0 or orig_h % value != 0:
            self.lbl_required_map_dims.setText(f"Dimensões Requeridas do Mapa: ESCALA INVÁLIDA — imagem {orig_w}x{orig_h} não divisível por {value}.")
            try:
                self.btn_add_maps.setEnabled(False)
            except Exception:
                pass
            self.required_map_dims = None
            return

        req_w = orig_w // value
        req_h = orig_h // value
        self.required_map_dims = (req_w, req_h)
        self.lbl_required_map_dims.setText(f"Dimensões Requeridas do Mapa: {req_w} x {req_h} px")
        try:
            self.btn_add_maps.setEnabled(True)
        except Exception:
            pass

    def _remove_selected_maps(self):
        """Remove os mapas selecionados na lista de mapas carregados."""
        try:
            selected_items = self.lst_maps.selectedItems()
        except Exception:
            return

        if not selected_items:
            return

        removed = []
        for item in selected_items:
            name = item.text()
            if name in self.segmentation_maps:
                self.segmentation_maps.pop(name, None)
                # também remover entradas relacionadas
                self.palette_inputs.pop(name, None)
                self.color_palettes.pop(name, None)
                removed.append(name)

        # Atualiza widgets e labels
        self._update_palette_widgets()
        self._clear_generated_art()
        self.lbl_maps_loaded.setText(f"{len(self.segmentation_maps)} mapas carregados." if self.segmentation_maps else "Nenhum mapa carregado.")
        # Desabilitar botão de remover se não houver mapas
        try:
            self.btn_remove_maps.setEnabled(len(self.segmentation_maps) > 0)
        except Exception:
            pass

    def _check_generate_ready(self):
        """Verifica se temos tudo para habilitar o botão 'Gerar'."""
        ready = bool(self.original_image and self.segmentation_maps and self.color_palettes)
        if ready:
            ready = any(s in self.segmentation_maps for s in self.color_palettes)
        try:
            self.btn_generate.setEnabled(ready)
        except Exception:
            pass
        return ready

    def _process_palettes(self):
        # If palettes were provided via the bulk editor, use them.
        # Otherwise, open the bulk editor so the user can define palettes.
        print("Processando paletas...")
        if not self.color_palettes:
            # open bulk editor to let user define palettes
            QMessageBox.information(self, "Definir Paletas", "Nenhuma paleta encontrada. Abra o editor para definir as paletas.")
            self._open_palette_bulk_editor()

        # After editor returns, check again
        if not self.color_palettes:
            QMessageBox.information(self, "Paletas Vazias", "Nenhuma paleta foi definida.")
            self.btn_generate.setEnabled(False)
            return

        # At this point color_palettes should contain parsed palettes
        QMessageBox.information(self, "Sucesso", f"Paletas prontas para {len(self.color_palettes)} assuntos.")
        self.btn_generate.setEnabled(bool(self.original_image and self.segmentation_maps and self.color_palettes))

    def _generate_pixel_art(self):
        print("Iniciando geração de pixel art (UI)...")
        if not self._check_generate_ready():
            QMessageBox.critical(self, "Erro", "Não é possível gerar. Verifique se a imagem original, os mapas e as paletas estão carregados e processados.")
            return

        try:
            self.lbl_img_pixel_art.setText("Processando... por favor, aguarde.")
        except Exception:
            pass

        # Allow UI to update before heavy processing
        try:
            QApplication.processEvents()
        except Exception:
            pass

        try:
            self.generated_pixel_art = generate_pixel_art(
                self.original_image,
                self.segmentation_maps,
                self.color_palettes,
                self.spin_scale_factor.value(),
            )

            if not self.generated_pixel_art:
                raise Exception("Algoritmo não retornou imagem.")

            pixmap = pil_to_qpixmap(self.generated_pixel_art)
            # Use nearest-neighbor (fast) transformation to avoid blurring the pixel art preview
            self.lbl_img_pixel_art.setPixmap(
                pixmap.scaled(self.lbl_img_pixel_art.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
            )
            self.btn_save.setEnabled(True)

        except Exception as e:
            print(f"ERRO na geração: {e}")
            self._clear_generated_art()
            QMessageBox.critical(self, "Erro na Geração", f"Ocorreu um erro durante o processamento:\n\n{e}")

    def _save_pixel_art(self):
        if not self.generated_pixel_art:
            QMessageBox.warning(self, "Nada para Salvar", "Gere uma imagem de pixel art primeiro.")
            return

        file_filter = "Imagem PNG (*.png)"
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Pixel Art", "", file_filter)

        if file_path:
            try:
                # Ensure extension
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                # Save PIL image
                self.generated_pixel_art.save(file_path, 'PNG')
                QMessageBox.information(self, "Sucesso", f"Imagem salva em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")
