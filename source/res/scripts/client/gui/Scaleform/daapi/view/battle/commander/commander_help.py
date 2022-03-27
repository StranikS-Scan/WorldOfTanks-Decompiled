# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/commander_help.py
from collections import defaultdict, namedtuple
import typing
import BigWorld
import SoundGroups
import aih_constants
from AvatarInputHandler import aih_global_binding
from RTSShared import RTSManner
from gui.Scaleform.daapi.view.meta.CommanderHelpMeta import CommanderHelpMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_control import event_dispatcher
from gui.battle_control.controllers.commander.common import MappedKeys
from gui.battle_control.controllers.commander.interfaces import IProxyVehicle
from gui.impl import backport
from gui.shared.utils.key_mapping import getScaleformKey, getBigworldKey
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.sounds.r4_sound_constants import R4_SOUND
_CommanderHelpButtonData = namedtuple('CommanderHelpButtonData', ['index',
 'key',
 'behaviour',
 'commandIcon'])

class CommanderHelp(CommanderHelpMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DIRECT_ORDER = 0
    _MANNER_ORDER = 1
    _MODIFIER_RETREAT_ORDER = 2
    _MODIFIER_APPEND_ORDER = 3
    _MODIFIER_FORCE_ORDER = 4
    _ORDER_TO_RENDERER = {_DIRECT_ORDER: 'BaseCommanderHelpItemUI',
     _MANNER_ORDER: 'CommanderHelpItemUI',
     _MODIFIER_RETREAT_ORDER: 'NoBGCommanderHelpItemUI',
     _MODIFIER_APPEND_ORDER: 'NoBGCommanderHelpItemUI',
     _MODIFIER_FORCE_ORDER: 'NoBGCommanderHelpItemUI'}
    _MODIFIER_ORDER = (_MODIFIER_RETREAT_ORDER, _MODIFIER_APPEND_ORDER, _MODIFIER_FORCE_ORDER)
    _ORDERS_LIST = [_CommanderHelpButtonData(index=0, key=MappedKeys.KEY_CONTROL_VEHICLE, behaviour=_DIRECT_ORDER, commandIcon='controlVehicle'),
     _CommanderHelpButtonData(index=1, key=MappedKeys.KEY_HALT, behaviour=_DIRECT_ORDER, commandIcon='halt'),
     _CommanderHelpButtonData(index=2, key=MappedKeys.KEY_SMART_MANNER, behaviour=_MANNER_ORDER, commandIcon='smart'),
     _CommanderHelpButtonData(index=3, key=MappedKeys.KEY_HOLD_MANNER, behaviour=_MANNER_ORDER, commandIcon='hold'),
     _CommanderHelpButtonData(index=4, key=MappedKeys.KEY_SCOUT_MANNER, behaviour=_MANNER_ORDER, commandIcon='scout'),
     _CommanderHelpButtonData(index=5, key=MappedKeys.KEY_RETREAT, behaviour=_MODIFIER_RETREAT_ORDER, commandIcon='retreat'),
     _CommanderHelpButtonData(index=6, key=MappedKeys.KEY_FORCE_ORDER_MODE, behaviour=_MODIFIER_FORCE_ORDER, commandIcon='forceOrder')]

    def __init__(self):
        super(CommanderHelp, self).__init__()
        self.__isVisible = True
        self.__vehicleManners = defaultdict(lambda : RTSManner.DEFAULT)
        self.__selectedIDs = []

    def onOrderButtonClicked(self, scaleformKey):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is None or rtsCommander.vehicles is None:
            return
        else:
            selected = rtsCommander.vehicles.values(lambda v: v.isSelected)
            if not selected:
                return
            bwKey = getBigworldKey(scaleformKey)
            if bwKey in R4_SOUND.KEYS_TO_MANNER_UI_SOUND:
                SoundGroups.g_instance.playSound2D(R4_SOUND.R4_MANNER_UI_EVENT_NAME)
            if bwKey == MappedKeys.getKey(MappedKeys.KEY_HALT):
                rtsCommander.halt(self.__selectedIDs)
            elif bwKey == MappedKeys.getKey(MappedKeys.KEY_CONTROL_VEHICLE):
                ctrl = self.__sessionProvider.dynamic.vehicleChange
                if ctrl is not None:
                    ctrl.changeVehicle(first(self.__selectedIDs))
            else:
                manner = MappedKeys.getMannerByKeyCode(bwKey)
                if manner is not None:
                    rtsCommander.changeManner(self.__selectedIDs, manner)
            return

    def _populate(self):
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onControlModeChanged)
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.onRTSKeyEvent += self.__onRTSKeyEvent
            if rtsCommander.vehicles:
                rtsCommander.vehicles.onVehicleCreated += self.__onVehicleCreated
                rtsCommander.vehicles.onSelectionChanged += self.__onSelectionChanged
                rtsCommander.vehicles.onMannerChanged += self.__onMannerChanged
                rtsCommander.vehicles.onMannerBlockStateChanged += self.__onMannerBlockStateChanged
        self.__setupPanelItems()

    def _dispose(self):
        self.__vehicleManners.clear()
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onControlModeChanged)
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander:
            rtsCommander.onRTSKeyEvent -= self.__onRTSKeyEvent
            if rtsCommander.vehicles:
                rtsCommander.vehicles.onVehicleCreated -= self.__onVehicleCreated
                rtsCommander.vehicles.onSelectionChanged -= self.__onSelectionChanged
                rtsCommander.vehicles.onMannerChanged -= self.__onMannerChanged
                rtsCommander.vehicles.onMannerBlockStateChanged -= self.__onMannerBlockStateChanged

    @staticmethod
    def __makeVO(keyID=0, isModifier=False, keyText='', renderer='', icon=''):
        return {'keyID': getScaleformKey(keyID),
         'keyText': keyText,
         'isModifier': isModifier,
         'rendererLinkage': renderer,
         'tooltipStr': TOOLTIPS_CONSTANTS.RTS_ORDER_INFO,
         'orderIcon': icon}

    def __setupPanelItems(self):
        items = []
        for _, mappedKey, behType, icon in self._ORDERS_LIST:
            keyText = ''
            if MappedKeys.isModifierKey(mappedKey):
                keyText = backport.text(MappedKeys.getModifierKeyString(mappedKey))
            items.append(self.__makeVO(keyID=MappedKeys.getKey(mappedKey), isModifier=behType in self._MODIFIER_ORDER, keyText=keyText, renderer=self._ORDER_TO_RENDERER[behType], icon=icon))

        self.as_setOrderItemsS(items)

    def __onVehicleCreated(self, vehicle):
        self.__vehicleManners[vehicle.id] = vehicle.manner

    def __onMannerChanged(self, vID, manner):
        self.__vehicleManners[vID] = manner
        if not self.__isVisible:
            return
        self.__invalidateOrderStates()

    def __onSelectionChanged(self, selectedVehiclesIDs):
        self.__updatePanel()

    def __onControlModeChanged(self, mode):
        if mode in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES:
            self.__updatePanel()

    def __updatePanel(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is None or rtsCommander.vehicles is None:
            return
        else:
            selected = rtsCommander.vehicles.values(lambda v: v.isSelected)
            if bool(selected) != self.__isVisible:
                event_dispatcher.showCommanderHelp(bool(selected))
                self.__isVisible = bool(selected)
            selectedVehID = [ veh.id for veh in selected ]
            if selectedVehID != self.__selectedIDs:
                self.__selectedIDs = selectedVehID
                self.__invalidateOrderStates()
            return

    def __isActiveMannerOnVehicles(self, manner):
        selectedManner = False
        if self.__selectedIDs is not None:
            selectedManner = all((self.__vehicleManners[vehID] == manner for vehID in self.__selectedIDs))
        return selectedManner

    def __invalidateOrderStates(self):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if rtsCommander is None or rtsCommander.vehicles is None:
            return
        else:
            for idx, mappedKey, behType, _ in self._ORDERS_LIST:
                keyValue = MappedKeys.getKey(mappedKey)
                if MappedKeys.isModifierKey(mappedKey):
                    isDown = MappedKeys.isModifierDown(mappedKey)
                else:
                    isDown = BigWorld.isKeyDown(keyValue)
                isActive = isDown
                isDisabled = False
                if behType == self._MANNER_ORDER:
                    manner = MappedKeys.getMannerByKeyCode(keyValue)
                    isDisabled = rtsCommander.vehicles.isMannerBlocked(manner)
                    if manner is not None and not isDisabled:
                        isActive = self.__isActiveMannerOnVehicles(manner) and bool(self.__selectedIDs) or isDown
                elif behType in self._MODIFIER_ORDER:
                    mouseInfo = self.__sessionProvider.dynamic.rtsBWCtrl.getMouseInfo()
                    isDisabled = not mouseInfo.mouseRightEnabled if mouseInfo else True
                    if not isDisabled:
                        if behType == self._MODIFIER_APPEND_ORDER:
                            isDisabled = not rtsCommander.isAppendModeEnabled
                        elif behType == self._MODIFIER_RETREAT_ORDER:
                            isDisabled = not rtsCommander.vehicles.isRetreatEnabled
                            if not isDisabled:
                                isActive = rtsCommander.isRetreatModeActive
                                isDown = isActive
                        elif behType == self._MODIFIER_FORCE_ORDER:
                            isDisabled = not rtsCommander.isForceOrderModeEnabled
                            isActive = rtsCommander.isForceOrderModeActive
                            isDown = isActive
                elif mappedKey == MappedKeys.KEY_CONTROL_VEHICLE:
                    isDisabled = not self.__sessionProvider.dynamic.vehicleChange.isEnabled
                elif mappedKey == MappedKeys.KEY_HALT:
                    isDisabled = rtsCommander.vehicles.isMannerBlocked(RTSManner.DEFAULT)
                self.as_updateOrderStateS(idx, isActive, isDown, isDisabled)

            return

    def __onRTSKeyEvent(self, isDown, key):
        if not self.__isVisible:
            return
        self.__invalidateOrderStates()

    def __onMannerBlockStateChanged(self, manner, blocked):
        if manner not in RTSManner.ALL:
            return
        self.__invalidateOrderStates()
