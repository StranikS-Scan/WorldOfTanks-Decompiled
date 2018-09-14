# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/StaticFormationProfileWindow.py
from gui import makeHtmlString
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.StaticFormationProfileWindowMeta import StaticFormationProfileWindowMeta
from adisp import process
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.shared.ClanCache import g_clanCache
from helpers import i18n

class StaticFormationProfileWindow(View, StaticFormationProfileWindowMeta, AppRef, AbstractWindowView):
    STATE_BAR = [{'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_SUMMARY,
      'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_UI},
     {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_STAFF,
      'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_UI},
     {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_LADDER,
      'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_UI},
     {'label': CYBERSPORT.STATICFORMATIONPROFILEWINDOW_TABSLBL_STATS,
      'view': CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_UI}]
    STATE_MAP = [(CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_SUMMARY_PY),
     (CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_STAFF_PY),
     (CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_STATS_PY),
     (CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_UI, CYBER_SPORT_ALIASES.STATIC_FORMATION_LADDER_PY)]

    def __init__(self, ctx = None):
        super(StaticFormationProfileWindow, self).__init__()

    def _populate(self):
        super(StaticFormationProfileWindow, self)._populate()
        self.__makeMainData()
        self.__updateActionButton()
        self.__updateFormationData()
        self.__setFormationEmblem()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(StaticFormationProfileWindow, self)._dispose()

    def __updateActionButton(self):
        labels = [CYBERSPORT.STATICFORMATIONPROFILEWINDOW_ACTIONBTN_OFFICER, CYBERSPORT.STATICFORMATIONPROFILEWINDOW_ACTIONBTN_SOLDIER, CYBERSPORT.STATICFORMATIONPROFILEWINDOW_ACTIONBTN_SENDREQUEST]
        actionBtnLbl = labels[0]
        isEnableActionBtn = True
        self.as_updateActionButtonS(actionBtnLbl, isEnableActionBtn)

    def __updateFormationData(self):
        link = makeHtmlString('html_templates:lobby/fortifications', 'link', {'text': i18n.makeString(CYBERSPORT.STATICFORMATIONPROFILEWINDOW_HYPERLINK_TEXT),
         'linkType': 'securityLink'})
        self.as_updateFormationInfoS({'isShowLink': True,
         'editLinkText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, link),
         'formationNameText': self.app.utilsManager.textManager.getText(TextType.PROMO_SUB_TITLE, 'formationNAME !!!')})

    def __makeMainData(self):
        self.as_setDataS({'stateMap': self.STATE_MAP,
         'stateBar': self.STATE_BAR})

    @process
    def __setFormationEmblem(self):
        enemyClanDBID = g_clanCache.clanDBID
        tID = 'clanInfo%d' % enemyClanDBID
        imageID = yield g_clanCache.getClanEmblemTextureID(enemyClanDBID, True, tID)
        self.as_setFormationEmblemS(imageID)

    def actionBtnClickHandler(self):
        pass
