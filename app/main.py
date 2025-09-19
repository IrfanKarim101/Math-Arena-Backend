from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory storage for demo (replace with DB later)
games: Dict[str, Dict] = {}

class PlayerScore(BaseModel):
    player: str
    correct: int
    wrong: int

@app.post("/create_game/{game_id}")
def create_game(game_id: str):
    if game_id in games:
        return {"error": "Game already exists"}
    games[game_id] = {"players": {}, "questions": []}
    return {"message": f"Game {game_id} created"}

@app.post("/join_game/{game_id}")
def join_game(game_id: str, player: str):
    if game_id not in games:
        return {"error": "Game not found"}
    games[game_id]["players"][player] = {"correct": 0, "wrong": 0}
    return {"message": f"{player} joined {game_id}"}

@app.post("/update_score/{game_id}")
def update_score(game_id: str, score: PlayerScore):
    if game_id not in games:
        return {"error": "Game not found"}
    games[game_id]["players"][score.player] = {
        "correct": score.correct,
        "wrong": score.wrong
    }
    return {"message": "Score updated", "data": games[game_id]}

@app.get("/get_scores/{game_id}")
def get_scores(game_id: str):
    return games.get(game_id, {"error": "Game not found"})

# WebSocket for real-time score updates
@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Update from {game_id}: {data}")
