# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/dialog_presets.py
from frameworks.wulf import ViewModel

class DialogPresets(ViewModel):
    __slots__ = ()
    QUIT_GAME = 'quitGame'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    BLUEPRINTS_CONVERSION = 'blueprintsConversion'
    MAPS_BLACKLIST = 'mapsBlacklist'
    TRANSPARENT_DEFAULT = 'transparentDefault'
    DEFAULT = 'default'

    def __init__(self, properties=0, commands=0):
        super(DialogPresets, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DialogPresets, self)._initialize()
