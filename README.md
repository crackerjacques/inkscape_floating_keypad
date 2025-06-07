# Floating Keypad
Stylus shortcuts for tablets with insufficient buttons for Inkscape
<img width="680" alt="Screenshot_20250607_164244" src="https://github.com/user-attachments/assets/8c89c9d6-7b41-4753-ae8e-d997a9c854eb" />



# Tested Environments.

Plasma Wayland / Ubuntu 24.04 on Raspberry Pi 5

Plasma X11 / Ubuntu 24.04  
Hyprland / Arch Linux  

Currently works only with Linux

# Prepare

Ubuntu/Debian/RaspiOS
```
pip install inkex pyqt5 pyautogui
sudo apt install wmctrl xdotool
```
Arch Linux
```
sudo pacman -S wmctrl xdotool
pip install inkex pyqt5 pyautogui
```

# Install
```
git clone https://github.com/crackerjacques/inkscape_floating_keypad.git
mkdir -p  ~/.config/inkscape/extensions # Only if it is not already there, which is often the case.
cp -r ./inkscape_floating_keypad/floating_keypad ~/.config/inkscape/extensions #
```

Relaunch Inkscape.  
Then You can find Floating Keypad.  
Inkscape -> Extension -> Utillity -> Floating Keypad
