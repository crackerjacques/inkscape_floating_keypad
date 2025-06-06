# inkscape_floating_keypad
Stylus shortcuts for tablets with insufficient buttons for Inkscape

# Tested Environments.

Plasma Wayland / Ubuntu 24.04 on Raspberry Pi 5

Plasma X11 / Ubuntu 24.04

Hyprland / Arch Linux

Currently works only with Linux

# floating keypad for Inkscape
<img width="453" alt="Screenshot_20250606_191751" src="https://github.com/user-attachments/assets/07a77355-dbac-415d-a173-93fe141b6f9e" />

# Prepare
```
pip install inkex pyqt5 pyautogui
sudo apt install wmctrl xdotool
```
# Install
```
git clone https://github.com/crackerjacques/inkscape_floating_keypad.git
mkdir -p  ~/.config/inkscape/extensions # Only if it is not already there, which is often the case.
cp -r ./inkscape_floating_keypad/floating_keypad ~/.config/inkscape/extensions #
```

Relaunch Inkscape.
Then You can find Floating Keypad
Inkscape -> Extension -> Utillity -> Floating Keypad
