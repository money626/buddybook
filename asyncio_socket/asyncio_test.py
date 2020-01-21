import asyncio
import json

class EchoClientProtocol(asyncio.Protocol):
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

async def client_main(message, ip_address):

    loop = asyncio.get_running_loop()
    port = 9487
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(lambda: EchoClientProtocol(message, on_con_lost), ip_address, port)

    try:
        await on_con_lost
    finally:
        transport.close()

async def send_request(request):
    await client_main(json.dumps(request))



