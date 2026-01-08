# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/progression_presenter_interface.py


class IProgressionCategoryPresenter(object):

    @classmethod
    def getPathToResource(cls):
        return NotImplementedError

    @classmethod
    def getViewAlias(cls):
        return NotImplementedError
