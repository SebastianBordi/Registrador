import I2C_LCD_driver
import time
import serial
import mysql.connector



tag = [0, 0, 0, 0]
suma = 0
empleados = []

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string(" ALMACEN DE RADIOS  ", 1)
mylcd.lcd_display_string("-  Identifiquece   -",2)
mylcd.lcd_display_string("-    Por favor     -",3)


def comparar():
    suma = tag[0] + tag[1]*256 + tag[2]*65536 + tag[3]*16777216
    mylcd.lcd_display_string("                    ",2)
    buffer = str.format("id: {0}",suma)
    mylcd.lcd_display_string(buffer,2)
    for empleado in empleados:
        if(suma == empleado[3]):
            mylcd.lcd_display_string("                    ",3)
            mylcd.lcd_display_string(str.format("{0} {1}",empleado[1],empleado[2]),3)
            loadData(int(empleado[0]))

#    if(suma == juanma):
#        mylcd.lcd_display_string("-    Juan Manuel   -",3)
#        loadData(1)
#    elif(suma == matias):
#        mylcd.lcd_display_string("-      Matias      -",3)
#        loadData(2)
    return 

def loadData(empleado):
    hora = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        cnx = mysql.connector.connect(user='sebastian', password='7355608',
                                 host='192.168.1.80',
                                 database='AlmacenDeRadios')
        query = str.format ("INSERT INTO Fichaje (idEmpleado, fecha) VALUES ({0}, '{1}')",empleado,hora)
        print (query)
        crs = cnx.cursor()
        crs.execute(query)
        cnx.commit()
        cnx.close()
    except mysql.connector.Error as err:
        print(err)
    return

def getEmployeds():
    try:
        cnx = mysql.connector.connect(user='sebastian', password='7355608',
                                 host='192.168.1.80',
                                 database='AlmacenDeRadios')
        query = str.format ("SELECT idEmpleado, nombre, apellido, tag FROM AlmacenDeRadios.Empleados")
        print (query)
        crs = cnx.cursor(buffered = True)
        crs.execute(query)
        cnx.commit()
        emp = crs.fetchall()
        for empl in emp:
            empleados.append(empl)
            print(empl[1])
        cnx.close()
    except mysql.connector.Error as err:
        print("error")
        print(err)
        print("error")
    return

#class empleado:
#    def __init__ (self, nombre, apellido, idEmpleado, tag):
#        self.nombre = nombre
#        self.apellido = apellido
#        self.idEmpleado = idEmpleado
#        self.tag = tag
#    def __str__(self):
#        return(str(self.nombre))


getEmployeds()
while(1):
    mylcd.lcd_display_string(str(time.strftime("%d/%m/%Y")),4,0)
    mylcd.lcd_display_string(str(time.strftime("%H:%M:%S")),4,12)
    if (ser.inWaiting()):
        readed = ser.readline()
        nums = readed.split(",")
        tag[0] = int(nums[1])
        tag[1] = int(nums[2])
        tag[2] = int(nums[3])
        tag[3] = int(nums[4])
        comparar()



    
