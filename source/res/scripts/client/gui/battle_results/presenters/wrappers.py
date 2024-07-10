# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/wrappers.py
import operator
from functools import wraps
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

def ifPresenterAvailable(defReturn=None):

    def decorator(method):

        @wraps(method)
        def wrapper(view, *args, **kwargs):
            presenter = dependency.instance(IBattleResultsService).getPresenter(view.arenaUniqueID)
            return method(view, *args, **kwargs) if presenter is not None else defReturn

        return wrapper

    return decorator


def hasPresenter(defReturn=None, abortAction=None):

    @dependency.replace_none_kwargs(battleResults=IBattleResultsService)
    def decorator(method, battleResults=None):

        @wraps(method)
        def wrapper(view, *args, **kwargs):
            presenter = battleResults.getPresenter(view.arenaUniqueID)
            if presenter is not None:
                return method(view, presenter=presenter, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(view) if abortAction is not None else defReturn

        return wrapper

    return decorator
