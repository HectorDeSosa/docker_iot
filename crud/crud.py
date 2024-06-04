from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os, logging
from werkzeug.middleware.proxy_fix import ProxyFix

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
mysql = MySQL(app)

# rutas
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos')
    datos = cur.fetchall()
    cur.close()
    return render_template('index.html', contactos = datos)

@app.route('/add_contact', methods=['POST'])
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
def borrar_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contactos WHERE id = {0}'.format(id))
    if mysql.connection.affected_rows():
        flash('Se eliminó un contacto')  # usa sesión
        logging.info("se eliminó un contacto")
    mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/editar/<id>', methods = ['GET'])
def conseguir_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos WHERE id = %s', (id,))
    datos = cur.fetchone()
    logging.info(datos)
    return render_template('editar-contacto.html', contacto = datos)

@app.route('/actualizar/<id>', methods=['POST'])
def actualizar_contacto(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE contactos SET nombre = %s, tel = %s, email = %s WHERE id = %s", (nombre, tel, email, id))
        if mysql.connection.affected_rows():
            flash('Se actualizó un contacto')  # usa sesión
            logging.info("se actualizó un contacto")
            mysql.connection.commit()
    return redirect(url_for('index'))
