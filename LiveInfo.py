#!/usr/bin/env python3

from socket import *
import asyncio

from tyretrack import pcars
import websockets
import json
import pickle
import os


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
lastMsg = None
mainInfo = {
    'trackLocation': '',
    'carName': '',
    'player': '',
    'opponentNames': [],
    'opponentInfo': {
    }
}


def update_main_info(pkt):
    global mainInfo
    if pkt['sPacketType'] == 1:
        mainInfo['trackLocation'] = pkt['sTrackLocation']
        mainInfo['carName'] = pkt['sCarName']
        mainInfo['player'] = pkt['sPlayerName']
        mainInfo['opponentNames'][0:len(pkt['sName'])] = pkt['sName']
    elif pkt['sPacketType'] == 2:
        mainInfo['opponentNames'][pkt['sOffset']:pkt['sOffset'] + len(pkt['sName'])] = pkt['sName']


def update_opponents(pkt):
    global mainInfo
    if pkt['sPacketType'] != 0:
        return

    for i, info in enumerate(pkt['sParticipationInfo']):
        if i not in mainInfo['opponentInfo']:
            mainInfo['opponentInfo'][i] = {'laps': {}}

        opponent = mainInfo['opponentInfo'][i]

        current_lap = info['sCurrentLap']
        current_sector = info['sCurrentSector'] - 1
        if current_sector == 0:
            current_lap -= 1

        if current_lap not in opponent['laps']:
            opponent['laps'][current_lap] = {}

        opponent['laps'][current_lap][current_sector] = info['sLastSectorTime']


async def handle_pjcars_pkt(data, addr):
    global lastMsg
    isPkt, pkt = pcars.decode_v2(data)
    if isPkt:
        if pkt['sPacketType'] == 0 and pkt['sGameState'] != 'GAME_FRONT_END':
            lastMsg = pkt
            asyncio.ensure_future(put_to_queue(pkt))
            if pkt['sCount'] == 0:
                # pprint.pprint(mainInfo['opponentInfo'])
                pass
        update_opponents(pkt)
        update_main_info(pkt)


async def put_to_queue(pkt):
    global queues
    for queue in queues:
        if queue.qsize() < 2:
            await queue.put(pkt)
        else:
            pass
            # too noisy in case of bad connection
            #print("pkt dropped")


async def handle_ws(websocket, path):
    print("connected")

    queue = asyncio.Queue()
    queues.append(queue)

    try:
        while True:
            pkt = await queue.get()

            await websocket.send(json.dumps({'m':mainInfo, 'c':pkt}, separators=(',', ':')))
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    finally:
        queues.remove(queue)

def save(loop):
    global mainInfo
    pickle.dump(mainInfo, open(os.path.dirname(os.path.realpath(__file__)) + '/current-state', 'wb'))

    loop.call_later(10, save, loop)

def main(_):
    global mainInfo
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 5606))

    try:
        mainInfo = pickle.load(open(os.path.dirname(os.path.realpath(__file__)) + '/current-state', 'rb'))
    except:
        print("Could not load old state")
        pass

    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(
            lambda: CoroutineClientProtocol(handle_pjcars_pkt),
            sock=s)
    start_server = websockets.serve(handle_ws, '', 8765)
    transport, protocol = loop.run_until_complete(connect)
    loop.run_until_complete(start_server)
    loop.call_later(0, save, loop)
    loop.run_forever()
    transport.close()
    loop.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
