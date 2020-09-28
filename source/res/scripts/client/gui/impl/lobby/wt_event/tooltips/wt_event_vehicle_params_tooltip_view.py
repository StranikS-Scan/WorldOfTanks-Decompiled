# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_vehicle_params_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_vehicle_params_tooltip_view_model import WtEventVehicleParamsTooltipViewModel
from gui.impl.pub import ViewImpl
from items.vehicles import getItemByCompactDescr

class WtEventVehicleParamsTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventVehicleParamsTooltipView())
        settings.model = WtEventVehicleParamsTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventVehicleParamsTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventVehicleParamsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            if kwargs.get('itemId') is not None:
                self.__fillCharacteristicData(model=model, *args, **kwargs)
            elif kwargs.get('isShell'):
                self.__fillShellData(model=model, *args, **kwargs)
            else:
                self.__fillSkillData(model=model, *args, **kwargs)
        return

    @staticmethod
    def __fillSkillData(model, intCD, *args, **kwargs):
        item = getItemByCompactDescr(intCD)
        rSection = R.strings.wt_event.tooltips.skills.dyn(item.name)
        rIcons = R.images.gui.maps.icons.artefact
        model.setIsSkill(True)
        model.setIcon(rIcons.dyn(item.iconName)())
        WtEventVehicleParamsTooltipView.__fillSkillTextFields(model, rSection)

    @staticmethod
    def __fillShellData(model, intCD, *args, **kwargs):
        item = getItemByCompactDescr(intCD)
        rSection = R.strings.wt_event.tooltips.shells.dyn(item.name.replace('-', '_'))
        iconID = R.images.gui.maps.icons.wtevent.hangar.dyn(item.iconName)()
        model.setIsSkill(True)
        model.setIcon(iconID)
        WtEventVehicleParamsTooltipView.__fillSkillTextFields(model, rSection)

    @staticmethod
    def __fillSkillTextFields(model, rSection):
        if rSection.length() == 4:
            model.setTitle(backport.text(rSection.shortTitle()))
            model.setText(backport.text(rSection.shortDescription()))
            model.setSkillTitle(backport.text(rSection.title()))
            model.setSkillDescription(backport.text(rSection.description()))

    @staticmethod
    def __fillCharacteristicData(model, itemId, *args, **kwargs):
        vehicle, section, param = itemId.split(':')
        if section == 'skills':
            return WtEventVehicleParamsTooltipView.__fillSkillData(model, int(param), *args, **kwargs)
        rSection = R.strings.wt_event.ttx
        iconID = R.images.gui.maps.icons.wtevent.characteristicPanel.dyn('{}_{}'.format(param, section))()
        model.setIsSkill(False)
        model.setIcon(iconID)
        rTitle = rSection.dyn(param).dyn('name').dyn(vehicle)
        if rTitle.exists():
            model.setTitle(backport.text(rTitle()))
        rText = rSection.dyn(param).dyn('text').dyn(vehicle)
        if rText.exists():
            model.setText(backport.text(rText()))
