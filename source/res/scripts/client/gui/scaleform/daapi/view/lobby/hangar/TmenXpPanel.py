# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TmenXpPanel.py
from async import await, async
from debug_utils import LOG_DEBUG
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.pub.dialog_window import DialogFlags
from gui.Scaleform.daapi.view.meta.TmenXpPanelMeta import TmenXpPanelMeta
from gui.shared.gui_items.processors.vehicle import VehicleDetachmentXPAccelerator
from gui.shared.utils import decorators
from gui.shared.formatters import text_styles
from gui.impl.dialogs import dialogs
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import makeTooltip
from gui.hangar_cameras.hangar_camera_switch_mixin import HangarCameraSwitchMixin
from uilogging.detachment.loggers import g_detachmentFlowLogger, DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION

class TmenXpPanel(TmenXpPanelMeta, HangarCameraSwitchMixin):
    _DET_ACC_XP_CB_CHECKED_PREFIX = 'checked'
    _DET_ACC_XP_CB_UNCHECKED_PREFIX = 'unchecked'
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET_BUTTONS)

    def _populate(self):
        super(TmenXpPanel, self)._populate()
        g_currentVehicle.onChanged += self._onVehicleChange
        self._onVehicleChange()

    def _dispose(self):
        g_currentVehicle.onChanged -= self._onVehicleChange
        super(TmenXpPanel, self)._dispose()

    @async
    def accelerateTmenXp(self, selected):
        vehicle = g_currentVehicle.item
        if vehicle.hasOldCrew:
            self.as_setTankmenXpPanelS(vehicle.isElite, False, False, R.strings.crew_operations.accelerateXP.checkbox.labelDisable())
            return
        isOk = not selected
        if selected:
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.SPEED_UP_LEARNING)
            xpAccelerator, icon, message = self._buildProperties()
            builder = ResSimpleDialogBuilder()
            builder.setMessagesAndButtons(xpAccelerator)
            builder.setIcon(icon)
            builder.setFormattedMessage(message)
            builder.setFlags(DialogFlags.WINDOW)
            self.disableCamera()
            isOk = yield await(dialogs.showSimple(builder.build()))
        if isOk:
            self.uiLogger.log(ACTION.SPEED_UP_LEARNING_CHECKBOX_CHANGED)
            self._changeStatusXPAccelerator(selected, vehicle)
        else:
            self._backToPreviousState(vehicle)
        self.restoreCamera()

    @decorators.process('updateTankmen')
    def _changeStatusXPAccelerator(self, selected, vehicle):
        result = yield VehicleDetachmentXPAccelerator(vehicle, bool(selected)).request()
        if not result.success:
            self._backToPreviousState(vehicle)
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _onVehicleChange(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            self.as_setTankmenXpPanelS(False, False, False, '')
            LOG_DEBUG('Do not show xpAccelerator: No current vehicle')
            return
        else:
            self._setVisibilitySettings(vehicle)
            return

    def _backToPreviousState(self, vehicle):
        self._setVisibilitySettings(vehicle)

    def _setVisibilitySettings(self, vehicle):
        hasOldCrew = vehicle.hasOldCrew
        isSelected = vehicle.isXPToDet if not hasOldCrew else False
        vehicleState = vehicle.isInBattle or vehicle.isInPrebattle
        isEnabled = not hasOldCrew and vehicle.isElite and not vehicleState
        label = backport.text(R.strings.crew_operations.accelerateXP.checkbox.label() if isEnabled or not hasOldCrew else R.strings.crew_operations.accelerateXP.checkbox.labelDisable())
        self.as_setTankmenXpPanelS(True, isSelected, isEnabled, label)
        if hasOldCrew:
            body = backport.text(R.strings.tooltips.hangar.xpAccelerator.oldCrew.elite.body()) if vehicle.isElite else backport.text(R.strings.tooltips.hangar.xpAccelerator.oldCrew.noElite.body())
        elif vehicle.isElite:
            state = self._DET_ACC_XP_CB_CHECKED_PREFIX if isSelected else self._DET_ACC_XP_CB_UNCHECKED_PREFIX
            body = backport.text(R.strings.tooltips.hangar.xpAccelerator.detachment.elite.dyn(state).body())
        else:
            body = backport.text(R.strings.tooltips.hangar.xpAccelerator.detachment.noElite.body())
        header = backport.text(R.strings.tooltips.hangar.xpAccelerator.header())
        self.as_setAccelerateCheckboxTooltipS(makeTooltip(header, body))

    def _buildProperties(self):
        xpAccelerator = R.strings.detachment.xpAccelerator
        icon = R.images.gui.maps.icons.detachment.xpAccelerator.detachment_exp_speed_up()
        message = self._format(xpAccelerator.message(), xpAccelerator.condition())
        return (xpAccelerator, icon, message)

    def _format(self, message, condition):
        return text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(message)), text_styles.mainBig(backport.text(condition)))
