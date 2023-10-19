import asyncio
import websockets
import re

connected = set()
banned_ips = set()
client_counter = 1


async def handle_websocket(websocket, path):
    global client_counter
    client_id = client_counter
    client_counter += 1

    connected.add((client_id, websocket))
    client_ip = websocket.remote_address[0]

    if client_ip in banned_ips:
        await websocket.send("You've been banned for using the forbidden word.")
        await websocket.close()
        connected.remove((client_id, websocket))
        return

    try:
        async for message in websocket:
            print(f"{client_id}: {message}")

            if re.search(r'\brum\b', message, re.IGNORECASE):
                await websocket.send("You've been banned for using the forbidden word.")
                await websocket.close()
                connected.remove((client_id, websocket))
                banned_ips.add(client_ip)
                return

            for _, client in connected:
                await client.send(f"{client_id}: {message}")

    finally:
        connected.remove((client_id, websocket))

        for _, client in connected:
            await client.send(f"Client {client_id} disconnected")

async def start_server():
    ip_address = "127.0.0.0"
    port = 8080
    server = await websockets.serve(handle_websocket, ip_address, port)
    print(f"Server started at ws://{ip_address}:{port}")

    try:
        await server.wait_closed()
    except asyncio.CancelledError:
        pass

async def main():
    await start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopping...")

""""
async def unban_user(ip_address):
    if ip_address in banned_ips:
        banned_ips.remove(ip_address)
        return True  # User unbanned
    return False  # User not found in the banned list


ip_to_unban = "192.168.56.1"
if unban_user(ip_to_unban):
    print(f"User with IP {ip_to_unban} has been unbanned.")
else:
    print(f"User with IP {ip_to_unban} is not in the banned list.")
    
"""
