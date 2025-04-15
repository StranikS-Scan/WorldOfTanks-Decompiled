# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tech_parameters_cmp.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.daapi.view.meta.BattleRoyaleTechParametersComponent import BattleRoyaleTechParametersComponent
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.doc_loaders.battle_royale_settings_loader import getVehicleProperties
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher

class TechParametersComponent(BattleRoyaleTechParametersComponent, InjectComponentAdaptor):

    def _makeInjectView(self):
        return TechParametersView(R.views.lobby.battle_royale.TechParametersVIew(), self.__updateHeight)

    def __updateHeight(self, value):
        self.as_updateHeightS(value)


class TechParametersView(ViewImpl):
    __slots__ = ('updateHeight',)

    def __init__(self, viewKey, updateHeight, viewModelClazz=TechParametersCmpViewModel):
        self.updateHeight = updateHeight
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.VIEW
        settings.model = viewModelClazz()
        super(TechParametersView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TechParametersView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TechParametersView, self)._onLoading(args, kwargs)
        self.__addListeners()
        self.__updateModel()

    def _finalize(self):
        self.__removeListeners()
        super(TechParametersView, self)._finalize()

    def __addListeners(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.viewModel.onClick += self.__onClick
        self.viewModel.onResized += self.__onResized

    def __removeListeners(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.viewModel.onClick -= self.__onClick
        self.viewModel.onResized -= self.__onResized

    def __onClick(self):
        event_dispatcher.showHangarVehicleConfigurator()

    def __onResized(self, value):
        self.updateHeight(value['height'])

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if br_helpers.isIncorrectVehicle(vehicle):
            return
        nationName = vehicle.nationName
        params = getVehicleProperties(nationName)
        with self.viewModel.transaction() as tx:
            tx.setSpotting(params.spotting)
            tx.setDifficulty(params.difficulty)
            tx.setSurvivability(params.survivability)
            tx.setMobility(params.mobility)
            tx.setDamage(params.damage)
