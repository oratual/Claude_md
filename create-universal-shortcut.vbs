' Crear acceso directo universal que no depende de versión de Ubuntu

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
DesktopPath = WshShell.SpecialFolders("Desktop")

' Copiar el archivo VBS al escritorio
ScriptPath = DesktopPath & "\LauncherClaude.vbs"
VbsContent = "' LauncherClaude - Ejecutar directamente" & vbCrLf & _
             "Set objShell = CreateObject(""WScript.Shell"")" & vbCrLf & _
             "objShell.CurrentDirectory = objShell.ExpandEnvironmentStrings(""%USERPROFILE%"")" & vbCrLf & _
             "objShell.Run """"""C:\Program Files\WezTerm\wezterm-gui.exe"""""" start -- wsl -e bash -lc """"cd ~/glados && ~/glados/scripts/launchers/proyecto-menu-v2.sh"""""", 0, False"

' Escribir el archivo VBS
Set objFile = fso.CreateTextFile(ScriptPath, True)
objFile.Write VbsContent
objFile.Close

' Crear acceso directo al VBS
Set oShellLink = WshShell.CreateShortcut(DesktopPath & "\LauncherClaude.lnk")
oShellLink.TargetPath = ScriptPath
oShellLink.WorkingDirectory = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
oShellLink.IconLocation = "C:\Program Files\WezTerm\wezterm-gui.exe, 0"
oShellLink.Description = "Menu principal de GLADOS con Claude"
oShellLink.Save

MsgBox "Acceso directo universal creado. No depende de la version de Ubuntu.", 64, "GLADOS"