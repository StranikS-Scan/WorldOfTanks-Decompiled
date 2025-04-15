# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quest_reroll_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_reroll_view_model import DailyQuestRerollViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.server_events.events_helpers import getRerollTimeout, getRerollTimeoutPrem
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.filters import StatesGroup, States
from helpers import dependency
from helpers import time_utils
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings

class DailyQuestRerollView(FullScreenDialogBaseView):
    __slots__ = ('_rerollPremium',)
    LAYOUT_ID = R.views.lobby.daily.DailyQuestRerollView()
    itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='daily_quests', entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)

    def __init__(self, rerollPremium, *args, **kwargs):
        self._rerollPremium = rerollPremium
        settings = ViewSettings(self.LAYOUT_ID)
        settings.args = args
        settings.kwargs = kwargs
        settings.model = DailyQuestRerollViewModel()
        super(DailyQuestRerollView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyQuestRerollView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestRerollView, self)._onLoading(*args, **kwargs)
        criteria = REQ_CRITERIA.IN_OWNERSHIP | REQ_CRITERIA.VEHICLE.IS_IN_BATTLE
        numTanksInBattle = len(self.itemsCache.items.getVehicles(criteria=criteria))
        _rerollTimeout = getRerollTimeoutPrem() if self._rerollPremium else getRerollTimeout()
        rerollTimeoutHours = int(_rerollTimeout / time_utils.ONE_MINUTE / time_utils.MINUTES_IN_HOUR)
        with self.viewModel.transaction() as model:
            model.setIsAlert(numTanksInBattle > 0)
            model.setIsPremium(self._rerollPremium)
            model.setRerollCooldown(rerollTimeoutHours)

    def _getEvents(self):
        return ((self.viewModel.onReroll, self.__onReroll), (self.viewModel.onClose, self.__onClose))

    def __onReroll(self):
        self._setResult(DialogButtons.SUBMIT)
        self.destroy()

    def __onClose(self):
        self._setResult(DialogButtons.CANCEL)
        self.destroy()

    def _getAdditionalData(self):
        return {}
