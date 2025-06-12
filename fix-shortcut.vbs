' Arreglar acceso directo LauncherClaude.lnk

Set WshShell = CreateObject("WScript.Shell")
DesktopPath = WshShell.SpecialFolders("Desktop")

' Eliminar acceso directo antiguo si existe
Set fso = CreateObject("Scripting.FileSystemObject")
oldLink = DesktopPath & "\LauncherClaude.lnk"
If fso.FileExists(oldLink) Then
    fso.DeleteFile(oldLink)
End If

' Crear nuevo acceso directo
Set oShellLink = WshShell.CreateShortcut(DesktopPath & "\LauncherClaude.lnk")
oShellLink.TargetPath = "\\wsl.localhost\Ubuntu\home\lauta\glados\LauncherClaude.bat"
oShellLink.WorkingDirectory = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
oShellLink.IconLocation = "C:\Program Files\WezTerm\wezterm-gui.exe, 0"
oShellLink.Description = "Menu principal de GLADOS con Claude"
oShellLink.Save

MsgBox "Acceso directo 'LauncherClaude' actualizado en el escritorio", 64, "GLADOS"