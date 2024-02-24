@echo off
echo Set WshShell = CreateObject("WScript.Shell") > hide.vbs
echo WshShell.Run "python app.py", 0 >> hide.vbs
echo WScript.Sleep 1000 >> hide.vbs
echo WshShell.Run "http://127.0.0.1:5000/", 1 >> hide.vbs
cscript //nologo hide.vbs
del hide.vbs
