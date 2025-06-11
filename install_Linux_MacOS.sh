#!/bin/bash

# install.sh - Script cài đặt Lappy Lab 4.1 cho Linux/macOS

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        LAPPY LAB 4.1                        ║"
    echo "║                   Cursor Management Tool                     ║"
    echo "║                     Cài đặt tự động                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

check_python() {
    echo -e "${BLUE}[1/4] Kiểm tra Python...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python chưa được cài đặt!"
        echo "Vui lòng cài đặt Python 3.8+ từ: https://python.org"
        exit 1
    fi
    
    # Kiểm tra phiên bản Python
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Cần Python 3.8 trở lên. Phiên bản hiện tại: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION đã được cài đặt"
}

check_pip() {
    echo -e "${BLUE}[2/4] Kiểm tra pip...${NC}"
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip chưa được cài đặt!"
        echo "Vui lòng cài đặt pip"
        exit 1
    fi
    
    print_success "pip đã sẵn sàng"
}

install_dependencies() {
    echo -e "${BLUE}[3/4] Cài đặt dependencies...${NC}"
    echo "Đang cài đặt các package cần thiết..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Không tìm thấy file requirements.txt!"
        exit 1
    fi
    
    $PIP_CMD install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        print_error "Lỗi cài đặt dependencies!"
        echo "Thử chạy lại với sudo hoặc sử dụng virtual environment"
        exit 1
    fi
    
    print_success "Đã cài đặt thành công tất cả dependencies"
}

check_installation() {
    echo -e "${BLUE}[4/4] Kiểm tra cài đặt...${NC}"
    
    $PYTHON_CMD -c "import tkinter, colorama, requests, psutil; print('✅ Tất cả module đã sẵn sàng')" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        print_error "Một số module chưa được cài đặt đúng"
        exit 1
    fi
}

make_executable() {
    # Tạo file executable cho Linux/macOS
    chmod +x run.py
    chmod +x build.py
    
    # Tạo symlink nếu muốn
    if [ -w "/usr/local/bin" ]; then
        ln -sf "$(pwd)/run.py" "/usr/local/bin/lappylab" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_info "Đã tạo symlink: lappylab -> $(pwd)/run.py"
        fi
    fi
}

# Main script
clear
print_header

# Kiểm tra hệ điều hành
OS=$(uname -s)
print_info "Hệ điều hành: $OS"

# Các bước cài đặt
check_python
check_pip
install_dependencies
check_installation
make_executable

# Hoàn thành
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    CÀI ĐẶT HOÀN TẤT!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_success "Lappy Lab 4.1 đã sẵn sàng sử dụng!"
echo ""
echo "Cách chạy ứng dụng:"
echo "  1. Chạy file: ./run.py"
echo "  2. Hoặc: $PYTHON_CMD main.py"
echo "  3. Hoặc: $PYTHON_CMD run.py"
if command -v lappylab &> /dev/null; then
    echo "  4. Hoặc: lappylab (từ bất kỳ đâu)"
fi
echo ""

# Hỏi có muốn chạy ngay không
read -p "Bạn có muốn chạy Lappy Lab ngay bây giờ? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Đang khởi động Lappy Lab..."
    $PYTHON_CMD run.py
else
    echo ""
    echo "👋 Cảm ơn bạn đã cài đặt Lappy Lab 4.1!"
    echo "Chạy '$PYTHON_CMD run.py' để bắt đầu sử dụng."
fi
