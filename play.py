import sys
import os
import vlc
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QSlider,QMenu,
                             QFileDialog, QPushButton, QGridLayout, QFrame,
                             QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# 设置 VLC 库路径（根据实际情况修改）
vlc_path = r'C:\Program Files\VideoLAN\VLC'
os.add_dll_directory(vlc_path)

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

# --- 用于捕获右键点击的 QFrame 子类，用于Multi Video的视频显示区域 ---
class VideoFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
        open_action = menu.addAction("Open file...")
        
        parent_widget = self.parent()
        if hasattr(parent_widget, 'open_file'):
            open_action.triggered.connect(parent_widget.open_file)
        
        menu.exec_(self.mapToGlobal(pos))

# --- Multi Video中的独立视频播放控件 ---
class VideoPlayerWidget(QWidget):

    def __init__(self, vlc_instance):
        super().__init__()
        self.vlc_instance = vlc_instance
        self.media = None
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(50)  # 明确设置初始音量
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 减少边距
        layout.setSpacing(4)
        
        # 视频显示区域
        self.video_frame = VideoFrame(self)
        self.video_frame.setStyleSheet("background-color: black; border: 2px solid #444;")
        self.video_frame.setMinimumSize(200, 150)
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_frame, 1)        
        
        
        # 播放控制条
        controls = QHBoxLayout()
        controls.setContentsMargins(4, 0, 4, 4)  # 调整边距
        controls.setSpacing(4)
        
        # 播放按钮
        self.play_btn = QPushButton("Play")
        #self.play_btn.setToolTip("Play/Pause")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setFixedHeight(30)
        controls.addWidget(self.play_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("Stop")
        #self.stop_btn.setToolTip("Stop")
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.setFixedHeight(30)
        controls.addWidget(self.stop_btn)
        
        # 进度条
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.sliderPressed.connect(self.slider_pressed_event)
        self.progress.sliderReleased.connect(self.slider_released_event)
        controls.addWidget(self.progress, 1)  # 添加拉伸因子
        
        # 音量条
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        self.volume.valueChanged.connect(self.change_volume)
        self.volume.setFixedWidth(100)
        controls.addWidget(self.volume)
       
        self.player.audio_set_volume(50)

        # 音量图标
        self.volume_icon = QLabel()
        self.volume_icon.setText("50%")
        #self.volume_icon.setStyleSheet("color: white;padding: 0px; margin: 0px; border: none;")
        #self.volume_icon.setPixmap(QIcon.fromTheme("audio-volume-medium").pixmap(16, 16))
        controls.addWidget(self.volume_icon)
        
        layout.addLayout(controls)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.slider_pressed_flag = False


    def open_file(self):
        # 弹出文件对话框，选择视频文件
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a video file", "", "Video (*.mp4 *.avi *.mkv *.mov)")
        if path:
            self.media = self.vlc_instance.media_new(path)
            self.player.set_media(self.media)
            # 设置视频输出窗口
            if platform.system() == "Windows":
                self.player.set_hwnd(self.video_frame.winId())
            elif platform.system() == "Darwin":
                self.player.set_nsobject(self.video_frame.winId())
            elif platform.system() == "Linux":
                self.player.set_xwindow(self.video_frame.winId())
            self.toggle_play()  # 加载后自动播放

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.setText("Play")
            self.timer.stop()
        else:
            self.player.play()
            self.play_btn.setText("Pause")
            self.timer.start(100)

    def stop(self):
        self.player.stop()
        self.play_btn.setText("Play")
        self.timer.stop()

    def slider_pressed_event(self):
        self.slider_pressed_flag = True

    def slider_released_event(self):
        self.slider_pressed_flag = False
        self.seek_video()

    def seek_video(self):
        pos = self.progress.value() / 1000.0
        self.player.set_position(pos)

    def change_volume(self, value):
        volume = max(0, min(100, value))  # 确保音量在0-100范围内
        self.player.audio_set_volume(volume)
        self.volume_icon.setText(f"{volume}%")
        self.volume_icon.setStyleSheet("background-color: #1e1e1e;color: white;padding: 0px; margin: 0px; border: none;")

    def update_ui(self):
        if not self.slider_pressed_flag:
            pos = self.player.get_position()
            self.progress.setValue(int(pos * 1000))


# --- 主窗口 ---
class MultiVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Window Video Player")
        self.setMinimumSize(QSize(800, 600))
        self.setStyleSheet(STYLE_SHEET)
        self.vlc_instance = vlc.Instance()
        
        # 设置窗口图标
        try:
            self.setWindowIcon(QIcon.fromTheme("video-x-generic"))
        except:
            pass
        
        # 默认模式为Single Video
        self.current_mode = "Single Video"
        # 默认窗口个数
        self.current_window_count = 4
        
        self.players = []         # Single Video下存放 (player, frame) 的列表
        self.multi_widgets = []   # Multi Video下存放 VideoPlayerWidget 的列表
        
        self.create_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.slider_pressed = False

    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 上方控制区域
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        
        # 添加播放模式选择框
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Single Video", "Multi Video"])
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)
        self.mode_label = QLabel("Play Mode:")
        self.mode_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.mode_label)
        control_layout.addWidget(self.mode_combo)
        
        # 全局打开文件按钮（仅在Single Video下启用）
        self.open_btn = QPushButton("Open File...")
        self.open_btn.setIcon(QIcon.fromTheme("document-open"))
        self.open_btn.clicked.connect(self.open_file)
        control_layout.addWidget(self.open_btn)
        
        # 全局播放按钮
        self.play_btn = QPushButton("Play")
        self.play_btn.setToolTip("Play/Pause")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setFixedHeight(30)
        control_layout.addWidget(self.play_btn)
        
        # 全局停止按钮
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.clicked.connect(self.stop_all)
        self.stop_btn.setFixedHeight(30)
        control_layout.addWidget(self.stop_btn)

        # 窗口布局下拉框：选择显示窗口个数（对两种模式都适用）
        self.window_combo = QComboBox()
        self.window_combo.addItems(["1", "2", "4", "6", "8", "9"])
        self.window_combo.setCurrentText("4")
        self.window_combo.currentIndexChanged.connect(self.change_window_count)
        self.layout_label = QLabel("Window Layout:")
        self.layout_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.layout_label)
        control_layout.addWidget(self.window_combo)
        
        # 将上方控制区域加入主布局
        main_layout.addLayout(control_layout)

        # 进度条（仅用于Single Video，全局进度）
        self.time_progress_layout = QHBoxLayout()
        self.time_progress_layout.setContentsMargins(0, 0, 0, 0)
        self.time_progress_layout.setSpacing(10)
        
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setContentsMargins(0, 0, 0, 0)
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.time_label.setStyleSheet("padding: 0px; margin: 0px; border: none;")
        self.time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_progress_layout.addWidget(self.time_label)

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.sliderPressed.connect(self.slider_pressed_event)
        self.progress.sliderReleased.connect(self.slider_released_event)
        self.progress.valueChanged.connect(self.seek_video)
        self.time_progress_layout.addWidget(self.progress, 1)
        
        main_layout.addLayout(self.time_progress_layout)

        # 视频容器
        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; border-radius: 4px;")
        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.video_container.setLayout(self.grid)
        main_layout.addWidget(self.video_container, 1)  # 添加拉伸因子

        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # 根据默认模式创建窗口
        self.setup_video_windows()

    def mode_changed(self, index):
        # 根据模式切换更新界面
        self.current_mode = self.mode_combo.currentText()
        if self.current_mode == "Single Video":
            self.open_btn.setEnabled(True)
            self.time_progress_layout.setEnabled(True)
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.status_bar.showMessage("Single Video mode - all windows play the same video")
        else:
            self.open_btn.setEnabled(False)
            self.time_progress_layout.setEnabled(False)
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.status_bar.showMessage("Multi Video mode - each window can play independent videos (right-click to load)")
        # 清除现有窗口并重新创建
        self.clear_video_container()
        self.setup_video_windows()

    def change_window_count(self, index):
        text = self.window_combo.itemText(index)
        self.current_window_count = int(text)
        self.clear_video_container()
        self.setup_video_windows()
        self.status_bar.showMessage(f"Changed to {self.current_window_count} window layout")

    
    def clear_video_container(self):
        # 单视频模式下终止播放器
        if self.current_mode == "Single Video":
            for player, frame in self.players:
                if player.is_playing():
                    player.stop()
            self.players.clear() 
        else: # 多视频模式
            self.multi_widgets.clear() # Clear the list of widgets

        # 清除网格布局中的部件
        while self.grid.count():
            child = self.grid.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()


    def setup_video_windows(self):
        # 根据当前模式和窗口个数创建视频窗口
        if self.current_mode == "Single Video":
            self.create_single_mode_windows()
        else:
            self.create_multi_mode_windows()
        self.arrange_windows()

    def create_single_mode_windows(self):
        # 原有Single Video：所有窗口共用同一媒体（后续调用 open_file 和 toggle_play 影响所有窗口）
        for _ in range(self.current_window_count):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("background-color: black; border: 2px solid #444;")
            player = self.vlc_instance.media_player_new()
            self.players.append((player, frame))

    def create_multi_mode_windows(self):
        # 每个窗口为独立 VideoPlayerWidget（内置控件包括右键选文件、独立控制、音量等）
        for _ in range(self.current_window_count):
            widget = VideoPlayerWidget(self.vlc_instance)
            widget.setStyleSheet(STYLE_SHEET)
            widget.volume_icon.setStyleSheet("background-color: #1e1e1e;color: white;padding: 0px; margin: 0px; border: none;")
            self.multi_widgets.append(widget)

    def arrange_windows(self):
        count = self.current_window_count
        rows = int(count ** 0.5)
        cols = count // rows
        if rows * cols < count:
            cols += 1
        # 清空旧布局
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        # 添加视频窗口到网格中
        if self.current_mode == "Single Video":
            for index, (player, frame) in enumerate(self.players):
                row = index // cols
                col = index % cols
                self.grid.addWidget(frame, row, col)
                # 设置视频输出
                if self.media_available() and frame.winId():
                    if platform.system() == "Windows":
                        player.set_hwnd(frame.winId())
                    elif platform.system() == "Darwin":
                        player.set_nsobject(frame.winId())
                    elif platform.system() == "Linux":
                        player.set_xwindow(frame.winId())
        else:
            for index, widget in enumerate(self.multi_widgets):
                row = index // cols
                col = index % cols
                self.grid.addWidget(widget, row, col)

    def media_available(self):
        # 检查是否已加载媒体（用于Single Video）
        return hasattr(self, 'media') and self.media is not None

    def open_file(self):
        # 仅在Single Video下，全局打开文件按钮响应
        if self.current_mode != "Single Video":
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a video file", "", "Video (*.mp4 *.avi *.mkv *.mov)")
        if path:
            self.load_video(path)
            self.toggle_play()  
            self.status_bar.showMessage(f"Playing: {os.path.basename(path)}")
        else:
            self.status_bar.showMessage("File not selected")

    def load_video(self, path):
        # 加载视频文件，并将同一媒体设置到所有播放器中
        # 避免重复加载相同文件
        if self.media_available() and self.media.get_mrl() == path:
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

    def toggle_play(self):
        # 仅针对Single Video，全局控制所有播放器播放或暂停
        if not self.media_available():
            self.status_bar.showMessage("No video loaded")
            return

        if self.is_playing():
            for player, _ in self.players:
                player.pause()
            self.play_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            self.play_btn.setText("Play")
            self.timer.stop()
        else:
            for player, _ in self.players:
                player.play()
            self.play_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
            self.play_btn.setText("Pause")
            self.timer.start(100)

    def stop_all(self):
        if self.current_mode == "Single Video":
            for player, _ in self.players:
                player.stop()
            self.play_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            self.timer.stop()
        else:
            for widget in self.multi_widgets:
                widget.stop()
        self.status_bar.showMessage("Playback stopped")

    def is_playing(self):
        if self.players:
            return self.players[0][0].is_playing()
        return False

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
        # 仅用于Single Video：更新时间进度条和标签
        if self.current_mode != "Single Video":
            return
        if not self.slider_pressed and self.players:
            positions = []
            for player, _ in self.players:
                pos = player.get_position()
                if pos != -1:
                    positions.append(pos)
            if positions:
                avg_position = sum(positions) / len(positions)
                self.progress.setValue(int(avg_position * 1000))

        if self.players and self.media_available():
            total_time = self.players[0][0].get_length() // 1000  # 单位秒
            current_time = self.players[0][0].get_time() // 1000
            total_time_str = self.format_time(total_time)
            current_time_str = self.format_time(current_time)
            self.time_label.setText(f"{current_time_str} / {total_time_str}")

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def closeEvent(self, event):
        # 关闭时释放所有播放器资源
        if self.current_mode == "Single Video":
            for player, _ in self.players:
                player.stop()
                player.release()
        else:
            for widget in self.multi_widgets:
                widget.player.stop()
                widget.player.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，看起来更现代
    
    # 设置默认字体
    font = QFont()
    font.setFamily("Segoe UI")  # Windows
    font.setPointSize(10)
    app.setFont(font)
    
    player = MultiVideoPlayer()
    player.show()
    sys.exit(app.exec_())
