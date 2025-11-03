#!/usr/bin/env python3
"""
TreeSense Imaging - Launch Script
Starts the Streamlit application and opens it in the default browser.
"""

import subprocess
import webbrowser
import time
import sys
import threading
from pathlib import Path

def open_browser():
    """Open the browser after a short delay to allow the server to start"""
    time.sleep(3)  # Wait for server to start
    url = "http://localhost:8501"
    print(f"\n🌐 Opening TreeSense Imaging in your default browser...")
    print(f"   URL: {url}")
    webbrowser.open(url)

def main():
    """Main function to launch the Streamlit app"""
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the streamlit-app directory.")
        sys.exit(1)
    
    print("🌳 TreeSense Imaging - Advanced Forest Analytics Platform")
    print("=" * 60)
    print("🚀 Starting the application...")
    print("📍 Local URL: http://localhost:8501")
    print("🌐 Opening in browser...")
    print("\n💡 Press Ctrl+C to stop the application")
    print("=" * 60)
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start Streamlit server
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--theme.primaryColor", "#2E8B57",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f8f0",
            "--theme.textColor", "#262730"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        print("Thank you for using TreeSense Imaging! 🌿")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting the application: {e}")
        print("Please make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
