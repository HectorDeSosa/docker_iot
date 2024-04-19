import asyncio, ssl, certifi, logging, os
import aiomqtt

#logging.getLogger(__name__)
logging.basicConfig(format='%(funcName)s: %(asctime)s - cliente mqtt - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S')

class Contador:
    def __init__(self):
        self.__contador = 0 #doble guion bajo privada
    def incrementar(self):
        self.__contador += 1
    def obtener_valor(self):
        return self.__contador

async def topico1(client):
    while True:
        async with client.messages() as messages:
            await client.subscribe(os.environ['TOPICO1'])
            async for message in messages:
                logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
        await asyncio.sleep(3)
async def topico2(client):
    while True:
        async with client.messages() as messages:
            await client.subscribe(os.environ['TOPICO2'])
            async for message in messages:
                logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
        await asyncio.sleep(3)
async def publicacion(client):
    while True:
        await client.publish(os.environ['PUBLICAR'],str(mi_contador.obtener_valor()))#aca publico el contador
        await asyncio.sleep(5)
async def contador():
    while True:
        mi_contador.incrementar()
        await asyncio.sleep(3)
async def master():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()
    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port=8883,
        tls_context=tls_context,
    ) as client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(topico1(client))
            tg.create_task(topico2(client))
            tg.create_task(publicacion(client), name='publicacionn')
            tg.create_task(contador(),name='cont')

if __name__ == "__main__":
    try:
        topico1 = asyncio.Queue()
        topico2 = asyncio.Queue()
        mi_contador = Contador()
        asyncio.run(master())
    except KeyboardInterrupt:
        pass


#docker image ls
#clienteMqtt $ docker image rm nombre -f
#docker build -t clientemqtt .
#docker run --rm --name cliente_mqtt clientemqtt
#docker-compose up --build
