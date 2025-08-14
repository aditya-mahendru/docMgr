#!/usr/bin/env python3
"""
Setup script for image processing functionality
Helps users install and configure required dependencies
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = [
        'PIL', 'pytesseract', 'cv2', 'groq'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_python_packages():
    """Install required Python packages"""
    print("\n📦 Installing Python packages...")
    
    packages_to_install = [
        'Pillow>=10.0.0',
        'pytesseract>=0.3.10', 
        'opencv-python>=4.8.0',
        'groq>=0.4.0'
    ]
    
    for package in packages_to_install:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR installation...")
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Tesseract OCR is installed")
        print(f"   Version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR is not installed")
        return False

def install_tesseract():
    """Install Tesseract OCR based on the operating system"""
    print("\n📥 Installing Tesseract OCR...")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return run_command("brew install tesseract", "Installing Tesseract via Homebrew")
    
    elif system == "linux":
        # Try different package managers
        if run_command("which apt-get", "Checking for apt-get"):
            return run_command("sudo apt-get update && sudo apt-get install -y tesseract-ocr", 
                             "Installing Tesseract via apt-get")
        elif run_command("which yum", "Checking for yum"):
            return run_command("sudo yum install -y tesseract", 
                             "Installing Tesseract via yum")
        elif run_command("which dnf", "Checking for dnf"):
            return run_command("sudo dnf install -y tesseract", 
                             "Installing Tesseract via dnf")
        else:
            print("❌ No supported package manager found")
            return False
    
    elif system == "windows":
        print("❌ Windows installation not supported via this script")
        print("   Please download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def check_groq_api_key():
    """Check if Groq API key is configured"""
    print("\n🔑 Checking Groq API key configuration...")
    
    # Load from .env file if it exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if groq_api_key:
        print("✅ GROQ_API_KEY is configured")
        print(f"   Key: {groq_api_key[:8]}...{groq_api_key[-4:]}")
        return True
    else:
        print("❌ GROQ_API_KEY is not configured")
        return False

def setup_groq_api_key():
    """Help user set up Groq API key"""
    print("\n🔑 Setting up Groq API key...")
    
    print("To use image processing, you need a Groq API key:")
    print("1. Sign up at https://console.groq.com/")
    print("2. Create an API key")
    print("3. Add it to your .env file")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        if os.path.exists('env_example.txt'):
            print("\n📝 Creating .env file from template...")
            with open('env_example.txt', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created from template")
        else:
            print("\n📝 Creating .env file...")
            with open('.env', 'w') as f:
                f.write("# Document Manager API Environment Variables\n\n")
                f.write("# Upload directory (optional, defaults to 'uploads')\n")
                f.write("UPLOAD_DIR=uploads\n\n")
                f.write("# Database path (optional, defaults to 'documents.db')\n")
                f.write("DATABASE_PATH=documents.db\n\n")
                f.write("# Groq API key for image description generation (required for image processing)\n")
                f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            print("✅ .env file created")
    
    print("\n📝 Please edit your .env file and add your Groq API key:")
    print("   GROQ_API_KEY=your_actual_api_key_here")
    
    return True

def test_setup():
    """Test the complete setup"""
    print("\n🧪 Testing the complete setup...")
    
    try:
        from test_image_processing import test_image_processing
        success = test_image_processing()
        return success
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Image Processing for Document Manager API\n")
    
    # Check current status
    print("📋 Current Status:")
    missing_packages = check_python_packages()
    tesseract_installed = check_tesseract()
    groq_configured = check_groq_api_key()
    
    # Install missing components
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing Python packages...")
        if not install_python_packages():
            print("❌ Failed to install Python packages")
            return False
    
    if not tesseract_installed:
        print("\n📥 Installing Tesseract OCR...")
        if not install_tesseract():
            print("❌ Failed to install Tesseract OCR")
            return False
    
    if not groq_configured:
        print("\n🔑 Setting up Groq API key...")
        if not setup_groq_api_key():
            print("❌ Failed to set up Groq API key")
            return False
    
    # Test the setup
    print("\n🎯 Testing the complete setup...")
    if test_setup():
        print("\n🎉 Image processing setup is complete!")
        print("\n📚 Next steps:")
        print("1. Make sure your .env file contains your Groq API key")
        print("2. Start the API: uvicorn app:app --reload")
        print("3. Test image upload with: python test_image_upload.py")
        return True
    else:
        print("\n❌ Setup test failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
