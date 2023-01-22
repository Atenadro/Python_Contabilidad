import sqlite3

# Abrir conexión a la base de datos
conn = sqlite3.connect("database_contabilidad.db")

# Crear cursor
cursor = conn.cursor()

# Crear tablas
cursor.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, apellido TEXT, email TEXT, contrasena CHAR)")
cursor.execute("CREATE TABLE cuentas (id INTEGER PRIMARY KEY, usuario_id INTEGER, cuenta TEXT, cuenta_descripcion TEXT, saldo REAL)")
cursor.execute("CREATE TABLE transacciones (id INTEGER PRIMARY KEY, usuario_id INTEGER, fecha DATE, cuenta TEXT, cuenta_id INTEGER, monto REAL, proveedor TEXT, categoria TEXT, descripcion TEXT, checking TEXT)")
cursor.execute("CREATE TABLE categorias (id INTEGER PRIMARY KEY, categoria TEXT, categoria_descripcion TEXT)")
cursor.execute("CREATE TABLE proveedores (id INTEGER PRIMARY KEY, proveedor TEXT, proveedor_descripcion TEXT)")
cursor.execute("CREATE TABLE productos (id INTEGER PRIMARY KEY, proveedor_id INTEGER, nombre TEXT, precio REAL)")

# Insertar datos a la tabla de Usuarios
cursor.execute("INSERT INTO usuarios (nombre, apellido, email, contrasena) VALUES ('Juan', 'Urdaneta', 'juandiegourdaneta@gmail.com', 'contrasena')")

# Insertar datos a la tabla de Cuentas
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Banco General', 'Yappy', '100')")
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Yappy', 'TLPTY', '0')")
cursor.execute("INSERT INTO cuentas (usuario_id, cuenta, cuenta_descripcion, saldo) VALUES ('1', 'Banistmo', 'Corriente', '220')")

# Insertar datos a la tabla de Proveedores
cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES ('', '')")
cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES ('iCodesWholesale', '')")
cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES ('ScratchMonkeys', '')")
cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES ('G2A', '')")
cursor.execute("INSERT INTO proveedores (proveedor, proveedor_descripcion) VALUES ('Kinguin', '')")

# Insertar datos a la tabla de Categorias
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Ingresos TLPTY', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Ingresos TLPTY Otros', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Ingresos Cambia Link', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Ingresos Otros', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Gastos TLPTY', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Costos TLPTY', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Gastos Cambia Link', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Costos Cambia Link', '')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Gastos Familiares', '- Arriendo')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Gastos Familiares', '- Mercado')")
cursor.execute("INSERT INTO categorias (categoria, categoria_descripcion) VALUES ('Gastos Familiares', '- Comidas Calle')")



# Insertar datos a la tabla de transacciones
cursor.execute("INSERT INTO transacciones (usuario_id, fecha, cuenta, cuenta_id, monto, categoria, descripcion, checking) VALUES ('1', '', 'Banco General', '1', '100', 'prueba', 'prueba000', '0')")
cursor.execute("INSERT INTO transacciones (usuario_id, fecha, cuenta, cuenta_id, monto, categoria, descripcion, checking) VALUES ('1', '', 'Banistmo', '3', '220', 'prueba', 'prueba000', '1')")

# Realizar commit
conn.commit()

# Cerrar conexión
conn.close()
