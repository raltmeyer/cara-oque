import sys
import os
import random
import vlc
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout, QFrame, QLineEdit
from PyQt5.QtCore import Qt

class KaraokeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karaoke para a Celita")
        self.setGeometry(100, 100, 800, 600)
        self.player = None
        self.current_file = None
        self.all_music_files = []
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Widget de menu
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout()
        self.label = QLabel("Selecione uma musica para tocar:")
        self.label.setAlignment(Qt.AlignCenter)
        self.menu_layout.addWidget(self.label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar músicas...")
        self.filter_input.textChanged.connect(self.filter_list)
        self.menu_layout.addWidget(self.filter_input)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_file_select)
        self.menu_layout.addWidget(self.list_widget)

        # Adiciona botao 'baixar musicas' no canto inferior direito
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.baixar_btn = QPushButton("baixar musicas")
        self.baixar_btn.clicked.connect(self.open_baixar_musicas)
        btn_layout.addWidget(self.baixar_btn)
        self.menu_layout.addLayout(btn_layout)

        self.menu_widget.setLayout(self.menu_layout)
        self.layout.addWidget(self.menu_widget)
        
        # Widget de video
        self.video_widget = QWidget()
        self.video_layout = QVBoxLayout(self.video_widget)
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_layout.addWidget(self.video_frame)
        
        self.back_btn = QPushButton("Voltar")
        self.back_btn.clicked.connect(self.back_to_menu)
        self.video_layout.addWidget(self.back_btn)
        
        self.layout.addWidget(self.video_widget)
        self.video_widget.hide()
        
        self.populate_list()

    def populate_list(self):
        self.all_music_files = []
        # Lista arquivos no diretorio 'musicas'
        music_dir = "musicas"
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
        for f in sorted(os.listdir(music_dir)):
            if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mp3')):
                self.all_music_files.append(f)
        self.filter_list(self.filter_input.text())

    def filter_list(self, text):
        self.list_widget.clear()
        for f in self.all_music_files:
            if text.lower() in f.lower():
                self.list_widget.addItem(f)

    def on_file_select(self, item):
        self.current_file = os.path.join("musicas", item.text())
        self.menu_widget.hide()
        self.video_widget.show()
        self.play_video()

    def open_baixar_musicas(self):
        try:
            from novas_musicas import MusicaSearchApp
            self.musica_search_window = MusicaSearchApp()
            self.musica_search_window.setAttribute(Qt.WA_DeleteOnClose)
            self.musica_search_window.destroyed.connect(self.populate_list)
            self.musica_search_window.show()
        except ImportError as e:
            QMessageBox.warning(self, "Erro", f"Erro ao importar 'novas_musicas': {e}")
        
    def play_video(self):
        if self.player:
            self.player.stop()
        else:
            self.instance = vlc.Instance('--quiet', '--no-xlib', '--logmode=none', '--verbose=0')
            self.player = self.instance.media_player_new()
            
        media = self.instance.media_new(self.current_file)
        self.player.set_media(media)

        if sys.platform.startswith('linux'):
            self.player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_frame.winId()))
            
        self.player.play()

        # Monitorar o término do vídeo
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

    def on_video_end(self, event):
        nota = random.randint(60, 100)
        if 60 <= nota <= 69:
            msg = f"Nota: {nota}\nVamos que voce consegue!"
        elif 70 <= nota <= 79:
            msg = f"Nota: {nota}\nEstá melhorando!"
        elif 80 <= nota <= 89:
            msg = f"Nota: {nota}\nUau!!!!!"
        else:
            msg = f"Nota: {nota}\nSou seu fã!"
        from PyQt5.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(self, "show_nota_message", Qt.QueuedConnection,)
        self._nota_msg = msg

    def show_nota_message(self):
        QMessageBox.information(self, "Sua Nota", getattr(self, '_nota_msg', ''))

    def toggle_pause(self):
        if self.player:
            if self.player.is_playing():
                self.player.pause()
            else:
                self.player.play()

    def back_to_menu(self):
        if self.player:
            self.player.stop()
        self.video_widget.hide()
        self.menu_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KaraokeApp()
    window.show()
    sys.exit(app.exec_())
