# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/crew_tab_view.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from debug_utils import LOG_DEBUG_DEV
from frameworks.wulf import ViewSettings, ViewFlags, ViewEvent
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.crew_tab_helper import PreviewTankman, isValidCrewForVehicle, getCrewPreviewTitle, getCustomHeader, getPreviewCrewMemberArgs
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import OFFER_CHANGED_EVENT
from gui.Scaleform.daapi.view.meta.VehiclePreviewCrewTabInjectMeta import VehiclePreviewCrewTabInjectMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.vehicle_preview.tabs.crew_tab_model import CrewTabModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.tabs.tankman_preview_model import TankmanPreviewModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTmanSkillsModel
from gui.impl.lobby.crew.tooltips.empty_skill_tooltip import EmptySkillTooltip
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import crewMemberRealSkillLevel
from gui.shared.gui_items.Vehicle import sortCrew
from helpers import dependency
from shared_utils import first
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from web.web_client_api.common import ItemPackTypeGroup, ItemPackType, ItemPackEntry
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
DOG = 'dog'

class CrewTabView(ViewImpl):
    __slots__ = ('_toolTipMgr', '_title', '_crewItemPack', '_isCustomCrew', '_vehicle', '_crew')
    __appLoader = dependency.descriptor(IAppLoader)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.tabs.CrewTabView())
        settings.flags = ViewFlags.VIEW
        settings.model = CrewTabModel()
        self._toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        self._isCustomCrew = False
        self._crewItemPack = None
        self._crew = []
        self._vehicle = None
        self._title = None
        super(CrewTabView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CrewTabView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL:
                skillName = str(event.getArgument('skillName'))
                skillLevel = crewMemberRealSkillLevel(self._vehicle, skillName)
                args = [skillName,
                 None,
                 skillLevel,
                 None,
                 event.getArgument('customName')]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TooltipConstants.VEHICLE_PREVIEW_CREW_MEMBER:
                tankmanIdx = int(event.getArgument('index'))
                slotIdx, tankman = self._crew[tankmanIdx]
                args = getPreviewCrewMemberArgs(self._isCustomCrew, slotIdx, tankman)
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER, isSpecial=True, specialArgs=args)
        return super(CrewTabView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.EmptySkillTooltip():
            LOG_DEBUG_DEV('createToolTipContent EmptySkillTooltip')
            tankmanIndex = int(event.getArgument('tankmanID'))
            _, tankman = self._crew[tankmanIndex]
            skillIndex = int(event.getArgument('skillIndex'))
            return EmptySkillTooltip(tankman, skillIndex)
        return super(CrewTabView, self).createToolTipContent(event, contentID)

    def updateData(self, crewStr, vehicleItems, crewItemPack):
        if vehicleItems is None or crewItemPack is None:
            return
        else:
            gID = first((item.groupID for item in vehicleItems if item.id == g_currentPreviewVehicle.item.intCD))
            if gID is None:
                return
            sortedCrewItems = sorted([ item for item in crewItemPack if item.groupID == gID ], key=lambda i: ItemPackTypeGroup.CREW.index(i.type), reverse=True)
            self._title = crewStr
            self._crewItemPack = sortedCrewItems[0] if sortedCrewItems else None
            self._isCustomCrew = self._crewItemPack and self._crewItemPack.extra and self._crewItemPack.type == ItemPackType.CREW_CUSTOM
            self._vehicle = self._getVehicle()
            self._crew = self._vehicle.crew
            self._update()
            return

    def _fillViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillExtraInfo(vm)
            self._fillTankmen(vm)

    def _fillExtraInfo(self, vm):
        skillIcon = ''
        skillName = ''
        customName = ''
        isLockedCrew = False
        if self._isCustomCrew:
            title, skillIcon, skillName, customName = getCustomHeader(self._crew)
            isLockedCrew = self._crewItemPack.extra.get('isLockedCrew', False)
        else:
            title = getCrewPreviewTitle(self._title, self._crewItemPack)
        vm.setIsLockedCrew(isLockedCrew)
        vm.headerModel.setTitle(title)
        vm.headerModel.setSkillName(skillName)
        vm.headerModel.setIconName(skillIcon)
        vm.headerModel.setSkillCustomName(customName)

    def _fillTankmen(self, vm):
        tankmenVL = vm.getTankmen()
        tankmenVL.clear()
        for _, tankman in self._crew:
            tmanModel = TankmanPreviewModel()
            if self._isCustomCrew:
                tmanModel.setName(tankman.fullUserName)
                tmanModel.setIcon(tankman.extensionLessIcon)
                setTmanSkillsModel(tmanModel.skills, tankman)
            rolesVL = tmanModel.getRoles()
            rolesVL.clear()
            for s in tankman.roles():
                rolesVL.addString(s)

            rolesVL.invalidate()
            tankmenVL.addViewModel(tmanModel)

        currentVehicle = g_currentPreviewVehicle.item
        if DOG in currentVehicle.tags:
            vm.setHasDog(True)
            vm.setNation(currentVehicle.nationName)
        tankmenVL.invalidate()

    def _update(self):
        if g_currentPreviewVehicle.isPresent():
            self._fillViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewTabView, self)._onLoading(*args, **kwargs)
        self._update()

    def _subscribe(self):
        super(CrewTabView, self)._subscribe()
        g_currentPreviewVehicle.onComponentInstalled += self._update
        g_currentPreviewVehicle.onChanged += self._update

    def _unsubscribe(self):
        super(CrewTabView, self)._unsubscribe()
        g_currentPreviewVehicle.onChanged -= self._update
        g_currentPreviewVehicle.onComponentInstalled -= self._update

    def _finalize(self):
        self._toolTipMgr = None
        self._crewItemPack = None
        self._crew = None
        self._vehicle = None
        super(CrewTabView, self)._finalize()
        return

    def _getListeners(self):
        return ((OFFER_CHANGED_EVENT, self._onOfferChanged),)

    def _getVehicle(self):
        vehicle = self.__itemsCache.items.getVehicleCopy(g_currentPreviewVehicle.item)
        if not self._isCustomCrew:
            perfectCrew = vehicle.getPerfectCrew()
            vehicle.crew = [ (idx, PreviewTankman(idx, tankman=tankman)) for idx, tankman in perfectCrew ]
            return vehicle
        roles = vehicle.descriptor.type.crewRoles
        tankmenItems = self._crewItemPack.extra.get('tankmen', [])
        if not isValidCrewForVehicle(tankmenItems, roles):
            raise SoftException('Invalid crew preset for this vehicle')
        crew = [ (idx, PreviewTankman(idx, tmanData, vehicle=vehicle)) for idx, tmanData in enumerate(tankmenItems) ]
        vehicle.crew = sortCrew(crew, roles)
        return vehicle

    def _onOfferChanged(self, event):
        ctx = event.ctx
        self.updateData(self._title, ctx.get('vehicleItems'), ctx.get('crewItems'))


class CrewTabInject(VehiclePreviewCrewTabInjectMeta):

    def _makeInjectView(self):
        skillsPanel = CrewTabView()
        return skillsPanel

    def updateInjectData(self, text, vehicleItems, crewItemPack):
        self.getInjectView().updateData(text, vehicleItems, crewItemPack)
