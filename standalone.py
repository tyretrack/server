import aiohttp
import argparse
import asyncio
import socket
from aiohttp import web

from tyretrack import pcars

queues = []


class CoroutineClientProtocol:
    def __init__(self, loop, dgramreceived):
        self.transport = None
        self.dgramreceived = dgramreceived
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.ensure_future(self.dgramreceived(data, addr), loop=self.loop)

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed")


async def websocket_handler(request):
    global queues
    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    queue = asyncio.Queue()
    queues.append(queue)

    try:
        while True:
            pkt = await queue.get()
            await ws.send_json({'c': pkt})
    finally:
        queues.remove(queue)

    print('Websocket connection closed')
    return ws


async def put_to_queue(pkt):
    global queues
    for queue in queues:
        if queue.qsize() < 2:
            await queue.put(pkt)
        else:
            pass
            # too noisy in case of bad connection
            # print("pkt dropped")


async def handle_pjcars_pkt(data, addr):
    isPkt, pkt = pcars.decode_v2(data)
    if isPkt:
        asyncio.ensure_future(put_to_queue(pkt))


def socket_setup(loop):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 5606))
    return loop.create_datagram_endpoint(
        lambda: CoroutineClientProtocol(loop, handle_pjcars_pkt),
        sock=s)


def main(_):
    debug = args.debug
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    app = web.Application()
    app.router.add_static(prefix='/assets', path='web/assets')
    app.router.add_routes([
        web.get('/', lambda _: web.FileResponse('web/index.html')),
        web.get('/stream', websocket_handler),
    ])

    loop.run_until_complete(socket_setup(loop))

    loop.set_debug(debug)

    web.run_app(app)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action="store_true", default=True)
    args = parser.parse_args()
    main(args)
