# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# from Json_Class.index import read_setting
# from PPMP import PPMP_Service as Nexeed
# from PPMP import PPMP_Service as PS
# from TCPReaders import modbus_tcp as tcp
# from RTUReader import modbus_rtu as rtu
import time

from App.RTUReaders.modbus_rtu import modbus_rtu
from PPMP.PPMP_Services import start_ppmp_post
from TCPReaders.modbus_tcp import modbus_tcp


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Welcome To docker')

    # TCP function is called.
    modbus_rtu()
    # time.sleep(1)
    # PPMP Service function is called.
    #start_ppmp_post()
