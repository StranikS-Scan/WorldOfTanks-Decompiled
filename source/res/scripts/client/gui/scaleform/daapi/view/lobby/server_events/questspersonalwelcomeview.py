# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsPersonalWelcomeView.py
import weakref
from helpers import i18n
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.server_events import settings as quest_settings
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.daapi.view.meta.QuestsPersonalWelcomeViewMeta import QuestsPersonalWelcomeViewMeta
from gui.Scaleform.locale.QUESTS import QUESTS

class QuestsPersonalWelcomeView(QuestsPersonalWelcomeViewMeta, AppRef):

    def __init__(self):
        super(QuestsPersonalWelcomeView, self).__init__()
        self.__proxy = None
        return

    def success(self):
        try:
            quest_settings.markPQIntroAsShown()
            self.__proxy._showSeasonsView()
        except:
            LOG_WARNING('Error while getting event window for showing seasons view')
            LOG_CURRENT_EXCEPTION()

    def _setMainView(self, eventsWindow):
        self.__proxy = weakref.proxy(eventsWindow)

    def _populate(self):
        super(QuestsPersonalWelcomeView, self)._populate()
        self.as_setDataS({'buttonLbl': QUESTS.QUESTSPERSONALWELCOMEVIEW_BTNLABEL,
         'titleText': self.app.utilsManager.textManager.getText(TextType.PROMO_TITLE, i18n.makeString(QUESTS.QUESTSPERSONALWELCOMEVIEW_MAINTITLE_TEXTLABEL)),
         'blockData': self.__makeBlocksData()})

    def _dispose(self):
        self.__proxy = None
        super(QuestsPersonalWelcomeView, self)._dispose()
        return

    def __makeBlocksData(self):
        result = []
        for blockName in ('block1', 'block2', 'block3'):
            result.append({'blockTitle': self.app.utilsManager.textManager.getText(TextType.PROMO_SUB_TITLE, i18n.makeString(QUESTS.questspersonalwelcomeview_textblock_header(blockName))),
             'blockBody': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(QUESTS.questspersonalwelcomeview_textblock_body(blockName)))})

        return result
