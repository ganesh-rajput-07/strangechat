# ANMS Chat - Anonymous 1-to-1 Chat Platform

A real-time anonymous chat platform built with FastAPI, WebSockets, and Redis.

## Features

- ✅ Anonymous text-based chat (no login required)
- ✅ Real-time WebSocket communication
- ✅ Redis-based matchmaking queue
- ✅ "Next" button to skip to next partner
- ✅ Automatic disconnect handling
- ✅ Basic content moderation
- 🚧 PostgreSQL logging (coming soon)

## Architecture

```
Client (Browser)
   ↓
FastAPI (WebSocket Server)
   ↓
Redis (Matchmaking + Sessions)
   ↓
PostgreSQL (Logs / Reports)
```

## Project Structure

```
ANMS_CHAT/
├── app/
│   ├── main.py              # FastAPI application & WebSocket endpoint
│   ├── websocket/
│   │   ├── manager.py       # Connection manager
│   │   └── matchmaking.py   # Redis-based matchmaking
│   ├── services/
│   │   ├── redis_client.py  # Redis operations
│   │   └── moderation.py    # Content moderation
│   ├── models/
│   └── utils/
├── static/
│   └── index.html           # Chat interface
├── docs/
│   └── tech_info.md         # Technical specification
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- Redis server (optional but recommended for production)

### Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Redis (optional):
```bash
# Create .env file
cp .env.example .env
# Edit .env with your Redis configuration
```

### Running the Application

#### With Redis (Recommended)
```bash
# Make sure Redis is running
redis-server

# Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Without Redis (Basic Mode)
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will run in basic mode without Redis (limited to simple in-memory matching).

### Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. Open the chat interface in your browser
2. The system will automatically match you with another user
3. Type messages and press Enter or click Send
4. Click "Next" to skip to a new partner
5. Close the tab to disconnect

## API Events

### Client → Server

- **connect**: `{ "type": "connect" }` (automatic on connection)
- **message**: `{ "type": "message", "text": "hello" }`
- **next**: `{ "type": "next" }`

### Server → Client

- **message**: `{ "type": "message", "text": "hello" }`
- **system**: `{ "type": "system", "message": "Stranger connected" }`
- **error**: `{ "type": "error", "message": "Error message" }`

## Redis Data Structures

- `waiting_queue` (list): Queue of users waiting for a match
- `active_chats` (hash): Active chat pairs (user_id → partner_id)

## Development

### Adding Features

- **Moderation**: Edit `app/services/moderation.py` to add banned words
- **Matchmaking**: Modify `app/websocket/matchmaking.py` for custom logic
- **UI**: Update `static/index.html` for frontend changes

### Testing

Open multiple browser tabs to test the chat functionality between different users.

## Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn + Uvicorn workers)
2. Set up Redis with persistence
3. Configure PostgreSQL for logging
4. Use a reverse proxy (Nginx)
5. Enable HTTPS

## License

MIT
