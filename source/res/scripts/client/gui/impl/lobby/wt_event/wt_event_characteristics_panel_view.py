# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_characteristics_panel_view.py
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.Scaleform.daapi.view.meta.WTEventParamsWidgetMeta import WTEventParamsWidgetMeta
from gui.impl.gen.view_models.views.lobby.wt_event.property_model import PropertyModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_characteristics_panel_view_model import WtEventCharacteristicsPanelViewModel
from gui.impl.lobby.wt_event.tooltips.wt_event_vehicle_params_tooltip_view import WtEventVehicleParamsTooltipView
from gui.impl.pub import ViewImpl, WindowImpl
from gui.wt_event.wt_event_helpers import getHunterDescr, getVehicleEquipmentsIDs
from items.vehicles import getItemByCompactDescr
from items.artefacts import InstantStunShootWT, ImpulseWT, AfterburningWT
_rSection = R.strings.wt_event.ttx
_BOSS_TTX_CONFIG = ['boss:pros:durability', 'boss:pros:dpm', 'boss:cons:mobility']
_HUNTER_TTX_CONFIG = ['hunter:pros:mobility', 'hunter:cons:dpm', 'hunter:cons:durability']

class WTEventCharacteristicsPanelWidget(WTEventParamsWidgetMeta, WTEventInjectWidget):
    __slots__ = ()

    def _makeInjectView(self):
        return WTEventCharacteristicsPanelView()


class WTEventCharacteristicsPanelView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCharacteristicsPanel(), flags=ViewFlags.COMPONENT, model=WtEventCharacteristicsPanelViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCharacteristicsPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventCharacteristicsPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        return WtEventVehicleParamsTooltipView(itemId=tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(WTEventCharacteristicsPanelView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()

    def __addListeners(self):
        g_currentVehicle.onChanged += self.__updateViewModel

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__updateViewModel

    def __updateViewModel(self):
        hunterCD = getHunterDescr()
        vehicleCD = g_currentVehicle.item.intCD if g_currentVehicle.item else None
        isHunter = hunterCD == vehicleCD
        with self.viewModel.transaction() as model:
            self.__fillList(model.pros, 'pros', isHunter)
            self.__fillList(model.cons, 'cons', isHunter)
            self.__fillSkillsList(model.skills)
            model.setSpecialInfo(backport.text(_rSection.special.hunter() if isHunter else _rSection.special.boss()))
        self.viewModel.setSkillDataInvalidator((self.viewModel.getSkillDataInvalidator() + 1) % 1000)
        self.viewModel.skills.invalidate()
        return

    @staticmethod
    def __fillList(model, key, isHunter):
        model.clearItems()
        config = _HUNTER_TTX_CONFIG if isHunter else _BOSS_TTX_CONFIG
        for ttx in config:
            vehicle, section, param = ttx.split(':')
            if section != key:
                continue
            item = PropertyModel()
            item.setId(ttx)
            icon = R.images.gui.maps.icons.wtevent.characteristicPanel.dyn('{}_{}'.format(param, key))
            if icon.exists():
                item.setIcon(icon())
            rText = _rSection.dyn(param).dyn('name').dyn(vehicle)
            if rText.exists():
                item.setText(backport.text(rText()))
            model.addViewModel(item)

    @staticmethod
    def __fillSkillsList(model):
        model.clearItems()
        rSkills = R.strings.wt_event.tooltips.skills
        skills = WTEventCharacteristicsPanelView.__getCurrentVehiclSkills()
        for skillItem in skills:
            item = PropertyModel()
            item.setId('_:skills:{}'.format(skillItem.compactDescr))
            item.setIcon(R.images.gui.maps.icons.artefact.dyn(skillItem.iconName)())
            rText = rSkills.dyn(skillItem.name).dyn('shortTitle')
            if rText.exists():
                item.setText(backport.text(rText()))
            model.addViewModel(item)

    @staticmethod
    def __getCurrentVehiclSkills():
        if g_currentVehicle.item is None:
            return []
        else:
            equipments = [ getItemByCompactDescr(intCD) for intCD in getVehicleEquipmentsIDs(g_currentVehicle.item.descriptor) ]
            return [ item for item in equipments if isinstance(item, (InstantStunShootWT, AfterburningWT, ImpulseWT)) ]


class WTEventCharacteristicsPanelWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventCharacteristicsPanelWindow, self).__init__(WindowFlags.WINDOW, content=WTEventCharacteristicsPanelView(), parent=parent)
