# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/ingame_help/fall_tanks_pages.py
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import HelpHintContext

class FallTanksHelpPagesFilter(object):
    _FILTER_CTX_KEY = HelpHintContext.MECHANICS

    @classmethod
    def filter(cls, builders):
        return [ b for b in builders if b.HINT_CONTEXT != cls._FILTER_CTX_KEY ]
