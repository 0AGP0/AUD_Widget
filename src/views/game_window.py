def setup_ui(self):
        """Arayüzü hazırla"""
        try:
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Ana düzen
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Zemin widget'ı
            self.ground_widget = GroundWidget(self.game_controller)
            layout.addWidget(self.ground_widget)
            
            # Kontrol paneli
            self.control_panel = ControlPanel()
            self.control_panel.close_game.connect(self.close)
            self.control_panel.minimize_game.connect(self.showMinimized)
            
            # Kontrol panelini game_controller'a bağla
            self.game_controller.set_control_panel(self.control_panel)
            
            # Köylü listesi sinyalini kontrol paneline bağla
            self.game_controller.villagers_updated.connect(self.control_panel.update_villagers)
            
            # Gece/gündüz sinyalini kontrol paneline bağla
            self.game_controller.day_night_changed.connect(self.control_panel.update_day_night_style)
            
            # İlk köylü listesini gönder
            if hasattr(self.game_controller, 'villagers'):
                self.game_controller.villagers_updated.emit(self.game_controller.villagers)
            
            # Kontrol panelini göster
            self.control_panel.show()
            
            print("Arayüz hazırlandı")
            
        except Exception as e:
            print(f"HATA: Arayüz hazırlanırken hata: {e}")
            import traceback
            traceback.print_exc() 