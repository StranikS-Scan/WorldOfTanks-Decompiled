# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tech_parameters_cmp.py
from frameworks.wulf import ViewFlags, ViewSettings
from CurrentVehicle import g_currentVehicle
from gui.doc_loaders.battle_royale_settings_loader import getVehicleProperties
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from gui.impl.gen.view_models.views.battle_royale.br_vehicle_specifications_model import BrVehicleSpecificationsModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class _Properties(object):
    GOOD = 'good'
    BAD = 'bad'


class TechParametersComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return TechParametersView(R.views.lobby.battleRoyale.tech_parameters_cmp.TechParametersCmp())


class TechParametersView(ViewImpl):

    def __init__(self, viewKey, viewModelClazz=TechParametersCmpViewModel):
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.COMPONENT
        settings.model = viewModelClazz()
        super(TechParametersView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TechParametersView, self).getViewModel()

    def _initialize(self):
        super(TechParametersView, self)._initialize()
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.__updateModel()

    def _finalize(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(TechParametersView, self)._finalize()

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if br_helpers.isIncorrectVehicle(vehicle):
            return
        nationName = vehicle.nationName
        props = getVehicleProperties(nationName)
        with self.viewModel.transaction() as model:
            model.setVehicleDescription(R.strings.battle_royale.vehicleDescription.dyn(nationName)())
            self.__createPropsGroup(props.strengths, model.vehicleGoodSpec.getItems(), _Properties.GOOD)
            self.__createPropsGroup(props.weaknesses, model.vehicleBadSpec.getItems(), _Properties.BAD)

    def __createPropsGroup(self, properties, groupModel, paramKey):
        groupModel.clear()
        for prop in properties:
            propModel = BrVehicleSpecificationsModel()
            propModel.setIconSource(R.images.gui.maps.icons.battleRoyale.hangar.vehicle_props.dyn('_'.join((paramKey, prop)))())
            propModel.setSpecName(R.strings.battle_royale.vehicleFeatures.spec.dyn(prop)())
            groupModel.addViewModel(propModel)

        groupModel.invalidate()
