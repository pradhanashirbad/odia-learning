import os
import subprocess
import time

def start_app():
    # Start Xvfb
    xvfb_process = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x16'])
    os.environ['DISPLAY'] = ':99'
    
    try:
        # Give Xvfb time to start
        time.sleep(2)
        
        # Import and run the main application
        from main import main
        main()
    finally:
        # Clean up
        xvfb_process.terminate()
        xvfb_process.wait()

if __name__ == "__main__":
    start_app()