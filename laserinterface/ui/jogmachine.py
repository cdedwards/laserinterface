
# dependencies
from threading import Thread
import logging
import ruamel.yaml

# kivy imports
from kivy.app import App
from kivy.properties import NumericProperty

# Submodules
from laserinterface.data.grbl_doc import COMMANDS
from laserinterface.ui.themedwidgets import ShadedBoxLayout


_log = logging.getLogger().getChild(__name__)

yaml = ruamel.yaml.YAML()
config_file = 'laserinterface/data/config.yaml'
with open(config_file, 'r') as ymlfile:
    laser_pulse_duration = yaml.load(
        ymlfile, )['GENERAL']['LASER_PULSE_DURATION']


class Jogger(ShadedBoxLayout):
    stepsize_range = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200]
    feedrate_range = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]

    stepsize = NumericProperty(10)
    feedrate = NumericProperty(5000)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.terminal = app.terminal
        self.machine = app.machine
        self.grbl = app.grbl
        self.gpio = app.gpio

    def set_stepsize(self, val):
        val = int(val)
        self.stepsize = self.stepsize_range[val]

    def set_feedrate(self, val):
        val = int(val)
        self.feedrate = self.feedrate_range[val]

    def jog(self, command=''):
        command = command.upper()

        # add '$J='+ for interruptable jogging
        gcode = '$J='+'G91G21'
        if command == '-X+Y':
            gcode += f'X-{self.stepsize}Y{self.stepsize}'
        elif command == '+Y':
            gcode += f'Y{self.stepsize}'
        elif command == '+X+Y':
            gcode += f'X{self.stepsize}Y{self.stepsize}'
        elif command == '-X':
            gcode += f'X-{self.stepsize}'
        elif command == '+X':
            gcode += f'X{self.stepsize}'
        elif command == '-X-Y':
            gcode += f'X-{self.stepsize}Y-{self.stepsize}'
        elif command == '-Y':
            gcode += f'Y-{self.stepsize}'
        elif command == '+X-Y':
            gcode += f'X{self.stepsize}Y-{self.stepsize}'

        gcode += f'F{self.feedrate}'

        self.grbl.serial_send(gcode)
        return

    def stop_jog(self):
        self.grbl.serial_send(COMMANDS['cancel jog'])

    def go_to_zero(self):
        self.grbl.serial_send(f'$J=G90X0Y0F{self.feedrate}')

    def set_zero(self):
        self.grbl.serial_send('G92X0Y0')

    def rehome(self):
        self.grbl.serial_send(COMMANDS['start homing'])

    def unlock_alarm(self):
        self.grbl.serial_send(COMMANDS['kill alarm'])

    def reset_grbl(self):
        def _reset():
            self.grbl.serial_send(COMMANDS['soft reset'], blocking=True)
            self.terminal.clear_all()

        send_thread = Thread(target=_reset)
        send_thread.start()

    def pulse_laser(self):
        ''' turns laser on for the configured period'''
        self.grbl.serial_send(f'M03 S1000 F{self.feedrate}')
        self.grbl.serial_send('G1')
        self.grbl.serial_send(f'G4 P{laser_pulse_duration}')
        self.grbl.serial_send('G0 M5 S0')
