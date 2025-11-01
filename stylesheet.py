"""stylesheet.py

Define the dark QSS stylesheet used by the application.
"""

dark_stylesheet = """
    QWidget {
        background-color: #2E2E2E;
        color: #E0E0E0;
        font-family: Arial, sans-serif;
    }
    QMainWindow {
        background-color: #2E2E2E;
    }
    QGroupBox {
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #444;
        border-radius: 5px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px 5px 5px;
    }
    QPushButton {
        background-color: #555;
        color: #E0E0E0;
        border: 1px solid #666;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #6A6A6A;
    }
    QPushButton:pressed {
        background-color: #4A4A4A;
    }
    QPushButton:disabled {
        background-color: #404040;
        color: #888;
    }
    QLabel {
        color: #E0E0E0;
        font-size: 13px;
    }
    QTextEdit {
        background-color: #252525;
        color: #E0E0E0;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 5px;
    }
    QSpinBox {
        background-color: #252525;
        color: #E0E0E0;
        border: 1px solid #444;
        padding: 5px;
        border-radius: 4px;
    }
    /* Estilo customizado para os QLabels de imagem */
    QLabel#ImageLabel {
        border: 1px dashed #555;
        background-color: #333;
        color: #888;
    }
"""
