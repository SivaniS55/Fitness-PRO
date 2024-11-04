import sys
from app import app

# Add this for better error reporting
if __name__ == '_main_':
    try:
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)