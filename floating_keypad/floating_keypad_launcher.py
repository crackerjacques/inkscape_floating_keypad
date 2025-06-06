#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inkex
import subprocess
import os
import sys

class FloatingKeypadLauncher(inkex.EffectExtension):
    """Launch floating keypad as Inkscape extension"""
    
    def effect(self):
        ext_dir = os.path.dirname(os.path.abspath(__file__))
        keypad_script = os.path.join(ext_dir, "floating_keypad.py")
        
        if not os.path.exists(keypad_script):
            return
        
        try:
            if sys.platform.startswith('linux'):
                subprocess.Popen([sys.executable, keypad_script], 
                               start_new_session=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif sys.platform == 'darwin':
                subprocess.Popen([sys.executable, keypad_script],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif sys.platform == 'win32':
                subprocess.Popen([sys.executable, keypad_script],
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        except:
            pass

if __name__ == '__main__':
    FloatingKeypadLauncher().run()