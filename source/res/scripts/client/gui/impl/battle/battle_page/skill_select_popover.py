# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/skill_select_popover.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_page.skill_select_popover_model import SkillSelectPopoverModel
from gui.impl.gen.view_models.views.lobby.comp7.skill_model import SkillModel
from gui.impl.pub import PopOverViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.tooltips.comp7_tooltips import getRoleEquipmentTooltipParts
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IPrebattleComp7SkillController
_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class SkillSelectPopover(PopOverViewImpl):
    __slots__ = ('__vehicle', '__panel')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicle, panel):
        settings = ViewSettings(R.views.battle.battle_page.SkillSelectPopover())
        settings.flags = ViewFlags.VIEW
        settings.model = SkillSelectPopoverModel()
        self.__vehicle = vehicle
        self.__panel = panel
        super(SkillSelectPopover, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SkillSelectPopover, self).getViewModel()

    def panelClear(self):
        self.__panel = None
        return

    def createToolTip(self, event):
        if event.contentID == _BACKPORT_TOOLTIP:
            intCD = event.getArgument('intCD')
            roleSkill = vehicles.g_cache.equipments()[intCD]
            header, body = getRoleEquipmentTooltipParts(roleSkill)
            tooltipData = createTooltipData(makeTooltip(header=header, body=body))
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        return super(SkillSelectPopover, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(SkillSelectPopover, self)._onLoading(*args, **kwargs)
        if self.__panel:
            self.__panel.setPopoverState(True)
        self.__setViewData()

    def _finalize(self):
        panel = self.__panel
        self.__panel = None
        self.__vehicle = None
        if panel:
            panel.setPopoverState(False)
        super(SkillSelectPopover, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onEquip, self.__onEquipSkill), (self.viewModel.onClose, self.__onClose), (self.__skillCtrl.onVehicleSkillUpdated, self.__onUpdatedSkill))

    def _getListeners(self):
        return ((events.GameEvent.FULL_STATS, self.__onClose, EVENT_BUS_SCOPE.BATTLE),)

    @property
    def __skillCtrl(self):
        return self.__sessionProvider.dynamic.comp7PrebattleSkillController

    @replaceNoneKwargsModel
    def __setViewData(self, model=None):
        equipments = self.__comp7Controller.getVehicleEquipments(self.__vehicle)
        skillsModel = model.skills
        skillsModel.clearItems()
        for equipmentID, config in equipments.iteritems():
            equipmentItem = config['item']
            equipmentModel = SkillModel()
            equipmentModel.setName(equipmentItem.name)
            equipmentModel.setIntCD(equipmentID)
            equipmentModel.setStartLevel(config['startLevel'])
            equipmentModel.setIsEquipped(equipmentID == self.__vehicle.selectedComp7Skill)
            skillsModel.addViewModel(equipmentModel)

        skillsModel.invalidate()

    def __onEquipSkill(self, event):
        intCD = int(event.get('intCD', 0))
        self.__skillCtrl.switchComp7Skill(intCD)

    @replaceNoneKwargsModel
    def __onUpdatedSkill(self, selectedComp7Skill, model=None):
        skillsModel = model.skills
        for skillModel in skillsModel.getItems():
            equipmentID = skillModel.getIntCD()
            skillModel.setIsEquipped(selectedComp7Skill == equipmentID)

        skillsModel.invalidate()

    def __onClose(self, *_):
        self.destroyWindow()
