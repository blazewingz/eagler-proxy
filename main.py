import asyncio
import websockets
import os

# ----------------- CONFI -----------------
ATERNOS_IP = "BlazeWingz-KTS.aternos.me"
ATERNOS_PORT = 21166
# -------------------------------------------------

async def handle_client(client_ws, path):
    try:
        server_reader, server_writer = await asyncio.open_connection(ATERNOS_IP, ATERNOS_PORT)
    except Exception as e:
        print(f"Failed to connect to Aternos: {e}")
        await client_ws.close()
        return

    async def forward_to_server():
        try:
            async for message in client_ws:
                server_writer.write(message if isinstance(message, bytes) else message.encode())
                await server_writer.drain()
        except Exception: pass
        finally: server_writer.close()

    async def forward_to_client():
        try:
            while True:
                data = await server_reader.read(4096)
                if not data: break
                await client_ws.send(data)
        except Exception: pass
        finally: await client_ws.close()

    await asyncio.gather(forward_to_server(), forward_to_client())

async def main():
    # Render assigns an environment variable port dynamically
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Web Proxy on port {port}... Forwarding to {ATERNOS_IP}:{ATERNOS_PORT}")
    async with websockets.serve(handle_client, "0.0.0.0", port):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
