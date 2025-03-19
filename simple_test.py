import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

def main():
    """En basit test penceresi"""
    # QApplication oluştur
    app = QApplication(sys.argv)
    
    # Basit bir pencere oluştur
    window = QMainWindow()
    window.setWindowTitle("Basit Test")
    window.setGeometry(100, 100, 400, 300)
    
    # Ana widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Etiket ekle
    label = QLabel("Bu bir test penceresidir")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    # Pencereyi göster
    window.show()
    
    # Uygulamayı çalıştır
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 