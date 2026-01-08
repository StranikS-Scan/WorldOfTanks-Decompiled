# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/vehicle_mechanic_widget.py
from __future__ import absolute_import
import typing
from collections import namedtuple
from itertools import chain
from gui.Scaleform.daapi.view.meta.BaseVehicleMechanicsWidgetMeta import BaseVehicleMechanicsWidgetMeta
from gui.shared.utils.key_mapping import getScaleformKey
from gui.veh_mechanics.battle.updaters.hotkey_updaters import IHotKeysView, HotKeyCommand
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import IMechanicPassengerView
HotKeyData = namedtuple('HotKeyData', ['command', 'isLong'])

class VehicleMechanicWidget(BaseVehicleMechanicsWidgetMeta, IHotKeysView, IMechanicPassengerView):
    _HOT_KEY_MAP = {}

    def setCrosshairType(self, crosshairType):
        self.as_setCrosshairTypeS(crosshairType)

    def setHotkeys(self, hotKeyCommands):
        self.as_setHotKeysS(tuple(chain.from_iterable([ [ {'keyCode': getScaleformKey(hotKeyCommand.key),
         'command': data.command,
         'isLong': data.isLong} for data in self._HOT_KEY_MAP.get(hotKeyCommand.command, ()) ] for hotKeyCommand in hotKeyCommands ])))

    def setVisibleForPassenger(self, visibleForPassenger):
        self.as_setVisibleS(visibleForPassenger)
