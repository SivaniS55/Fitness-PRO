import app
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add a simple test route directly here
@app.route('/user.html')
def index():
    return 'Flask app is running!'

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return {"error": "Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500

# Application entry point
if __name__ == '_main_':
    try:
        app.run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)