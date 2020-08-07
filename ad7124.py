########################################################################################################################
#                                             Imports Required                                                         #
########################################################################################################################
from ad7124_config import *
import time
import spidev
from enum import Enum


########################################################################################################################
#                                            Class Definitions                                                         #
########################################################################################################################
class References(Enum):
    REFIN1 = 0
    REFIN2 = 1
    INTERNAL = 2
    AVDD = 3

########################################################################################################################
#                                          Constant Variables                                                          #
########################################################################################################################

# AD7124 Constant Values #
AD7124_DUMMY_BYTE = 0x00
AD7124_RESET_BYTE = 0xFF

# Communication Register bits #
AD7124_COMM_REG_WEN = (0 << 7)
AD7124_COMM_REG_WR = (0 << 6)
AD7124_COMM_REG_RD = (1 << 6)

AD7124_CH_REG_START = 0x09

AD7124_CHANNELS = [
    'AD7124_CH0_MAP_REG',
    'AD7124_CH1_MAP_REG',
    'AD7124_CH2_MAP_REG',
    'AD7124_CH3_MAP_REG',
    'AD7124_CH4_MAP_REG',
    'AD7124_CH5_MAP_REG',
    'AD7124_CH6_MAP_REG',
    'AD7124_CH7_MAP_REG',
    'AD7124_CH8_MAP_REG',
    'AD7124_CH9_MAP_REG',
    'AD7124_CH10_MAP_REG',
    'AD7124_CH11_MAP_REG',
    'AD7124_CH12_MAP_REG',
    'AD7124_CH13_MAP_REG',
    'AD7124_CH14_MAP_REG',
    'AD7124_CH15_MAP_REG'
]

AD7124_CONFIGS = [
    'AD7124_CFG0_REG',
    'AD7124_CFG1_REG',
    'AD7124_CFG2_REG',
    'AD7124_CFG3_REG',
    'AD7124_CFG4_REG',
    'AD7124_CFG5_REG',
    'AD7124_CFG6_REG',
    'AD7124_CFG7_REG'
]

# Status Register bits #
AD7124_STATUS_REG_RDY = (1 << 7)
AD7124_STATUS_REG_ERROR_FLAG = (1 << 6)
AD7124_STATUS_REG_POR_FLAG = (1 << 4)

# ADC_Control Register bits #
AD7124_ADC_CTRL_REG_DOUT_RDY_DEL = (1 << 12)
AD7124_ADC_CTRL_REG_CONT_READ = (1 << 11)
AD7124_ADC_CTRL_REG_DATA_STATUS = (1 << 10)
AD7124_ADC_CTRL_REG_CS_EN = (1 << 9)
AD7124_ADC_CTRL_REG_REF_EN = (1 << 8)

# IO_Control_1 Register bits #
AD7124_IO_CTRL1_REG_GPIO_DAT2 = (1 << 23)
AD7124_IO_CTRL1_REG_GPIO_DAT1 = (1 << 22)
AD7124_IO_CTRL1_REG_GPIO_CTRL2 = (1 << 19)
AD7124_IO_CTRL1_REG_GPIO_CTRL1 = (1 << 18)
AD7124_IO_CTRL1_REG_PDSW = (1 << 15)

# IO_Control_1 AD7124-8 specific bits #
AD7124_8_IO_CTRL1_REG_GPIO_DAT4 = (1 << 23)
AD7124_8_IO_CTRL1_REG_GPIO_DAT3 = (1 << 22)
AD7124_8_IO_CTRL1_REG_GPIO_DAT2 = (1 << 21)
AD7124_8_IO_CTRL1_REG_GPIO_DAT1 = (1 << 20)
AD7124_8_IO_CTRL1_REG_GPIO_CTRL4 = (1 << 19)
AD7124_8_IO_CTRL1_REG_GPIO_CTRL3 = (1 << 18)
AD7124_8_IO_CTRL1_REG_GPIO_CTRL2 = (1 << 17)
AD7124_8_IO_CTRL1_REG_GPIO_CTRL1 = (1 << 16)

# IO_Control_2 Register bits #
AD7124_IO_CTRL2_REG_GPIO_VBIAS7 = (1 << 15)
AD7124_IO_CTRL2_REG_GPIO_VBIAS6 = (1 << 14)
AD7124_IO_CTRL2_REG_GPIO_VBIAS5 = (1 << 11)
AD7124_IO_CTRL2_REG_GPIO_VBIAS4 = (1 << 10)
AD7124_IO_CTRL2_REG_GPIO_VBIAS3 = (1 << 5)
AD7124_IO_CTRL2_REG_GPIO_VBIAS2 = (1 << 4)
AD7124_IO_CTRL2_REG_GPIO_VBIAS1 = (1 << 1)
AD7124_IO_CTRL2_REG_GPIO_VBIAS0 = (1 << 0)

# IO_Control_2 AD7124-8 specific bits #
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS15 = (1 << 15)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS14 = (1 << 14)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS13 = (1 << 13)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS12 = (1 << 12)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS11 = (1 << 11)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS10 = (1 << 10)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS9 = (1 << 9)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS8 = (1 << 8)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS7 = (1 << 7)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS6 = (1 << 6)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS5 = (1 << 5)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS4 = (1 << 4)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS3 = (1 << 3)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS2 = (1 << 2)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS1 = (1 << 1)
AD7124_8_IO_CTRL2_REG_GPIO_VBIAS0 = (1 << 0)

# Error Register bits #
AD7124_ERR_REG_LDO_CAP_ERR = (1 << 19)
AD7124_ERR_REG_ADC_CAL_ERR = (1 << 18)
AD7124_ERR_REG_ADC_CONV_ERR = (1 << 17)
AD7124_ERR_REG_ADC_SAT_ERR = (1 << 16)
AD7124_ERR_REG_AINP_OV_ERR = (1 << 15)
AD7124_ERR_REG_AINP_UV_ERR = (1 << 14)
AD7124_ERR_REG_AINM_OV_ERR = (1 << 13)
AD7124_ERR_REG_AINM_UV_ERR = (1 << 12)
AD7124_ERR_REG_REF_DET_ERR = (1 << 11)
AD7124_ERR_REG_DLDO_PSM_ERR = (1 << 9)
AD7124_ERR_REG_ALDO_PSM_ERR = (1 << 7)
AD7124_ERR_REG_SPI_IGNORE_ERR = (1 << 6)
AD7124_ERR_REG_SPI_SLCK_CNT_ERR = (1 << 5)
AD7124_ERR_REG_SPI_READ_ERR = (1 << 4)
AD7124_ERR_REG_SPI_WRITE_ERR = (1 << 3)
AD7124_ERR_REG_SPI_CRC_ERR = (1 << 2)
AD7124_ERR_REG_MM_CRC_ERR = (1 << 1)

# Error_En Register bits #
AD7124_ERREN_REG_MCLK_CNT_EN = (1 << 22)
AD7124_ERREN_REG_LDO_CAP_CHK_TEST_EN = (1 << 21)
AD7124_ERREN_REG_ADC_CAL_ERR_EN = (1 << 18)
AD7124_ERREN_REG_ADC_CONV_ERR_EN = (1 << 17)
AD7124_ERREN_REG_ADC_SAT_ERR_EN = (1 << 16)
AD7124_ERREN_REG_AINP_OV_ERR_EN = (1 << 15)
AD7124_ERREN_REG_AINP_UV_ERR_EN = (1 << 14)
AD7124_ERREN_REG_AINM_OV_ERR_EN = (1 << 13)
AD7124_ERREN_REG_AINM_UV_ERR_EN = (1 << 12)
AD7124_ERREN_REG_REF_DET_ERR_EN = (1 << 11)
AD7124_ERREN_REG_DLDO_PSM_TRIP_TEST_EN = (1 << 10)
AD7124_ERREN_REG_DLDO_PSM_ERR_ERR = (1 << 9)
AD7124_ERREN_REG_ALDO_PSM_TRIP_TEST_EN = (1 << 8)
AD7124_ERREN_REG_ALDO_PSM_ERR_EN = (1 << 7)
AD7124_ERREN_REG_SPI_IGNORE_ERR_EN = (1 << 6)
AD7124_ERREN_REG_SPI_SCLK_CNT_ERR_EN = (1 << 5)
AD7124_ERREN_REG_SPI_READ_ERR_EN = (1 << 4)
AD7124_ERREN_REG_SPI_WRITE_ERR_EN = (1 << 3)
AD7124_ERREN_REG_SPI_CRC_ERR_EN = (1 << 2)
AD7124_ERREN_REG_MM_CRC_ERR_EN = (1 << 1)

# Channel Registers 0-15 bits #
AD7124_CH_MAP_REG_CH_ENABLE = (1 << 15)
AD7124_CH_MAP_REG_CH_CONFIG = (7 << 12)

# Configuration Registers 0-7 bits #
AD7124_CFG_REG_BIPOLAR = (1 << 11)
AD7124_CFG_REG_REF_BUFP = (1 << 8)
AD7124_CFG_REG_REF_BUFM = (1 << 7)
AD7124_CFG_REG_AIN_BUFP = (1 << 6)
AD7124_CFG_REG_AINN_BUFM = (1 << 5)
AD7124_CFG_REG_REF_SEL = (3 << 3)
AD7124_CFG_REG_GAIN = (7 << 0)

# Filter Register 0-7 bits #
AD7124_FILT_REG_REJ60 = (1 << 20)
AD7124_FILT_REG_SINGLE_CYCLE = (1 << 16)

# Reference Voltages #
AD7124_CFG_REF_REFIN1 = 0x00
AD7124_CFG_REF_REFIN2 = 0x01
AD7124_CFG_REF_INTERNAL = 0x02
AD7124_CFG_REF_AVDD = 0x03

# Polarity #
AD7124_CFG_UNIPOLAR = 0x00
AD7124_CFG_BIPOLAR = 0x01

########################################################################################################################
#                                            Global Variables                                                          #
########################################################################################################################

# Set DEBUG to True to allow for verbose printing to the terminal
DEBUG = False

# Set the Variant to Unknown until it can be read from the AD7124
ad7124_variant = 'Unknown'

# Reference Voltage Values
reference_voltage = []
reference_voltage.insert(AD7124_CFG_REF_REFIN1, 2.5)
reference_voltage.insert(AD7124_CFG_REF_REFIN2, 2.5)
reference_voltage.insert(AD7124_CFG_REF_INTERNAL, 2.5)
reference_voltage.insert(AD7124_CFG_REF_AVDD, 3.3)

# Gain Values
gain_values = [1, 2, 4, 8, 16, 32, 64, 128]

# SPI Variables
spi = spidev.SpiDev()


########################################################################################################################
#                                                  SPI Support Functions                                               #
########################################################################################################################

# Function for initializing the SPI interface
def spi_init():
    global spi

    spi.open(1, 0)
    spi.max_speed_hz = 8000000
    spi.mode = 0b11


########################################################################################################################
#                                               AD7124 Support Functions                                               #
########################################################################################################################

# Function for reading the ID register of the AD7124
# If the ID register doesn't contain a value corresponding to the AD7124-4 or AD7124-8, or can't be read at all,
# hang execution and print an error to the terminal every 5 seconds
def read_id():
    global spi
    global ad7124_variant
    ret_val = spi.xfer2([(AD7124_COMM_REG_RD | ad7124_register_settings['AD7124_ID_REG']['address']), AD7124_DUMMY_BYTE])
    if (ret_val[1] == 0x04) or (ret_val[1] == 0x06):
        ad7124_variant = 'AD7124-4'
        if DEBUG:
            print('{} detected with ID {}'.format(ad7124_variant, ret_val[1]))
    elif (ret_val[1] == 0x14) or (ret_val[1] == 0x16):
        ad7124_variant = 'AD7124-8'
        if DEBUG:
            print('{} detected with ID {}'.format(ad7124_variant, ret_val[1]))
    else:
        if DEBUG:
            print('Unknown AD7124 variant detected with ID {}'.format(ret_val[1]))
        while True:
            print('Please check your physical connections and restart the script')
            time.sleep(5)


# Function for waiting for the device to power on
def wait_for_power_on():
    global spi
    powered_on = 0x00
    timeout = 10

    while (not powered_on) and timeout:
        timeout = timeout - 1
        ret_val = spi.xfer2([(AD7124_COMM_REG_RD | ad7124_register_settings['AD7124_STATUS_REG']['address']), AD7124_DUMMY_BYTE])
        powered_on = ret_val[1] & AD7124_STATUS_REG_POR_FLAG
        if DEBUG:
            print('Waiting for AD7124 to power on.')
        time.sleep(1)

    if timeout or powered_on:
        if DEBUG:
            print('AD7124 powered on and ready.')
    else:
        print('AD7124 error powering up, timeout limit reached.')


# Function to reset the AD7124 and return it to it's Power On Reset (POR) state.
def reset():
    global spi
    spi.xfer2([AD7124_RESET_BYTE, AD7124_RESET_BYTE, AD7124_RESET_BYTE, AD7124_RESET_BYTE, AD7124_RESET_BYTE,
               AD7124_RESET_BYTE, AD7124_RESET_BYTE, AD7124_RESET_BYTE])
    wait_for_power_on()


# Function to load the values in the AD7124_DEFAULT_REGISTER_SETTINGS array into the AD7124 device
def load_default_settings():
    global spi

    for register in ad7124_register_settings:
        if ad7124_register_settings[register]['r/w'] == 'rw':
            spi_data = [(ad7124_register_settings[register]['address'] | AD7124_COMM_REG_WR)]
            for byte in range(ad7124_register_settings[register]['size']):
                spi_data.insert(1, ((ad7124_register_settings[register]['default_value'] >> (8 * byte)) & 0xFF))
            spi.xfer2(spi_data)
            if DEBUG:
                print(spi_data)


# Function for reading the AD7124 status register
def read_status_register():
    global spi

    ret_val = spi.xfer2([ad7124_register_settings['AD7124_STATUS_REG']['address'] | AD7124_COMM_REG_RD,
                         AD7124_DUMMY_BYTE])

    return ret_val[1]


# Function for checking if the data register in the AD7124 is ready to be read. This is done by reading the 
# Ready bit in the status register 
def check_data_ready():
    global spi

    data_ready = (not (read_status_register() & AD7124_STATUS_REG_RDY))
    return data_ready


# Function for converting the raw ADC value or 'Code' to voltage
def convert_raw_value(raw, polarity, vref, gain):
    if polarity == AD7124_CFG_BIPOLAR:
        return convert_raw_value_bipolar(raw, vref, gain)
    else:
        return convert_raw_value_unipolar(raw, vref, gain)


# Function for converting the raw ADC value or 'Code' to voltage if the channel is configured for unipolar mode.
def convert_raw_value_unipolar(raw, vref, gain):
    return (raw * vref) / ((2 ** 24) * gain)


# Function for converting the raw ADC value or 'Code' to voltage if the channel is configured for bipolar mode.
def convert_raw_value_bipolar(raw, vref, gain):
    return ((raw / (2 ** 23)) - 1) / (gain / vref)


# Function for initializing the AD7124 for operation with the settings stored in AD7124_DEFAULT_REGISTER_SETTINGS
def init():
    global spi

    spi_init()
    reset()
    read_id()
    load_default_settings()
    if DEBUG:
        print('AD7124 setup complete.')


# Function for initializing the AD7124 for operation with the settings stored in AD7124_TEST_REGISTER_SETTINGS
def init_test():
    global spi

    spi_init()
    reset()
    read_id()
    load_test_settings()
    if DEBUG:
        print('AD7124 test setup complete.')


# Function for reading the AD7124 data register
def read_data_reg():
    global spi

    ret_val = spi.xfer2([(ad7124_register_settings['AD7124_DATA_REG']['address'] | AD7124_COMM_REG_RD),
                         AD7124_DUMMY_BYTE,
                         AD7124_DUMMY_BYTE,
                         AD7124_DUMMY_BYTE,
                         AD7124_DUMMY_BYTE])

    return ret_val