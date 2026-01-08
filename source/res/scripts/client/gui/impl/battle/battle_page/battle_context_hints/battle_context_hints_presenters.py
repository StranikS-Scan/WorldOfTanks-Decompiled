# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/battle_context_hints_presenters.py
import typing
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.impl.gen.view_models.views.battle.battle_context_hints.info_battle_context_hint_model import InfoBattleContextHintModel

class BattleContextHintsViewPresenter(object):

    def __init__(self, *args, **kwargs):
        pass

    def updateModel(self, viewModel):
        raise NotImplementedError


class InfoHintPresenter(BattleContextHintsViewPresenter):

    def __init__(self, duration, hintId, *args, **kwargs):
        super(InfoHintPresenter, self).__init__(duration, hintId, *args, **kwargs)
        self.__duration = duration
        self.__hintId = hintId

    def updateModel(self, viewModel):
        viewModel.setDuration(self.__duration)
        viewModel.setHintId(self.__hintId)


class InSafetyWhileNotObservedHintPresenter(BattleContextHintsViewPresenter):

    def updateModel(self, viewModel):
        pass


class FueltankCritHintPresenter(BattleContextHintsViewPresenter):

    def updateModel(self, viewModel):
        pass
