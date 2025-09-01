# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/vehicle_mechanic_widget.py
import typing
from collections import namedtuple
from gui.Scaleform.daapi.view.meta.BaseVehicleMechanicsWidgetMeta import BaseVehicleMechanicsWidgetMeta
from gui.shared.utils.key_mapping import getScaleformKey
from gui.veh_mechanics.battle.updaters.hotkey_updaters import IHotKeysView, HotKeyCommand
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import IMechanicPassengerView
HotKeyData = namedtuple('HotKeyData', ['command', 'isLong'])

class VehicleMechanicWidget(BaseVehicleMechanicsWidgetMeta, IHotKeysView, IMechanicPassengerView):
    _HOT_KEY_MAP = dict()

    def setHotkeys(self, hotKeyCommands):
        viewData = []
        for hotKeyCommand in hotKeyCommands:
            if hotKeyCommand.command in self._HOT_KEY_MAP:
                viewData.extend([ {'keyCode': getScaleformKey(hotKeyCommand.key),
                 'command': data.command,
                 'isLong': data.isLong} for data in self._HOT_KEY_MAP[hotKeyCommand.command] ])

        self.as_setHotKeysS(viewData)

    def setVisible(self, visible):
        self.as_setVisibleS(visible)

    def setCrosshairType(self, crosshairType):
        self.as_setCrosshairTypeS(crosshairType)
