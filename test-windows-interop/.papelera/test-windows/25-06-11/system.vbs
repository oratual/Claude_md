Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set colItems = objWMIService.ExecQuery("Select * from Win32_OperatingSystem")

For Each objItem in colItems
    WScript.Echo "OS Name: " & objItem.Name
    WScript.Echo "Version: " & objItem.Version
    WScript.Echo "Build Number: " & objItem.BuildNumber
    WScript.Echo "Architecture: " & objItem.OSArchitecture
    WScript.Echo "Total Memory: " & Round(objItem.TotalVisibleMemorySize / 1024 / 1024, 2) & " GB"
    WScript.Echo "Free Memory: " & Round(objItem.FreePhysicalMemory / 1024 / 1024, 2) & " GB"
Next

' Create a file
Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.CreateTextFile("C:\temp\vbs_test.txt", True)
file.WriteLine "Created by VBScript at " & Now()
file.Close
WScript.Echo vbCrLf & "Created file: C:\temp\vbs_test.txt"