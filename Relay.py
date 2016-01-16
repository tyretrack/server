#!/usr/bin/env python3
import argparse
import asyncio
import logging
import pickle
import struct
import sys
import zlib
from socket import *

import PjParser


class CoroutineClientProtocol:
    def __init__(self, dgramreceived):
        self.transport = None
        self.dgramreceived = dgramreceived

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.ensure_future(self.dgramreceived(data, addr))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed")


queues = []
lastMsg = {}
handledPackets = 0


async def handle_pjcars_pkt(data, addr):
    isPkt, pkt = PjParser.decode(data)
    if isPkt:
        if pkt['sPacketType'] == 0 and pkt['sGameState'] != 'GAME_FRONT_END':
            asyncio.ensure_future(put_to_queue(pkt))


async def put_to_queue(data):
    global queues, handledPackets, lastMsg
    handledPackets += 1

    pkt = {}
    for key in data:
        if key not in lastMsg or data[key] != lastMsg[key]:
            pkt[key] = data[key]

    for queue in queues:
        if queue.qsize() < 1:
            await queue.put(pkt)
        else:
            pass
    lastMsg = data

async def send_pkt(writer, data):
    pkt = zlib.compress(pickle.dumps(data, 4), 1)
    writer.write(struct.pack('!H', len(pkt)))
    writer.write(pkt)
    await writer.drain()

async def handle_socket(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global lastMsg
    remote_addr = writer.transport.get_extra_info('peername')
    logging.info('Client connected %s:%s', remote_addr[0], remote_addr[1])

    await send_pkt(writer, lastMsg)

    queue = asyncio.Queue()
    queues.append(queue)

    try:
        while True:
            data = await queue.get()
            await send_pkt(writer, data)

    except ConnectionResetError:
        logging.info('Client disconnect %s:%s', remote_addr[0], remote_addr[1])
    finally:
        queues.remove(queue)


def open_udp_broadcast_listener(loop, port, handler):
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', port))

    connect = loop.create_datagram_endpoint(
            lambda: CoroutineClientProtocol(handler),
            sock=s)

    return connect


def gather_stats(loop):
    global handledPackets

    logging.info('%s Pkt/min:', handledPackets)
    handledPackets = 0

    loop.call_later(60, gather_stats, loop)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str, help='Listen IP', default='')
    parser.add_argument('--port', type=int, help='The port', default=8888)
    parser.add_argument('--log', type=str, help='log level', default='INFO')
    args = parser.parse_args()
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)

    loop = asyncio.get_event_loop()

    loop.run_until_complete(open_udp_broadcast_listener(loop, 5606, handle_pjcars_pkt))
    server = loop.run_until_complete(asyncio.start_server(handle_socket, args.host, args.port))
    loop.call_later(60, gather_stats, loop)

    for sock in server.sockets:
        addr = sock.getsockname()
        logging.info('Listening for connections on %s:%s', addr[0], addr[1])

    loop.run_forever()
    loop.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
