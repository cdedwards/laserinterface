
# dependencies
import ruamel.yaml

# kivy imports
from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

# submodules
from laserinterface.ui.themedwidgets import ShadedBoxLayout


yaml = ruamel.yaml.YAML()
config_file = 'laserinterface/data/config.yaml'
with open(config_file, 'r') as ymlfile:
    gpio_config = yaml.load(ymlfile)['GPIO']

# Colors in RGBA
STATE = {
    'GREEN':  [0.2, 0.5, 0.2, 1],
    'ORANGE': [0.75, 0.6, 0.2, 1],
    'RED':    [0.5, 0.2, 0.2, 1],
}


class GpioInputIcons(BoxLayout):
    temp_state = NumericProperty(99)
    cooling_state = BooleanProperty(False)
    front_cover_state = BooleanProperty(False)
    top_cover_state = BooleanProperty(False)
    estop_state = BooleanProperty(False)

    config = gpio_config

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.terminal = app.terminal
        self.machine = app.machine
        self.grbl = app.grbl
        self.gpio = app.gpio

        if self.machine:
            self.machine.add_gpio_callback(self.change_state)
            self.machine.add_temp_callback(self.change_temp)

    @mainthread
    def change_state(self, item, state):
        if item == 'IN_FRONT_COVER':
            self.front_cover_state = state
        elif item == 'IN_TOP_COVER':
            self.top_cover_state = state
        elif item == 'IN_COOLING':
            self.cooling_state = state
        elif item == 'IN_ESTOP':
            self.estop_state = state

    @mainthread
    def change_temp(self, temp):
        self.temp_state = temp


class GpioInputLabels(ShadedBoxLayout):
    temp_state = NumericProperty(99)
    cooling_state = BooleanProperty(False)
    front_cover_state = BooleanProperty(False)
    top_cover_state = BooleanProperty(False)
    estop_state = BooleanProperty(False)

    config = gpio_config

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.terminal = app.terminal
        self.machine = app.machine
        self.grbl = app.grbl
        self.gpio = app.gpio

        self.machine.add_gpio_callback(self.change_state)
        self.machine.add_temp_callback(self.change_temp)

    @mainthread
    def change_state(self, item, state):
        if item == 'IN_FRONT_COVER':
            self.front_cover_state = state
        elif item == 'IN_TOP_COVER':
            self.top_cover_state = state
        elif item == 'IN_COOLING':
            self.cooling_state = state
        elif item == 'IN_ESTOP':
            self.estop_state = state

    @mainthread
    def change_temp(self, temp):
        self.temp_state = temp


class GpioOutputController(ShadedBoxLayout):
    config = gpio_config

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.terminal = app.terminal
        self.machine = app.machine
        self.grbl = app.grbl
        self.gpio = app.gpio

        self.machine.add_gpio_callback(self.pin_changed)

    @mainthread
    def pin_changed(self, item, state):
        if item.startswith('OUT_'):
            button = self.ids.get(item[4:])
            if button:
                if state:
                    button.background_color = STATE['GREEN']
                else:
                    button.background_color = STATE['RED']


if __name__ == '__main__':
    from kivy.app import App  # noqa
    from kivy.lang import Builder  # noqa
    from os.path import join, dirname  # noqa
    from kivy import resources  # noqa

    data_dir = join(dirname(__file__), '..', 'data')
    resources.resource_add_path(data_dir)

    filename = join(dirname(__file__), 'kv', 'gpiodisplay.kv')
    kv_file = Builder.load_file(filename)

    class TestApp(App):
        def build(self):
            return GpioInputIcons()

    TestApp().run()
