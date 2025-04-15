# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/gui_constants.py
from constants_utils import ConstInjector
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers import flag_constants

class QuestFlagTypes(flag_constants.QuestFlagTypes, ConstInjector):
    _const_type = str
    EPIC = 'epicQuests'


class ViewAlias(VIEW_ALIAS, ConstInjector):
    _const_type = str
