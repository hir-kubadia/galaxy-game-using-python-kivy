import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "includes": ["kivy"], "include_msvcr": True, "include_files": ["begin.wav", "bg_horizontal.jpg", "bg_vertical.jpg", "Eurostile.ttf", "galaxy.kv", "galaxy.wav", "game_icon.jpg", "gameover_impact.wav", "menu.kv", "menu.py", "music1.wav", "Sackers-Gothic-Std-Light.ttf", "tile_generation.py", "transforms.py", "user_actions.py"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Galaxy 3D",
    version="1.0",
    description="Dive into the Endless Galaxy!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)
