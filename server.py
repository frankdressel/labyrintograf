import asyncio
from multiprocessing import Process, Pipe
import websockets
import jsonpickle
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 23
GPIO_ECHO = 24

GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)

parent_conn, child_conn = Pipe()

def entfernung():
        GPIO.output(GPIO_TRIGGER, False)
        time.sleep(0.00002)

        # Trig High setzen
        GPIO.output(GPIO_TRIGGER, True)

        # Trig Low setzen (nach 0.01ms)
        time.sleep(0.00005)
        GPIO.output(GPIO_TRIGGER, False)

        Startzeit = time.time()
        Endzeit = time.time()

        # Start/Stop Zeit ermitteln
        while GPIO.input(GPIO_ECHO) == 0:
                Startzeit = time.time()

        while GPIO.input(GPIO_ECHO) == 1:
                Endzeit = time.time()

        # Vergangene Zeit
        Zeitdifferenz = Endzeit - Startzeit

        # Schallgeschwindigkeit (34300 cm/s) einbeziehen
        entfernung = (Zeitdifferenz * 34300) / 2

        return entfernung

async def hello(websocket, path):
    while True:
        await websocket.send(jsonpickle.encode(parent_conn.recv()))
        time.sleep(0.01)

def measure(conn):
    while True:
        distance=entfernung()
        conn.send(distance)
        time.sleep(0.01)

if __name__ == '__main__':
    Process(target=measure, args=(child_conn,)).start()

    try:
        start_server = websockets.serve(hello, port=5678)
    
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        print("Programm abgebrochen")
        GPIO.cleanup()

