# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPrebattleHints.py
from gui.Scaleform.daapi.view.meta.BCPrebattleHintsMeta import BCPrebattleHintsMeta

class BCPrebattleHints(BCPrebattleHintsMeta):

    def __init__(self, settings):
        super(BCPrebattleHints, self).__init__()
        self.__visibleHints = settings.get('visible_hints', set())
        self.__invisibleHints = settings.get('invisible_hints', set())

    def _populate(self):
        super(BCPrebattleHints, self)._populate()
        self.as_setHintsVisibilityS(self.__visibleHints, self.__invisibleHints)

    def _dispose(self):
        super(BCPrebattleHints, self)._dispose()
        self.__visibleHints = None
        self.__invisibleHints = None
        return
