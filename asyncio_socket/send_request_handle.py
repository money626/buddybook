from . import asyncio_server
import json,  asyncio

class ClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

async def client_by_protocol(message, ip_address):

    loop = asyncio.get_running_loop()
    port = 9486
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(lambda: ClientProtocol(message, on_con_lost), ip_address, port)

    try:
        await on_con_lost
    finally:
        transport.close()

async def client_main(message, ip_address):
    port = 6666
    try:
        reader, writer = await asyncio.open_connection(ip_address, port)
        writer.write(message.encode('utf-8'))
        await writer.drain()
        writer.write_eof()
        print('Client connection closed')
        writer.close()
        return True
    except Exception as e:
        print(e)
    finally:
        return False
