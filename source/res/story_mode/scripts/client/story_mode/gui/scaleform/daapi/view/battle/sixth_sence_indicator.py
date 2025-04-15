# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/sixth_sence_indicator.py
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class StoryModeSixthSenseIndicator(SixthSenseIndicator):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _show(self):
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        if vehicle is not None:
            self.enabled = 'SMDetectionDelayObservableComponent' not in vehicle.dynamicComponents
        super(StoryModeSixthSenseIndicator, self)._show()
        return
