import asyncio
import datetime

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the File API Server
PORT_Server = 6002 # The port used by the PM Server

clients = set()  # Track connected clients

# Function to send periodic messages to all clients
async def broadcast_messages():
    while True:
        await asyncio.sleep(0.5)  # Wait for 3 seconds
        message = f"Server broadcast at {datetime.datetime.now().strftime('%H:%M:%S')}"
        print(f"Broadcasting: {message}")

        for writer in clients.copy():
            try:
                writer.write(message.encode())
                await writer.drain()
            except Exception as e:
                print(f"Error sending to client: {e}")
                clients.discard(writer)

# Asyncio Server
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")

    clients.add(writer)  # Register new client

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            writer.write(message.encode() + b'\n' + "Received".encode()) 

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print(f"Connection closed from {addr}")
        clients.discard(writer)
        writer.close()
        await writer.wait_closed()

async def async_server():
    server = await asyncio.start_server(
        handle_client, HOST, 8888
    )

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    # Start broadcasting messages independently
    asyncio.create_task(broadcast_messages())

    async with server:
        await server.serve_forever()

# Asyncio Client with periodic messages
async def async_client():
    try:
        reader, writer = await asyncio.open_connection(
            HOST, PORT_Client
        )

        print("Connected to server. Sending messages every second...")

        async def read_from_server():
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                print(f"Server message: {data.decode()}")

        asyncio.create_task(read_from_server())

        message_count = 0
        while True:
            message = f"Message #{message_count}"
            print(f"Sending: {message}")

            writer.write(message.encode())
            await writer.drain()

            message_count += 1
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("Client shutting down...")
    except Exception as e:
        print(f"Error in client: {e}")
    finally:
        print("Closing connection...")
        writer.close()
        await writer.wait_closed()

# Run server or client
async def main():
    try:
        # Uncomment the one you want to run:
        await async_server()
        # await async_client()
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
