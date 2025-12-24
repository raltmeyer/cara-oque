import sys
import json
import subprocess
import urllib.parse
import yaml
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QLabel, QDialog, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class DownloadWorker(QThread):
	progress_signal = pyqtSignal(float)
	finished_signal = pyqtSignal(str)
	error_signal = pyqtSignal(str)

	def __init__(self, url, ydl_opts):
		super().__init__()
		self.url = url
		self.ydl_opts = ydl_opts

	def run(self):
		self.ydl_opts['progress_hooks'] = [self.hook]
		try:
			from yt_dlp import YoutubeDL
			with YoutubeDL(self.ydl_opts) as ydl:
				ydl.download([self.url])
			self.finished_signal.emit("Download concluído para a pasta 'musicas'.")
		except Exception as e:
			self.error_signal.emit(str(e))

	def hook(self, d):
		if d['status'] == 'downloading':
			total = d.get('total_bytes') or d.get('total_bytes_estimate')
			downloaded = d.get('downloaded_bytes', 0)
			if total:
				p = (downloaded / total) * 100
				self.progress_signal.emit(p)

class DownloadDialog(QDialog):
	def __init__(self, title, parent=None):
		super().__init__(parent)
		self.setWindowTitle(f"Baixando: {title}")
		self.setFixedSize(400, 150)
		layout = QVBoxLayout()
		
		self.label = QLabel("Aguarde, iniciando download...")
		self.label.setAlignment(Qt.AlignCenter)
		layout.addWidget(self.label)
		
		self.pbar = QProgressBar()
		self.pbar.setValue(0)
		layout.addWidget(self.pbar)
		
		self.btn_close = QPushButton("Fechar")
		self.btn_close.clicked.connect(self.accept)
		self.btn_close.hide()
		layout.addWidget(self.btn_close)
		
		self.setLayout(layout)

	def update_progress(self, val):
		self.pbar.setValue(int(val))
		self.label.setText(f"Baixando... {int(val)}%")

	def on_finished(self, msg):
		self.pbar.setValue(100)
		self.label.setText(msg)
		self.btn_close.show()

	def on_error(self, msg):
		self.label.setText(f"Erro: {msg}")
		self.btn_close.show()

class MusicaSearchApp(QWidget):
	def download_video(self, title, video_id):
		import os
		# Garante que o diretorio 'musicas' exista
		musicas_dir = os.path.join(os.getcwd(), "musicas")
		if not os.path.exists(musicas_dir):
			os.makedirs(musicas_dir)
		url = f"https://www.youtube.com/watch?v={video_id}"
		ydl_opts = {
			'outtmpl': os.path.join(musicas_dir, f"%(title)s.%(ext)s"),
			'format': 'mp4',
			'quiet': True,
			'noplaylist': True,
			'merge_output_format': 'mp4',
		}
		
		self.dlg = DownloadDialog(title, self)
		self.worker = DownloadWorker(url, ydl_opts)
		self.worker.progress_signal.connect(self.dlg.update_progress)
		self.worker.finished_signal.connect(self.dlg.on_finished)
		self.worker.error_signal.connect(self.dlg.on_error)
		self.worker.start()
		self.dlg.exec_()

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Pesquisar Música")
		self.setGeometry(200, 200, 700, 500)
		self.init_ui()


	def init_ui(self):
		layout = QVBoxLayout()
		self.label = QLabel("Digite o nome da música:")
		layout.addWidget(self.label)
		self.textbox = QLineEdit()
		self.textbox.setPlaceholderText("Nome da música...")
		layout.addWidget(self.textbox)
		self.search_btn = QPushButton("Pesquisar")
		self.search_btn.clicked.connect(self.search_music)
		layout.addWidget(self.search_btn)
		self.results_list = QListWidget()
		self.results_list.itemClicked.connect(self.on_result_clicked)
		layout.addWidget(self.results_list)
		self.setLayout(layout)

	def on_result_clicked(self, item):
		text = item.text()
		if text == "Nenhum vídeo encontrado." or text.startswith("Erro na pesquisa"):
			return
		title, sep, video_id = text.partition("|||")
		if not video_id:
			return
		reply = QMessageBox.question(
			self,
			"Download",
			f"Deseja fazer download da música '{title}'?",
			QMessageBox.Cancel | QMessageBox.Yes,
			QMessageBox.Cancel
		)
		if reply == QMessageBox.Yes:
			self.download_video(title, video_id)
		# caso contrario: nao faz nada (cancelar)

	def search_music(self):
		query = self.textbox.text().strip()
		if not query:
			QMessageBox.warning(self, "Aviso", "Digite o nome da música para pesquisar.")
			return
		self.results_list.clear()
		
		channels = []
		try:
			with open("channels.yaml", "r") as f:
				data = yaml.safe_load(f)
				channels = data.get("channels", [])
		except Exception as e:
			self.results_list.addItem(f"Erro ao ler channels.yaml: {e}")
			return

		encoded_query = urllib.parse.quote(query)
		found = False

		for channel in channels:
			search_query = f"https://www.youtube.com/{channel}/search?query={encoded_query}"
			try:
				result = subprocess.run([
					sys.executable, '-m', 'yt_dlp', '--flat-playlist', '--dump-json', '--playlist-end', '20', search_query
				], capture_output=True, text=True, check=True)
					# yt-dlp produz um JSON por linha
				lines = result.stdout.strip().split('\n')
				for line in lines:
					try:
						video = json.loads(line)
						if video.get('_type') == 'url' and video.get('ie_key') == 'Youtube':
							title = video.get('title', 'Sem título')
							video_id = video.get('id', '')
							self.results_list.addItem(f"{title}|||{video_id}")
							found = True
					except Exception:
						continue
			except Exception as e:
				continue

		if not found:
			self.results_list.addItem("Nenhum vídeo encontrado.")


# Suporte para iniciar a partir de outro script (oque.py)
def run_musica_search_app(on_close_callback=None):
	app = QApplication.instance()
	created_app = False
	if app is None:
		app = QApplication(sys.argv)
		created_app = True

	window = MusicaSearchApp()
	if on_close_callback:
		window.closeEvent = lambda event: (on_close_callback(), event.accept())
	window.show()

	if created_app:
		sys.exit(app.exec_())

if __name__ == "__main__":
	run_musica_search_app()
