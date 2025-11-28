"""
MT5 REST API Server Launcher
Starts the FastAPI server for MT5 client authentication
"""
import uvicorn
from src.mt5_api import app


def main():
    """Start the MT5 REST API server"""
    print("="*60)
    print("MT5 REST API Server")
    print("="*60)
    print("\nStarting server on http://localhost:8000")
    print("API Documentation available at http://localhost:8000/docs")
    print("Alternative docs at http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server")
    print("="*60)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Set to True for development
    )


if __name__ == "__main__":
    main()
