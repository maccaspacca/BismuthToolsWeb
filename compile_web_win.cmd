cd "C:\Program Files (x86)\Bismuth\tools" 

rem - edit the above line to the path of your files

pyinstaller.exe --uac-admin --onefile --log-level=INFO --version-file=webversion.txt bismuthtoolsweb.py --icon=db.ico --hidden-import bismuthtoolsweb

pause
