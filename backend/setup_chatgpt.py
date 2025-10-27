#!/usr/bin/env python3
"""
Setup script for ChatGPT Integration
This script helps set up the ChatGPT integration for the Stroke Detection System
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✓ {env_file} already exists")
        return True
    
    env_content = """# Environment Configuration for Stroke System
# Fill in your actual values

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./stroke.db

# Application Configuration
DEBUG=True
SECRET_KEY=your_secret_key_here
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"✓ Created {env_file} file")
        print("⚠️  Please edit .env file and add your OpenAI API key")
        return True
    except Exception as e:
        print(f"✗ Failed to create {env_file}: {e}")
        return False

def run_migration():
    """Run database migration"""
    print("\nRunning database migration...")
    try:
        subprocess.check_call([sys.executable, "migrate_database.py"])
        print("✓ Database migration completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Database migration failed: {e}")
        return False

def main():
    """Main setup function"""
    print("ChatGPT Integration Setup for Stroke Detection System")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Run migration
    if not run_migration():
        return False
    
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Start the server: python main.py")
    print("3. Access the physician dashboard to use ChatGPT treatment plans")
    print("\nFor more information, see CHATGPT_INTEGRATION_README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
