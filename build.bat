copy opencsv.cmd .\dist\
pyinstaller.exe -F idsub.py
pyinstaller.exe -F mondrop.py
rmdir /Q /S .\build

copy /B /Y .\dist\mondrop.exe \\PC-ZAX-001\Share\csv2lua\
