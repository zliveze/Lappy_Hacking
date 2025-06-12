# build_advanced.ps1 - Advanced build script cho Lappy Lab 4.1

param(
    [switch]$Clean,
    [switch]$Installer,
    [switch]$Quick,
    [switch]$Help
)

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Magenta = "Magenta"

function Write-Header {
    Write-Host "========================================" -ForegroundColor $Cyan
    Write-Host "🏗️ Lappy Lab 4.1 - Advanced Build Script" -ForegroundColor $Cyan
    Write-Host "========================================" -ForegroundColor $Cyan
    Write-Host ""
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️ $Message" -ForegroundColor $Yellow
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️ $Message" -ForegroundColor $Cyan
}

function Show-Help {
    Write-Header
    Write-Host "📋 CÁCH SỬ DỤNG:" -ForegroundColor $Magenta
    Write-Host ""
    Write-Host "  .\build_advanced.ps1                # Build thông thường"
    Write-Host "  .\build_advanced.ps1 -Clean         # Build + Clean"
    Write-Host "  .\build_advanced.ps1 -Installer     # Build + Installer"
    Write-Host "  .\build_advanced.ps1 -Quick         # Quick build (auto)"
    Write-Host "  .\build_advanced.ps1 -Help          # Hiển thị help"
    Write-Host ""
    Write-Host "📦 OUTPUT:" -ForegroundColor $Magenta
    Write-Host "  - dist/LappyLab.exe                 # Executable file"
    Write-Host "  - LappyLab_Setup.exe                # Installer (nếu có -Installer)"
    Write-Host ""
    Write-Host "🎨 ICON:" -ForegroundColor $Magenta
    Write-Host "  - Tự động sử dụng: public/image/icon.ico"
    Write-Host ""
}

function Test-Requirements {
    Write-Info "Kiểm tra requirements..."
    
    # Kiểm tra Python
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python: $pythonVersion"
        } else {
            Write-Error "Python không được tìm thấy!"
            return $false
        }
    } catch {
        Write-Error "Python không được tìm thấy!"
        return $false
    }
    
    # Kiểm tra PyInstaller
    try {
        python -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PyInstaller đã sẵn sàng"
        } else {
            Write-Warning "PyInstaller chưa được cài đặt"
            Write-Info "Đang cài đặt PyInstaller..."
            pip install pyinstaller
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PyInstaller đã được cài đặt"
            } else {
                Write-Error "Không thể cài đặt PyInstaller"
                return $false
            }
        }
    } catch {
        Write-Error "Lỗi kiểm tra PyInstaller"
        return $false
    }
    
    # Kiểm tra icon
    if (Test-Path "public/image/icon.ico") {
        Write-Success "Icon tìm thấy: public/image/icon.ico"
    } else {
        Write-Warning "Không tìm thấy icon"
    }
    
    return $true
}

function Start-Build {
    Write-Info "Bắt đầu build executable..."
    Write-Host "⏳ Quá trình này có thể mất vài phút..." -ForegroundColor $Yellow
    Write-Host ""
    
    # Chạy build script
    python build.py
    
    # Kiểm tra kết quả
    if (Test-Path "dist/LappyLab.exe") {
        $size = (Get-Item "dist/LappyLab.exe").Length
        $sizeMB = [math]::Round($size / 1MB, 1)
        Write-Success "Build thành công!"
        Write-Success "File: dist/LappyLab.exe ($sizeMB MB)"
        return $true
    } else {
        Write-Error "Build thất bại!"
        return $false
    }
}

function Start-QuickBuild {
    Write-Info "Quick Build Mode - Tự động build + clean"
    
    if (-not (Test-Requirements)) {
        return $false
    }
    
    if (Start-Build) {
        Write-Info "Dọn dẹp files tạm..."
        python -c "from build import clean_build_files; clean_build_files()"
        Write-Success "Quick build hoàn tất!"
        return $true
    }
    
    return $false
}

# Main logic
if ($Help) {
    Show-Help
    exit 0
}

Write-Header

if ($Quick) {
    $success = Start-QuickBuild
} else {
    if (-not (Test-Requirements)) {
        Write-Error "Requirements không đủ!"
        exit 1
    }
    
    $success = Start-Build
    
    if ($success -and $Clean) {
        Write-Info "Dọn dẹp files tạm..."
        python -c "from build import clean_build_files; clean_build_files()"
    }
    
    if ($success -and $Installer) {
        Write-Info "Tạo installer..."
        python -c "from build import create_installer; create_installer()"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor $Cyan
if ($success) {
    Write-Host "🎉 BUILD HOÀN TẤT!" -ForegroundColor $Green
    Write-Host "🚀 Có thể chạy: dist/LappyLab.exe" -ForegroundColor $Green
} else {
    Write-Host "❌ BUILD THẤT BẠI!" -ForegroundColor $Red
}
Write-Host "========================================" -ForegroundColor $Cyan

# Mở thư mục dist nếu build thành công
if ($success -and (Test-Path "dist")) {
    $choice = Read-Host "Bạn có muốn mở thư mục dist? (y/N)"
    if ($choice -eq "y" -or $choice -eq "Y") {
        Start-Process "explorer" -ArgumentList "dist"
    }
}
