# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/optional_device_alt_key_data.py
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData

class OptionalDeviceAltKeyData(DefaultAltKeyData):

    @staticmethod
    def _getHeader(item, mechanicName):
        return item.shortUserName
