call "bluekit_env\Scripts\activate.bat"

start pyinstaller --onefile --hide-console hide-early --splash "app\resource\images\jellyfish_square.png" -i "app\resource\images\jellyfish_800_clipped.png" --uac-admin -n Bluekit bluekit.py