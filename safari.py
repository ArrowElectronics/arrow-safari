########################################################################################################################
#                                            Imports Required                                                          #
########################################################################################################################
import ad7124
import time
import logging


########################################################################################################################
#                                            Support Functions                                                         #
########################################################################################################################

# Function for reading data from the AD7124 sensor
def ad7124_read_data():

    # Wait until the AD7124 indicates it is ready before reading data
    while not ad7124.check_data_ready():
        # wait for conversion to complete
        pass

    # Read from the AD7124 data register
    #
    # Byte 0 - Garbage
    # Bytes 1, 2, 3 - Raw ADC reading
    # Byte 4 - Status register Contents
    ret_val = ad7124.read_data_reg()

    # Shift the bytes into the proper position and OR them together to get the raw ADC value or 'Code'
    adc_raw_value = (ret_val[1] << 16) | (ret_val[2] << 8) | (ret_val[3] << 0)

    # Mask the status register byte to identify the channel the raw value corresponds to
    channel = ret_val[4] & 0x0F

    # Read the config number from the AD7124_DEFAULT_REGISTER_SETTINGS array
    config = (ad7124.ad7124_register_settings[ad7124.AD7124_CHANNELS[channel]]['default_value'] & ad7124.AD7124_CH_MAP_REG_CH_CONFIG) >> 12

    # Convert the config number into an array index to look up values from the AD7124_DEFAULT_REGISTER_SETTINGS array
    ad7124_config = ad7124.ad7124_register_settings[ad7124.AD7124_CONFIGS[config]]['default_value']

    # Read the voltage reference from the AD7124_DEFAULT_REGISTER_SETTINGS array
    ad7124_reference = (ad7124_config & ad7124.AD7124_CFG_REG_REF_SEL) >> 3

    # Look up the corresponding VREF voltage from the reference_voltage array
    vref = ad7124.reference_voltage[ad7124_reference]

    # Look up the polarity from the AD7124_DEFAULT_REGISTER_SETTINGS array
    polarity = (ad7124_config & ad7124.AD7124_CFG_REG_BIPOLAR) >> 11

    # Look up the gain from the AD7124_DEFAULT_REGISTER_SETTINGS array
    gain = ad7124.gain_values[(ad7124_config & ad7124.AD7124_CFG_REG_GAIN) >> 0]

    # Convert the raw ADC value (Code) to a voltage
    voltage = ad7124.convert_raw_value(adc_raw_value, polarity, vref, gain)

    # Send the data across the serial connection
    print('channel,{},voltage,{},code,{}'.format(channel, voltage, adc_raw_value))


########################################################################################################################
#                                                   Main Loop                                                          #
########################################################################################################################
if __name__ == '__main__':

    # Attempt to initialize the AD7124.
    #
    # If there is a problem communicating with the AD7124, this function will hang
    ad7124.init()
    print('Starting AD7124 Data Collection...')

    while True:
        # Continuously read data from the AD7124
        ad7124_read_data()