#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Varsayılan ev ve inşaat alanı resimleri oluşturmak için script
"""

from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect, QPoint
import os

def create_directory_if_not_exists(directory):
    """Dizin yoksa oluştur"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Dizin oluşturuldu: {directory}")

def create_house_image(filename, width, height, color1, color2, roof_color):
    """Ev resmi oluştur"""
    # Pixmap oluştur
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)  # Şeffaf arka plan
    
    # Çizim için painter oluştur
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Evin gövdesi için gradyan oluştur
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0, color1)
    gradient.setColorAt(1, color2)
    
    # Evin gövdesini çiz
    house_rect = QRect(5, height // 3, width - 10, height - height // 3 - 5)
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(Qt.black, 2))
    painter.drawRect(house_rect)
    
    # Çatıyı çiz
    roof_points = [
        QPoint(0, height // 3),
        QPoint(width // 2, 5),
        QPoint(width, height // 3)
    ]
    painter.setBrush(QBrush(roof_color))
    painter.drawPolygon(roof_points)
    
    # Kapıyı çiz
    door_width = width // 4
    door_height = (height - height // 3) // 2
    door_x = (width - door_width) // 2
    door_y = height - door_height - 5
    painter.setBrush(QBrush(QColor(139, 69, 19)))  # Kahverengi
    painter.drawRect(door_x, door_y, door_width, door_height)
    
    # Pencereyi çiz
    window_size = width // 5
    window_x = (width - window_size) // 2
    window_y = height // 3 + (height - height // 3) // 4
    painter.setBrush(QBrush(QColor(173, 216, 230)))  # Açık mavi
    painter.drawRect(window_x, window_y, window_size, window_size)
    
    # Çizimi bitir
    painter.end()
    
    # Resmi kaydet
    pixmap.save(filename)
    print(f"Ev resmi oluşturuldu: {filename}")

def create_building_site_image(filename, width, height):
    """İnşaat alanı resmi oluştur"""
    # Pixmap oluştur
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)  # Şeffaf arka plan
    
    # Çizim için painter oluştur
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Zemini çiz
    ground_rect = QRect(0, height - 20, width, 20)
    painter.setBrush(QBrush(QColor(150, 75, 0)))  # Kahverengi
    painter.setPen(QPen(Qt.black, 2))
    painter.drawRect(ground_rect)
    
    # İskeleyi çiz
    scaffold_color = QColor(160, 82, 45)  # Koyu kahverengi
    
    # Dikey kirişler
    beam_width = 5
    for x in [10, width - 15]:
        painter.setBrush(QBrush(scaffold_color))
        painter.drawRect(x, 10, beam_width, height - 30)
    
    # Yatay kirişler
    for y in [15, height // 2, height - 30]:
        painter.setBrush(QBrush(scaffold_color))
        painter.drawRect(10, y, width - 25, beam_width)
    
    # İnşaat malzemeleri
    # Tuğlalar
    brick_color = QColor(178, 34, 34)  # Kırmızı-kahverengi
    for i in range(5):
        for j in range(2):
            painter.setBrush(QBrush(brick_color))
            painter.drawRect(20 + i * 15, height - 40 - j * 10, 12, 8)
    
    # Çimento torbası
    painter.setBrush(QBrush(QColor(169, 169, 169)))  # Gri
    painter.drawEllipse(width - 40, height - 50, 25, 30)
    
    # Çizimi bitir
    painter.end()
    
    # Resmi kaydet
    pixmap.save(filename)
    print(f"İnşaat alanı resmi oluşturuldu: {filename}")

def main():
    """Ana fonksiyon"""
    # Assets dizinini oluştur
    assets_dir = os.path.join("src", "assets")
    create_directory_if_not_exists(assets_dir)
    
    # Ev resimlerini oluştur
    house_configs = [
        # (dosya adı, genişlik, yükseklik, renk1, renk2, çatı rengi)
        ("ev1.png", 80, 60, QColor(255, 255, 224), QColor(245, 222, 179), QColor(139, 69, 19)),  # Sarı ev, kahverengi çatı
        ("ev2.png", 80, 60, QColor(176, 224, 230), QColor(135, 206, 235), QColor(47, 79, 79)),   # Mavi ev, koyu mavi çatı
        ("ev3.png", 100, 70, QColor(152, 251, 152), QColor(144, 238, 144), QColor(34, 139, 34)), # Yeşil ev, koyu yeşil çatı
        ("ev4.png", 120, 80, QColor(255, 182, 193), QColor(255, 105, 180), QColor(139, 0, 139))  # Pembe ev, mor çatı
    ]
    
    for config in house_configs:
        filename, width, height, color1, color2, roof_color = config
        filepath = os.path.join(assets_dir, filename)
        create_house_image(filepath, width, height, color1, color2, roof_color)
    
    # İnşaat alanı resmini oluştur
    building_site_path = os.path.join(assets_dir, "insaat.png")
    create_building_site_image(building_site_path, 100, 80)
    
    print("Tüm resimler başarıyla oluşturuldu!")

if __name__ == "__main__":
    main() 