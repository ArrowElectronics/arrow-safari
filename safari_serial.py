# Import required packages
import threading
from threading import Thread
import time
import datetime
import re
import logging
import os
import serial as pyserial
import sys
import glob
import re
import json

from IPython.display import display, Markdown, clear_output, Image, HTML
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, Layout, Box, Button, Label, FloatText, Textarea, Dropdown, IntText

# Class for Serial connectivity
class Serial:
    def __init__(self, channels):
        self.BAUD = 115200  # Serial Baud Rate
        self.serial = None
        self.serial_buffer = ""
        self.data_collection_running = False
        self.channels = channels
        self.serial_connected = False
        self.data_collection_in_progress = False
        
        # Serial port selection dropdown widget
        self.serial_ports = self.__serial_port_scan()
        
        if len(self.serial_ports) == 0:
            self.serial_ports.append("No Serial Cable Connected")
              
        self.selected_serial_port = self.serial_ports[0]
        
        
        self.serial_port_list = widgets.Dropdown(
                                options=self.serial_ports,
                                value=self.selected_serial_port,
                                description='Serial Port:')
        self.serial_port_list.observe(self.on_serial_port_change)
        
        # Serial port connect/disconnect button widget
        self.serial_connection_button = widgets.Button(description = 'Connect')
        self.serial_connection_button.on_click(self.on_serial_connection_button_clicked)
        
        # Serial port scan button widget
        self.serial_scan_button = widgets.Button(description = 'Scan')
        self.serial_scan_button.on_click(self.on_serial_scan_button_clicked)
        
        # Data collection start/stop button widget
        self.data_collect_button = widgets.Button(description = 'Start Data Collection')
        self.data_collect_button.on_click(self.on_data_collect_button_clicked)
        self.data_collect_button.disabled = True
        
        # Display the Serial widgets
        display(widgets.HBox([self.serial_port_list, self.serial_connection_button, self.serial_scan_button]))
        display(widgets.HBox([self.data_collect_button]))

        # Setup threading to continually read data from the serial port
        self.thread = threading.Thread(target=self.read_serial)
        self.thread.daemon = True
            
    def on_serial_connection_button_clicked(self, arg):
        if self.serial_connected:
            self.disconnect_serial()
        else:
            self.connect_serial(self.selected_serial_port, self.BAUD)
            
    def on_serial_scan_button_clicked(self, arg):
        self.serial_ports = self.__serial_port_scan()
        
        if len(self.serial_ports) == 0:
            self.serial_ports.append("No Serial Cable Connected")
              
        self.serial_port_list.options = self.serial_ports
            
    def on_data_collect_button_clicked(self, arg):
        if not self.data_collection_in_progress:
            self.data_collection_start()
            self.data_collection_in_progress = True
            self.data_collect_button.description = "Stop Data Collection"
        else:
            self.data_collection_stop()
            self.data_collection_in_progress = False
            self.data_collect_button.description = "Start Data Collection"

    # Function for opening a serial connection on the specified port
    def connect_serial(self, port, baud):
        """ The function initiates the Connection to the UART device with the specified Port.

        :param port: Serial port to connect to.
        :param baud: Baud rate of the serial connection.
        :returns:
            0 if the serial connection is successfully opened.
            -1 if the connection fails to open.
        """
        try:
            self.serial = pyserial.Serial(port, baud, timeout=0, writeTimeout=0)  # ensure non-blocking
            self.serial_connected = True
            self.serial_port_list.disabled = True
            self.serial_connection_button.disabled = True
            self.serial_scan_button.disabled = True
            
            # Start a thread to handle receiving serial data
            if not self.thread.is_alive():
                self.thread.start()

            # Kill any running processes
            self.__serial_ctrl_c()
            time.sleep(0.25)
            self.__login()
            return 0
        except Exception as e:
            logging.exception(e)
            print("Cant Open Specified Port")
            return -1
        
    def disconnect_serial(self):
        """ This function is for disconnecting and quitting the application.
            Sometimes the application throws a couple of errors while it is being shut down, the fix isn't out yet

        :returns:
            0 if the serial connection is successfully closed.
            -1 if the connection fails to close.
        """

        try:
            self.serial_connected = False
            self.serial.close()
            self.serial_port_list.disabled = False
            self.serial_scan_button.disabled = False
            self.data_collect_button.disabled = True
            self.serial_connection_button.description = "Connect"
            return 0

        except Exception as e:
            logging.exception(e)
            return -1
        
    def write_serial(self, string):
        string = string + "\n"
        self.serial.write(string.encode('utf-8'))
        
    def write_file_to_meerkat(self, file):
        self.serial.write(str("rm /root/python/" + file + "\n").encode('utf-8'))
        f = open(file, "r")
        for line in f:
            #Remove excess newline character since we will insert one line at a time
            line = line.rstrip('\n')
            #print(str("echo '" + line + "' >> /root/python/" + file + "\n").encode('utf-8'))
            self.serial.write(str("echo \"" + line + "\" >> /root/python/" + file + "\n").encode('utf-8'))
        f.close()

    def read_serial(self):
        # Infinite loop is okay since this is running in it's own thread.
        while True:
            # Only try to read the serial port if connected
            if self.serial_connected:
                try:
                    c = self.serial.read().decode('unicode_escape')  # attempt to read a character from Serial

                    # was anything read?
                    if len(c) == 0:
                        pass

                    # check if character is a delimeter
                    if c == '\r':
                        c = ''  # don't want returns. chuck it

                    if c == '\n':
                        self.serial_buffer += "\n"  # add the newline to the buffer

                        # Parse the received serial data since we've received a full line
                        if "login" in self.serial_buffer:
                            # Only want to enable buttons if we can confirm there is a good connection to the board
                            self.__serial_connection_established()
                            self.__login()
                        elif "-sh: root: not found" in self.serial_buffer:
                            # Only want to enable buttons if we can confirm there is a good connection to the board
                            self.__serial_connection_established()
                        elif "AD7124 error" in self.serial_buffer:
                            self.__serial_ctrl_c()
                        elif "channel" in self.serial_buffer \
                                and "voltage" in self.serial_buffer \
                                and "code" in self.serial_buffer:
                                    self.update_plot_data(self.serial_buffer)

                        self.serial_buffer = ""  # empty the buffer
                    else:
                        self.serial_buffer += c  # add to the buffer

                except Exception as e:
                    # Occasionally the serial port will not read the complete string. We are ignoring these errors for now
                    #logging.exception(e)
                    pass
            
    def update_plot_data(self, data_string):
        """ Parse the data_string into key values and store the data into arrays

        :param data_string: String to parse into relevant data
        :return: Nothing
        """
        try:
            p = re.compile(r'[-+]?\d*\.\d+|\d+')
            if "timestamp" in data_string:
                channel, timestamp, voltage, code = p.findall(data_string)
            else:
                channel, voltage, code = p.findall(data_string)
                
            self.channels[channel]["voltages"].append(self.channels[channel]["voltage_format_func"](float(voltage)))
            self.channels[channel]["values"].append(self.channels[channel]["value_conversion_func"](float(voltage), float(code)))
            self.channels[channel]["timestamps"].append(datetime.datetime.utcnow().strftime('%S.%f')[:-3])

            # Limit lists to the max elements value
            self.channels[channel]["timestamps"] = self.channels[channel]["timestamps"][-self.channels[channel]["max_elements"]:]
            self.channels[channel]["voltages"] = self.channels[channel]["voltages"][-self.channels[channel]["max_elements"]:]
            self.channels[channel]["values"] = self.channels[channel]["values"][-self.channels[channel]["max_elements"]:]

        except Exception as e:
            # Occasionally the serial port will not read the complete string. We are ignoring these errors for now
            #logging.exception(e)
            pass
            
    def on_serial_port_change(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.selected_serial_port = change['new']            

    def __serial_port_scan(self):
        """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                self.serial = pyserial.Serial(port)
                self.serial.close()
                result.append(port)
            except (OSError, pyserial.SerialException):
                pass

        return result
    
    def __serial_connection_established(self):
        self.serial_connection_button.disabled = False
        self.serial_connection_button.description = "Disconnect"
        self.data_collect_button.description = "Start Data Collection"
        self.data_collect_button.disabled = False
    
    def __serial_ctrl_c(self):
        """ Send a ctrl+c command to the terminal

        :return: Nothing
        """
        if self.serial_connected:
            self.serial.write("\x03\n".encode('utf-8'))
            
    def __login(self):
        """ Login to the device

        :return: Nothing
        """
        if self.serial_connected:
            self.serial.write("root\n".encode('utf-8'))
            
    def data_collection_start(self):
        """ Start the data collection script on the device.

        :return: Nothing
        """        
        self.data_collection_running = True
        self.serial.write("echo 100 > /sys/class/gpio/export\n".encode('utf-8'))
        self.serial.write("echo out > /sys/class/gpio/gpio100/direction\n".encode('utf-8'))
        self.serial.write("echo 1 > /sys/class/gpio/gpio100/value\n".encode('utf-8'))
        self.serial.write("python /root/python/safari.py\n".encode('utf-8'))

    def data_collection_stop(self):
        """ Stop the data collection script, or any running script, on the device

        :return: Nothing
        """
        self.data_collection_running = False
        self.__serial_ctrl_c()
        self.serial.write("echo 100 > /sys/class/gpio/export\n".encode('utf-8'))
        self.serial.write("echo out > /sys/class/gpio/gpio100/direction\n".encode('utf-8'))
        self.serial.write("echo 0 > /sys/class/gpio/gpio100/value\n".encode('utf-8'))
        
    # Function for starting the motor
    def data_collection_start_stop(self):
        
        if not self.data_collection_running:
            if self.serial_connected:
                self.data_collection_start()
                self.data_collect_button="Stop"
            else:
                print("Serial Port Error", "Serial Port Not Open.")
        else:
            if self.serial_connected:
                self.data_collection_start()
                self.btn_start_motor.configure(text="Start")
            else:
                print("Serial Port Error", "Serial Port Not Open.")