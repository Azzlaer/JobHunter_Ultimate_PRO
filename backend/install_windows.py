import json, pathlib, re, sys, winreg
HOST="com.azzlaer.jobhunter"
ROOT=pathlib.Path(__file__).resolve().parent
if len(sys.argv)<2 or not re.fullmatch(r"[a-p]{32}",sys.argv[1].strip()):
    raise SystemExit("Uso: py install_windows.py <ID_EXTENSION_CHROME>")
extid=sys.argv[1].strip()
launcher=ROOT/"jobhunter_host.cmd"
launcher.write_text('@echo off\r\n"'+sys.executable+'" "'+str(ROOT/"native_host.py")+'"\r\n',encoding="utf-8")
manifest=ROOT/"native_host_manifest.json"
manifest.write_text(json.dumps({"name":HOST,"description":"JobHunter SQLite local","path":str(launcher),"type":"stdio","allowed_origins":["chrome-extension://"+extid+"/"]},indent=2),encoding="utf-8")
with winreg.CreateKey(winreg.HKEY_CURRENT_USER,"Software\\Google\\Chrome\\NativeMessagingHosts\\"+HOST) as key:
    winreg.SetValueEx(key,"",0,winreg.REG_SZ,str(manifest))
print("Instalado para",extid,". Reinicia Chrome.")
