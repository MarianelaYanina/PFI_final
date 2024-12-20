from colorama import init, Fore, Back
init(autoreset=True)
import sqlite3
import os



#BASE DE DATOS

def conectar_db():
    directorio_actual= os.path.dirname(os.path.abspath(__file__))
    nombre_bbdd= os.path.join(directorio_actual,"inventario.db")
    try:
        return sqlite3.connect(nombre_bbdd)
    except sqlite3.Error as e:
        print(Back.RED + f"Error al conectar la Base de Datos {e}.")
        return None



def inicializar_bbdd(conexion=conectar_db()):
    cursor=conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL CHECK(cantidad >= 0),
            precio REAL NOT NULL CHECK(precio > 0),
            categoria TEXT        
        )
''')
    
    conexion.commit()
    conexion.close()

#CREACION DEL MENU DE OPCIONES

def mostrar_menu():
    print(Fore.CYAN + "Menú para la gestión de productos: \n")
    print("1.Registro: Alta de productos nuevos.")
    print("2.Visualizacion: Consulta de datos de productos.")
    print("3.Actualizacion: Modificar la cantidad en stock de un producto.")
    print("4.Eliminacion: Dar de baja productos.")
    print("5.Listado: Listado completo de los productos en la base de datos.")
    print("6.Reporte de bajo stock: Lista de productos con cantidad minimo bajo.")
    print(Fore.RED + "7.SALIR")

def registrar_producto(conexion=conectar_db()):

    print(Back.CYAN + "\n ---REGISTRO DE PRODUCTO NUEVO ---\n")

    nombre=input("Nombre del producto: ").strip()
    descripcion=input("Descripción del producto: ").strip()

    #validacion para carga de precio

    while True:
        try:
            precio=float(input("Precio del producto: $ "))
            if precio > 0 :
                break
            else:
                print(Back.RED + "Entrada invalida, ingrese un numero mayor a cero.")
        except ValueError:
            print(Back.RED + "Entrada invalida, debe ingresar un numero.")

    #validacion para la carga de cantidad

    while True:
        try:
            cantidad=float(input(f"Cantidad en stock de {nombre}: "))
            if cantidad > 0 :
                break
            else:
                print(Back.RED + "Entrada invalida, el stock no puede ser un número negativo.")
        except ValueError:
            print(Back.RED + "Entrada invalida, debe ingresar un numero.")

    categoria=input("Categoria del producto: ").strip()

    cursor=conexion.cursor()

    try:
        cursor.execute('''
            INSERT INTO productos (codigo, nombre, descripcion, cantidad, precio, categoria)
        VALUES (NULL, ?, ?, ?, ?, ?)
        ''',(nombre, descripcion, cantidad, precio, categoria))

        id_producto= cursor.lastrowid #10
        codigo=f"PROD{id_producto}"
        cursor.execute('''
            UPDATE productos SET codigo = ? WHERE id = ?''', (codigo, id_producto))

        conexion.commit()
        print(Fore.GREEN + f"producto registrado con éxito. codigo asignado: {codigo}.")


    except sqlite3.IntegrityError:
        print(Back.RED + "Error, no se pudo cargar el producto.")

    finally:
        conexion.close()

def buscar_producto(conexion=conectar_db()):
    
    print(Back.CYAN + "\n --- BUSQUEDA DE PRODUCTO ---\n")
    codigo=input("Ingrese el código del porducto que desea buscar: ").strip()

    cursor=conexion.cursor()
    cursor.execute('''SELECT * FROM productos WHERE codigo = ?''', (codigo,)) #no puede qedar abierto el llamado a la variable.
    producto= cursor.fetchone()

    conexion.close()

    if producto:
        _, codigo, nombre, descripcion, cantidad, precio, categoria = producto
        print(f"\n Producto encontrado con el código   :   {codigo}.")
        print(f"Nombre                                 :   {nombre}.")
        print(f"Descripción                            :   {descripcion}.")
        print(f"Cantidad                               :   {cantidad}.")
        print(f"Precio                                 :  ${precio}.")
        print(f"Categoria                              :   {categoria}.")
    else:
        print(Back.RED + f"No se encontro el producto bajo el código: {codigo}.")

def mostrar_productos(conexion=conectar_db()):
    
    print(Back.CYAN + "\n ---LISTADO DE TODOS LOS PRODUCTOS ---\n")
    cursor=conexion.cursor()

    cursor.execute('''SELECT * FROM productos''')
    productos=cursor.fetchall()
    
    conexion.close()

    if not productos:
        print(Back.RED + "El inventario esta vacio, no  hay productos registrados.")
    else:
        for _, codigo, nombre, descripcion, cantidad, precio ,categoria in productos:
            print(f"\n Código       :   {codigo}.")
            print(f"Nombre          :   {nombre}.")
            print(f"Descripción     :   {descripcion}.")
            print(f"Cantidad        :   {cantidad}.")
            print(f"Precio          :  ${precio}.")
            print(f"Categoria       :   {categoria}.")

def actualizar_producto(conexion=conectar_db()):
    
    print(Back.CYAN + "\n --- ACTUALIZACION DE PRODUCTO ---\n")
    cursor=conexion.cursor()

    #solicitud de codigo y validacion
    codigo=input("Por favor ingrese el código del producto que desea modificar: ").strip().upper()
    

    cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
    producto=cursor.fetchone()

    if producto:
        _,codigo, nombre, descripcion, cantidad, precio, categoria = producto
        print(f"Producto encontrado con el código: {codigo}.")
        print("Ingrese los nuevos datos del producto o presione 'ENTER' para salir.")

        nuevo_nombre= input("Ingrese el nuevo nombre: ") or nombre #nuevo nombre O el nombre q ya tiene.
        nueva_descripcion= input("Ingrese una nueva descripción: ") or descripcion

        while True:
            nueva_cantidad=input("ingrese la nueva cantidad: ")
            if not nueva_cantidad:
                nueva_cantidad = cantidad
                break
            try:
                nueva_cantidad=int(nueva_cantidad)
                if nueva_cantidad >= 0 :
                    break
                else:
                    print(Back.RED + "La cantidad debe ser un numero mayor a cero.")
            except ValueError:
                print(Back.RED + "Por favor ingrese un numero.")

            while True:
                nuevo_precio=input("Ingrese el nuevo precio: $")
                if not nuevo_precio:
                    nuevo_precio = precio #se tiene q comparar con la variable
                    break
                try:
                    nuevo_precio=int(nuevo_precio)
                    if nuevo_precio >= 0 :
                        break
                    else:
                        print(Back.RED + "El precio debe ser un numero mayor a cero.")
                except ValueError:
                    print(Back.RED + "Por favor ingrese un numero.")

        nueva_categoria=input("Ingrese la nueva categoria: ") or categoria

        cursor.execute('''
        UPDATE productos SET nombre=', descripcion=?, precio=?, cantidad=?, categoria=? WHERE codigo=?
        ''',
            (nuevo_nombre, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_categoria, codigo))
        
        conexion.commit()

    else: #x si no encuentra el codigo
        print(Back.RED + f"El código {codigo} no se encuentra registrado.")

def eliminar_producto(conexion=conectar_db()):

    print(Back.CYAN + "\n --- ELIMINAR PRODUCTO ---\n")
    
    codigo= input("Ingrese el código del producto que desea eliminar: ")

    cursor=conexion.cursor()
    cursor.execute('''DELETE FROM productos WHERE codigo=?''', (codigo))

    if cursor.rowcount:
        conexion.commit()
        print(Fore.GREEN + "Producto eliminado con éxito.")
    else:
        print(Back.RED + f"No se encontro ningún producto con el código: {codigo}.")

def reporte_bajo_stock(conexion=conectar_db()):

    print(Fore.CYAN + "\n--- REPORTE DE BAJO STOCK ---\n")

    while True:
        try:
            limite=int(input("Ingrese el limite de cantidad para el reporte de bajo stock: "))
            if limite >= 0:
                break
            else:
                print(Back.RED + "El límite de bajo stock no puede ser negativo.")
        except ValueError:
            print(Back.RED + "Error: Ingrese valores numéricos.")

    cursor=conexion.cursor()
    cursor.execute('''SELECT * FROM productos WHERE cantidad<=? ORDER BY cantidad DESC''',(limite, ))
    productos=cursor.fetchall()
    conexion.close()

    if not productos:
        print(Fore.GREEN + "No se encontraron productos en bajo stock.")

    else:
        print("\n--- Productos encontrados en BAJO STOCK ---\n")
        for _,codigo, nombre, descripcion, cantidad, precio, categoria in productos:
            print(f"\n Código       :   {codigo}.")
            print(f"Nombre          :   {nombre}.")
            print(f"Descripción     :   {descripcion}.")
            print(f"Cantidad        :   {cantidad}.")
            print(f"Precio          :  ${precio}.")
            print(f"Categoria       :   {categoria}.")
            print("-" * 50)


#PROGRAMA PRINCIPAL (el if va a corroborar q la ejecucion de la BD no sea un modulo, osea q este x dentro no por fuera)  
if __name__ == "__main__":  #si el nombre de este archivo es igual al contenido y no a un modulo, puedo ejecutar el programa
    inicializar_bbdd()

    while True:
        mostrar_menu()

        try:
            opcion=int(input("\n Ingrese una opcion entre 1 y 7: "))

            if opcion == 7:
                print("\n Saliendo del sistema, ¡HASTA PRONTO! :D ")
                break

            elif opcion == 1:
                registrar_producto()

            elif opcion == 2:
                buscar_producto()

            elif opcion == 3:
                actualizar_producto()

            elif opcion == 4:
                eliminar_producto()

            elif opcion == 5:
                mostrar_productos()

            elif opcion == 6:
                reporte_bajo_stock()

            else:
                print(Back.RED + "Opción no valida, por favor seleccione entre 1 y 7.")

        except ValueError:
            print(Back.RED + "Opción no valida, por favor ingrese un numero.")



