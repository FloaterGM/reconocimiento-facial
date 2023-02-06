#--------------------------------------Importamos librerias--------------------------------------------

from tkinter import *
import os
import cv2
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np
from datetime import datetime
import pyodbc
from mysql.connector import Error
import face_recognition as fr

#---------------------------- Conexion con base de datos ---------------------------------------

def create_server_connection():
    connection = NONE
    try:
        connection = ("Driver={SQL Server Native Client 11.0};"
            "Server=pepeelchispa.database.windows.net;"
            "Database=turnos2;"
            "UID=cvalenciah;"
            "PWD=Cris123.;")

        conexion = pyodbc.connect(connection)
        print("SQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return conexion

conexion = create_server_connection()

#---------------------------- Creacion de insert query ---------------------------------------

def insertData(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


#---------------------------- Creacion de read query ------------------------------------------

def readData(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


#--------------------------- Funcion para almacenar el registro facial --------------------------------------
    
def registro_facial():
    if usuarioNombre.get() != '' and usuario.get() != '':
        query = f"insert into empleado (cedula, nombre) values ('{usuario.get()}', '{usuarioNombre.get()}')"
        insertData(conexion, query)

        #Vamos a capturar el rostro
        cap = cv2.VideoCapture(0)               #Elegimos la camara con la que vamos a hacer la deteccion
        while(True):
            ret,frame = cap.read()              #Leemos el video
            cv2.imshow('Registro Facial',frame)         #Mostramos el video en pantalla
            if cv2.waitKey(1) == 27:            #Cuando oprimamos "Escape" rompe el video
                break
        usuario_img = usuario.get()
        os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial/img")
        cv2.imwrite(usuario_img+".jpg",frame)       #Guardamos la ultima caputra del video como imagen y asignamos el nombre del usuario
        cap.release()                               #Cerramos
        cv2.destroyAllWindows()

        os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial")
        usuario_entrada.delete(0, END)
        usuarioNombre.delete(0, END)   #Limpiamos los text variables
        Label(pantalla1, text = "Registro Facial Exitoso", fg = "green", font = ("Calibri",11)).pack()

        #----------------- Detectamos el rostro y exportamos los pixeles --------------------------
        
        def reg_rostro(img, lista_resultados):
            os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial/img")
            data = pyplot.imread(img)
            for i in range(len(lista_resultados)):
                x1,y1,ancho, alto = lista_resultados[i]['box']
                x2,y2 = x1 + ancho, y1 + alto
                pyplot.subplot(1, len(lista_resultados), i+1)
                pyplot.axis('off')
                cara_reg = data[y1:y2, x1:x2]
                cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen con un tamaño de 150x200
                cv2.imwrite(usuario_img+".jpg",cara_reg)
                pyplot.imshow(data[y1:y2, x1:x2])
            pyplot.show()
            os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial")


        os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial/img")
        img = usuario_img+".jpg"
        pixeles = pyplot.imread(img)
        detector = MTCNN()
        caras = detector.detect_faces(pixeles)
        os.chdir("C:/Users/Temp Tech/Desktop/Carpetas/Sistema-de-Login-con-Reconocimiento-Facial")
        reg_rostro(img, caras)
        pantalla1.destroy()
    else:
        Label(pantalla1, text = "Debes ingresar ambos datos", fg = "red", font = ("Calibri", 11)).pack()   
    
#------------------------Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario #Globalizamos las variables para usarlas en otras funciones
    global usuarioNombre
    global usuario_nombre
    global usuario_entrada
    global pantalla1
    pantalla1 = Toplevel(pantalla) #Esta pantalla es de un nivel superior a la principal
    pantalla1.title("Registro personal")
    pantalla1.geometry("400x350")  #Asignamos el tamaño de la ventana
    
    #--------- Empezaremos a crear las entradas ----------------------------------------
    
    usuario = StringVar()
    usuario_nombre = StringVar()
    
    Label(pantalla1, text = "Registro facial: debe de asignar un usuario:").pack()
    Label(pantalla1, text = "").pack()  #Dejamos un poco de espacio
    Label(pantalla1, text = "Usuario * ").pack()  #Mostramos en la pantalla 1 el usuario
    usuario_entrada = Entry(pantalla1, textvariable = usuario) #Creamos un text variable para que el usuario ingrese la info
    usuario_entrada.pack()

    Label(pantalla1, text = "Nombre Completo * ").pack()  #Mostramos en la pantalla 1 el usuario
    usuarioNombre = Entry(pantalla1, textvariable = usuario_nombre) #Creamos un text variable para que el usuario ingrese la info
    usuarioNombre.pack()

    #------------ Vamos a crear el boton para hacer el registro facial --------------------
    Label(pantalla1, text = "").pack()
    Button(pantalla1, text = "Detectar", width = 15, height = 1, command = registro_facial).pack()
    
#--------------------------Funcion para el Login Facial --------------------------------------------------------
def login_facial():
#------------------------------Vamos a capturar el rostro-----------------------------------------------------
    path = 'img'
    images = []
    clases = []
    lista = os.listdir(path)

    comp1 = 100

    for lis in lista:
        #Se leen las imagenes
        imgdb = cv2.imread(f'{path}/{lis}')
        #Almacenamos las imagenes
        images.append(imgdb)
        #Guardamos el nombre de las imagenes
        clases.append(os.path.splitext(lis)[0])


    def codRostros(imagenes):
        listacod = []

        for img in imagenes:
            #Se aplica la correcion de color
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #Codificacion de imagen
            cod = list(fr.face_encodings(img)[0])

            #Almacenamos en lista
            listacod.append(cod)
        
        return listacod

    #Se llama la funcion
    rostrosCod = codRostros(images)

    #Se selecciona el dispositivo de captura de video
    cap = cv2.VideoCapture(0)

    flag = True

    #Se inicia el ciclo para el reconocimiento facial
    while flag == True:
        #Leemos cada frame
        ret, frame = cap.read()
        cv2.imshow("Deteccion",frame)
        frame2 = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        if cv2.waitKey(1) == 27:            #Cuando oprimamos "Escape" termina el video
            break
        
        #Realizamos una conversion de color sobre el video
        rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

        #localizamos los rostros y los codificamos
        faces = fr.face_locations(rgb)
        facesCod = fr.face_encodings(rgb, faces)

        for faceCod in zip(facesCod):
            #Se realiza la lectura y comparacion de los rostros
            comparacion = fr.compare_faces(rostrosCod, faceCod[0], tolerance=0.5)

            #Se calcula que tan similes son la foto en la base de datos y el frame del video
            similitud = fr.face_distance(rostrosCod, faceCod[0])

            min = np.argmin(similitud)

            #Se ejecuta el codigo si se cumple la condicion de comparacion
            if comparacion[min]:
                identificacion = clases[min]
                #Se toman variables de tiempo para validaciones e inserciones en base de datos
                dia = datetime.today()
                hora = dia.strftime("%H:%M:%S")
                horaValidacion = int(dia.strftime("%H"))
                dia = dia.strftime("%d/%m/%Y")
                #Se instancia el query para la base de datos
                queryConsulta = f"select horaEntrada from horas where cedula='{identificacion}' and fecha='{dia}'"
                horaEntrada = readData(conexion, queryConsulta)
                queryConsulta = f"select nombre from empleado where cedula='{identificacion}'"
                nombreEmpleado = readData(conexion, queryConsulta)
                nombreEmpleado = list(nombreEmpleado[0])
                validacionHoraEntrada = list(horaEntrada)
                #Se valida que si haya hecho la consulta de manera correcta
                if len(validacionHoraEntrada) != 0:
                    horaEntrada = list(horaEntrada[0])
                    #Se valida que la hora de entrada no exista ya en la base de datos
                    if horaEntrada != '':
                        print("Bienvenido:",nombreEmpleado[0])
                        diferencia = int(horaEntrada[0].split(":")[0]) - horaValidacion
                        if diferencia <= -3 or diferencia >= 3:
                            queryConsulta = f"select horaSalida from horas where cedula='{identificacion}' and fecha='{dia}'"
                            horaSalida = readData(conexion, queryConsulta)
                            validacionHoraSalida = list(horaSalida)
                            if len(validacionHoraSalida) == 0:
                                query = f"update horas set horaSalida = '{hora}' where cedula = '{identificacion}'"
                                insertData(conexion, query)
                            else:
                                print("Ya tienes tu hora de salida")
                        else:
                            print("Espera un minimo de 3 horas para realizar salida")
                    else:
                        query = f"Insert into horas (cedula, horaEntrada, fecha) values ('{identificacion}', '{hora}', '{dia}')"
                        insertData(conexion, query)
                else:
                    query = f"Insert into horas (cedula, horaEntrada, fecha) values ('{identificacion}', '{hora}', '{dia}')"
                    insertData(conexion, query)
                flag = False
                cv2.destroyAllWindows()
            else:
                print("Compatibilidad con la foto del registro: ",int(similitud[min] * 100),"%")
            cv2.destroyAllWindows()      
            
# Comprobacion en consola

def salidaManualPantalla():
    global ccEmpleado #Globalizamos las variables para usarlas en otras funciones
    global Anotacion
    global pantallaSalida
    global ccempleado
    global anotacion
    pantallaSalida = Toplevel(pantallaAdmin) #Esta pantalla es de un nivel superior a la principal
    pantallaSalida.title("Salida manual de empleado")
    pantallaSalida.geometry("400x350")  #Asignamos el tamaño de la ventana
    
    #--------- Empezaremos a crear las entradas ----------------------------------------
    
    ccEmpleado = StringVar()
    Anotacion = StringVar()
    
    Label(pantallaSalida, text = "Ingresar cedula de usuario").pack()
    Label(pantallaSalida, text = "").pack()  #Dejamos un poco de espacio
    Label(pantallaSalida, text = "C.C Empleado* ").pack()  #Mostramos en la pantalla 1 el usuario
    ccempleado = Entry(pantallaSalida, textvariable = ccEmpleado) #Creamos un text variable para que el usuario ingrese la info
    ccempleado.pack()

    Label(pantallaSalida, text = "Anotacion * ").pack()  #Mostramos en la pantalla 1 el usuario
    anotacion = Entry(pantallaSalida, textvariable = Anotacion) #Creamos un text variable para que el usuario ingrese la info
    anotacion.pack()

    def salir():
        hora = datetime.today()
        dia = hora.strftime("%d/%m/%Y")
        hora = hora.strftime("%H:%M:%S")
        queryConsulta = f"select cedula from empleado where cedula='{ccEmpleado.get()}'"
        existeEmpleado = readData(conexion, queryConsulta)
        if(len(existeEmpleado) != 0):
            queryInsertar = f"update horas set horaSalida = '{hora}' where cedula = '{ccempleado.get()}' and fecha = '{dia}'"
            insertData(conexion, queryInsertar)
            queryInsertar = f"update horas set anotacion = '{anotacion.get()}' where cedula = '{ccempleado.get()}' and fecha = '{dia}'"
            insertData(conexion, queryInsertar)
            pantallaSalida.destroy()
            pantallaAdmin.destroy()
        else:
            print("No existe la cedula en la base de datos")

    Label(pantallaSalida, text="").pack()
    Button(pantallaSalida, text="Salida Manual", height="2", width="30", command= salir).pack()

def admin():
    global administrador #Globalizamos las variables para usarlas en otras funciones
    global contraseñaAdmin
    global pantallaAdmin
    pantallaAdmin = Toplevel(pantalla) #Esta pantalla es de un nivel superior a la principal
    pantallaAdmin.title("login administrador")
    pantallaAdmin.geometry("400x350")  #Asignamos el tamaño de la ventana
    
    #--------- Empezaremos a crear las entradas ----------------------------------------
    
    administrador = StringVar()
    contraseñaAdmin = StringVar()
    
    Label(pantallaAdmin, text = "Ingreso de usuario Administrador: ").pack()
    Label(pantallaAdmin, text = "").pack()  #Dejamos un poco de espacio
    Label(pantallaAdmin, text = "C.C Admin * ").pack()  #Mostramos en la pantalla 1 el usuario
    admini = Entry(pantallaAdmin, textvariable = administrador) #Creamos un text variable para que el usuario ingrese la info
    admini.pack()

    Label(pantallaAdmin, text = "Contraseña * ").pack()  #Mostramos en la pantalla 1 el usuario
    contraAdmin = Entry(pantallaAdmin, textvariable = contraseñaAdmin) #Creamos un text variable para que el usuario ingrese la info
    contraAdmin.pack()
    Label(pantallaAdmin, text = "").pack()
        
    def comprobacionAdmin():
        if administrador.get() == "administrador" and contraseñaAdmin.get() == "admin123.":
            salidaManualPantalla()
        else:
            print("Nope")

    Button(pantallaAdmin, text="Ingresar", height="2", width="30", command= comprobacionAdmin).pack()

    
        
    
def pantalla_principal():
    global pantalla          #Globalizamos la variable para usarla en otras funciones
    pantalla = Tk()
    pantalla.geometry("400x350")  #Asignamos el tamaño de la ventana 
    pantalla.title("Control Horario")       #Asignamos el titulo de la pantalla
    Label(text = "Reconocimiento facial", bg = "gray", width = "300", height = "2", font = ("Verdana", 13)).pack() #Asignamos caracteristicas de la ventana
    
#------------------------- Vamos a Crear los Botones ------------------------------------------------------
    
    Label(text = "").pack()  #Creamos el espacio entre el titulo y el primer boton
    Button(text = "ingreso/salida", height = "2", width = "30", command = login_facial).pack()
    Label(text = "").pack() #Creamos el espacio entre el segundo boton y el segundo boton
    Button(text = "Registro", height = "2", width = "30", command = registro).pack()
    Label(text = "").pack()
    Button(text = "Admin", height="2", width="30", command= admin).pack()
    

    pantalla.mainloop()

pantalla_principal()
