# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/commander_cmp.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.commander_cmp_view_model import CommanderCmpViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IRacingEventController

class CommanderComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return CommanderView()


class CommanderView(ViewImpl):
    _racingEventController = dependency.descriptor(IRacingEventController)

    def __init__(self, *args, **kwargs):
        super(CommanderView, self).__init__(R.views.lobby.race.commander_cmp.CommanderCmp(), ViewFlags.COMPONENT, CommanderCmpViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(CommanderView, self).getViewModel()

    def _initialize(self):
        super(CommanderView, self)._initialize()
        self._racingEventController.onRacingTeamChanged += self.__onRacingTeamChanged
        self.__updateModel()

    def _finalize(self):
        self._racingEventController.onRacingTeamChanged -= self.__onRacingTeamChanged
        super(CommanderView, self)._finalize()

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return
        else:
            pilotId = self._racingEventController.getRacingTeam()
            with self.getViewModel().transaction() as model:
                commanderInfo = R.strings.festival.race.hangar.commanderSlot.pilot.num(pilotId)
                model.setFirstName(backport.text(commanderInfo.firstName()))
                model.setLastName(backport.text(commanderInfo.secondName()))
                model.setDescription(backport.text(commanderInfo.description()))
                model.setIcon(R.images.gui.maps.icons.race.hangar.pilot.dyn('pilot_%d' % pilotId)())
            return

    def __onRacingTeamChanged(self, *_):
        self.__updateModel()
