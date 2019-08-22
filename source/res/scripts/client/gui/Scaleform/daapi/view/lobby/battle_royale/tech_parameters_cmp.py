# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tech_parameters_cmp.py
from frameworks.wulf import ViewFlags
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from gui.impl.gen.view_models.views.battle_royale.br_vehicle_specifications_model import BrVehicleSpecificationsModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.common.battle_royale_helpers import isIncorrectVehicle
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class _Properties(object):
    GOOD = 'good'
    BAD = 'bad'


class _VehicleProperties(object):
    SPEED = 'speed'
    DPM = 'dpm'
    RADAR = 'radar'
    ARMOR = 'armor'
    HP = 'hp'
    DAMAGE = 'damage'
    PENETRATION = 'penetration'
    RESOLVER = 'revolver'


_VEHICLES_PROPERTIES_FOR_NATIONS = {'ussr': {_Properties.GOOD: (_VehicleProperties.SPEED, _VehicleProperties.PENETRATION),
          _Properties.BAD: (_VehicleProperties.RADAR, _VehicleProperties.DPM)},
 'usa': {_Properties.GOOD: (_VehicleProperties.RADAR, _VehicleProperties.DPM),
         _Properties.BAD: (_VehicleProperties.ARMOR, _VehicleProperties.DAMAGE)},
 'germany': {_Properties.GOOD: (_VehicleProperties.ARMOR, _VehicleProperties.DAMAGE),
             _Properties.BAD: (_VehicleProperties.SPEED, _VehicleProperties.PENETRATION)}}

class TechParametersComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return TechParametersView()


class TechParametersView(ViewImpl):

    def __init__(self, *args, **kwargs):
        super(TechParametersView, self).__init__(R.views.lobby.battleRoyale.tech_parameters_cmp.TechParametersCmp(), ViewFlags.COMPONENT, TechParametersCmpViewModel, *args, **kwargs)

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
        if isIncorrectVehicle(vehicle):
            return
        nationName = vehicle.nationName
        self.__createPropsGroup(nationName, _Properties.GOOD)
        self.__createPropsGroup(nationName, _Properties.BAD)

    def __createPropsGroup(self, nationName, propertyGroup):
        props = self.__getSpecItems(propertyGroup)
        if props is None:
            return
        else:
            props.clear()
            nationGoodProps = _VEHICLES_PROPERTIES_FOR_NATIONS[nationName][propertyGroup]
            for prop in nationGoodProps:
                propModel = BrVehicleSpecificationsModel()
                propModel.setIconSource(R.images.gui.maps.icons.battleRoyale.hangar.vehicle_props.dyn('_'.join((propertyGroup, prop)))())
                propModel.setSpecName(backport.text(R.strings.br_hangar.vehicleFeatures.spec.dyn(prop)()))
                props.addViewModel(propModel)

            props.invalidate()
            return

    def __getSpecItems(self, propertyGroup):
        if propertyGroup == _Properties.GOOD:
            return self.viewModel.vehicleGoodSpec.getItems()
        else:
            return self.viewModel.vehicleBadSpec.getItems() if propertyGroup == _Properties.BAD else None
