#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import subprocess
import os
import signal
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSystemTrayIcon, QMenu)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import pyautogui

class FloatingKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.inkscape_window_id = None
        self.collapsed = False
        self.normal_height = 250
        self.collapsed_height = 40
        self.init_ui()
        self.setup_window()
        self.setup_tray_icon()
        self.find_inkscape_window()
        
    def setup_tray_icon(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)
            
            # Tray menu
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)
            hide_action = tray_menu.addAction("Hide")
            hide_action.triggered.connect(self.hide)
            tray_menu.addSeparator()
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.close_application)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()
        except:
            pass
    
    def tray_icon_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
        
    def find_inkscape_window(self):
        """Find Inkscape window"""
        try:
            # Find Inkscape window using wmctrl with class name
            result = subprocess.run(['wmctrl', '-lx'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                # Check for Inkscape window class (more accurate)
                if 'inkscape.Inkscape' in line or 'org.inkscape.Inkscape' in line:
                    self.inkscape_window_id = line.split()[0]
                    print(f"Found Inkscape window: {self.inkscape_window_id}")
                    break
                    
            # If not found by class, try xdotool search
            if not self.inkscape_window_id:
                try:
                    result = subprocess.run(['xdotool', 'search', '--class', 'inkscape'], 
                                         capture_output=True, text=True)
                    if result.stdout.strip():
                        # Get the first window ID
                        window_ids = result.stdout.strip().split('\n')
                        self.inkscape_window_id = hex(int(window_ids[0]))
                        print(f"Found Inkscape window via xdotool: {self.inkscape_window_id}")
                except:
                    pass
                    
        except Exception as e:
            print(f"Window search error: {e}")
            print("Please ensure wmctrl is installed: sudo apt install wmctrl")
        
    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.title = QLabel("Inkscape Keypad")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        self.title.setCursor(Qt.PointingHandCursor)
        self.main_layout.addWidget(self.title)
        
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setSpacing(5)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        basic_layout = QHBoxLayout()
        basic_layout.setSpacing(3)
        
        copy_btn = self.create_button("Copy", lambda: self.send_key_to_inkscape('ctrl+c'))
        paste_btn = self.create_button("Paste", lambda: self.send_key_to_inkscape('ctrl+v'))
        cut_btn = self.create_button("Cut", lambda: self.send_key_to_inkscape('ctrl+x'))
        
        basic_layout.addWidget(copy_btn)
        basic_layout.addWidget(paste_btn)
        basic_layout.addWidget(cut_btn)
        
        edit_layout = QHBoxLayout()
        edit_layout.setSpacing(3)
        
        undo_btn = self.create_button("Undo", lambda: self.send_key_to_inkscape('ctrl+z'))
        redo_btn = self.create_button("Redo", lambda: self.send_key_to_inkscape('ctrl+y'))
        del_btn = self.create_button("Del", lambda: self.send_key_to_inkscape('Delete'))
        
        edit_layout.addWidget(undo_btn)
        edit_layout.addWidget(redo_btn)
        edit_layout.addWidget(del_btn)
        
        select_layout = QHBoxLayout()
        select_layout.setSpacing(3)
        
        all_btn = self.create_button("All", lambda: self.send_key_to_inkscape('ctrl+a'))
        group_btn = self.create_button("Group", lambda: self.send_key_to_inkscape('ctrl+g'))
        ungroup_btn = self.create_button("Ungrp", lambda: self.send_key_to_inkscape('ctrl+shift+g'))
        
        select_layout.addWidget(all_btn)
        select_layout.addWidget(group_btn)
        select_layout.addWidget(ungroup_btn)
        
        transform_layout = QHBoxLayout()
        transform_layout.setSpacing(3)
        
        duplicate_btn = self.create_button("Dup", lambda: self.send_key_to_inkscape('ctrl+d'))
        flip_h_btn = self.create_button("FlipH", lambda: self.send_key_to_inkscape('h'))
        flip_v_btn = self.create_button("FlipV", lambda: self.send_key_to_inkscape('v'))
        
        transform_layout.addWidget(duplicate_btn)
        transform_layout.addWidget(flip_h_btn)
        transform_layout.addWidget(flip_v_btn)
        
        layer_layout = QHBoxLayout()
        layer_layout.setSpacing(3)
        
        raise_btn = self.create_button("Raise", lambda: self.send_key_to_inkscape('Page_Up'))
        lower_btn = self.create_button("Lower", lambda: self.send_key_to_inkscape('Page_Down'))
        front_btn = self.create_button("Front", lambda: self.send_key_to_inkscape('Home'))
        back_btn = self.create_button("Back", lambda: self.send_key_to_inkscape('End'))
        
        layer_layout.addWidget(raise_btn)
        layer_layout.addWidget(lower_btn)
        layer_layout.addWidget(front_btn)
        layer_layout.addWidget(back_btn)
        
        util_layout = QHBoxLayout()
        util_layout.setSpacing(3)
        
        refresh_btn = self.create_button("↻", self.find_inkscape_window, color="#44aa44")
        minimize_btn = self.create_button("_", self.hide, color="#888888")
        close_btn = self.create_button("×", self.close_application, color="#ff4444")
        
        util_layout.addWidget(refresh_btn)
        util_layout.addWidget(minimize_btn)
        util_layout.addStretch()
        util_layout.addWidget(close_btn)
        
        self.buttons_layout.addLayout(basic_layout)
        self.buttons_layout.addLayout(edit_layout)
        self.buttons_layout.addLayout(select_layout)
        self.buttons_layout.addLayout(transform_layout)
        self.buttons_layout.addLayout(layer_layout)
        self.buttons_layout.addLayout(util_layout)
        
        self.main_layout.addWidget(self.buttons_container)
        
        self.setLayout(self.main_layout)
        
    def create_button(self, text, callback, color="#4a90e2"):
        btn = QPushButton(text)
        btn.setFixedSize(50, 30)
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
        # Prevent focus
        btn.setFocusPolicy(Qt.NoFocus)
        return btn
        
    def lighten_color(self, color):
        color_map = {
            "#4a90e2": "#5ba0f2",
            "#ff4444": "#ff6666",
            "#44aa44": "#66cc66",
            "#888888": "#aaaaaa"
        }
        return color_map.get(color, color)
        
    def darken_color(self, color):
        color_map = {
            "#4a90e2": "#3a80d2",
            "#ff4444": "#dd2222",
            "#44aa44": "#228822",
            "#888888": "#666666"
        }
        return color_map.get(color, color)
        
    def setup_window(self):
        # Window settings
        self.setWindowTitle("Inkscape Floating Keypad")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Prevent focus
        self.setFocusPolicy(Qt.NoFocus)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 120);
                border-radius: 10px;
            }
        """)
        
        self.setFixedSize(220, self.normal_height)
        
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - self.width() - 50, 50)
        
    def send_key_to_inkscape(self, key_combination):
        try:
            if not self.inkscape_window_id:
                self.find_inkscape_window()
                
            if self.inkscape_window_id:
                subprocess.run(['wmctrl', '-i', '-a', self.inkscape_window_id], 
                             capture_output=True)
                time.sleep(0.05)  # Brief wait
            else:
                subprocess.run(['xdotool', 'windowactivate', '--sync', 
                              '$(xdotool search --class inkscape | head -1)'], 
                              shell=True, capture_output=True)
                time.sleep(0.05)
                
            if '+' in key_combination:
                keys = key_combination.replace('ctrl', 'control').replace('+', '+')
                subprocess.run(['xdotool', 'key', keys], capture_output=True)
            else:
                subprocess.run(['xdotool', 'key', key_combination], capture_output=True)
                
            print(f"Sent key: {key_combination}")
            
        except Exception as e:
            print(f"Key send error: {e}")
            print("Please ensure xdotool is installed: sudo apt install xdotool")
            
            try:
                if '+' in key_combination:
                    pyautogui.hotkey(*key_combination.split('+'))
                else:
                    pyautogui.press(key_combination.lower())
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
        """Handle window close event"""
        print("closeEvent called")
        event.accept()
        self.close_application()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click on window"""
        if event.button() == Qt.LeftButton:
            if event.y() < 40:
                self.toggle_collapse()
    
    def toggle_collapse(self):
        """Toggle between collapsed and expanded state"""
        if self.collapsed:
            # Expand
            self.buttons_container.show()
            self.setFixedHeight(self.normal_height)
            self.collapsed = False
            self.title.setText("Inkscape Keypad")
        else:
            # Collapse
            self.buttons_container.hide()
            self.setFixedHeight(self.collapsed_height)
            self.collapsed = True
            self.title.setText("Inkscape Keypad ▼")
    
    def mousePressEvent(self, event):
        """Enable window dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Drag window"""
        if hasattr(self, 'drag_start') and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)

def check_dependencies():
    """Check required dependencies"""
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
    # Check dependencies
    check_dependencies()
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    
    app.setQuitOnLastWindowClosed(False)
    
    keypad = FloatingKeyboard()
    keypad.show()
    
    print("Inkscape Floating Keypad started")
    print("Usage:")
    print("- Click buttons to send keys to Inkscape")
    print("- ↻ button to refresh Inkscape window")
    print("- _ button to minimize (to system tray)")
    print("- Drag window to move")
    print("- × button to quit")
    
    signal.signal(signal.SIGINT, lambda *args: keypad.close_application())
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()