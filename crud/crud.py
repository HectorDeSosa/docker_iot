from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import os, logging
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
import ssl, certifi, json, traceback
import aiomqtt, asyncio
logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)
app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
app.config['PERMANENT_SESSION_LIFETIME']=300
mysql = MySQL(app)

# rutas

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    """Registrar usuario"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("usuario"):
            return "el campo usuario es oblicatorio"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "el campo contraseña es oblicatorio"

        passhash=generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (usuario, hash) VALUES (%s,%s)", (request.form.get("usuario"), passhash[17:]))
        if mysql.connection.affected_rows():
            flash('Se agregó un usuario')  # usa sesión
            logging.info("se agregó un usuario")
        mysql.connection.commit()
        return redirect(url_for('index'))

    return render_template('registrar.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("usuario"):
            return "el campo usuario es oblicatorio"
        # Ensure password was submitted
        elif not request.form.get("password"):
            return "el campo contraseña es oblicatorio"

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario LIKE %s", (request.form.get("usuario"),))
        rows=cur.fetchone()
        if(rows):
            if (check_password_hash('scrypt:32768:8:1$' + rows[2],request.form.get("password"))):
                session.permanent = True
                session["user_id"]=request.form.get("usuario")
                logging.info("se autenticó correctamente")
                return redirect(url_for('index'))
            else:
                flash('usuario o contraseña incorrecto')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/')
@require_login
def index():
    return render_template('index.html')

async def main():
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
        try: 
            if request.method == 'POST' and 'setbotton' in request.form:
                if request.form['ventilador']=='vent1':
                    await client.publish(topic='setpoint1', payload=str(request.form['setpoint']) , qos=1)
                else:
                    await client.publish(topic='setpoint2', payload=str(request.form['setpoint']) , qos=1)
            elif request.method == 'POST' and 'encender' in request.form:
                if request.form['ventilador']=='vent1':
                    await client.publish(topic='rele1', payload='ON' , qos=1)
                else:
                    await client.publish(topic='rele2', payload='ON' , qos=1)
            
            elif request.method == 'POST' and 'apagar' in request.form:
                if request.form['ventilador']=='vent1':
                    await client.publish(topic='rele1', payload='OFF' , qos=1)
                else:
                    await client.publish(topic='rele2', payload='OFF' , qos=1)
            elif request.method == 'POST' and 'modo' in request.form:
                if request.form['ventilador']=='vent1':
                    await client.publish(topic='modo1', payload=str(request.form['modosel']) , qos=1)
                else:
                    await client.publish(topic='modo2', payload=str(request.form['modosel']) , qos=1)
            elif request.method == 'POST' and 'perbutton' in request.form:
                await client.publish(topic='periodo', payload=str(request.form['periodo']) , qos=1)
        except:
            logging.info('Error en botones')
            return "Error en los botones de control"


@app.route('/topico', methods=['GET','POST'])
@require_login
def topico():
    if request.method == 'POST':
        if not request.form.get("ventilador"):
            return 'Seleccionar un ventilador es obligatorio'
        if 'modo' in request.form:
            if not request.form.get('modosel'):
                return "Ingresar un modo es obligatorio"
        asyncio.run(main()) 
    return redirect(url_for('index'))

@app.route('/tema', methods=['GET','POST'])
@require_login
def tema():
    if request.method == 'POST':
        if not request.form.get("temas"):
            return 'Seleccionar un tema'
        session["theme"]=request.form.get("temas")
        logging.info("se establecio el tema: "+ request.form.get("temas"))
    return redirect(url_for('index'))

#no se usa
"""
@app.route('/add_contact', methods=['POST'])
@require_login
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contactos (nombre, tel, email) VALUES (%s,%s,%s)"
                    , (nombre, tel, email))
        if mysql.connection.affected_rows():
            flash('Se agregó un contacto')  # usa sesión
            logging.info("se agregó un contacto")
            mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/borrar/<string:id>', methods = ['GET'])
@require_login
def borrar_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contactos WHERE id = {0}'.format(id))
    if mysql.connection.affected_rows():
        flash('Se eliminó un contacto')  # usa sesión
        logging.info("se eliminó un contacto")
        mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/editar/<id>', methods = ['GET'])
@require_login
def conseguir_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos WHERE id = %s', (id,))
    datos = cur.fetchone()
    logging.info(datos)
    return render_template('editar-contacto.html', contacto = datos)

@app.route('/actualizar/<id>', methods=['POST'])
@require_login
def actualizar_contacto(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE contactos SET nombre=%s, tel=%s, email=%s WHERE id=%s", (nombre, tel, email, id))
    if mysql.connection.affected_rows():
        flash('Se actualizó un contacto')  # usa sesión
        logging.info("se actualizó un contacto")
        mysql.connection.commit()
    return redirect(url_for('index'))
"""
@app.route("/logout")
@require_login
def logout():
    session.clear()
    logging.info("el usuario {} cerró su sesión".format(session.get("user_id")))
    return redirect(url_for('index'))
