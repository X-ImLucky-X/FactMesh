import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import uvicorn
from backend import config

def start_server():
    print(f"Starting Fact Knowledge Layer on http://localhost:{config.PORT}")
    print(f"Interactive UI: http://localhost:{config.PORT}")
    print(f"API Documentation (Swagger): http://localhost:{config.PORT}/docs")
    uvicorn.run(
        "backend.api:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )

if __name__ == "__main__":
    # If arguments are passed, forward to CLI
    if len(sys.argv) > 1 and sys.argv[1] != "serve":
        import cli
        cli.main()
    else:
        start_server()
