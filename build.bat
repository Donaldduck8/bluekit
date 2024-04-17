call "app_test\Scripts\activate.bat"

start pyinstaller --onefile --splash "app\resource\images\jellyfish_square.png" -i "app\resource\images\jellyfish_800_clipped.png" --uac-admin -n BlueKit demo.py