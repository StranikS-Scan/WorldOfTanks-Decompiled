# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/squad/entity.py
import json
from CurrentVehicle import g_currentPreviewVehicle
from comp7_light.gui.comp7_light_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from comp7_light.gui.prb_control.entities.base.ctx import Comp7LightPrbAction
from comp7_light.gui.prb_control.entities.comp7_light_prb_helpers import Comp7LightViewPresenter
from comp7_light.gui.prb_control.entities.pre_queue.vehicles_watcher import Comp7LightVehiclesWatcher
from comp7_light.gui.prb_control.entities.scheduler import Comp7LightScheduler
from comp7_light.gui.prb_control.entities.squad.action_handler import Comp7LightSquadActionsHandler
from comp7_light.gui.prb_control.entities.squad.actions_validator import Comp7LightSquadActionsValidator
from comp7_light_constants import PREBATTLE_TYPE
from constants import QUEUE_TYPE
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.shared import IItemsCache

class Comp7LightSquadEntryPoint(SquadEntryPoint):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self, accountsToInvite=None):
        super(Comp7LightSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.COMP7_LIGHT, accountsToInvite)
        self.__squadSize = self.__comp7LightController.getModeSettings().squadSizes[1]

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.COMP7_LIGHT, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def configure(self, action):
        super(Comp7LightSquadEntryPoint, self).configure(action)
        if isinstance(action, Comp7LightPrbAction):
            self.__squadSize = action.getSquadSize()

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByPrbType(PREBATTLE_TYPE.COMP7_LIGHT, modeExtrasStr=json.dumps({'squadSize': self.__squadSize}))


class Comp7LightSquadEntity(SquadEntity):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(Comp7LightSquadEntity, self).__init__(FUNCTIONAL_FLAG.COMP7_LIGHT, PREBATTLE_TYPE.COMP7_LIGHT)
        self.__watcher = None
        self.__validIntCDs = set()
        self.__introPresenter = Comp7LightViewPresenter()
        self.__toggleAfterPreviewLeave = False
        self.storage = prequeue_storage_getter(QUEUE_TYPE.COMP7_LIGHT)()
        return

    def init(self, ctx=None):
        self.storage.release()
        result = super(Comp7LightSquadEntity, self).init(ctx)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_currentPreviewVehicle.onSelected += self.__onPreviewVehicleSelected
        self.__watcher = Comp7LightVehiclesWatcher()
        self.__watcher.start()
        self.__introPresenter.init()
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        g_currentPreviewVehicle.onSelected -= self.__onPreviewVehicleSelected
        self.__introPresenter.fini()
        self.__introPresenter = None
        return super(Comp7LightSquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(Comp7LightSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.COMP7_LIGHT

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__comp7LightController.isEnabled() else super(Comp7LightSquadEntity, self).getConfirmDialogMeta(ctx)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.COMP7_LIGHT_SQUAD, PREBATTLE_ACTION_NAME.COMP7_LIGHT)

    def _createActionsValidator(self):
        return Comp7LightSquadActionsValidator(self)

    def _createScheduler(self):
        return Comp7LightScheduler(self)

    def _createActionsHandler(self):
        return Comp7LightSquadActionsHandler(self)

    def _createRosterSettings(self):
        _, unit = self.getUnit(safe=True)
        return Comp7LightRosterSettings(unit)

    def _buildStats(self, unitMgrID, unit):
        self._rosterSettings.updateSettings(unit)
        return super(Comp7LightSquadEntity, self)._buildStats(unitMgrID, unit)

    def __onVehicleClientStateChanged(self, intCDs):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        allIntCDs = set((vehicle.intCD for vehicle in vehs))
        validIntCDs = allIntCDs - intCDs
        isReady = self.getPlayerInfo().isReady
        if isReady and self.__validIntCDs != validIntCDs:
            if not g_currentPreviewVehicle.isPresent():
                self.togglePlayerReadyAction(True)
            else:
                self.__toggleAfterPreviewLeave = True
        self.__validIntCDs = validIntCDs

    def __onPreviewVehicleSelected(self):
        if self.__toggleAfterPreviewLeave and not g_currentPreviewVehicle.isPresent():
            self.togglePlayerReadyAction(True)
            self.__toggleAfterPreviewLeave = False


class Comp7LightRosterSettings(DynamicRosterSettings):

    def updateSettings(self, unit):
        self._maxSlots = unit.getSquadSize()

    def _extractSettings(self, unit):
        settings = super(Comp7LightRosterSettings, self)._extractSettings(unit)
        settings['maxSlots'] = unit.getSquadSize()
        return settings
