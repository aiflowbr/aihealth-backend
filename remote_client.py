import asyncio
import websockets

# import json
from time import sleep
import signal

# async def websocket_client():
#     uri = "ws://localhost:8099/ws"
#     async with websockets.connect(uri) as websocket:
#         while True:
#             js = json.dumps({"msg": "teste"})
#             print(js)
#             await websocket.send(js)
#             message = await websocket.recv()
#             print(f"Received message: {message}")


# asyncio.get_event_loop().run_until_complete(websocket_client())
async def receive_messages(websocket):
    while True:
        if shutdown_flag.is_set():
            break
        message = await websocket.recv()
        print(f"Received message from server: {message}")


# async def send_message(websocket):
#     while True:
#         sleep(1)
#         # message = input(
#         #     "Digite a mensagem que deseja enviar (ou pressione Enter para sair): "
#         # )
#         # if message:
#         #     await websocket.send(message)


async def main():
    uri = "ws://localhost:8099/ws"
    async with websockets.connect(uri) as websocket:
        # await receive_messages(websocket)
        task1 = asyncio.create_task(receive_messages(websocket))
        await asyncio.gather(task1)


async def shutdown(signal, loop, shutdown_flag):
    print("Finalizando o loop de evento...")
    shutdown_flag.set()
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    # await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    shutdown_flag = asyncio.Event()
    # for sig in (signal.SIGINT, signal.SIGTERM):
    #     loop.add_signal_handler(
    #         sig, lambda sig=sig: asyncio.create_task(shutdown(sig, loop))
    #     )
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda sig=sig: asyncio.create_task(shutdown(sig, loop, shutdown_flag))
        )

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Programa interrompido pelo usuário.")
        # shutdown_flag.set()
        # for sig in (signal.SIGINT, signal.SIGTERM):
        #     loop.remove_signal_handler(sig)
