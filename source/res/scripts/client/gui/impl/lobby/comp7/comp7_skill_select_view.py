# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_skill_select_view.py
import logging
from adisp import adisp_process
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from BWUtil import AsyncReturn
from gui import SystemMessages
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialog_template_button import ButtonPresenter
from gui.impl.dialogs.gf_builders import BaseDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.comp7.comp7_skill_select_view_model import Comp7SkillSelectViewModel
from gui.impl.gen.view_models.views.lobby.comp7.skill_model import SkillModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7.comp7_model_helpers import fillEquipmentStats
from gui.impl.lobby.comp7.tooltips.comp7_charge_tooltip import Comp7ChargeTooltip
from gui.impl.lobby.comp7.tooltips.comp7_skill_tooltip import Comp7SkillTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.gui_items.processors.comp7 import SetSkillProcessor
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from PlayerEvents import g_playerEvents
from items import vehicles
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
from th_async import th_async, th_await
_logger = logging.getLogger(__name__)
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent
_R_TEXT = R.strings.comp7.skillSelect.confirm
_R_ARTEFACTS = R.strings.artefacts
_R_ICON = R.images.gui.maps.icons.roleSkills.c_128x128
_SUBMIT_ID = 'submit'
_CANCEL_ID = 'cancel'

class Comp7SkillSelectView(ViewImpl):
    __slots__ = ('__periodicNotifier', '__equippedSkill', '__selectedSkill')
    __itemsCache = dependency.descriptor(IItemsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = Comp7SkillSelectViewModel()
        self.__equippedSkill = 0
        self.__selectedSkill = 0
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeasonEnd, self.__onDestroy)
        super(Comp7SkillSelectView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Comp7SkillSelectView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.comp7.tooltips.Comp7SkillTooltip():
            intCD = event.getArgument('intCD')
            return Comp7SkillTooltip(intCD)
        return Comp7ChargeTooltip() if contentID == R.views.lobby.comp7.tooltips.Comp7ChargeTooltip() else super(Comp7SkillSelectView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(Comp7SkillSelectView, self)._onLoading(*args, **kwargs)
        self.__setViewData()

    def _onLoaded(self, *args, **kwargs):
        super(Comp7SkillSelectView, self)._onLoaded(*args, **kwargs)
        self.__periodicNotifier.startNotification()

    def _finalize(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        super(Comp7SkillSelectView, self)._finalize()

    def _getEvents(self):
        return ((g_playerEvents.onEnqueued, self.__onDestroy),
         (self.viewModel.onClose, self.__onDestroy),
         (self.viewModel.onSelect, self.__onSelectSkill),
         (self.viewModel.onEquip, self.__onEquipSkill),
         (self.__comp7Controller.onComp7SkillsConfigChanged, self.__onConfigChanged))

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onDestroy, EVENT_BUS_SCOPE.LOBBY),)

    def __onConfigChanged(self):
        self.__setViewData()

    @replaceNoneKwargsModel
    def __setViewData(self, model=None):
        self.__selectedSkill = 0
        vehicle = g_currentVehicle.item
        fillVehicleModel(model.tankInfo, vehicle)
        currentEquipment = self.__comp7Controller.getVehicleSkillEquipment(vehicle)
        self.__equippedSkill = currentEquipment.id.itemID
        equipments = self.__comp7Controller.getVehicleEquipments(vehicle)
        skillsModel = model.skills
        skillsModel.clearItems()
        for equipmentID, config in equipments.iteritems():
            equipmentItem = config['item']
            equipmentModel = SkillModel()
            equipmentModel.setName(equipmentItem.name)
            equipmentModel.setIntCD(equipmentID)
            equipmentModel.setStartLevel(config['startLevel'])
            equipmentModel.setIsEquipped(equipmentID == self.__equippedSkill)
            fillEquipmentStats(equipmentModel.skillsStats, equipmentItem)
            skillsModel.addViewModel(equipmentModel)

        skillsModel.invalidate()

    def __onUpdated(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeasonEnd, self.__onDestroy)
        self.__periodicNotifier.startNotification()
        self.__setViewData()

    @th_async
    def _canQuit(self):
        if not self.__selectedSkill or self.__selectedSkill == self.__equippedSkill:
            raise AsyncReturn(True)
        equipment = vehicles.g_cache.equipments()[self.__selectedSkill]
        builder = BaseDialogBuilder()
        builder.setTitle(backport.text(_R_TEXT.title(), skillName=backport.text(_R_ARTEFACTS.dyn(equipment.name).dyn('name')())))
        builder.setIcon(_R_ICON.dyn(equipment.name)())
        builder.addButton(ButtonPresenter(_R_TEXT.submit(), _SUBMIT_ID, ButtonType.PRIMARY))
        builder.addButton(ButtonPresenter(_R_TEXT.cancel(), _CANCEL_ID, ButtonType.SECONDARY))
        builder.setFocusedButtonID(_SUBMIT_ID)
        result = yield th_await(dialogs.show(builder.build()))
        if result.result == _SUBMIT_ID:
            self.__equipSkill(self.__selectedSkill)
            raise AsyncReturn(False)
        elif result.result == _CANCEL_ID:
            raise AsyncReturn(True)
        raise AsyncReturn(False)

    @th_async
    def __onDestroy(self, *_):
        quitResult = yield th_await(self._canQuit())
        if quitResult:
            self.destroyWindow()

    def __onSelectSkill(self, event):
        self.__selectedSkill = int(event.get('intCD', 0))

    def __onEquipSkill(self, event):
        equipmentID = int(event.get('intCD', 0))
        self.__equipSkill(equipmentID)

    @adisp_process
    def __equipSkill(self, equipmentID):
        processor = SetSkillProcessor(equipmentID, g_currentVehicle.item)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.destroyWindow()

    def __getTimeTillCurrentSeasonEnd(self):
        return time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.__comp7Controller.getCurrentSeason().getEndDate()))


class Comp7SkillSelectWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(Comp7SkillSelectWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=Comp7SkillSelectView(R.views.lobby.comp7.Comp7SkillSelectView()), parent=parent)
