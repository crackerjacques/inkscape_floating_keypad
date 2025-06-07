#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inkex
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
            command = f'nohup "{sys.executable}" "{keypad_script}" > /dev/null 2>&1 &'
            os.system(command)
        except:
            # Fallback
            try:
                os.system(f'"{sys.executable}" "{keypad_script}" &')
            except:
                pass

if __name__ == '__main__':
    FloatingKeypadLauncher().run()
