# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/recruit_panel.py
from functools import partial
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.recruit_panel_base import RecruitPanelBase
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getVisibleCrewWidgetName
from gui.impl.auxiliary.vehicle_helper import getBestRecruitsForVehicle
from gui.impl.gen import R
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showConvertView
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.tankman import TankmanReturn, TankmanLoad
from gui.shared.gui_items.processors.tankman import TankmanUnload, TankmanEquip
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.detachment_constants import DetachmentConvertationPropertiesMasks
from skeletons.gui.game_control import IDetachmentController
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class RecruitPanel(RecruitPanelBase):
    detachmentController = dependency.descriptor(IDetachmentController)
    uiLogger = DetachmentLogger(GROUP.HANGAR_RECRUIT_PANEL)

    def _populate(self):
        super(RecruitPanel, self)._populate()
        self.detachmentController.onShowIntroVideoSwitched += self.__introVideoSwitchHandler
        self.lobbyContext.onServerSettingsChanged += self.__onLobbyServerSettingChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.as_setVisibleS(False)

    def _dispose(self):
        self.detachmentController.onShowIntroVideoSwitched -= self.__introVideoSwitchHandler
        self.lobbyContext.onServerSettingsChanged -= self.__onLobbyServerSettingChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(RecruitPanel, self)._dispose()

    def updateRecruitPanel(self):
        itemsCache = self.itemsCache
        vehicle = g_currentVehicle.item
        visible = getVisibleCrewWidgetName() == HANGAR_ALIASES.CREW
        self.as_setVisibleS(visible)
        if not visible:
            return
        criteria = REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.TANKMAN.IN_TANK | ~REQ_CRITERIA.TANKMAN.DISMISSED | REQ_CRITERIA.NATIONS([vehicle.nationID])
        allTankmen = itemsCache.items.getTankmen(criteria)
        isBarracksNotEmpty = any(itemsCache.items.removeUnsuitableTankmen(allTankmen.values(), ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE))
        validation, validationMask = self._validateCrewConvertion(vehicle, vehicle.crew, isBarracksNotEmpty)
        showLeaderWarning = bool(validationMask & DetachmentConvertationPropertiesMasks.PRESET)
        tankmenData = self._getRecruitsData(vehicle, vehicle.crew, showLeaderWarning, not isBarracksNotEmpty)
        roles = self._getRoleData(vehicle, vehicle.crew)
        self.__updateConvertButton(validation, validationMask)
        self.as_tankmenResponseS({'roles': roles,
         'tankmen': tankmenData,
         'autoRecruit': not isBarracksNotEmpty,
         'recruitFilters': self._getFilterData()})
        self._updateDogData(g_currentVehicle.item)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW_CONFIRMATION)
    def onConvertClick(self):
        showConvertView(g_currentVehicle.item)

    def equipTankman(self, tmanInvID, slot):
        vehicle = g_currentVehicle.item
        if not vehicle:
            return
        slot = int(slot)
        tankman = self.itemsCache.items.getTankman(int(tmanInvID))
        requiredRole = vehicle.descriptor.type.crewRoles[slot][0]
        if requiredRole != tankman.role:
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.RECRUIT_ROLE_CHANGE_DIALOG)
            self.openChangeRoleWindow(tmanInvID, requiredRole, vehicle, callback=partial(self.equipTankmanComplete, vehicle, tankman, slot))
            return
        self.equipTankmanComplete(vehicle, tankman, slot)

    @decorators.process('equipping')
    def equipTankmanComplete(self, vehicle, tankman, slot, result=None):
        if result and not result.success:
            return
        result = yield TankmanEquip(tankman, vehicle, slot).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def unloadAllTankman(self):
        self.onUnloadRecruits(None)
        return

    def onOpenChangeRole(self, event):
        vehicle = g_currentVehicle.item
        recruitID = event.ctx['recruitID']
        ctx = {'tankmanID': recruitID,
         'currentVehicleCD': vehicle.descriptor.type.compactDescr}
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.ROLE_CHANGE, VIEW_ALIAS.ROLE_CHANGE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    @decorators.process('unloading')
    def onUnloadRecruits(self, _):
        result = yield TankmanUnload(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('unloading')
    def onUnloadRecruit(self, event):
        recruitID = event.ctx['recruitID']
        tankman = self.itemsCache.items.getTankman(recruitID)
        result = yield TankmanUnload(g_currentVehicle.item, tankman.vehicleSlotIdx).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('crewReturning')
    def onSetBestCrew(self, event):
        vehicle = g_currentVehicle.item
        isNative = event.ctx['isNative']
        crew = getBestRecruitsForVehicle(vehicle, native=isNative)
        result = yield TankmanLoad(vehicle, crew, isNative).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('crewReturning')
    def onReturnCrew(self, _):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def onRetrainRecruits(self, _):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RETRAIN_CREW)), EVENT_BUS_SCOPE.LOBBY)

    def onConvertRecruits(self, event):
        showConvertView(g_currentVehicle.item)

    @uiLogger.dLog(ACTION.SHOW_VIDEO_INTRO)
    def onPlayVideoClick(self):
        self.detachmentController.showIntroVideo()

    def __updateConvertButton(self, validation, validationMask):
        errorInfo, convertPanelTooltip = self.__getConvertPanelState(validation, validationMask)
        data = {'showPlayButton': self.detachmentController.isIntroVideoOn,
         'info': errorInfo or backport.text(R.strings.detachment.crew.validation.available()),
         'convertEnabled': not bool(errorInfo),
         'tooltipData': {'tooltip': convertPanelTooltip},
         'playButtonTooltipData': {'tooltip': TOOLTIPS.DETACHMENT_CONVERTPANEL_PLAYBUTTON}}
        self.as_setConvertDataS(data)

    def __introVideoSwitchHandler(self):
        self.updateRecruitPanel()

    def __getConvertPanelState(self, validation, validationMask):
        info = ''
        tooltip = TOOLTIPS.DETACHMENT_CONVERTPANEL
        if g_currentVehicle.isInBattle():
            info = backport.text(R.strings.detachment.crew.validation.in_battle())
            tooltip = makeTooltip(text_styles.errorBig(backport.text(R.strings.tooltips.hangar.crew.convertValidation.inBattle.header())), backport.text(R.strings.tooltips.hangar.crew.convertValidation.inBattle.body()))
        elif g_currentVehicle.isInUnit():
            info = backport.text(R.strings.detachment.crew.validation.in_unit())
            tooltip = makeTooltip(text_styles.errorBig(backport.text(R.strings.tooltips.hangar.crew.convertValidation.inUnit.header())), backport.text(R.strings.tooltips.hangar.crew.convertValidation.inUnit.body()))
        elif validationMask & DetachmentConvertationPropertiesMasks.FULL_CREW:
            info = backport.text(R.strings.detachment.crew.validation.full_crew())
            tooltip = makeTooltip(text_styles.errorBig(backport.text(R.strings.tooltips.hangar.crew.convertValidation.full_crew.header())), backport.text(R.strings.tooltips.hangar.crew.convertValidation.full_crew.body()))
        elif validationMask & DetachmentConvertationPropertiesMasks.PRESET:
            info = backport.text(R.strings.detachment.crew.validation.preset())
            tooltip = makeTooltip(text_styles.errorBig(backport.text(R.strings.tooltips.hangar.crew.convertValidation.preset.header())), backport.text(R.strings.tooltips.hangar.crew.convertValidation.preset.body()))
        elif validationMask & DetachmentConvertationPropertiesMasks.SPECIALIZATION:
            info = backport.text(R.strings.detachment.crew.validation.specialization())
            tooltip = makeTooltip(text_styles.errorBig(backport.text(R.strings.tooltips.hangar.crew.convertValidation.specialization.header())), backport.text(R.strings.tooltips.hangar.crew.convertValidation.specialization.body()))
        elif not self.lobbyContext.getServerSettings().isDetachmentManualConversionEnabled():
            info = backport.text(R.strings.detachment.crew.validation.other())
            tooltip = TOOLTIPS.DETACHMENT_CONVERTPANEL_DISABLED
        elif not validation:
            info = backport.text(R.strings.detachment.crew.validation.other())
        return (info, tooltip)

    def __onLobbyServerSettingChanged(self, newSettings):
        newSettings.onServerSettingsChange += self.__onServerSettingsChange

    def __onServerSettingsChange(self, _):
        self.updateRecruitPanel()
