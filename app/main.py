from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.websocket.manager import manager
from app.websocket.matchmaking import matchmaker
from app.services.redis_client import redis_client
from app.services.moderation import moderate_message
import os


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get():
    """Serve the chat interface"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/favicon.svg")
async def favicon():
    """Serve favicon"""
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat"""
    # Connect and get user_id
    user_id = await manager.connect(websocket)
    
    try:
        # Try to match with another user
        matched = await matchmaker.try_match(user_id)
        
        if not matched:
            # Notify user they're in queue
            await manager.send_personal_message({
                "type": "system",
                "message": "Waiting for a stranger..."
            }, user_id)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "message":
                # Moderate message
                text = data.get("text", "")
                is_allowed, reason = moderate_message(text)
                
                if not is_allowed:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": reason
                    }, user_id)
                    continue
                
                # Send to partner
                await manager.broadcast_to_pair({
                    "type": "message",
                    "text": text
                }, user_id)
            
            elif message_type == "next":
                # Handle next button
                await matchmaker.handle_next(user_id)
    
    except WebSocketDisconnect:
        # Handle disconnect
        partner_id = manager.get_partner(user_id)
        if partner_id:
            # Store previous partners for potential reconnection
            redis_client.set_previous_partner(user_id, partner_id, 20)
            redis_client.set_previous_partner(partner_id, user_id, 20)
            
            await manager.send_personal_message({
                "type": "system",
                "message": "Stranger disconnected"
            }, partner_id)
            redis_client.remove_active_chat(partner_id)
            
            # Requeue the partner for potential reconnection
            redis_client.add_to_queue(partner_id)
        
        manager.disconnect(user_id)
        redis_client.remove_active_chat(user_id)
        redis_client.remove_user_from_queue(user_id)


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    try:
        redis_client.connect()
        print("Connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        print("Running without Redis (basic 2-user chat only)")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
