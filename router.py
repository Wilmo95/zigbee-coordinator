from datetime import datetime
import linecache
import serial
import json

ser = serial.Serial('/dev/ttyAMA0', 19200)
messages = ['NEWNODE', 'BCAST', 'MCAST', 'UCAST']  # possible messages
devices = list()


# conversion python dictionary to json
def pyt_to_json(dic):
    y = json.dumps(dic)
    return y


# coo configuration
"""
def configuration_coo():
    ser.write("ATS0C=password\r\n")  # password
    ser.write("ATS0E=BEC4\r\n")     # prompt enable 1
    ser.write("ATS0F=00FF\r\n")     # prompt enable 2
    ser.write("ATS03=9D58547CB3BBAB19\r\n")  # preferred EPAN ID
    ser.write("ATS08=B47477641BBA47FE97F29AD47B8C6F88\r\n")  # trust key
    ser.write("ATS11=0000\r\n")  # device specify
    ser.write("ATS15=00200600\r\n")   # I/O configuration
    ser.write("ATS10=4B08\r\n")  # extended function
    ser.write("ATS0A=0000\r\n")   # main function
    ser.write("AT+EN\r\n")  # creat new PAN
"""


def message_received(buff):
    type_of_message = buff.split(':', 1)[0]

    if type_of_message == messages[0]:
        nwk, eui = get_info_newnode(buff)
        node_to_file(nwk, eui)
        devices.append(Device(nwk, eui))
        print("New device")

    elif type_of_message == messages[1]:
        eui, message = get_info_message(buff)
        message_to_file(eui, message)
        print("BCAST message")

    elif type_of_message == messages[2]:
        eui, message = get_info_message(buff)
        message_to_file(eui, message)
        print("MCAST message")

    elif type_of_message == messages[3]:
        eui, message = get_info_message(buff)
        message_to_file(eui, message)
        print("UCAST message")


def get_info_newnode(buff):
    new_buff = buff[8:]
    nwk = new_buff.split(',', 2)[0]
    eui = new_buff.split(',', 2)[1]
    return nwk, eui


def node_to_file(nwk, eui):
    f = open("devices.txt", "a")
    f.write(nwk + ":" + eui + "\r\n")
    f.close()


def get_info_message(buff):
    new_buff = buff[6:]
    eui = (new_buff.split(',', 2)[0])
    # m_length = (new_buff.split(',', 2)[1]) #not needed now
    message = new_buff.split('=', 1)[1]
    return eui, message


def message_to_file(eui, message):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_pyth = {
        "Message": message,
        "EUI": eui,
        "time": time

    }
    data_json = pyt_to_json(data_pyth)
    with open("messages.json", "a") as f:
        f.write(data_json)


def number_of_devices():
    num_lines = sum(1 for line in open('devices.txt'))
    return num_lines


def device_from_txt(n):
    f = "devices.txt"
    for i in range(n):
        line = linecache.getline(f, i + 1)
        nwk = line[:4]
        eui = line[5:]
        devices.append(Device(nwk, eui))


def get_address(i):
    d = devices[i]
    adr = d.eui
    return adr


class Device:
    def __init__(self, nwk, eui):
        self.nwk = nwk
        self.eui = eui


def show_devices():
    i = 0
    for d in devices:
        i = i+1
        print(i, d.nwk, d.eui)


with open("devices.txt", "a+") as a:
    a.write("")


def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Show the list of the devices")
    print("2. Change register in ZED")
    print("3. Menu Option 3")
    print("4. Menu Option 4")
    print("5. Exit")
    print(67 * "-")

# main


n = number_of_devices()
device_from_txt(n)

while True:
    try:
        if ser.inWaiting() > 0:
            data = ser.readline()
            message_received(data)

    except KeyboardInterrupt: #ctrl + c jako wejscie do menu
        loop = True
        while loop:
            print_menu()  # Displays menu
            choice = input("Enter your choice [1-5]: ")

            if choice == 1:
                print("Menu 1 has been selected")
                show_devices()
            # opcja wpisywania wartosci do rejestru - wciaz niegotowa
            elif choice == 2:
                print("Menu 2 has been selected")
                show_devices()
                which_device = input("Number of device")
                address = get_address(which_device)
                value = input("Set Value") # tu bedzie wpisywana wartosc rejestru
                command = "AT+BCAST:00," # tu bedze pobierana komenda w przyszlosci
                ser.write(command+str(value)+"\r\n")
                print(address)
            elif choice == 3:
                print("Menu 3 has been selected")
                # You can add your code or functions here
            elif choice == 4:
                print("Menu 4 has been selected")
                # You can add your code or functions here
            elif choice == 5:
                print("Exit the menu")
                # You can add your code or functions here
                loop = False  # This will make the while loop to end as not value of loop is set to False
            else:
                # Any integer inputs other than values 1-5 we print an error message
                print("Wrong option selection. Enter any key to try again..")