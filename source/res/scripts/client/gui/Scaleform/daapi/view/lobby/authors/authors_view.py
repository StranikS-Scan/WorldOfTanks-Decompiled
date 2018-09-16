# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/authors/authors_view.py
import WWISE
from gui.Scaleform.daapi.view.meta.AuthorsViewMeta import AuthorsViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import getClientLanguage
_STATE_HANGAR_FILTERED = 'STATE_hangar_filtered'

class AuthorsView(AuthorsViewMeta):

    def _populate(self):
        super(AuthorsView, self)._populate()
        self.setBgPath()
        WWISE.WW_setState(_STATE_HANGAR_FILTERED, '{}_on'.format(_STATE_HANGAR_FILTERED))

    def onClose(self):
        self.destroy()
        WWISE.WW_setState(_STATE_HANGAR_FILTERED, '{}_off'.format(_STATE_HANGAR_FILTERED))

    def setBgPath(self):
        if getClientLanguage() in ('ru', 'be', 'uk', 'kk'):
            self.flashObject.as_setBgPath(RES_ICONS.MAPS_ICONS_AUTHORS_BG_RU)
        else:
            self.flashObject.as_setBgPath(RES_ICONS.MAPS_ICONS_AUTHORS_BG_EN)
