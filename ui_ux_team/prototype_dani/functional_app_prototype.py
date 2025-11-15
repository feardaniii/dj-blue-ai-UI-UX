from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QSlider, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QFrame
)
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
import sys
from pathlib import Path

# === CONSTANTS ===
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# === Smooth Clickable Slider ===
class SmoothSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, *args, **kwargs):
        super().__init__(orientation, *args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.orientation() == Qt.Horizontal:
                x = event.position().x()
                vmin, vmax = self.minimum(), self.maximum()
                w = max(1, self.width() - 1)
                value = vmin + round((x / w) * (vmax - vmin))
            else:
                y = event.position().y()
                vmin, vmax = self.minimum(), self.maximum()
                h = max(1, self.height() - 1)
                value = vmax - round((y / h) * (vmax - vmin))
            self.setValue(value)
            event.accept()
        super().mousePressEvent(event)

# === Hover Button ===
class HoverButton(QPushButton):
    def __init__(self, icon_path, size=50, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.btn_size = size
        self.is_hovered = False
        
        self.setup_button()
        
    def setup_button(self):
        try:
            pix = QPixmap(str(self.icon_path))
            if not pix.isNull():
                pix = pix.scaled(self.btn_size, self.btn_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setIcon(QIcon(pix))
                self.setIconSize(QSize(self.btn_size, self.btn_size))
        except Exception as e:
            print(f"Error loading icon {self.icon_path}: {e}")
            
        self.setFixedSize(self.btn_size + 20, self.btn_size + 20)
        self.setFlat(True)
        self.setStyleSheet("border: none; background: transparent;")
        self.setCursor(Qt.PointingHandCursor)
        
        # Glow effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.glow.setColor(QColor(0, 200, 255, 180))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.glow.setBlurRadius(20)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.glow.setBlurRadius(0)
        super().leaveEvent(event)

# === Animated Heart Button ===
class HeartButton(QPushButton):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.is_liked = False
        
        try:
            pix = QPixmap(str(icon_path))
            if not pix.isNull():
                pix = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setIcon(QIcon(pix))
                self.setIconSize(QSize(40, 40))
        except Exception as e:
            print(f"Error loading heart icon: {e}")
            
        self.setFixedSize(60, 60)
        self.setFlat(True)
        self.setStyleSheet("border: none; background: transparent;")
        self.setCursor(Qt.PointingHandCursor)
        
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.glow.setColor(QColor(255, 0, 128))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        # Scale animation
        self.scale_anim = QPropertyAnimation(self, b"iconSize")
        self.scale_anim.setDuration(200)
        self.scale_anim.setEasingCurve(QEasingCurve.OutBack)
        
    def toggle_like(self):
        self.is_liked = not self.is_liked
        
        if self.is_liked:
            self.glow.setBlurRadius(25)
            self.scale_anim.setStartValue(QSize(40, 40))
            self.scale_anim.setEndValue(QSize(50, 50))
            self.scale_anim.start()
        else:
            self.glow.setBlurRadius(0)
            self.scale_anim.setStartValue(QSize(50, 50))
            self.scale_anim.setEndValue(QSize(40, 40))
            self.scale_anim.start()

# === Album Art with Glow ===
class AlbumArtWidget(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.setAlignment(Qt.AlignCenter)
        
        try:
            pix = QPixmap(str(image_path))
            if not pix.isNull():
                pix = pix.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(pix)
        except Exception as e:
            print(f"Error loading album art: {e}")
            self.setText("♪")
            self.setStyleSheet("font-size: 100px; color: #00ffff;")
        
        # Pulsing glow
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(20)
        self.glow.setColor(QColor(0, 255, 255, 150))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        # Animation
        self.anim = QPropertyAnimation(self.glow, b"blurRadius")
        self.anim.setDuration(2000)
        self.anim.setStartValue(20)
        self.anim.setEndValue(40)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.setLoopCount(-1)
        
    def start_glow(self):
        self.anim.start()
        
    def stop_glow(self):
        self.anim.stop()
        self.glow.setBlurRadius(20)

# === Volume Control ===
class VolumeControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 280)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container for volume bar
        container = QWidget()
        container.setFixedSize(50, 250)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Volume bar image
        self.volume_bg = QLabel()
        try:
            volume_pix = QPixmap(str(ASSETS_DIR / "volumebar.png"))
            if not volume_pix.isNull():
                self.volume_bg.setPixmap(volume_pix.scaled(40, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print(f"Error loading volume bar: {e}")
            
        self.volume_bg.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.volume_bg)
        
        # Functional slider
        self.slider = SmoothSlider(Qt.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(70)
        self.slider.setFixedSize(40, 220)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: transparent;
                width: 8px;
            }
            QSlider::sub-page:vertical {
                background: transparent;
            }
            QSlider::handle:vertical {
                background: rgba(0, 255, 255, 200);
                border: 2px solid #00ffff;
                height: 16px;
                width: 16px;
                border-radius: 8px;
                margin: 0 -4px;
            }
        """)
        self.slider.setParent(container)
        self.slider.move(5, 15)
        
        layout.addWidget(container)
        
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.4)
        container.setGraphicsEffect(self.opacity_effect)
        
        # Glow
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.glow.setColor(QColor(0, 255, 255, 180))
        self.glow.setOffset(0, 0)
        self.volume_bg.setGraphicsEffect(self.glow)
        
    def enterEvent(self, event):
        self.opacity_effect.setOpacity(1.0)
        self.glow.setBlurRadius(20)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.opacity_effect.setOpacity(0.4)
        self.glow.setBlurRadius(0)
        super().leaveEvent(event)

# === Tab Button ===
class TabButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.is_active = False
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
        
    def set_active(self, active):
        self.is_active = active
        self.update_style()
        
    def update_style(self):
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    color: #00ffff;
                    font-size: 16px;
                    font-weight: bold;
                    border: none;
                    border-bottom: 3px solid #00ffff;
                    padding: 8px 20px;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    color: #6B7B9F;
                    font-size: 16px;
                    border: none;
                    padding: 8px 20px;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #00ffff;
                }
            """)

# === Main Music Player ===
class DJBlueAIMusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DJ Blue AI")
        self.setFixedSize(1000, 750)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0e17, stop:1 #1a2235);
                color: white;
            }
        """)
        
        self.is_playing = False
        self.current_time = 45
        self.total_time = 190
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 25, 30, 25)
        
        # === TOP BAR ===
        top_bar = self.create_top_bar()
        main_layout.addLayout(top_bar)
        
        # === MAIN CONTENT ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left: Volume
        self.volume_control = VolumeControl()
        content_layout.addWidget(self.volume_control, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Center: Album + Controls
        center_layout = QVBoxLayout()
        center_layout.setSpacing(25)
        
        # Album art
        album_container = QHBoxLayout()
        album_container.addStretch()
        self.album_art = AlbumArtWidget(ASSETS_DIR / "cover.png")
        album_container.addWidget(self.album_art)
        album_container.addStretch()
        center_layout.addLayout(album_container)
        
        # Progress
        progress_layout = self.create_progress_bar()
        center_layout.addLayout(progress_layout)
        
        # Controls
        controls = self.create_controls()
        center_layout.addLayout(controls)
        
        content_layout.addLayout(center_layout, 1)
        
        # Right: Heart
        right_layout = QVBoxLayout()
        right_layout.addSpacing(80)
        self.heart_btn = HeartButton(ASSETS_DIR / "favorite.png")
        self.heart_btn.clicked.connect(self.heart_btn.toggle_like)
        right_layout.addWidget(self.heart_btn, 0, Qt.AlignRight)
        right_layout.addStretch()
        content_layout.addLayout(right_layout)
        
        main_layout.addLayout(content_layout, 1)
        
        # === TABS ===
        tabs = self.create_tabs()
        main_layout.addLayout(tabs)
        
        # === TIMER ===
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_progress)
        
    def create_top_bar(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Left buttons
        menu_btn = HoverButton(ASSETS_DIR / "menu.png", 28)
        ai_btn = HoverButton(ASSETS_DIR / "aimascot.png", 38)
        ai_btn.clicked.connect(lambda: print("🤖 AI Chat opened!"))
        
        layout.addWidget(menu_btn)
        layout.addWidget(ai_btn)
        layout.addSpacing(30)
        
        # Title - simple text without gradient
        title = QLabel("DJ Blue AI")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #00ffff;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Right buttons
        cast_btn = HoverButton(ASSETS_DIR / "casticon.png", 28)
        opts_btn = HoverButton(ASSETS_DIR / "options.png", 28)
        close_btn = HoverButton(ASSETS_DIR / "close.png", 28)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(cast_btn)
        layout.addWidget(opts_btn)
        layout.addWidget(close_btn)
        
        return layout
        
    def create_progress_bar(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Time labels
        time_layout = QHBoxLayout()
        self.time_label = QLabel(self.format_time(self.current_time))
        self.total_label = QLabel(self.format_time(self.total_time))
        
        for label in [self.time_label, self.total_label]:
            label.setStyleSheet("color: #00ffff; font-size: 18px; font-weight: bold;")
        
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_label)
        
        # Slider
        self.progress_slider = SmoothSlider()
        self.progress_slider.setRange(0, self.total_time)
        self.progress_slider.setValue(self.current_time)
        self.progress_slider.valueChanged.connect(self.on_slider_change)
        self.progress_slider.setFixedHeight(30)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #23345b;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00ffff, stop:1 #ff00ff);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ffff;
                border: 3px solid #0a0e17;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
        """)
        
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setColor(QColor(0, 255, 255, 120))
        glow.setOffset(0, 0)
        self.progress_slider.setGraphicsEffect(glow)
        
        layout.addLayout(time_layout)
        layout.addWidget(self.progress_slider)
        
        return layout
        
    def create_controls(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.addStretch()
        
        self.shuffle_btn = HoverButton(ASSETS_DIR / "shuffle.png", 35)
        self.prev_btn = HoverButton(ASSETS_DIR / "previous.png", 42)
        self.play_btn = HoverButton(ASSETS_DIR / "play.png", 65)
        self.next_btn = HoverButton(ASSETS_DIR / "next.png", 42)
        self.repeat_btn = HoverButton(ASSETS_DIR / "repeat.png", 35)
        
        self.play_btn.clicked.connect(self.toggle_play)
        self.prev_btn.clicked.connect(self.previous_track)
        self.next_btn.clicked.connect(self.next_track)
        
        for btn in [self.shuffle_btn, self.prev_btn, self.play_btn, self.next_btn, self.repeat_btn]:
            layout.addWidget(btn)
        
        layout.addStretch()
        return layout
        
    def create_tabs(self):
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.tab_upnext = TabButton("UP NEXT")
        self.tab_lyrics = TabButton("LYRICS")
        self.tab_related = TabButton("RELATED")
        
        self.tab_upnext.set_active(True)
        
        self.tab_upnext.clicked.connect(lambda: self.switch_tab(0))
        self.tab_lyrics.clicked.connect(lambda: self.switch_tab(1))
        self.tab_related.clicked.connect(lambda: self.switch_tab(2))
        
        sep1 = QLabel("|")
        sep2 = QLabel("|")
        sep1.setStyleSheet("color: #444; font-size: 16px;")
        sep2.setStyleSheet("color: #444; font-size: 16px;")
        
        layout.addWidget(self.tab_upnext)
        layout.addWidget(sep1)
        layout.addWidget(self.tab_lyrics)
        layout.addWidget(sep2)
        layout.addWidget(self.tab_related)
        layout.addStretch()
        
        return layout
        
    def switch_tab(self, index):
        tabs = [self.tab_upnext, self.tab_lyrics, self.tab_related]
        names = ['UP NEXT', 'LYRICS', 'RELATED']
        for i, tab in enumerate(tabs):
            tab.set_active(i == index)
        print(f"📋 Switched to: {names[index]}")
        
    def toggle_play(self):
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            icon_path = ASSETS_DIR / "pause.png"
            self.timer.start()
            self.album_art.start_glow()
            print("▶️  Playing...")
        else:
            icon_path = ASSETS_DIR / "play.png"
            self.timer.stop()
            self.album_art.stop_glow()
            print("⏸️  Paused")
            
        try:
            pix = QPixmap(str(icon_path))
            if not pix.isNull():
                pix = pix.scaled(65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.play_btn.setIcon(QIcon(pix))
        except Exception as e:
            print(f"Error changing play icon: {e}")
        
    def update_progress(self):
        if self.current_time < self.total_time:
            self.current_time += 1
            self.progress_slider.setValue(self.current_time)
            self.time_label.setText(self.format_time(self.current_time))
        else:
            self.timer.stop()
            self.is_playing = False
            print("⏹️  Track ended")
            
    def on_slider_change(self, value):
        self.current_time = value
        self.time_label.setText(self.format_time(value))
        
    def previous_track(self):
        print("⏮️  Previous track")
        self.current_time = 0
        self.progress_slider.setValue(0)
        
    def next_track(self):
        print("⏭️  Next track")
        self.current_time = 0
        self.progress_slider.setValue(0)
        
    @staticmethod
    def format_time(seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"

# === MAIN ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = DJBlueAIMusicPlayer()
    player.show()
    sys.exit(app.exec())