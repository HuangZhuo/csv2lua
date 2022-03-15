copy opencsv.cmd .\dist\
pyinstaller.exe -F idsub.py
pyinstaller.exe -F mondrop.py
rmdir /q /s .\build