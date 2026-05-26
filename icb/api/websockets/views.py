import json

from icb.core.logger import logger
from fastapi import Depends, WebSocket
from main import app

from icb.core.security import User, get_current_active_user, get_current_active_user_from_ws
from icb.core.websocket import PlayloadMessage, manager, WSMessageType


@app.websocket("/api/v1/ws/connect")
async def websocket_connect(
    websocket: WebSocket,
    client_id: str = None,
    user: User = Depends(get_current_active_user_from_ws),
):
    if not client_id:
        client_id = user.id

    await manager.connect(websocket, client_id)
    message = PlayloadMessage(
                client_id=client_id,
                content={"message": f"Client: {client_id} is connected!"},
                msg_type=WSMessageType.GREATING,
            )
    await manager.send_personal_message(message.to_dict(), client_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_content = json.loads(data)
            message = PlayloadMessage(
                client_id=client_id,
                content=message_content,
                username=user.username,
                msg_type=WSMessageType.GREATING,
            )
            await manager.send_personal_message(message.to_dict(), client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, client_id)


@app.websocket("/api/v1/ws/disconnect")
async def websocket_disconnect(
    websocket: WebSocket,
    client_id: str = None,
    user: User = Depends(get_current_active_user_from_ws),
):
    """
    Endpoint to explicitly disconnect a WebSocket connection.
    """
    if not client_id:
        client_id = user.id
    try:
        await manager.disconnect(websocket, client_id)
        logger.info(f"WebSocket connection for {client_id} has been disconnected.")
        await websocket.close()
    except Exception as e:
        logger.error(f"Error during disconnection: {e}")


@app.post("/api/v1/ws/send")
async def send_message(message: str, client_id: str = None, user: User = Depends(get_current_active_user)):
    if not client_id:
        client_id = user.id
    if not message:
        return {'message': 'Not message'}
    
    message = PlayloadMessage(client_id=client_id, content={"name": message},
                              username=user.username, msg_type=WSMessageType.TRANSACTION)
    await manager.send_personal_message(message.to_dict(), client_id)
    return {'message': 'Send'}
