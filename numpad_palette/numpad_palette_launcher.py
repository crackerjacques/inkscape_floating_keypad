#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inkex
import os
import sys

class NumpadPaletteLauncher(inkex.EffectExtension):
    def effect(self):
        ext_dir = os.path.dirname(os.path.abspath(__file__))
        palette_script = os.path.join(ext_dir, "numpad_palette.py")
        
        if not os.path.exists(palette_script):
            return
        
        try:
            command = f'nohup "{sys.executable}" "{palette_script}" > /dev/null 2>&1 &'
            os.system(command)
        except:
            try:
                os.system(f'"{sys.executable}" "{palette_script}" &')
            except:
                pass

if __name__ == '__main__':
    NumpadPaletteLauncher().run() 
