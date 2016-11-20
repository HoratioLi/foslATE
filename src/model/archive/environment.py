'''
Created on 12-06-2013

@author: Trung Huynh
'''


from ConfigParser import RawConfigParser


class Environment():
    def __init__(self, **kwargs):
        self.number_of_devices = kwargs.get('number_of_devices', 1)
        self.device_code_name = kwargs.get('number_of_devices', '')
        self.device_type = kwargs.get('number_of_devices', '')

        self.log_level = kwargs.get('log_level')
        self.log_folder = kwargs.get('log_folder')

        self.srfpc_path = kwargs.get('srfpc_path', '')
        self.eac_path = kwargs.get('eac_path', '')
        self.cc2541_firmware_path = kwargs.get('cc2541_firmware_path', '')
        self.efm32_firmware_path = kwargs.get('efm32_firmware_path', '')
        self.efm32_firmware_path_final = kwargs.get('efm32_firmware_path_final', '')
        self.eb_id_list = kwargs.get('eb_id_list', [])
        self.jlink_sn_list = kwargs.get('jlink_sn_list', [])

    def check(self):
        return len(self.eb_id_list) == self.number_of_devices and len(self.jlink_sn_list) == self.number_of_devices

    def generateTemplate(self):
        self.number_of_devices = 1
        self.device_code_name = 'Saturn'
        self.device_type = 'Shine'
        self.log_level = 'DEBUG'
        self.log_folder = 'C:\\Users\\Trung Huynh\\workspace\\misfit\\shine_production\\src\\log'
        self.srfpc_path = 'C:\\Program Files (x86)\\Texas Instruments\\SmartRF Tools\\Flash Programmer\\bin\\SmartRFProgConsole.exe'
        self.eac_path = 'C:\\Program Files (x86)\\energyAware Commander\\eACommander.exe'
        self.cc2541_firmware_path = 'C:\\Users\\Trung Huynh\\Downloads\\SBLplusController_v1.3.1_20130502.hex'
        self.efm32_firmware_path = 'C:\\Users\\Trung Huynh\\Downloads\\Saturn.bin'
        self.efm32_firmware_path_final = 'C:\\Users\\Trung Huynh\\Downloads\\Saturn.bin'
        self.eb_id_list = ['8571']
        self.jlink_sn_list = ['440006754']
        self.save()

    def load(self):
        config = RawConfigParser()
        config.read('settings.cfg')

        self.number_of_devices = config.getint('GENERAL', 'number_of_devices')
        self.device_code_name = config.get('GENERAL', 'device_code_name')
        self.device_type = config.get('GENERAL', 'device_type')

        self.log_level = config.get('LOGGING', 'log_level')
        self.log_folder = config.get('LOGGING', 'log_folder')

        self.srfpc_path = config.get('PATHS', 'srfpc_path')
        self.eac_path = config.get('PATHS', 'eac_path')
        self.cc2541_firmware_path = config.get('PATHS', 'cc2541_firmware_path')
        self.efm32_firmware_path = config.get('PATHS', 'efm32_firmware_path')
        self.efm32_firmware_path_final = config.get('PATHS', 'efm32_firmware_path_final')

        self.eb_id_list = config.get('EB IDs and J-LINK S/Ns', 'eb_ids').split(',')
        self.jlink_sn_list = config.get('EB IDs and J-LINK S/Ns', 'jlink_sn').split(',')

    def save(self):
        config = RawConfigParser()

        config.add_section('GENERAL')
        config.set('GENERAL', 'number_of_devices', self.number_of_devices)
        config.set('GENERAL', 'device_code_name', self.device_code_name)
        config.set('GENERAL', 'device_type', self.device_type)

        config.add_section('LOGGING')
        config.set('LOGGING', 'log_level', self.log_level)
        config.set('LOGGING', 'log_folder', self.log_folder)

        config.add_section('PATHS')
        config.set('PATHS', 'srfpc_path', self.srfpc_path)
        config.set('PATHS', 'eac_path', self.eac_path)
        config.set('PATHS', 'cc2541_firmware_path', self.cc2541_firmware_path)
        config.set('PATHS', 'efm32_firmware_path', self.efm32_firmware_path)
        config.set('PATHS', 'efm32_firmware_path_final', self.efm32_firmware_path_final)

        config.add_section('EB IDs and J-LINK S/Ns')
        config.set('EB IDs and J-LINK S/Ns', 'eb_ids', ','.join(self.eb_id_list))
        config.set('EB IDs and J-LINK S/Ns', 'jlink_sn', ','.join(self.jlink_sn_list))

        with open('settings.cfg', 'wb') as configfile:
            config.write(configfile)
