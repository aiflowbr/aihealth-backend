from fastapi import FastAPI, WebSocket
import asyncio
from queue import Queue
import json
from time import sleep

app = FastAPI()

# Lista de clientes conectados
clients = []

# Fila de logs
log_queue = Queue()


counter_log = 0


# Função para adicionar logs à fila
def add_log():
    global counter_log
    counter_log = counter_log + 1
    log_queue.put(json.dumps({"log": f"Log Counter: {counter_log}"}))
    sleep(1)


# Função para enviar logs em loop para o cliente
async def send_logs(websocket):
    while True:
        add_log()
        log_message = log_queue.get()
        print("mensagem enviada")
        await websocket.send_json(log_message)


# Rota WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    # async de logs
    asyncio.create_task(send_logs(websocket))

    try:
        while True:
            data = await websocket.receive_json()
            # Enviar mensagem para todos os clientes
            await asyncio.gather(*[client.send_json(data) for client in clients])
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        clients.remove(websocket)
