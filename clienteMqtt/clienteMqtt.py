import asyncio, ssl, certifi, logging
from asyncio_mqtt import Client, ProtocolVersion
from environs import Env

env = Env()
env.read_env() #lee el archivo con las variables. por defecto .env

logging.basicConfig(format='%(asctime)s - cliente mqtt - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S')

async def main(client):
    while True:
        async with client.messages() as messages:
            await client.subscribe(env("TOPICO1"))
            await client.subscribe(env("TOPICO2"))
            async for message in messages:
                logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
        await asyncio.sleep(5)
async def publicacion(client):
    while True:
        await client.publish(env("PUBLICAR"),"probando el topico")
        await asyncio.sleep(10)
async def master():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
    tls_context.maximum_version = ssl.TLSVersion.TLSv1_3
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()
    
    async with Client(
        env("SERVIDOR"),
        protocol=ProtocolVersion.V31,
        port=8883,
        tls_context=tls_context,
    ) as client:
        await asyncio.gather(main(client), publicacion(client))

if __name__ == "__main__":
    asyncio.run(master())

#docker image ls
#clienteMqtt $ docker image rm nombre -f
#docker build -t clientemqtt .
#docker run --rm --name cliente_mqtt clientemqtt
#docker-compose up --build