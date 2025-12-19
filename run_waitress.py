"""
Production Server for LuminaryAI using Waitress
Recommended for Windows to avoid socket errors
"""
from waitress import serve
from app import app
import logging

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Starting LuminaryAI with Waitress (Production Server)")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("API Docs: http://localhost:5000/api/health")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        serve(
            app, 
            host='0.0.0.0', 
            port=5000, 
            threads=4,
            url_scheme='http',
            connection_limit=100,
            cleanup_interval=30,
            channel_timeout=120
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Server error: {str(e)}")
