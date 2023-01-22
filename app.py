from flask import Flask, request, render_template, redirect
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def home():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   cursor.execute("SELECT * FROM transacciones WHERE categoria IN (?, ?, ?, ?) ORDER BY fecha DESC LIMIT 12", ('Ingresos TLPTY', 'Ingresos TLPTY Otros', 'Ingresos Cambia Link', 'Ingresos Otros', ))
   data = cursor.fetchall()
   con.close()
   return render_template("index.html", data=data)

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
   return redirect("/config")

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
   return redirect("/config")

# Pantalla de Transacciones Ingresos y Egresos
@app.route('/transacciones')
def transacciones():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()

   today = datetime.now()
   today_ago = today - timedelta(days=15)
   today_ago = today_ago.strftime('%Y-%m-%d')
   today = today.strftime('%Y-%m-%d')

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
   # Listas desplegables de opciones
   cursor.execute("SELECT * FROM proveedores")
   opciones_proveedor = cursor.fetchall()
   cursor.execute("SELECT * FROM categorias")
   opciones_categoria= cursor.fetchall()
   cursor.execute("SELECT * FROM cuentas")
   opciones_cuenta = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", today=today, today_ago=today_ago, opciones_cuenta=opciones_cuenta, opciones_categoria=opciones_categoria, opciones_proveedor=opciones_proveedor, data=data, num_pages=num_pages, page=page)

@app.route('/ingresar_transaccion', methods=['POST'])
def ingresar_datos_transaccion():
   nombre_usuario = request.form['usuario_id']
   fecha = request.form['fecha']
   categoria = request.form['categoria']   
   cuenta_id = request.form['cuenta']
   monto = request.form['monto']
   if categoria == 'Ingresos TLPTY' or categoria == 'Ingresos TLPTY Otros' or categoria == 'Ingresos Cambia Link' or categoria == 'Ingresos Otros':
      monto = monto
   else:
      monto = -int(monto)

   proveedor = request.form['proveedor']
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
   cursor.execute("SELECT cuenta FROM cuentas WHERE id = ?", (cuenta_id,))
   cuenta = cursor.fetchone()[0]

   if usuario_id is None:
      return render_template("error.html", message="Debe introducir un usuario registrado y un ID de cuenta correcto")
   else:
      usuario_id = usuario_id[0]
      cursor.execute("INSERT INTO transacciones (usuario_id, fecha, descripcion, monto, categoria, cuenta, cuenta_id, checking, proveedor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (usuario_id, fecha, descripcion, monto, categoria, cuenta, cuenta_id, 'Pendiente', proveedor))
      
      cursor.execute("SELECT saldo FROM cuentas WHERE id = ?", (cuenta_id,))
      saldo = cursor.fetchone()[0]
      saldo = saldo + int(monto)
      cursor.execute("UPDATE cuentas SET saldo = ? WHERE id = ?", (saldo, cuenta_id))

      conn.commit()
      conn.close()
      return redirect(f"/transacciones?page={num_pages}")

@app.route('/eliminar_transaccion', methods=['POST'])
def eliminar_transaccion():
   conn = sqlite3.connect("database_contabilidad.db")
   cursor = conn.cursor()
   
   sentencia = "DELETE FROM transacciones WHERE id = ?"
   id_eliminar = request.form['id']

   cursor.execute("SELECT monto FROM transacciones WHERE id = ?", (id_eliminar,))
   monto = cursor.fetchone()[0]
   cursor.execute("SELECT cuenta FROM transacciones WHERE id = ?", (id_eliminar,))
   cuenta = cursor.fetchone()[0]

   cursor.execute("SELECT saldo FROM cuentas WHERE cuenta = ?", (cuenta,))
   saldo = cursor.fetchone()[0]

   saldo = saldo - int(monto)
   cursor.execute("UPDATE cuentas SET saldo = ? WHERE cuenta = ?", (saldo, cuenta))

   cursor.execute(sentencia, (id_eliminar,))
   conn.commit()
   conn.close()
   return redirect("/transacciones")

@app.route('/update_status', methods=['POST'])
def update_status():
   id = request.form['id']
   status = request.form.get('status')

   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   
   cursor.execute("UPDATE transacciones SET checking = ? WHERE id = ?", (status, id))
   conn.commit()
   conn.close()

   return redirect('/transacciones')

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
   saldo = 0
   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (nombre_usuario,))
   usuario_id = cursor.fetchone()
   if usuario_id is None:
      return render_template("error.html", message="Debe introducir un usuario registrado")
   else:
      usuario_id = usuario_id[0]
      cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES (?, ?, ?, ?)", (usuario_id, cuenta, cuenta_descripcion, saldo))
      conn.commit()
      conn.close()
      return redirect("/cuentas")

@app.route('/buscar_fecha', methods=['POST', 'GET'])
def buscar_fecha():
   if request.method == 'POST':
        buscar_inicial = request.form['buscar_inicial']
        buscar_final = request.form['buscar_final']
   else:
        buscar_inicial = request.args.get('buscar_inicial')
        buscar_final = request.args.get('buscar_final')
        
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()

   today = datetime.now()
   today_ago = today - timedelta(days=15)
   today_ago = today_ago.strftime('%Y-%m-%d')
   today = today.strftime('%Y-%m-%d')

   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute(f"SELECT COUNT(*) FROM transacciones WHERE fecha BETWEEN '{buscar_inicial}' AND '{buscar_final}'")
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM transacciones WHERE fecha BETWEEN '{buscar_inicial}' AND '{buscar_final}' LIMIT {per_page} OFFSET {(page-1)*per_page}")
   data = cursor.fetchall()

   cursor.execute("SELECT * FROM proveedores")
   opciones_proveedor = cursor.fetchall()

   cursor.execute("SELECT * FROM categorias")
   opciones_categoria= cursor.fetchall()

   cursor.execute("SELECT * FROM cuentas")
   opciones_cuenta = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", today=today, today_ago=today_ago, opciones_cuenta=opciones_cuenta, opciones_categoria=opciones_categoria, opciones_proveedor=opciones_proveedor, data=data, num_pages=num_pages, page=page)


@app.route('/buscar_cuenta', methods=['POST'])
def buscar_cuenta():
   buscar = request.form['buscar']
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()

   today = datetime.now()
   today_ago = today - timedelta(days=15)
   today_ago = today_ago.strftime('%Y-%m-%d')
   today = today.strftime('%Y-%m-%d')

   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM transacciones WHERE cuenta = ?", (buscar,))
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM transacciones WHERE cuenta = ? LIMIT {per_page} OFFSET {(page-1)*per_page}", (buscar,))
   data = cursor.fetchall()

   cursor.execute("SELECT * FROM proveedores")
   opciones_proveedor = cursor.fetchall()

   cursor.execute("SELECT * FROM categorias")
   opciones_categoria= cursor.fetchall()

   cursor.execute("SELECT * FROM cuentas")
   opciones_cuenta = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", today=today, today_ago=today_ago, opciones_cuenta=opciones_cuenta, opciones_categoria=opciones_categoria, opciones_proveedor=opciones_proveedor, data=data, num_pages=num_pages, page=page)

@app.route('/buscar_categoria', methods=['POST'])
def buscar_categoria():
   buscar = request.form['buscar']
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()

   today = datetime.now()
   today_ago = today - timedelta(days=15)
   today_ago = today_ago.strftime('%Y-%m-%d')
   today = today.strftime('%Y-%m-%d')

   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM transacciones WHERE categoria = ?", (buscar,))
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM transacciones WHERE categoria = ? LIMIT {per_page} OFFSET {(page-1)*per_page}", (buscar,))
   data = cursor.fetchall()

   cursor.execute("SELECT * FROM proveedores")
   opciones_proveedor = cursor.fetchall()

   cursor.execute("SELECT * FROM categorias")
   opciones_categoria= cursor.fetchall()

   cursor.execute("SELECT * FROM cuentas")
   opciones_cuenta = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", today=today, today_ago=today_ago, opciones_cuenta=opciones_cuenta, opciones_categoria=opciones_categoria, opciones_proveedor=opciones_proveedor, data=data, num_pages=num_pages, page=page)

@app.route('/buscar_estado', methods=['POST'])
def buscar_estado():
   buscar = request.form['buscar_estado']
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()

   today = datetime.now()
   today_ago = today - timedelta(days=15)
   today_ago = today_ago.strftime('%Y-%m-%d')
   today = today.strftime('%Y-%m-%d')

   # Obtenemos la página solicitada
   page = request.args.get('page', default=1, type=int)
   # Establecemos el número de elementos por página
   per_page = 12
   # Calculamos el número de páginas
   cursor.execute("SELECT COUNT(*) FROM transacciones WHERE checking = ?", (buscar,))
   num_items = cursor.fetchone()[0]
   num_pages = num_items // per_page + (num_items % per_page > 0)
   # Realizamos la consulta limitando el número de resultados y saltando a la página deseada
   cursor.execute(f"SELECT * FROM transacciones WHERE checking = ? LIMIT {per_page} OFFSET {(page-1)*per_page}", (buscar,))
   data = cursor.fetchall()
   
   cursor.execute("SELECT * FROM proveedores")
   opciones_proveedor = cursor.fetchall()

   cursor.execute("SELECT * FROM categorias")
   opciones_categoria= cursor.fetchall()

   cursor.execute("SELECT * FROM cuentas")
   opciones_cuenta = cursor.fetchall()
   con.close()
   return render_template("transacciones.html", today=today, today_ago=today_ago, opciones_cuenta=opciones_cuenta, opciones_categoria=opciones_categoria, opciones_proveedor=opciones_proveedor, data=data, num_pages=num_pages, page=page)

@app.route('/ingresar_proveedor', methods=['POST'])
def ingresar_proveedor():
   proveedor = request.form['proveedor']
   proveedor_descripcion = request.form['proveedor_descripcion']
   conn = sqlite3.connect('database_contabilidad.db')
   cursor = conn.cursor()
   cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES (?, ?)", (proveedor, proveedor_descripcion))
   conn.commit()
   conn.close()
   return redirect("/config")

@app.route('/informes')
def informes():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   
   def get_current_time():
      return datetime.now()
   current_time = get_current_time()
   today_semanal = current_time - timedelta(days=7)
   today_semanal = today_semanal.strftime('%Y-%m-%d')   
   today_mensual = current_time - timedelta(days=30)
   today_mensual = today_mensual.strftime('%Y-%m-%d')
   current_time = current_time.strftime('%Y-%m-%d')

   def sum_categoria_diario(categoria):
      cursor.execute(f"SELECT SUM(monto) FROM transacciones WHERE categoria = '{categoria}' AND fecha = '{current_time}'")
      x = cursor.fetchone()
      if x == (None,):
         x = 0
      else:
         x = abs(x[0])
      return x

   def sum_categoria_semanal(categoria):
      cursor.execute(f"SELECT SUM(monto) FROM transacciones WHERE categoria = '{categoria}' AND fecha BETWEEN '{today_semanal}' AND '{current_time}'")
      x = cursor.fetchone()
      if x == (None,):
         x = 0
      else:
         x = abs(x[0])
      return x
   
   def sum_categoria_mensual(categoria):
      cursor.execute(f"SELECT SUM(monto) FROM transacciones WHERE categoria = '{categoria}' AND fecha BETWEEN '{today_mensual}' AND '{current_time}'")
      x = cursor.fetchone()
      if x == (None,):
         x = 0
      else:
         x = abs(x[0])
      return x
 
# Gastos Familiares
# Gastos Familiares Diarios
   diarios_familiares = sum_categoria_diario('Gastos Familiares')

# Gastos Familiares Semanales
   semanal_familiares = sum_categoria_semanal('Gastos Familiares')

# Gastos Familiares Mensuales
   mensual_familiares = sum_categoria_mensual('Gastos Familiares')

# TLPTY Gastos
# Gastos Todo Licencias Diarios - Gastos para vender productos
   diarios_tlpty = sum_categoria_diario('Gastos TLPTY')

# Gastos Todo Licencias Semanales - Gastos para vender productos
   semanal_tlpty = sum_categoria_semanal('Gastos TLPTY')

# Gastos Todo Licencias Mensuales - Gastos para vender productos
   mensual_tlpty = sum_categoria_mensual('Gastos TLPTY')

# TLPTY Costos
# Costos Todo Licencias Diarios - Costos de los productos
   diarios_tlptyc = sum_categoria_diario('Costos TLPTY')

# Costos Todo Licencias Semanales - Costos de los productos
   semanal_tlptyc = sum_categoria_semanal('Costos TLPTY')

# Costos Todo Licencias Mensuales - Costos de los productos
   mensual_tlptyc = sum_categoria_mensual('Costos TLPTY')

# Cambia Link Gastos
# Gastos Cambia Link Diarios - Gastos para cambios
   diarios_cl = sum_categoria_diario('Gastos Cambia Link')

# Gastos Cambia Link Semanales - Gastos para cambios
   semanal_cl = sum_categoria_semanal('Gastos Cambia Link')

# Gastos Cambia Link Mensuales - Gastos para cambios
   mensual_cl = sum_categoria_mensual('Gastos Cambia Link')

# Cambia Link Costos
# Costos Cambia Link Diarios - Costos de los cambios
   diarios_clc = sum_categoria_diario('Costos Cambia Link')

# Costos Cambia Link Semanales - Costos de los cambios
   semanal_clc = sum_categoria_semanal('Costos Cambia Link')

# Costos Cambia Link Mensuales - Costos de los cambios
   mensual_clc = sum_categoria_mensual('Costos Cambia Link')
   
   diarios_total = abs(diarios_tlpty+diarios_tlptyc+diarios_cl+diarios_clc+diarios_familiares)
   semanal_total = abs(semanal_tlpty+semanal_tlptyc+semanal_cl+semanal_clc+semanal_familiares)
   mensual_total = abs(mensual_tlpty+mensual_tlptyc+mensual_cl+mensual_clc+mensual_familiares)

# Ingresos
# Ingresos TLPTY Diarios
   diarios_itlpty = sum_categoria_diario('Ingresos TLPTY')

# Ingresos TLPTY Semanales
   semanal_itlpty = sum_categoria_semanal('Ingresos TLPTY')

# Ingresos TLPTY Mensuales
   mensual_itlpty = sum_categoria_mensual('Ingresos TLPTY')

# Ingresos Otros TLPTY Diarios
   diarios_iotlpty = sum_categoria_diario('Ingresos TLPTY Otros')

# Ingresos Otros TLPTY Semanales
   semanal_iotlpty = sum_categoria_semanal('Ingresos TLPTY Otros')

# Ingresos Otros TLPTY Mensuales
   mensual_iotlpty = sum_categoria_mensual('Ingresos TLPTY Otros')

   ingresos_diarios_total = abs(diarios_itlpty+diarios_iotlpty)
   ingresos_semanal_total = abs(semanal_itlpty+semanal_iotlpty)
   ingresos_mensual_total = abs(mensual_itlpty+mensual_iotlpty)

# Ingresos Cambia Link Diarios
   diarios_icl = sum_categoria_diario('Ingresos Cambia Link')

# Ingresos Cambia Link Semanales
   semanal_icl = sum_categoria_semanal('Ingresos Cambia Link')

# Ingresos Cambia Link Mensuales
   mensual_icl = sum_categoria_mensual('Ingresos Cambia Link')

# Ingresos Otros Diarios
   diarios_iocl = sum_categoria_diario('Ingresos Otros')

# Ingresos Otros Semanales
   semanal_iocl = sum_categoria_semanal('Ingresos Otros')

# Ingresos Otros Mensuales
   mensual_iocl = sum_categoria_mensual('Ingresos Otros')

   con.close()
   return render_template("informes.html", ingresos_diarios_total=ingresos_diarios_total, ingresos_semanal_total=ingresos_semanal_total, ingresos_mensual_total=ingresos_mensual_total, diarios_total=diarios_total, semanal_total=semanal_total, mensual_total=mensual_total, diarios_familiares=diarios_familiares, semanal_familiares=semanal_familiares, mensual_familiares=mensual_familiares, diarios_tlpty=diarios_tlpty, semanal_tlpty=semanal_tlpty, mensual_tlpty=mensual_tlpty, diarios_tlptyc=diarios_tlptyc, semanal_tlptyc=semanal_tlptyc, mensual_tlptyc=mensual_tlptyc, diarios_cl=diarios_cl, semanal_cl=semanal_cl, mensual_cl=mensual_cl, diarios_clc=diarios_clc, semanal_clc=semanal_clc, mensual_clc=mensual_clc, diarios_itlpty=diarios_itlpty, semanal_itlpty=semanal_itlpty, mensual_itlpty=mensual_itlpty, diarios_iotlpty=diarios_iotlpty, semanal_iotlpty=semanal_iotlpty, mensual_iotlpty=mensual_iotlpty, diarios_icl=diarios_icl, semanal_icl=semanal_icl, mensual_icl=mensual_icl, diarios_iocl=diarios_iocl, semanal_iocl=semanal_iocl, mensual_iocl=mensual_iocl)

@app.route('/config')
def config():
   con = sqlite3.connect("database_contabilidad.db")
   cursor = con.cursor()
   cursor.execute("SELECT * FROM proveedores")
   data_proveedores = cursor.fetchall()
   cursor.execute("SELECT * FROM usuarios")
   data_usuarios = cursor.fetchall()
   con.close()
   return render_template("config.html", data_proveedores=data_proveedores, data_usuarios=data_usuarios)
   
if __name__ == '__main__':
   app.run(debug=True)