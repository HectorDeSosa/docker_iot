from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging, os, asyncio, aiomysql, traceback, locale
import matplotlib.pyplot as plt
from io import BytesIO
import ssl, certifi, json, traceback
import aiomqtt

token=os.environ["TB_TOKEN"]

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre=update.message.from_user.first_name
    else:
        nombre=""
    if update.message.from_user.last_name:
        apellido=update.message.from_user.last_name
    else:
        apellido=""
    kb = [["temperatura"],["humedad"],["gráfico temperatura"],["gráfico humedad"]]
    await context.bot.send_message(update.message.chat.id, text="Bienvenido al Bot "+ nombre + " " + apellido,reply_markup=ReplyKeyboardMarkup(kb))
    """ #funciona 
    #una ves conectado estaria bueno que empiece a recibir todo lo que se publica 
    #el el topico hector/#
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()
    async with aiomqtt.Client(
        os.environ["SERVIDOR"],
        username=os.environ["MQTT_USR"],
        password=os.environ["MQTT_PASS"],
        port=int(os.environ["PUERTO_MQTTS"]),
        tls_context=tls_context,
    ) as client:
        await client.subscribe(os.environ['TOPICO'])
        async for message in client.messages:
            #ver si funciona
            await context.bot.send_message(update.message.chat.id, 
                text=str(message.topic) + ": " + message.payload.decode("utf-8"))
            #logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
"""
async def acercade(update: Update, context):
    await context.bot.send_message(update.message.chat.id, text="Este bot fue creado para el curso de IoT FIO")
"""
async def kill(update: Update, context):
    logging.info(context.args)
    if context.args and context.args[0] == '@e':
        await context.bot.send_animation(update.message.chat.id, "CgACAgEAAxkBAAOPZkuctzsWZVlDSNoP9PavSZmH5poAAmUCAALrx0lEVKaX7K-68Ns1BA")
        await asyncio.sleep(6)
        await context.bot.send_message(update.message.chat.id, text="¡¡¡Ahora estan todos muertos!!!")
    else:
        await context.bot.send_message(update.message.chat.id, text="☠️ ¡¡¡Esto es muy peligroso!!! ☠️")
"""
async def topicos(update: Update, context):
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()
    async with aiomqtt.Client(
        os.environ["SERVIDOR"],
        username=os.environ["MQTT_USR"],
        password=os.environ["MQTT_PASS"],
        port=int(os.environ["PUERTO_MQTTS"]),
        tls_context=tls_context,
    ) as client:
        #con el formato /setpoint 30.5
        #separo lo que llega
        topico,msg=update.message.text.split(' ',1)
        topico=topico[1:] #saca la barra /
        logging.info(f"{topico}: {msg}")
        #si el mensaje es por ejemplo /setpoint 22.3 hoo
        if len(msg.split())!=1:
            await context.bot.send_message(update.message.chat.id, text="argumento incorrecto")
            return
        if topico == "setpoint":
            #condicion de que la temperatura sea mayor a 0°C
            #si se quiere se puede cambiar esta temperatura
            #pongo un try por si no puede convertir
            try:
                if float(msg) > 0.0:
                    await client.publish(topic=topico, payload=msg , qos=1)
                    await context.bot.send_message(update.message.chat.id, text="setpoint correcto")
                else:
                    await context.bot.send_message(update.message.chat.id, text="setpoint incorrecto")
            except ValueError:
                await context.bot.send_message(update.message.chat.id, text="argumento incorrecto")
        elif topico == "periodo":
            #condicion de que el periodo sea mayor a cero
            try:
                if float(msg) > 0.0:
                    await client.publish(topic=topico, payload=msg , qos=1)
                    await context.bot.send_message(update.message.chat.id, text="periodo correcto")
                else:
                    await context.bot.send_message(update.message.chat.id, text="periodo incorrecto")
            except ValueError:
                await context.bot.send_message(update.message.chat.id, text="argumento incorrecto")
        elif topico == "modo":
            #modo puede ser auto/manual
            if msg in ["auto", "manual"]:
                await client.publish(topic=topico, payload=msg , qos=1)
                await context.bot.send_message(update.message.chat.id, text="modo correcto")
            else:
                await context.bot.send_message(update.message.chat.id, text="modo incorrecto")
        elif topico == "destello":
            if msg in ["ON", "OFF"]:
                await client.publish(topic=topico, payload=msg , qos=1)
                await context.bot.send_message(update.message.chat.id, text="destello correcto")
            else:
                await context.bot.send_message(update.message.chat.id, text="destello incorrecto")  
        elif topico == "rele":
            if msg in ["ON", "OFF"]:
                await client.publish(topic=topico, payload=msg , qos=1)
                await context.bot.send_message(update.message.chat.id, text="estado de rele correcto")
            else:
                await context.bot.send_message(update.message.chat.id, text="estado de rele incorrecto")
        else:
            await context.bot.send_message(update.message.chat.id, text="Tópico Incorrecto")
async def medicion(update: Update, context):
    logging.info(update.message.text)
    sql = f"SELECT timestamp, {update.message.text} FROM mediciones ORDER BY timestamp DESC LIMIT 1"
    conn = await aiomysql.connect(host=os.environ["MARIADB_SERVER"], port=3306,
                                    user=os.environ["MARIADB_USER"],
                                    password=os.environ["MARIADB_USER_PASS"],
                                    db=os.environ["MARIADB_DB"])
    async with conn.cursor() as cur:
        await cur.execute(sql)
        r = await cur.fetchone()
        if update.message.text == 'temperatura':
            unidad = 'ºC'
        else:
            unidad = '%'
        await context.bot.send_message(update.message.chat.id,
                                    text="La última {} es de {} {},\nregistrada a las {:%H:%M:%S %d/%m/%Y}"
                                    .format(update.message.text, str(r[1]).replace('.',','), unidad, r[0]))
        logging.info("La última {} es de {} {}, medida a las {:%H:%M:%S %d/%m/%Y}".format(update.message.text, r[1], unidad, r[0]))
    conn.close()

async def graficos(update: Update, context):
    logging.info(update.message.text)
    sql = f"SELECT timestamp, {update.message.text.split()[1]} FROM mediciones where id mod 2 = 0 AND timestamp >= '2024-03-16 16:09:00' - INTERVAL 1 DAY ORDER BY timestamp"
    conn = await aiomysql.connect(host=os.environ["MARIADB_SERVER"], port=3306,
                                    user=os.environ["MARIADB_USER"],
                                    password=os.environ["MARIADB_USER_PASS"],
                                    db=os.environ["MARIADB_DB"])
    async with conn.cursor() as cur:
        await cur.execute(sql)
        filas = await cur.fetchall()

        fig, ax = plt.subplots(figsize=(7, 4))
        fecha,var=zip(*filas)
        ax.plot(fecha,var)
        ax.grid(True, which='both')
        ax.set_title(update.message.text, fontsize=14, verticalalignment='bottom')
        ax.set_xlabel('fecha')
        ax.set_ylabel('unidad')

        buffer = BytesIO()
        fig.tight_layout()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buffer)
    conn.close()

def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('acercade', acercade))
    #application.add_handler(CommandHandler('kill', kill))
    application.add_handler(CommandHandler('setpoint', topicos))
    application.add_handler(CommandHandler('periodo', topicos))
    application.add_handler(CommandHandler('modo', topicos))
    application.add_handler(CommandHandler('destello', topicos))
    application.add_handler(CommandHandler('rele', topicos))
    application.add_handler(MessageHandler(filters.Regex("^(temperatura|humedad)$"), medicion))
    application.add_handler(MessageHandler(filters.Regex("^(gráfico temperatura|gráfico humedad)$"), graficos))
    application.run_polling()

if __name__ == '__main__':
    main()
