#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import subprocess
import os
import signal
import yaml
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSystemTrayIcon, QMenu, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import pyautogui

class NumpadPalette(QWidget):
    def __init__(self):
        super().__init__()
        self.inkscape_window_id = None
        self.collapsed = False
        self.normal_height = 280
        self.collapsed_height = 40
        self.shortcut_mode = False
        self.key_mappings = {}
        self.load_key_mappings()
        self.init_ui()
        self.setup_window()
        self.setup_tray_icon()
        self.find_inkscape_window()
    
    def load_key_mappings(self):
        config_file = os.path.join(os.path.dirname(__file__), "numpad_config.yaml")
        default_config = {
            '7': {'label': '7', 'key': '7', 'color': '#4a90e2'},
            '8': {'label': '8', 'key': '8', 'color': '#4a90e2'},
            '9': {'label': '9', 'key': '9', 'color': '#4a90e2'},
            '4': {'label': '4', 'key': '4', 'color': '#4a90e2'},
            '5': {'label': '5', 'key': '5', 'color': '#4a90e2'},
            '6': {'label': '6', 'key': '6', 'color': '#4a90e2'},
            '1': {'label': '1', 'key': '1', 'color': '#4a90e2'},
            '2': {'label': '2', 'key': '2', 'color': '#4a90e2'},
            '3': {'label': '3', 'key': '3', 'color': '#4a90e2'},
            '0': {'label': '0', 'key': '0', 'color': '#4a90e2'},
            'return': {'label': 'Enter', 'key': 'Return', 'color': '#44aa44'},
            'backspace': {'label': 'BS', 'key': 'BackSpace', 'color': '#ff8800'},
            'delete': {'label': 'Del', 'key': 'Delete', 'color': '#ff8800'}
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.key_mappings = yaml.safe_load(f)
                print(f"Loaded config from {config_file}")
            else:
                self.key_mappings = default_config
                self.save_default_config(config_file)
                print(f"Created default config at {config_file}")
        except Exception as e:
            print(f"Error loading config: {e}")
            self.key_mappings = default_config
    
    def save_default_config(self, config_file):
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.key_mappings, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Error saving default config: {e}")
    
    def setup_tray_icon(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.blue)
            icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)
            hide_action = tray_menu.addAction("Hide")
            hide_action.triggered.connect(self.hide)
            tray_menu.addSeparator()
            reload_action = tray_menu.addAction("Reload Config")
            reload_action.triggered.connect(self.reload_config)
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.close_application)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()
        except:
            pass
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def reload_config(self):
        print("Reloading configuration...")
        mode_state = self.shortcut_mode
        self.load_key_mappings()
        self.recreate_ui()
        self.shortcut_mode = mode_state
        if hasattr(self, 'mode_btn'):
            self.update_mode_button_style()
            self.update_all_buttons()
    
    def find_inkscape_window(self):
        try:
            result = subprocess.run(['wmctrl', '-lG'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inkscape.Inkscape' in line or 'org.inkscape.Inkscape' in line or 'Inkscape' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        self.inkscape_window_id = parts[0]
                        inkscape_x = int(parts[2])
                        inkscape_y = int(parts[3])
                        print(f"Found Inkscape window: {self.inkscape_window_id} at ({inkscape_x}, {inkscape_y})")
                        self.position_on_inkscape_screen(inkscape_x, inkscape_y)
                        return
            
            result = subprocess.run(['wmctrl', '-lx'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inkscape.Inkscape' in line or 'org.inkscape.Inkscape' in line:
                    self.inkscape_window_id = line.split()[0]
                    print(f"Found Inkscape window: {self.inkscape_window_id}")
                    break
                    
            if not self.inkscape_window_id:
                try:
                    result = subprocess.run(['xdotool', 'search', '--class', 'inkscape'], 
                                         capture_output=True, text=True)
                    if result.stdout.strip():
                        window_ids = result.stdout.strip().split('\n')
                        self.inkscape_window_id = hex(int(window_ids[0]))
                        print(f"Found Inkscape window via xdotool: {self.inkscape_window_id}")
                except:
                    pass
        except Exception as e:
            print(f"Window search error: {e}")
            print("Please ensure wmctrl is installed: sudo apt install wmctrl")
    
    def position_on_inkscape_screen(self, inkscape_x, inkscape_y):
        app = QApplication.instance()
        desktop = app.desktop()
        
        # Find which screen contains Inkscape
        for i in range(desktop.screenCount()):
            screen_geo = desktop.screenGeometry(i)
            if (screen_geo.x() <= inkscape_x < screen_geo.x() + screen_geo.width() and
                screen_geo.y() <= inkscape_y < screen_geo.y() + screen_geo.height()):
                # Position palette on this screen's right edge
                palette_x = screen_geo.x() + screen_geo.width() - self.width() - 50
                palette_y = screen_geo.y() + 50
                self.move(palette_x, palette_y)
                print(f"Positioned palette on screen {i} at ({palette_x}, {palette_y})")
                return
        
        # Fallback to primary screen
        screen = desktop.screenGeometry()
        self.move(screen.width() - self.width() - 50, 50)
    
    def get_button_label(self, key_id):
        if self.shortcut_mode:
            return self.key_mappings.get(key_id, {}).get('label', key_id)[:5]
        else:
            if key_id == 'return':
                return 'Enter'
            elif key_id == 'backspace':
                return 'BS'
            elif key_id == 'delete':
                return 'Del'
            return key_id
    
    def get_button_key(self, key_id):
        if self.shortcut_mode:
            return self.key_mappings.get(key_id, {}).get('key', key_id)
        else:
            if key_id == 'return':
                return 'Return'
            elif key_id == 'backspace':
                return 'BackSpace'
            elif key_id == 'delete':
                return 'Delete'
            return key_id
    
    def get_button_color(self, key_id):
        if self.shortcut_mode:
            return self.key_mappings.get(key_id, {}).get('color', '#4a90e2')
        else:
            if key_id == 'return':
                return '#44aa44'
            elif key_id in ['backspace', 'delete']:
                return '#ff8800'
            return '#4a90e2'
    
    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.title = QLabel("Numpad Palette")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        self.title.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.title)
        
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setSpacing(5)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        numpad_layout = QGridLayout()
        numpad_layout.setSpacing(10)
        
        self.btn_7 = self.create_button(
            self.get_button_label('7'),
            lambda: self.send_key_to_inkscape(self.get_button_key('7')),
            color=self.get_button_color('7')
        )
        numpad_layout.addWidget(self.btn_7, 0, 0)
        
        self.btn_8 = self.create_button(
            self.get_button_label('8'),
            lambda: self.send_key_to_inkscape(self.get_button_key('8')),
            color=self.get_button_color('8')
        )
        numpad_layout.addWidget(self.btn_8, 0, 1)
        
        self.btn_9 = self.create_button(
            self.get_button_label('9'),
            lambda: self.send_key_to_inkscape(self.get_button_key('9')),
            color=self.get_button_color('9')
        )
        numpad_layout.addWidget(self.btn_9, 0, 2)
        
        self.btn_4 = self.create_button(
            self.get_button_label('4'),
            lambda: self.send_key_to_inkscape(self.get_button_key('4')),
            color=self.get_button_color('4')
        )
        numpad_layout.addWidget(self.btn_4, 1, 0)
        
        self.btn_5 = self.create_button(
            self.get_button_label('5'),
            lambda: self.send_key_to_inkscape(self.get_button_key('5')),
            color=self.get_button_color('5')
        )
        numpad_layout.addWidget(self.btn_5, 1, 1)
        
        self.btn_6 = self.create_button(
            self.get_button_label('6'),
            lambda: self.send_key_to_inkscape(self.get_button_key('6')),
            color=self.get_button_color('6')
        )
        numpad_layout.addWidget(self.btn_6, 1, 2)
        
        self.btn_1 = self.create_button(
            self.get_button_label('1'),
            lambda: self.send_key_to_inkscape(self.get_button_key('1')),
            color=self.get_button_color('1')
        )
        numpad_layout.addWidget(self.btn_1, 2, 0)
        
        self.btn_2 = self.create_button(
            self.get_button_label('2'),
            lambda: self.send_key_to_inkscape(self.get_button_key('2')),
            color=self.get_button_color('2')
        )
        numpad_layout.addWidget(self.btn_2, 2, 1)
        
        self.btn_3 = self.create_button(
            self.get_button_label('3'),
            lambda: self.send_key_to_inkscape(self.get_button_key('3')),
            color=self.get_button_color('3')
        )
        numpad_layout.addWidget(self.btn_3, 2, 2)
        
        self.btn_0 = self.create_button(
            self.get_button_label('0'),
            lambda: self.send_key_to_inkscape(self.get_button_key('0')),
            color=self.get_button_color('0')
        )
        numpad_layout.addWidget(self.btn_0, 3, 0)
        
        self.btn_return = self.create_button(
            self.get_button_label('return'),
            lambda: self.send_key_to_inkscape(self.get_button_key('return')),
            color=self.get_button_color('return'),
            size=(100, 40)
        )
        numpad_layout.addWidget(self.btn_return, 3, 1, 1, 2)
        
        self.btn_backspace = self.create_button(
            self.get_button_label('backspace'),
            lambda: self.send_key_to_inkscape(self.get_button_key('backspace')),
            color=self.get_button_color('backspace')
        )
        numpad_layout.addWidget(self.btn_backspace, 4, 0)
        
        self.btn_delete = self.create_button(
            self.get_button_label('delete'),
            lambda: self.send_key_to_inkscape(self.get_button_key('delete')),
            color=self.get_button_color('delete')
        )
        numpad_layout.addWidget(self.btn_delete, 4, 1)
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        
        self.mode_btn = self.create_toggle_button("NUM", self.toggle_mode)
        self.update_mode_button_style()
        
        refresh_btn = self.create_button("↻", self.find_inkscape_window, 
                                       color="#44aa44", size=(35, 30))
        reload_btn = self.create_button("⟲", self.reload_config, 
                                      color="#4aa444", size=(35, 30))
        close_btn = self.create_button("×", self.close_application, 
                                     color="#ff4444", size=(35, 30))
        
        control_layout.addWidget(self.mode_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(reload_btn)
        control_layout.addStretch()
        control_layout.addWidget(close_btn)
        
        self.buttons_layout.addLayout(numpad_layout)
        self.buttons_layout.addLayout(control_layout)
        
        self.main_layout.addWidget(self.buttons_container)
        self.setLayout(self.main_layout)
    
    def recreate_ui(self):
        self.hide()
        if self.layout():
            QWidget().setLayout(self.layout())
        for child in self.findChildren(QWidget):
            child.setParent(None)
        self.init_ui()
        self.show()
    
    def create_button(self, text, callback, color="#4a90e2", size=(45, 40)):
        btn = QPushButton(text)
        btn.setFixedSize(size[0], size[1])
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #333;
                border-radius: 5px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        btn.setFocusPolicy(Qt.NoFocus)
        return btn
    
    def create_toggle_button(self, text, callback, color="#4a90e2", size=(50, 30)):
        btn = QPushButton(text)
        btn.setFixedSize(size[0], size[1])
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #333;
                border-radius: 5px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        btn.setFocusPolicy(Qt.NoFocus)
        return btn
    
    def toggle_mode(self):
        self.shortcut_mode = not self.shortcut_mode
        self.update_mode_button_style()
        self.update_all_buttons()
        mode_text = "shortcut" if self.shortcut_mode else "numpad"
        print(f"Mode switched to: {mode_text}")
    
    def update_mode_button_style(self):
        if self.shortcut_mode:
            self.mode_btn.setText("SC")
            self.mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff8800;
                    color: white;
                    border: 2px solid #ffaa00;
                    border-radius: 5px;
                    font-size: 9px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ffaa00;
                }
            """)
        else:
            self.mode_btn.setText("NUM")
            self.mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 5px;
                    font-size: 9px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5ba0f2;
                }
                QPushButton:pressed {
                    background-color: #3a80d2;
                }
            """)
    
    def update_all_buttons(self):
        buttons = {
            '7': self.btn_7, '8': self.btn_8, '9': self.btn_9,
            '4': self.btn_4, '5': self.btn_5, '6': self.btn_6,
            '1': self.btn_1, '2': self.btn_2, '3': self.btn_3,
            '0': self.btn_0, 'return': self.btn_return,
            'backspace': self.btn_backspace, 'delete': self.btn_delete
        }
        
        for key_id, button in buttons.items():
            button.setText(self.get_button_label(key_id))
            color = self.get_button_color(key_id)
            
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 1px solid #333;
                    border-radius: 5px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color)};
                }}
            """)
    
    def lighten_color(self, color):
        color_map = {
            "#4a90e2": "#5ba0f2", "#ff4444": "#ff6666", "#44aa44": "#66cc66",
            "#4aa444": "#6cc466", "#ff8800": "#ffaa00", "#888888": "#aaaaaa"
        }
        return color_map.get(color, color)
        
    def darken_color(self, color):
        color_map = {
            "#4a90e2": "#3a80d2", "#ff4444": "#dd2222", "#44aa44": "#228822",
            "#4aa444": "#2a8a24", "#ff8800": "#cc6600", "#888888": "#666666"
        }
        return color_map.get(color, color)
    
    def setup_window(self):
        self.setWindowTitle("Numpad Palette")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 120);
                border-radius: 10px;
            }
        """)
        
        self.setFixedSize(175, self.normal_height)
        
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - self.width() - 50, 50)
    
    def send_key_to_inkscape(self, key_combination):
        try:
            if not isinstance(key_combination, str):
                print(f"Invalid key combination type: {type(key_combination)}")
                return
                
            if not self.inkscape_window_id:
                self.find_inkscape_window()
                
            if self.inkscape_window_id:
                subprocess.run(['wmctrl', '-i', '-a', self.inkscape_window_id], 
                             capture_output=True)
                time.sleep(0.05)
            else:
                subprocess.run(['xdotool', 'windowactivate', '--sync', 
                              '$(xdotool search --class inkscape | head -1)'], 
                              shell=True, capture_output=True)
                time.sleep(0.05)
            
            final_key = str(key_combination)
                
            if '+' in final_key:
                keys = final_key.replace('ctrl', 'control')
                subprocess.run(['xdotool', 'key', keys], capture_output=True)
            else:
                subprocess.run(['xdotool', 'key', final_key], capture_output=True)
                
            mode_text = "shortcut" if self.shortcut_mode else "numpad"
            print(f"Sent key: {final_key} ({mode_text} mode)")
            
        except Exception as e:
            print(f"Key send error: {e}")
            
            try:
                if not isinstance(key_combination, str):
                    print(f"Fallback: Invalid key combination type: {type(key_combination)}")
                    return
                    
                final_key = str(key_combination)
                
                if '+' in final_key:
                    pyautogui.hotkey(*final_key.split('+'))
                else:
                    pyautogui.press(final_key.lower())
                        
                mode_text = "shortcut" if self.shortcut_mode else "numpad"
                print(f"Fallback sent key: {final_key} ({mode_text} mode)")
                        
            except Exception as fallback_error:
                print(f"Fallback error: {fallback_error}")
    
    def close_application(self):
        print("Quitting application...")
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        self.hide()
        QApplication.quit()
        os._exit(0)
    
    def closeEvent(self, event):
        print("closeEvent called")
        event.accept()
        self.close_application()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.y() < 40:
                self.toggle_collapse()
    
    def toggle_collapse(self):
        if self.collapsed:
            self.buttons_container.show()
            self.setFixedHeight(self.normal_height)
            self.collapsed = False
            self.title.setText("Numpad Palette")
        else:
            self.buttons_container.hide()
            self.setFixedHeight(self.collapsed_height)
            self.collapsed = True
            self.title.setText("Numpad Palette ▼")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_start') and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)

def check_dependencies():
    missing_tools = []
    
    try:
        subprocess.run(['wmctrl', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('wmctrl')
        
    try:
        subprocess.run(['xdotool', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_tools.append('xdotool')
        
    if missing_tools:
        print("Please install the following tools:")
        for tool in missing_tools:
            print(f"  sudo apt install {tool}")
        print()

def main():
    check_dependencies()
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    
    app.setQuitOnLastWindowClosed(False)
    
    palette = NumpadPalette()
    palette.show()
    
    print("Numpad Palette started")
    print("Usage:")
    print("- NUM: Numpad mode (direct number input)")
    print("- SC: Shortcut mode (YAML configured keys)")
    print("- Configure shortcuts in numpad_config.yaml")
    print("- ↻ button to refresh Inkscape window")
    print("- ⟲ button to reload configuration")
    print("- Drag window to move, × button to quit")
    
    signal.signal(signal.SIGINT, lambda *args: palette.close_application())
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()