import sys
import os
import vlc
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QSlider,
                             QFileDialog, QPushButton, QGridLayout, QFrame,
                             QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize

# Path of VLC
vlc_path = r'C:\Program Files\VideoLAN\VLC'

os.add_dll_directory(vlc_path)


class MultiVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi window player")
        self.setMinimumSize(QSize(800, 600))

        self.vlc_instance = vlc.Instance()
        self.media = None
        self.players = []
        self.current_window_count = 4
        self.is_playing = False  

        self.create_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.slider_pressed = False

    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        control_layout = QHBoxLayout()

        self.open_btn = QPushButton("Open file...")
        self.open_btn.clicked.connect(self.open_file)
        control_layout.addWidget(self.open_btn)

        self.window_combo = QComboBox()
        self.window_combo.addItems(["Layout","1","2", "4", "6", "8", "9"])
        self.window_combo.currentIndexChanged.connect(self.change_window_count)
        control_layout.addWidget(self.window_combo)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)

        main_layout.addLayout(control_layout)

        # progress bar
        time_progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setContentsMargins(0, 0, 0, 0)
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.time_label.setStyleSheet("""
            padding: 0px;
            margin: 0px;
            border: none;
        """)
        self.time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        time_progress_layout.addWidget(self.time_label)

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.sliderPressed.connect(self.slider_pressed_event)
        self.progress.sliderReleased.connect(self.slider_released_event)
        self.progress.valueChanged.connect(self.seek_video)
        time_progress_layout.addWidget(self.progress)

        main_layout.addLayout(time_progress_layout)

        # video container
        self.video_container = QWidget()
        self.grid = QGridLayout()
        self.video_container.setLayout(self.grid)
        main_layout.addWidget(self.video_container)

        self.create_video_windows()



    def create_video_windows(self):
        for _ in range(self.current_window_count):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("background-color: black;")
            player = self.vlc_instance.media_player_new()
            self.players.append((player, frame))

        self.arrange_windows()

    def arrange_windows(self):
        count = self.current_window_count
        rows = int(count ** 0.5)
        cols = count // rows
        if rows * cols < count:
            cols += 1

        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

        for index, (_, frame) in enumerate(self.players):
            row = index // cols
            col = index % cols
            self.grid.addWidget(frame, row, col)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a video file", "", "Video (*.mp4 *.avi *.mkv *.mov)")
        if path:
            self.load_video(path)
            self.toggle_play()  
        else:
            print("File not selected")

    def load_video(self, path):
        if self.media and self.media.get_mrl() == path:
            return
        self.media = self.vlc_instance.media_new(path)
        for player, frame in self.players:
            player.set_media(self.media)
            if platform.system() == "Windows":
                player.set_hwnd(frame.winId())
            elif platform.system() == "Darwin":
                player.set_nsobject(frame.winId())
            elif platform.system() == "Linux":
                player.set_xwindow(frame.winId())

    def change_window_count(self, index):
        if self.window_combo.itemText(index) == "Layout":
            return
        current_position = 0
        if self.media and self.is_playing:
            current_position = self.players[0][0].get_position()
            for player, _ in self.players:
                player.stop()
                player.release()
        
        self.current_window_count = int(self.window_combo.itemText(index))
        self.players.clear()
        self.create_video_windows()
        if self.media:
            self.load_video(self.media.get_mrl())
            if self.is_playing:
                for player, _ in self.players:
                    player.play()
                    player.set_position(current_position)
                self.timer.start(100)

    def toggle_play(self):
        if not self.media:
            return

        if self.is_playing:
            for player, _ in self.players:
                player.pause()
            self.play_btn.setText("Play")
            self.timer.stop()
            self.is_playing = False
        else:
            for player, _ in self.players:
                player.play()
            self.play_btn.setText("Pause")
            self.timer.start(100)
            self.is_playing = True

    def slider_pressed_event(self):
        self.slider_pressed = True

    def slider_released_event(self):
        self.slider_pressed = False
        self.sync_playback()

    def seek_video(self, value):
        if self.slider_pressed:
            self.sync_playback()

    def sync_playback(self):
        position = self.progress.value() / 1000.0
        for player, _ in self.players:
            player.set_position(position)

    def update_ui(self):
        if not self.slider_pressed and self.players:
            positions = []
            for player, _ in self.players:
                position = player.get_position()
                if position != -1:
                    positions.append(position)
            if positions:
                avg_position = sum(positions) / len(positions)
                self.progress.setValue(int(avg_position * 1000))

        if self.players and self.media:
            total_time = self.players[0][0].get_length() // 1000  # 总时长，单位：秒
            current_time = self.players[0][0].get_time() // 1000  # 当前时间，单位：秒
            total_time_str = self.format_time(total_time)
            current_time_str = self.format_time(current_time)
            self.time_label.setText(f"{current_time_str} / {total_time_str}")

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def closeEvent(self, event):
        for player, _ in self.players:
            player.stop()
            player.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MultiVideoPlayer()
    player.show()
    sys.exit(app.exec_())