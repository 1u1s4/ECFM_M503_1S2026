APP_STYLESHEET = """
QMainWindow {
    background: #000000;
}

QScrollArea {
    background: #000000;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: #000000;
}

QWidget#rootWidget {
    background: #000000;
    color: #ffffff;
    font-family: 'Space Mono', 'IBM Plex Mono', 'JetBrains Mono', monospace;
}

QLabel#appTitle {
    color: #ffffff;
    font-size: 38px;
    font-weight: 700;
    letter-spacing: 3px;
}

QLabel#appSubtitle {
    color: #ffffff;
    font-size: 12px;
    letter-spacing: 2px;
}

QLabel#headerChip {
    border: 3px solid #ffffff;
    padding: 6px 10px;
    background: #000000;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#panelTitle {
    color: #000000;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#panelSubtitle {
    color: #000000;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#mutedLabel {
    font-size: 10px;
    color: #000000;
    letter-spacing: 1px;
}

QLabel#badge,
QLabel#statusBadge {
    border: 4px solid #000000;
    padding: 6px 12px;
    background: #ffffff;
    font-weight: 700;
    color: #000000;
}

QLabel#statusBadge {
    background: #000000;
    color: #ffffff;
    min-width: 112px;
}

QLabel#infoPill {
    border: 3px solid #000000;
    padding: 7px 10px;
    background: #ffffff;
    color: #000000;
    font-size: 11px;
    font-weight: 700;
}

QFrame#metricCard {
    background: #ffffff;
    border: 3px solid #000000;
}

QLabel#metricKey {
    color: #000000;
    font-size: 10px;
    letter-spacing: 1px;
}

QLabel#metricValue {
    color: #000000;
    font-size: 13px;
    font-weight: 700;
}

QFrame#panelFrame {
    background: #ffffff;
    border: 4px solid #000000;
}

QSpinBox, QDoubleSpinBox {
    border: 4px solid #000000;
    padding: 8px 12px;
    background: #ffffff;
    selection-background-color: #000000;
    selection-color: #ffffff;
    min-width: 110px;
    min-height: 20px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton {
    border: 4px solid #000000;
    background: #ffffff;
    color: #000000;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#primaryButton {
    background: #000000;
    color: #ffffff;
}

QPushButton:hover {
    background: #000000;
    color: #ffffff;
}

QPushButton:pressed {
    padding-left: 14px;
    padding-top: 14px;
}
"""
