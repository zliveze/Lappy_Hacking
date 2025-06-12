# run_hidden.ps1 - Chạy Lappy Lab hoàn toàn ẩn (không có cửa sổ CMD)

# Thiết lập để ẩn PowerShell window
Add-Type -Name Window -Namespace Console -MemberDefinition '
[DllImport("Kernel32.dll")]
public static extern IntPtr GetConsoleWindow();

[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
'

# Ẩn PowerShell console
$consolePtr = [Console.Window]::GetConsoleWindow()
[Console.Window]::ShowWindow($consolePtr, 0) # 0 = SW_HIDE

# Chuyển đến thư mục script
Set-Location -Path $PSScriptRoot

# Kiểm tra quyền admin
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Nếu không có quyền admin, chạy lại với quyền admin
if (-not (Test-Administrator)) {
    Write-Host "Requesting administrator privileges..."
    Start-Process PowerShell -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Tìm pythonw.exe
$pythonwPath = $null
$pythonPaths = @(
    "pythonw",
    "python",
    "$env:LOCALAPPDATA\Programs\Python\Python*\pythonw.exe",
    "$env:PROGRAMFILES\Python*\pythonw.exe",
    "$env:PROGRAMFILES(X86)\Python*\pythonw.exe"
)

foreach ($path in $pythonPaths) {
    try {
        if ($path -like "*\*") {
            # Đường dẫn có wildcard
            $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $pythonwPath = $found.FullName
                break
            }
        } else {
            # Command name
            $result = Get-Command $path -ErrorAction SilentlyContinue
            if ($result) {
                $pythonwPath = $result.Source
                break
            }
        }
    } catch {
        continue
    }
}

# Chạy ứng dụng
if ($pythonwPath) {
    Write-Host "Starting Lappy Lab with: $pythonwPath"
    Start-Process -FilePath $pythonwPath -ArgumentList "main.pyw" -WindowStyle Hidden -WorkingDirectory $PSScriptRoot
} else {
    Write-Host "Python not found! Please install Python."
    Start-Sleep -Seconds 3
}
