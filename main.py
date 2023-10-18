import asyncio
import websockets
import re

connected = set()
banned_users = set()
client_counter = 1
ban_file = "banned_users.txt"

async def handle_websocket(websocket, path):
    global client_counter
    client_id = client_counter
    client_counter += 1

    connected.add((client_id, websocket))

    try:
        async for message in websocket:
            print(f"{client_id}: {message}")

            if re.search(r'\brum\b', message, re.IGNORECASE):
                await websocket.send("You've been banned for using the forbidden word.")
                await websocket.close()
                connected.remove((client_id, websocket))
                banned_users.add(client_id)
                save_banned_users()
                return

            for _, client in connected:
                await client.send(f"{client_id}: {message}")

    finally:
        connected.remove((client_id, websocket))

        for _, client in connected:
            await client.send(f"Client {client_id} disconnected")

async def start_server():
    load_banned_users()
    ip_address = "127.0.0.1"
    port = 8080
    server = await websockets.serve(handle_websocket, ip_address, port)
    print(f"Server started at ws://{ip_address}:{port}")

    try:
        await server.wait_closed()
    except asyncio.CancelledError:
        pass

def load_banned_users():
    try:
        with open(ban_file, 'r') as file:
            for line in file:
                banned_users.add(int(line.strip()))
    except FileNotFoundError:
        pass

def save_banned_users():
    with open(ban_file, 'w') as file:
        for user_id in banned_users:
            file.write(f"{user_id}\n")

async def main():
    await start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopping...")


