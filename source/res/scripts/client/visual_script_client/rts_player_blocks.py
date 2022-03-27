# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/rts_player_blocks.py
from WeakMethod import WeakMethodProxy
from visual_script.block import Block
from visual_script.dependency import dependencyImporter
from visual_script.misc import errorVScript
from visual_script.slot_types import SLOT_TYPE
from visual_script.tunable_event_block import TunableEventBlock
from visual_script_client.player_blocks import PlayerMeta, PlayerEventMeta
from RTSShared import RTSManner
from visual_script_client.vehicle_common import TriggerListener
vehicles, helpers, TriggersManager, gun_marker_ctrl, Avatar, event_dispatcher = dependencyImporter('items.vehicles', 'helpers', 'TriggersManager', 'AvatarInputHandler.gun_marker_ctrl', 'Avatar', 'gui.battle_control.event_dispatcher')

class RTSBootcampPlayerInputControl(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(RTSBootcampPlayerInputControl, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self.inputs = {}
        self.__keyRightMouse = 'Right Mouse'
        self.__keyDoubleClick = 'Right Mouse Doubleclick'
        self.__addInputSlot('WASD', WeakMethodProxy(self.__handleWASD))
        self.__addInputSlot('Hold', WeakMethodProxy(self.__handleHold))
        self.__addInputSlot('Scout', WeakMethodProxy(self.__handleScout))
        self.__addInputSlot('Halt', WeakMethodProxy(self.__handleHalt))
        self.__addInputSlot('Retreat', WeakMethodProxy(self.__handleRetreat))
        self.__addInputSlot('Queue Command', WeakMethodProxy(self.__handleQueueCommand))
        self.__addInputSlot('Change Vehicle', WeakMethodProxy(self.__handleChangeVehicle))
        self.__addInputSlot('Camera Adjustments', WeakMethodProxy(self.__handleCameraAdjustments))
        self.__addInputSlot('Middle Mouse Rotate', WeakMethodProxy(self.__handleMiddleMouseRotate))
        self.__addInputSlot(self.__keyRightMouse, WeakMethodProxy(self.__handleRightMouse))
        self.__addInputSlot(self.__keyDoubleClick, WeakMethodProxy(self.__handleRightMouseDoubleclick))
        self.__addInputSlot('Mouse Zoom', WeakMethodProxy(self.__handleMouseZoom))
        self.__addInputSlot('Force Order', WeakMethodProxy(self.__handleForceOrder))
        self.__addInputSlot('Minimap Interaction', WeakMethodProxy(self.__handleMinimapInteraction))
        for control, _ in self.inputs.itervalues():
            control.setDefaultValue(False)

    def __del__(self):
        self.inputs.clear()

    def validate(self):
        rightMouse, _ = self.inputs[self.__keyRightMouse]
        rightDouble, _ = self.inputs[self.__keyDoubleClick]
        return "Right Mouse Doubleclick won't work if Right Mouse is disabled!" if not self.__getCorrectValue(rightMouse) and self.__getCorrectValue(rightDouble) else super(RTSBootcampPlayerInputControl, self).validate()

    def _execute(self):
        if self._avatar:
            vehiclesMgr = self._avatar.guiSessionProvider.dynamic.rtsCommander.vehicles
            vehiclesMgr.resetBlockedManners()
        for control, fn in self.inputs.itervalues():
            fn(control)

        self._out.call()

    def __addInputSlot(self, name, process):
        self.inputs[name] = (self._makeDataInputSlot(name, SLOT_TYPE.BOOL), process)

    def __getCorrectValue(self, control):
        return control.getValue() if control.hasValue() else False

    def __handleWASD(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsCommander.enableHorizontalCameraMovement(self.__getCorrectValue(control))

    def __handleHold(self, control):
        if self._avatar and not self.__getCorrectValue(control):
            vehiclesMgr = self._avatar.guiSessionProvider.dynamic.rtsCommander.vehicles
            vehiclesMgr.blockManner(RTSManner.HOLD)

    def __handleScout(self, control):
        if self._avatar and not self.__getCorrectValue(control):
            vehiclesMgr = self._avatar.guiSessionProvider.dynamic.rtsCommander.vehicles
            vehiclesMgr.blockManner(RTSManner.SCOUT)

    def __handleRetreat(self, control):
        if not self._avatar:
            return
        vehiclesMgr = self._avatar.guiSessionProvider.dynamic.rtsCommander.vehicles
        vehiclesMgr.isRetreatEnabled = self.__getCorrectValue(control)

    def __handleForceOrder(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsCommander.isForceOrderModeEnabled = self.__getCorrectValue(control)

    def __handleQueueCommand(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsCommander.isAppendModeEnabled = self.__getCorrectValue(control)

    def __handleChangeVehicle(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.vehicleChange.setEnabled(self.__getCorrectValue(control))

    def __handleCameraAdjustments(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsCommander.enablePlayerCameraAdjustment(self.__getCorrectValue(control))

    def __handleMiddleMouseRotate(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsBWCtrl.setMouseWheelEnabled(self.__getCorrectValue(control))

    def __handleRightMouse(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsBWCtrl.setMouseRightEnabled(self.__getCorrectValue(control))

    def __handleRightMouseDoubleclick(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsBWCtrl.setMouseDoubleRightEnabled(self.__getCorrectValue(control))

    def __handleMouseZoom(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsBWCtrl.setMouseScrollEnabled(self.__getCorrectValue(control))

    def __handleHalt(self, control):
        if self._avatar and not self.__getCorrectValue(control):
            vehiclesMgr = self._avatar.guiSessionProvider.dynamic.rtsCommander.vehicles
            vehiclesMgr.blockManner(RTSManner.DEFENSIVE)

    def __handleMinimapInteraction(self, control):
        if not self._avatar:
            return
        self._avatar.guiSessionProvider.dynamic.rtsCommander.isMinimapInteractionEnabled = self.__getCorrectValue(control)


class RTSBootcampToggleMinimapVisibility(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(RTSBootcampToggleMinimapVisibility, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self.input = self._makeDataInputSlot('Visibility', SLOT_TYPE.BOOL)
        self.input.setDefaultValue(True)

    def _execute(self):
        isVisible = self.input.getValue() if self.input.hasValue() else True
        event_dispatcher.setMinimapVisibilityCmd(isVisible)
        self._out.call()


class OnPlayerTankmanMode(TunableEventBlock, PlayerEventMeta, TriggerListener):
    _EVENT_SLOT_NAMES = ['onEnter', 'onExit']

    def onStartScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.addListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onFinishScript(self):
        manager = TriggersManager.g_manager
        if manager:
            manager.delListener(self)
        else:
            errorVScript(self, 'TriggersManager.g_manager is None')

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.TANKMAN_MODE:
            self._index = 0
            self._callOnEnter()

    def onTriggerDeactivated(self, params):
        triggerType = params.get('type')
        if triggerType == TriggersManager.TRIGGER_TYPE.TANKMAN_MODE:
            self._index = 1
            self._callOnExit()

    @TunableEventBlock.eventProcessor
    def _callOnEnter(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callOnExit(self):
        pass


class RTSGetVoiceOverLanguageSwitch(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(RTSGetVoiceOverLanguageSwitch, self).__init__(*args, **kwargs)
        self._voiceOverLanguageSwitch = self._makeDataOutputSlot('languageSwitch', SLOT_TYPE.STR, self._getVoiceOverLanguageSwitch)

    def _getVoiceOverLanguageSwitch(self):
        from gui.sounds.r4_sound_constants import R4_SOUND
        switchName = R4_SOUND.getVoiceOverLanguageSwitch()
        self._voiceOverLanguageSwitch.setValue(switchName)


class RTSEnableVoicesForIngameSoundNotifications(Block, PlayerMeta):

    def __init__(self, *args, **kwargs):
        super(RTSEnableVoicesForIngameSoundNotifications, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self.enableVoices = self._makeDataInputSlot('enableVoices', SLOT_TYPE.BOOL)
        self.enableVoices.setDefaultValue(True)
        self.clearQueue = self._makeDataInputSlot('clearQueue', SLOT_TYPE.BOOL)
        self.clearQueue.setDefaultValue(False)

    def _execute(self):
        isEnabled = self.enableVoices.getValue() if self.enableVoices.hasValue() else True
        clearQueue = self.clearQueue.getValue() if self.clearQueue.hasValue() else False
        avatar = self._avatar
        if avatar and avatar.soundNotifications:
            avatar.soundNotifications.enableVoices(isEnabled, clearQueue)
        self._out.call()
