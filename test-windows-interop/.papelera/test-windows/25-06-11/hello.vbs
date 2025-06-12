' VBScript simple
MsgBox "Hola desde VBScript ejecutado en WSL!", vbInformation, "Test VBS"

' Obtener información del sistema
Set objWMI = GetObject("winmgmts:\\.\root\cimv2")
Set colItems = objWMI.ExecQuery("Select * from Win32_ComputerSystem")

For Each objItem in colItems
    WScript.Echo "Nombre PC: " & objItem.Name
    WScript.Echo "Fabricante: " & objItem.Manufacturer
    WScript.Echo "Modelo: " & objItem.Model
Next

WScript.Echo "Script VBS completado!"