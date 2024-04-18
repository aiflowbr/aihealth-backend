ws_clients = []

async def send_to_all(msg):
    for cli in ws_clients:
        await cli.send_json(msg)