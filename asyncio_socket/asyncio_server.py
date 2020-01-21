import asyncio
from asyncio_socket import requestHandle
import json
import threading

handler = None

class RequestHandleProtocol(asyncio.Protocol):
    def __init__(self):
        global handler
        self.transport = None
        loop = asyncio.get_event_loop()
        self.handler = handler
    def connection_made(self, transport):
        self.transport = transport
        self.peername = self.transport.get_extra_info('peername')
    def data_received(self, data):
        print("data received")
        print(self.peername)
        try:
            request = json.loads(data.decode())
            print(self.handler)
            self.handler.request_handle(request, self.peername)
        except json.decoder.JSONDecodeError:
            print('verify failed')
        self.transport.write(data)
        self.transport.close()
async def server_by_protocol():
    host = '0.0.0.0'
    port = 9487
    loop = asyncio.get_event_loop()
    server = await loop.create_server(RequestHandleProtocol, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with server:
        await server.serve_forever()
async def server_socket(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = []
    global handler
    addr = writer.get_extra_info('peername')
    chunk = await reader.read(4096)
    data.append(chunk)
    while chunk:

        chunk = await reader.read(4096)
        data.append(chunk)
    data = b"".join(data).decode()
    data = json.loads(data)
    #print(data)
    handler.request_handle(data, addr)

    print(f"Send: hello")
    writer.write('hello'.encode('utf-8'))
    await writer.drain()

    print("Close the connection")
    writer.close()

async def server_main():
    host = '0.0.0.0'
    port = 9487
    server = await asyncio.start_server(server_socket, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with server:
        await server.serve_forever()

def run_main():
    global handler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    handler = requestHandle.RequestHandler(loop)
    loop.create_task(server_main())
    loop.run_forever()



if __name__ == '__main__':
    run_main()