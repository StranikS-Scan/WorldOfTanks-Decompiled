# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/fun_presenters_factory.py
import logging
from fun_random_common.fun_constants import FunSubModeImpl
from fun_random.gui.battle_results.pbs_helpers import getEventID
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.battle_results.presenter import FunRandomBattleResultsPresenter
from fun_random.gui.shared.fun_system_factory import registerFunBattleResultsPresenter, collectFunBattleResultsPresenter
_logger = logging.getLogger(__name__)
registerFunBattleResultsPresenter(FunSubModeImpl.DEFAULT, FunRandomBattleResultsPresenter)

class FunRandomBattleResultsPresenterFactory(FunSubModesWatcher):

    def __new__(cls, reusable):
        subModeID = getEventID(reusable)
        subMode = cls.getSubMode(subModeID)
        if subMode is None:
            _logger.error('[FunRandomBattleResultsPresenterFactory] Missing a sub mode with id %s', subModeID)
            return
        else:
            subModeImpl = subMode.getSubModeImpl()
            presenterCls = collectFunBattleResultsPresenter(subModeImpl) or FunRandomBattleResultsPresenter
            return presenterCls(reusable)
