import I2C_LCD_driver
import time
import serial
import mysql.connector
from mysql.connector import (connection)
import socket
import RPi.GPIO as GPIO


LED_VERDE = 17
LED_ROJO = 18
BUZZER = 27


#Variables Globales
tag = [0, 0, 0, 0]
suma = 0
empleados = []
conStat = False
error = False
#Variables de conexion 
sqlUSer = 'usuario'
sqlPass = 'password'
sqlHost = 'localhost'
sqlDaBa = 'ResgitrosDeEmpleados'
sqlPort = 3306

#Configuraciones 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_ROJO, GPIO.OUT)
GPIO.setup(LED_VERDE, GPIO.OUT)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
mylcd = I2C_LCD_driver.lcd()

#Subrrutina principal 
def main():
    global conStat
    global error
    GPIO.output(LED_ROJO, True)
    init()
    time.sleep(0.25)
    GPIO.output(LED_ROJO, False)
    time.sleep(0.25)
    GPIO.output(LED_ROJO, True)
    time.sleep(0.25)
    GPIO.output(LED_ROJO, False)
    time.sleep(0.25)
    GPIO.output(LED_ROJO, True)
    time.sleep(0.25)
    GPIO.output(LED_ROJO, False)

    getEmployeds()
    mylcd.lcd_display_string("    Registrados     ", 1)
    mylcd.lcd_display_string("-  Identifiquece   -",2)
    mylcd.lcd_display_string("-    Por favor     -",3)
    mylcd.lcd_display_string("                    ",4)
    while(1):
        mylcd.lcd_display_string(str(time.strftime("%d/%m")),4,15)
        mylcd.lcd_display_string(str(time.strftime("%H:%M")),4,9)
        if error: 
            GPIO.output(LED_ROJO,True)
        else:
            GPIO.output(LED_ROJO,False)
        if conStat: 
            GPIO.output(LED_VERDE,True)
        else:
            GPIO.output(LED_VERDE,False)

        if (ser.inWaiting()):
            readed = ser.readline()
            nums = readed.split(",")
            tag[0] = int(nums[1])
            tag[1] = int(nums[2])
            tag[2] = int(nums[3])
            tag[3] = int(nums[4])
            compare()
        
#Subrrutina de inicializacion 
def init():
    global conStat
    global error
    #Obtiebe la direccion IP
    try:
        IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
            [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) 
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    except:
        IP = "IP Error !!         "
        print(IP)

    mylcd.lcd_display_string(str.format("{0}          ",IP),1)
    mylcd.lcd_display_string("Conectando a base de",2)
    mylcd.lcd_display_string("Datos               ",3)
    mylcd.lcd_display_string("                    ",4)
    #Testea la conexion con la base de datos 
    cnx = getCon()
    if cnx:
        mylcd.lcd_display_string("Conectado           ",4)
        conStat = True
    else:
        mylcd.lcd_display_string("Error al conectar   ",4)
        conStat = False
        print ("Se utilizara Host local")
        print ("Para reintentar conexion reinicie")

#Subrrutina que compara el tag leido con los tags de los empleados 
def compare():
    suma = tag[0] + tag[1]*256 + tag[2]*65536 + tag[3]*16777216
    mylcd.lcd_display_string("                    ",2)
    mylcd.lcd_display_string(str.format("id: {0}",suma),2)
    for empleado in empleados:
        if(suma == empleado[3]):
            mylcd.lcd_display_string("                    ",3)
            mylcd.lcd_display_string(str.format("{0} {1}",empleado[1],empleado[2]),3)
            loadData(int(empleado[0]))
    return 

#Subrrutina que carga el tag y la hora de ficheo
def loadData(empleado):
    global conStat
    global error
    hora = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    cnx = getCon()
    if(cnx):  
        conStat = True
        query = str.format ("INSERT INTO Fichaje (idEmpleado, fecha) VALUES ({0}, '{1}')",empleado,hora)
        print (query)
        crs = cnx.cursor()
        crs.execute(query)
        cnx.commit()
        cnx.close()
    else:
        conStat = False
    return None

#Subrrutina que obtiene la lista de empleados 
def getEmployeds():
    global conStat
    global error
    cnx = getCon()
    if(cnx):
        conStat = True
        query = str.format ("SELECT idEmpleado, nombre, apellido, tag FROM AlmacenDeRadios.Empleados")
        print (query)
        crs = cnx.cursor(buffered = True)
        crs.execute(query)
        cnx.commit()
        emp = crs.fetchall()
        for empl in emp:
            empleados.append(empl)
            print(str.format("{1}, {0} -- {2}",empl[1],empl[2],empl[3]))
        cnx.close()
    else:
        conStat = False
    return None

#Subrrutina que devuelve un objeto que es la conexion a la base de datos
def getCon():
    globals()
    try:
        cnx = connection.MySQLConnection(user=sqlUSer, 
                                    password=sqlPass,
                                    host=sqlHost,
                                    database=sqlDaBa,
                                    port=sqlPort)
        print("Conexion obtenida")
        return cnx
    except mysql.connector.Error as err:
        print("Error al conectarse con base de datos")
        print(err)
        return None

main()