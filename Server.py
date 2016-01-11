#!/usr/bin/env python

import argparse
import asyncio
import json
import logging
import pickle
import struct
import sys
import zlib

import websockets

queues = []
handledPackets = 0
lastMsg = {}


async def handle_writes(websocket, queue):
    while True:
        pkt = await queue.get()
        await websocket.send(json.dumps({'c': pkt}, separators=(',', ':')))


async def handle_reads(websocket):
    while True:
        pkt = await websocket.recv()
        print(pkt)


async def handle_ws(websocket, path):
    global lastMsg
    remote_addr = websocket.remote_address
    logging.info("WS Client connected %s:%s", remote_addr[0], remote_addr[1])

    await websocket.send(json.dumps({'c': lastMsg}, separators=(',', ':')))

    queue = asyncio.Queue()
    queues.append(queue)

    try:
        fs = [handle_writes(websocket, queue), handle_reads(websocket)]
        (_, pending) = await asyncio.wait(fs, return_when=asyncio.FIRST_EXCEPTION)
        for f in pending:
            f.cancel()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        logging.info("WS Client disconnected %s:%s", remote_addr[0], remote_addr[1])
        queues.remove(queue)


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


async def read_from_server(host: str, port: int, loop):
    # Exponential backoff
    timeout = 0
    while True:
        try:
            logging.info('Sleeping %s s', timeout)
            await asyncio.sleep(timeout)
            (reader, writer) = await asyncio.open_connection(host=host, port=port, loop=loop)
            timeout = 0  # Reset timeout after successful connection
            logging.info('Connected to %s:%s', host, port)
            try:
                while True:
                    pkt = await reader.readexactly(2)
                    len = struct.unpack('!H', pkt)[0]
                    pkt = pickle.loads(zlib.decompress(await reader.readexactly(len)))
                    asyncio.ensure_future(put_to_queue(pkt))

            except ConnectionResetError:
                logging.warning("Connection closed (%s:%s)", host, port)
            except asyncio.IncompleteReadError:
                logging.warning("Could not complete read (%s:%s)", host, port)
        except ConnectionRefusedError:
            logging.warning('Connection refused (%s:%s)', host, port)
        except OSError:  # Multiple connection refued at the same time (ipv4/6)
            logging.warning('Connection refused (%s:%s)', host, port)
        finally:
            if timeout == 0:
                timeout = 0.25
            timeout *= 2  # double our waiting time
            timeout = min(timeout, 30)  # clamp to 30 s


def gather_stats(loop):
    global handledPackets

    logging.info('%s Pkt/min:', handledPackets)
    handledPackets = 0

    loop.call_later(60, gather_stats, loop)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('remote_server', type=str, help='The server to connect to')
    parser.add_argument('remote_port', type=int, help='The port', default=8888)
    parser.add_argument('--host', type=str, help='Listen IP', default='')
    parser.add_argument('--port', type=int, help='The port', default=8765)
    parser.add_argument('--log', type=str, help='log level', default='INFO')
    args = parser.parse_args()
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)

    loop = asyncio.get_event_loop()
    ws_server = loop.run_until_complete(websockets.serve(handle_ws, args.host, args.port, loop=loop))
    asyncio.ensure_future(read_from_server(args.remote_server, args.remote_port, loop))
    loop.call_later(60, gather_stats, loop)

    for sock in ws_server.server.sockets:
        addr = sock.getsockname()
        logging.info('Listening for Websocket connections on %s:%s', addr[0], addr[1])

    loop.run_forever()
    loop.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
