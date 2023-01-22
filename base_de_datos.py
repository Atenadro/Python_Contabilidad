import sqlite3

# Abrir conexión a la base de datos
conn = sqlite3.connect("database_contabilidad.db")

# Crear cursor
cursor = conn.cursor()

# Crear tablas
cursor.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, apellido TEXT, email TEXT, contrasena CHAR)")
cursor.execute("CREATE TABLE cuentas (id INTEGER PRIMARY KEY, usuario_id INTEGER, cuenta TEXT, cuenta_descripcion TEXT, saldo REAL)")
cursor.execute("CREATE TABLE transacciones (id INTEGER PRIMARY KEY, usuario_id INTEGER, fecha DATE, tipo TEXT, cuenta TEXT, monto REAL, categoria TEXT, descripcion TEXT)")
cursor.execute("CREATE TABLE proveedores (id INTEGER PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE productos (id INTEGER PRIMARY KEY, proveedor_id INTEGER, nombre TEXT, precio REAL)")

# Insertar datos a la tabla de usuarios
cursor.execute("INSERT INTO usuarios (nombre, apellido, email, contrasena) VALUES ('Juan', 'Urdaneta', 'juandiegourdaneta@gmail.com', 'contrasena')")

# Insertar datos a la tabla de cuentas
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Banco General', 'TLPTY', '100')")
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Yappy', 'TLPTY', '0')")
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Banistmo', 'TLPTY', '220')")

# Insertar datos a la tabla de transacciones
cursor.execute("INSERT INTO transacciones (usuario_id, fecha, tipo, cuenta, monto, categoria, descripcion) VALUES ('1', '', 'ingreso', 'Banco General', '100', 'prueba', 'prueba000')")
cursor.execute("INSERT INTO transacciones (usuario_id, fecha, tipo, cuenta, monto, categoria, descripcion) VALUES ('1', '', 'ingreso', 'Banistmo', '220', 'prueba', 'prueba000')")

# Realizar commit
conn.commit()

# Cerrar conexión
conn.close()
