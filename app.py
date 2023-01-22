from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM usuarios")
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM usuarios LIMIT {per_page} OFFSET {(page-1)*per_page}")
   data = cursor.fetchall()
   con.close()
   return render_template("index.html", data=data, num_pages=num_pages, page=page)

@app.route('/ingresar_datos', methods=['POST'])
def ingresar_datos():
   id = request.form['id']
   nombre = request.form['nombre']
   apellido = request.form['apellido']
   email = request.form['email']
   contrasena = request.form['contrasena']
   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   cursor.execute("INSERT INTO usuarios (id, nombre, apellido, email, contrasena) VALUES (?, ?, ?, ?, ?)", (id, nombre, apellido, email, contrasena))
   conn.commit()
   conn.close()
   return redirect("/")

@app.route('/editar_datos', methods=['POST'])
def editar_datos():
   id = request.form['id']
   nombre = request.form['nombre']
   apellido = request.form['apellido']
   email = request.form['email']
   contrasena = request.form['contrasena']
   conn = sqlite3.connect("database_contabilidad.db")
   cursor = conn.cursor()
   cursor.execute("UPDATE usuarios SET nombre=?, apellido=?, contrasena=?, email=?, WHERE id=?", (nombre, apellido, id, email, contrasena))
   conn.commit()
   conn.close()
   return redirect("/")

@app.route('/eliminar', methods=['POST'])
def eliminar():
   conn = sqlite3.connect("database_contabilidad.db")
   cursor = conn.cursor()
   sentencia = "DELETE FROM usuarios WHERE id = ?"
   id_eliminar = request.form['id']
   cursor.execute(sentencia, (id_eliminar,))
   conn.commit()
   conn.close()
   return redirect("/")

@app.route('/transacciones')
def transacciones():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM transacciones")
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM transacciones LIMIT {per_page} OFFSET {(page-1)*per_page}")
   data = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", data=data, num_pages=num_pages, page=page)

@app.route('/ingresar_transaccion', methods=['POST'])
def ingresar_datos_transaccion():
   nombre_usuario = request.form['usuario_id']
   fecha = request.form['fecha']
   tipo = request.form['tipo']
   nombre_cuenta = request.form['cuenta']
   monto = request.form['monto']
   if tipo == 'ingreso':
      monto = monto
   else:
      monto = -int(monto)
   categoria = request.form['categoria']
   descripcion = request.form['descripcion']
   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM transacciones")
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (nombre_usuario,))
   usuario_id = cursor.fetchone()
   cursor.execute("SELECT cuenta FROM cuentas WHERE id = ?", (nombre_cuenta,))
   cuenta = cursor.fetchone()
   if usuario_id is None:
      return render_template("error.html", message="Debe introducir un usuario registrado y un ID de cuenta correcto")
   else:
      if cuenta is None:
         return render_template("error.html", message="Debe introducir una ID de cuenta correcto")
      else:
         cuenta = cuenta[0]
         usuario_id = usuario_id[0]
         cursor.execute("INSERT INTO transacciones (usuario_id, fecha, descripcion, monto, tipo, categoria, cuenta) VALUES (?, ?, ?, ?, ?, ?, ?)", (usuario_id, fecha, descripcion, monto, tipo, categoria, cuenta))
         
         cursor.execute("SELECT saldo FROM cuentas WHERE cuenta = ?", (cuenta,))
         saldo = cursor.fetchone()[0]
         saldo = saldo + int(monto)
         cursor.execute("UPDATE cuentas SET saldo = ? WHERE cuenta = ?", (saldo, cuenta))

         conn.commit()
         conn.close()
         return redirect(f"/transacciones?page={num_pages}")

@app.route('/cuentas')
def cuentas():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   cursor.execute("SELECT * FROM cuentas")
   data = cursor.fetchall()

   con.close()
   return render_template("cuentas.html", data=data)

@app.route('/ingresar_cuenta', methods=['POST'])
def ingresar_cuenta():
   nombre_usuario = request.form['usuario_id']
   cuenta = request.form['cuenta']
   cuenta_descripcion = request.form['cuenta_descripcion']
   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (nombre_usuario,))
   usuario_id = cursor.fetchone()
   if usuario_id is None:
      return render_template("error.html", message="Debe introducir un usuario registrado")
   else:
      usuario_id = usuario_id[0]
      cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, saldo) VALUES (?, ?, ?)", (usuario_id, cuenta, cuenta_descripcion))
      conn.commit()
      conn.close()
      return redirect("/cuentas")
   

if __name__ == '__main__':
   app.run(debug=True)
