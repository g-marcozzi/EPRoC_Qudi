import visa
import time
import numpy as np

from core.module import Base
from core.configoption import ConfigOption
from interface.test_magnet_interface import EprocMagnetInterface


class MagnetBrukerESP300(Base, EprocMagnetInterface):
    """

    Example config for copy-paste:

    magnet_bruker:
        module.Class: 'magnet.test_magnet_bruker_esp300.MagnetBrukerESP300'
        gpib_address: 'GPIB0::12::INSTR'
        gpib_timeout: 10
    """

    # visa address of the hardware : this can be over ethernet, the name is here for
    # backward compatibility
    _address = ConfigOption('gpib_address', missing='error')
    _timeout = ConfigOption('gpib_timeout', 10, missing='warn')

    def on_activate(self):
        """ Initialisation performed during activation of the module. """
        self._timeout = self._timeout * 1000
        self.rm = visa.ResourceManager()
        try:
            self._connection = self.rm.open_resource(self._address,
                                                     timeout=self._timeout)
        except:
            self.log.error('Could not connect to the address >>{}<<.'.format(self._address))
            raise

        self.log.info('Magnet initialised and connected.')
        return

    def on_deactivate(self):
        """ Cleanup performed during deactivation of the module. """
        self.rm.close()
        return

    def _command_wait(self, command_str):
        """
        Writes the command in command_str via ressource manager and waits until the device has finished
        processing it.
        @param command_str: The command to be written
        """
        self._connection.write(command_str)
        self._connection.write('*WAI')
        while int(float(self._connection.query('*OPC?'))) != 1:
            time.sleep(0.2)
        return

    def off(self):
        return 0

    def set_central_field(self, field=None):
        field = round(field, 2)
        self._connection.write('CF{}'.format(field))
        time.sleep(0.05)  # is this enough?
        # self._connection.write('LE')
        # led_status = self._connection.read()
        # while led_status == 1:
        #     time.sleep(0.01)
        #     led_status = self._connection.query('LE')
        return field

    def set_sweep(self, cf=None, width=None, wait_time=None):
        self._connection.write('CF{}'.format(cf))
        time.sleep(1)
        field = self._connection.write('FC')
        self._connection.write('SW{}'.format(width))
        self._connection.write('TM{}'.format(wait_time))
        time.sleep(1)
        field = self._connection.write('FC')
        return cf, width, wait_time
