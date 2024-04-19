import asyncio, ssl, certifi, logging, os
import aiomqtt

#logging.getLogger(__name__)
logging.basicConfig(format='%(taskName)s: %(asctime)s - cliente mqtt - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S')

class Contador:
    def __init__(self):
        self.__contador = 0 #doble guion bajo privada
    def incrementar(self):
        self.__contador += 1
    def obtener_valor(self):
        return self.__contador

async def topico_uno():
    while True:
        message = await topico1.get()
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))

async def topico_dos():
    while True:
        message = await topico2.get()
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
async def admin(client):
    while True:
        async for message in client.messages:
            if message.topic.matches(os.environ['TOPICO1']):
                topico1.put_nowait(message)
            elif message.topic.matches(os.environ['TOPICO2']):
                topico2.put_nowait(message)
async def publicacion(client):
    while True:
        await client.publish(os.environ['PUBLICAR'],str(mi_contador.obtener_valor()))#aca publico el contador
        await asyncio.sleep(5)
async def contador():
    while True:
        mi_contador.incrementar()
        await asyncio.sleep(3)
async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port=8883,
        tls_context=tls_context,
    ) as client:
        await client.subscribe(os.environ['TOPICO1'])
        await client.subscribe(os.environ['TOPICO2'])
        async with asyncio.TaskGroup() as tg:
            tg.create_task(admin(client))
            tg.create_task(topico_uno())
            tg.create_task(topico_dos())
            tg.create_task(publicacion(client), name='publicacionn')
            tg.create_task(contador(),name='cont')


if __name__ == "__main__":
    try:
        topico1 = asyncio.Queue()
        topico2 = asyncio.Queue()
        mi_contador = Contador()
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


#docker image ls
#clienteMqtt $ docker image rm nombre -f
#docker build -t clientemqtt .
#docker run --rm --name cliente_mqtt clientemqtt
#docker-compose up --build
