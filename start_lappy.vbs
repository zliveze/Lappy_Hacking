' start_lappy.vbs - Chạy Lappy Lab hoàn toàn ẩn (không có cửa sổ nào)
' VBScript không hiển thị cửa sổ console

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Lấy thư mục hiện tại của script
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Chuyển đến thư mục script
objShell.CurrentDirectory = strScriptPath

' Kiểm tra quyền admin
Function IsAdmin()
    On Error Resume Next
    CreateObject("WScript.Shell").Run "net session", 0, True
    IsAdmin = (Err.Number = 0)
    On Error GoTo 0
End Function

' Nếu không có quyền admin, chạy lại với quyền admin
If Not IsAdmin() Then
    ' Chạy lại với quyền admin (ẩn hoàn toàn)
    objShell.Run "powershell -WindowStyle Hidden -Command ""Start-Process wscript -ArgumentList '" & WScript.ScriptFullName & "' -Verb RunAs""", 0, False
    WScript.Quit
End If

' Tìm pythonw.exe
pythonwPath = ""
pythonPaths = Array("pythonw", "python")

For Each pythonCmd In pythonPaths
    On Error Resume Next
    objShell.Run "where " & pythonCmd, 0, True
    If Err.Number = 0 Then
        pythonwPath = pythonCmd
        Exit For
    End If
    On Error GoTo 0
Next

' Chạy ứng dụng hoàn toàn ẩn
If pythonwPath <> "" Then
    ' Sử dụng pythonw để chạy main.pyw (hoàn toàn ẩn)
    objShell.Run pythonwPath & " main.pyw", 0, False
Else
    ' Nếu không tìm thấy python, hiển thị thông báo lỗi
    MsgBox "Không tìm thấy Python! Vui lòng cài đặt Python.", vbCritical, "Lỗi"
End If
