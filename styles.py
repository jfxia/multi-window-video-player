# 全局样式表
STYLE_SHEET = """
    QMainWindow {
        background-color: #2d2d2d;
    }
    QWidget {
        color: #e0e0e0;
        background-color: #2d2d2d;
    }
    QFrame {
        border: 1px solid #444;
        border-radius: 3px;
    }
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 60px;
    }
    QPushButton:hover {
        background-color: #5a5a5a !important;
        border: 1px solid #555 !important;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    QComboBox {
        background-color: #3a3a3a;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 3px;
        min-width: 100px;
    }
    QComboBox:hover {
        background-color: #4a4a4a;
        border: 1px solid #555;
    }
    QComboBox::drop-down {
        width: 20px;
        border-left: 1px solid #444;
    }
    QComboBox QAbstractItemView {
        background-color: #3a3a3a;
        selection-background-color: #505050;
    }
    QLabel {
        color: #e0e0e0;
    }
    QSlider::groove:horizontal {
        border: 1px solid #444;
        height: 8px;
        background: #3a3a3a;
        margin: 2px 0;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9cff, stop:1 #0078ff);
        border: 1px solid #222222;
        width: 12px;
        margin: -2px 0;
        border-radius: 9px;
    }
    QSlider::sub-page:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9cff, stop:1 #0078ff);
        border-radius: 4px;
    }
"""