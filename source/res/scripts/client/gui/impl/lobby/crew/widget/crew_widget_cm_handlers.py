# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/crew_widget_cm_handlers.py
from gui import SystemMessages
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.processors.tankman import TankmanUnload
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewMetricsLoggerWithParent
from uilogging.crew.logging_constants import CrewViewKeys, CrewTankmanContextMenuKeys, LAYOUT_ID_TO_ITEM
CM_RETRAIN_COLOR = 13347959

class CREW(object):
    PERSONAL_FILE = 'personalFile'
    RETRAIN = 'retrain'
    CHANGE_CREW_MEMBER = 'changeCrewMember'
    SEND_TO_BARRACKS = 'sendToToBarracks'
    DISMISS = 'dismiss'
    QUICK_TRAINING = 'quickTraining'
    CHANGE_SPECIALIZATION = 'changeSpecialization'


class CrewContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):
    __slots__ = ('_uiLogger', '_parentViewKey')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cmProxy, ctx=None):
        self._uiLogger = CrewMetricsLoggerWithParent()
        super(CrewContextMenuHandler, self).__init__(cmProxy, ctx, {CREW.PERSONAL_FILE: 'showPersonalFile',
         CREW.RETRAIN: 'retrain',
         CREW.QUICK_TRAINING: 'showQuickTraining',
         CREW.CHANGE_CREW_MEMBER: 'changeCrewMember',
         CREW.CHANGE_SPECIALIZATION: 'changeSpecialization',
         CREW.SEND_TO_BARRACKS: 'sendToToBarracks',
         CREW.DISMISS: 'dismiss'})

    def showPersonalFile(self):
        event_dispatcher.showPersonalCase(int(self._tankmanID), previousViewID=self._previousViewID)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.PERSONAL_FILE)

    def showQuickTraining(self):
        event_dispatcher.showQuickTraining(tankmanInvID=int(self._tankmanID), previousViewID=self._previousViewID, vehicleInvID=self._vehicle.invID if self._vehicle else NO_VEHICLE_ID)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.QUICK_TRAINING)

    def retrain(self):
        dialogs.showRetrainSingleDialog(self._tankmanID, self._vehicle.intCD, targetSlotIdx=self._slotIdx, parentViewKey=self._parentViewKey)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.RETRAIN)

    def changeCrewMember(self):
        event_dispatcher.showChangeCrewMember(self._slotIdx, self._vehicle.invID, self._previousViewID)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.CHANGE_MEMBER)

    @decorators.adisp_process('unloading')
    def sendToToBarracks(self):
        tankman = self.itemsCache.items.getTankman(self._tankmanID)
        result = yield TankmanUnload(self._vehicle.invID, tankman.vehicleSlotIdx).request()
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.SEND_TO_BARRACKS)
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def dismiss(self):
        dialogs.showDismissTankmanDialog(int(self._tankmanID), self._parentViewKey)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.DISMISS)

    def changeSpecialization(self):
        event_dispatcher.showTankChange(int(self._tankmanID), self._previousViewID)
        self._uiLogger.logClick(CrewTankmanContextMenuKeys.TANK_CHANGE)

    def _generateOptions(self, ctx=None):
        isNotLocked = not self._vehicle.isCrewLocked if self._vehicle else True
        isRetrainAvailable = False
        if self._vehicle:
            for _, tman in self._vehicle.crew:
                if tman and tman.invID == self._tankmanID:
                    isRetrainAvailable = not tman.isMaxCurrentVehicleSkillsEfficiency
                    break

        isNotInQuickTraining = self._previousViewID != R.views.lobby.crew.QuickTrainingView()
        return [self._makeItem(CREW.PERSONAL_FILE, MENU.contextmenu('crewWidgetPersonalFile')),
         self._makeItem(CREW.RETRAIN, MENU.contextmenu('crewWidgetRetrain'), {'visible': isRetrainAvailable,
          'textColor': CM_RETRAIN_COLOR}),
         self._makeItem(CREW.QUICK_TRAINING, MENU.contextmenu('crewWidgetQuickTraining')),
         self._makeItem(CREW.CHANGE_CREW_MEMBER, MENU.contextmenu('crewWidgetChangeCrewMember'), {'enabled': self._vehicle and isNotLocked}),
         self._makeItem(CREW.CHANGE_SPECIALIZATION, MENU.contextmenu('crewWidgetChangeSpecialization'), {'enabled': isNotLocked}),
         self._makeItem(CREW.SEND_TO_BARRACKS, MENU.contextmenu('crewWidgetSendToToBarracks'), {'visible': isNotInQuickTraining,
          'enabled': self._vehicle and isNotLocked}),
         self._makeItem(CREW.DISMISS, MENU.contextmenu('crewWidgetDismiss'), {'visible': isNotInQuickTraining,
          'enabled': isNotLocked})]

    def _initFlashValues(self, ctx):
        self._slotIdx = int(ctx.slotIdx)
        self._tankmanID = int(ctx.tankmanID)
        previousViewID = ctx.previousViewID
        self._previousViewID = int(previousViewID) if previousViewID else None
        self._parentViewKey = LAYOUT_ID_TO_ITEM.get(self._previousViewID, CrewViewKeys.HANGAR)
        self._uiLogger.setParentViewKey(self._parentViewKey)
        tankman = self.itemsCache.items.getTankman(self._tankmanID)
        if tankman or not tankman.isDismissed:
            self._vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID) if tankman.vehicleInvID > 0 else None
        return

    def _clearFlashValues(self):
        self._slotIdx = None
        self._tankmanID = None
        self._vehicle = None
        self._previousViewID = None
        self._parentViewKey = CrewViewKeys.HANGAR
        return
