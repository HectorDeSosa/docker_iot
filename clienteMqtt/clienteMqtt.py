import asyncio, ssl, certifi, logging, os, sys
import aiomqtt

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
        logging.info(os.environ['PUBLICAR']+': '+str(mi_contador.obtener_valor()))
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
        #Hice de dos formas, para probar y ambas funcionan. 
        task_1=asyncio.create_task(topico_uno(),name='task1')
        #task_1.set_name('task1')
        task_2=asyncio.create_task(topico_dos(),name='task2')
        task_3=asyncio.create_task(admin(client))
        task_4=asyncio.create_task(publicacion(client),name='cont')
        task_5=asyncio.create_task(contador())
        await asyncio.gather(task_1,task_2,task_3,task_4,task_5)
        """
        async with asyncio.TaskGroup() as tg:
            tg.create_task(admin(client))
            tg.create_task(topico_uno(),name='topico_uno')
            tg.create_task(topico_dos(),name='topico_dos')
            tg.create_task(publicacion(client))
            tg.create_task(contador())
        """

if __name__ == "__main__":
    try:
        topico1 = asyncio.Queue()
        topico2 = asyncio.Queue()
        mi_contador = Contador()
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)

#docker image ls
#clienteMqtt $ docker image rmi -f nombress 
#docker build -t clientemqtt .
#docker run --rm --name cliente_mqtt clientemqtt
#docker-compose up --build
