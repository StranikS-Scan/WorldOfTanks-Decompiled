# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/__init__.py
from adisp import process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.fortifications import FortClanStatisticsData
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes
from gui.Scaleform.framework.ScopeTemplates import LOBBY_SUB_SCOPE, MultipleScope
from gui.Scaleform.framework.ScopeTemplates import SimpleScope, VIEW_SCOPE
from gui.Scaleform.framework.ScopeTemplates import WINDOW_SCOPE
from gui.Scaleform.framework.managers import context_menu
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent
from gui.shared.utils.functions import getViewName
from shared_utils import CONST_CONTAINER

class FORT_SCOPE_TYPE(CONST_CONTAINER):
    FORT_WINDOWED_MULTISCOPE = 'FortWindowed'


class FortifiedWindowScopes(object):
    ASSIGN_BUILD_DLG_SCOPE = SimpleScope(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, VIEW_SCOPE)
    FORT_MAIN_SCOPE = SimpleScope(FORTIFICATION_ALIASES.MAIN_VIEW_ALIAS, LOBBY_SUB_SCOPE)
    FORT_WINDOWED_MULTISCOPE = MultipleScope(FORT_SCOPE_TYPE.FORT_WINDOWED_MULTISCOPE, (WINDOW_SCOPE, FORT_MAIN_SCOPE))


def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.fortifications.FortContextMenuHandler import FortContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.FORT_BUILDING, FortContextMenuHandler),)


class FortificationEffects(object):
    NONE_STATE = 'none'
    FADE_IN = 0
    VISIBLE = 2
    FADE_OUT = 1
    INVISIBLE = 3
    DONT_MOVE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    TEXTS = {FORTIFICATION_ALIASES.MODE_COMMON: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_COMMON_TITLE,
                                         'descrText': ''},
     FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_COMMONTUTOR_TITLE,
                                                  'descrText': ''},
     FORTIFICATION_ALIASES.MODE_DIRECTIONS: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_DIRECTIONS_TITLE,
                                             'descrText': FORTIFICATIONS.FORTMAINVIEW_DIRECTIONS_SELECTINGSTATUS},
     FORTIFICATION_ALIASES.MODE_DIRECTIONS_TUTORIAL: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_DIRECTIONSTUTOR_TITLE,
                                                      'descrText': ''},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TITLE,
                                                          'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_EXPORTINGSTATUS},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TITLE,
                                                         'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_IMPORTINGSTATUS},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TITLE,
                                                             'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_NOTAVAILABLESTATUS},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTINGTUTOR_TITLE,
                                                        'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TUTORIALDESCR},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TITLE,
                                                                   'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_EXPORTINGSTATUS},
     FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_NEXT_STEP: {'headerTitle': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_TITLE,
                                                                  'descrText': FORTIFICATIONS.FORTMAINVIEW_TRANSPORTING_IMPORTINGSTATUS}}

    @classmethod
    def getStates(cls):
        isClanProfileDisabled = not g_lobbyContext.getServerSettings().clanProfile.isEnabled()
        return {cls.NONE_STATE: {FORTIFICATION_ALIASES.MODE_COMMON: {'yellowVignette': cls.INVISIBLE,
                                                              'descrTextMove': cls.DONT_MOVE,
                                                              'statsBtn': cls.VISIBLE if isClanProfileDisabled else cls.INVISIBLE,
                                                              'clanListBtn': cls.VISIBLE,
                                                              'clanProfileBtn': cls.VISIBLE if not isClanProfileDisabled else cls.INVISIBLE,
                                                              'settingBtn': cls.VISIBLE,
                                                              'calendarBtn': cls.VISIBLE,
                                                              'transportToggle': cls.VISIBLE,
                                                              'clanInfo': cls.VISIBLE,
                                                              'totalDepotQuantity': cls.VISIBLE,
                                                              'footerBitmapFill': cls.VISIBLE,
                                                              'ordersPanel': cls.VISIBLE,
                                                              'orderSelector': cls.VISIBLE,
                                                              'sortieBtn': cls.VISIBLE,
                                                              'intelligenceButton': cls.VISIBLE,
                                                              'leaveModeBtn': cls.INVISIBLE,
                                                              'tutorialArrow': cls.INVISIBLE,
                                                              'infoTF': cls.VISIBLE,
                                                              'timeAlert': cls.VISIBLE},
                          FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL: {'yellowVignette': cls.FADE_IN,
                                                                       'descrTextMove': cls.DONT_MOVE,
                                                                       'statsBtn': cls.INVISIBLE,
                                                                       'clanProfileBtn': cls.INVISIBLE,
                                                                       'clanListBtn': cls.INVISIBLE,
                                                                       'settingBtn': cls.INVISIBLE,
                                                                       'calendarBtn': cls.INVISIBLE,
                                                                       'transportToggle': cls.INVISIBLE,
                                                                       'clanInfo': cls.INVISIBLE,
                                                                       'totalDepotQuantity': cls.INVISIBLE,
                                                                       'footerBitmapFill': cls.INVISIBLE,
                                                                       'ordersPanel': cls.INVISIBLE,
                                                                       'orderSelector': cls.INVISIBLE,
                                                                       'sortieBtn': cls.INVISIBLE,
                                                                       'intelligenceButton': cls.INVISIBLE,
                                                                       'leaveModeBtn': cls.INVISIBLE,
                                                                       'tutorialArrow': cls.INVISIBLE,
                                                                       'infoTF': cls.FADE_OUT,
                                                                       'timeAlert': cls.FADE_OUT},
                          FORTIFICATION_ALIASES.MODE_DIRECTIONS_TUTORIAL: {'yellowVignette': cls.FADE_IN,
                                                                           'descrTextMove': cls.DONT_MOVE,
                                                                           'statsBtn': cls.INVISIBLE,
                                                                           'clanListBtn': cls.INVISIBLE,
                                                                           'clanProfileBtn': cls.INVISIBLE,
                                                                           'settingBtn': cls.INVISIBLE,
                                                                           'calendarBtn': cls.INVISIBLE,
                                                                           'transportToggle': cls.INVISIBLE,
                                                                           'clanInfo': cls.INVISIBLE,
                                                                           'totalDepotQuantity': cls.INVISIBLE,
                                                                           'footerBitmapFill': cls.INVISIBLE,
                                                                           'ordersPanel': cls.INVISIBLE,
                                                                           'orderSelector': cls.INVISIBLE,
                                                                           'sortieBtn': cls.INVISIBLE,
                                                                           'intelligenceButton': cls.INVISIBLE,
                                                                           'leaveModeBtn': cls.INVISIBLE,
                                                                           'tutorialArrow': cls.INVISIBLE,
                                                                           'infoTF': cls.FADE_OUT,
                                                                           'timeAlert': cls.FADE_OUT},
                          FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL: {'yellowVignette': cls.FADE_IN,
                                                                             'descrTextMove': cls.MOVE_DOWN,
                                                                             'statsBtn': cls.INVISIBLE,
                                                                             'clanListBtn': cls.INVISIBLE,
                                                                             'clanProfileBtn': cls.INVISIBLE,
                                                                             'settingBtn': cls.INVISIBLE,
                                                                             'calendarBtn': cls.INVISIBLE,
                                                                             'transportToggle': cls.VISIBLE,
                                                                             'clanInfo': cls.INVISIBLE,
                                                                             'totalDepotQuantity': cls.VISIBLE,
                                                                             'footerBitmapFill': cls.INVISIBLE,
                                                                             'ordersPanel': cls.INVISIBLE,
                                                                             'orderSelector': cls.INVISIBLE,
                                                                             'sortieBtn': cls.INVISIBLE,
                                                                             'intelligenceButton': cls.INVISIBLE,
                                                                             'leaveModeBtn': cls.INVISIBLE,
                                                                             'tutorialArrow': cls.FADE_IN,
                                                                             'infoTF': cls.FADE_OUT,
                                                                             'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_COMMON: {FORTIFICATION_ALIASES.MODE_DIRECTIONS: {'yellowVignette': cls.FADE_IN,
                                                                                     'descrTextMove': cls.MOVE_DOWN,
                                                                                     'statsBtn': cls.VISIBLE if isClanProfileDisabled else cls.INVISIBLE,
                                                                                     'clanListBtn': cls.VISIBLE,
                                                                                     'clanProfileBtn': cls.VISIBLE if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                     'settingBtn': cls.INVISIBLE,
                                                                                     'calendarBtn': cls.VISIBLE,
                                                                                     'transportToggle': cls.INVISIBLE,
                                                                                     'clanInfo': cls.FADE_OUT,
                                                                                     'totalDepotQuantity': cls.INVISIBLE,
                                                                                     'footerBitmapFill': cls.FADE_OUT,
                                                                                     'ordersPanel': cls.FADE_OUT,
                                                                                     'orderSelector': cls.FADE_OUT,
                                                                                     'sortieBtn': cls.FADE_OUT,
                                                                                     'intelligenceButton': cls.FADE_OUT,
                                                                                     'leaveModeBtn': cls.FADE_IN,
                                                                                     'tutorialArrow': cls.INVISIBLE,
                                                                                     'infoTF': cls.FADE_OUT,
                                                                                     'timeAlert': cls.FADE_OUT},
                                             FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {'yellowVignette': cls.FADE_IN,
                                                                                                  'descrTextMove': cls.MOVE_DOWN,
                                                                                                  'statsBtn': cls.FADE_OUT if isClanProfileDisabled else cls.INVISIBLE,
                                                                                                  'clanListBtn': cls.FADE_OUT,
                                                                                                  'clanProfileBtn': cls.FADE_OUT if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                                  'settingBtn': cls.FADE_OUT,
                                                                                                  'calendarBtn': cls.FADE_OUT,
                                                                                                  'transportToggle': cls.VISIBLE,
                                                                                                  'clanInfo': cls.FADE_OUT,
                                                                                                  'totalDepotQuantity': cls.VISIBLE,
                                                                                                  'footerBitmapFill': cls.FADE_OUT,
                                                                                                  'ordersPanel': cls.FADE_OUT,
                                                                                                  'orderSelector': cls.FADE_OUT,
                                                                                                  'sortieBtn': cls.FADE_OUT,
                                                                                                  'intelligenceButton': cls.FADE_OUT,
                                                                                                  'leaveModeBtn': cls.FADE_IN,
                                                                                                  'tutorialArrow': cls.INVISIBLE,
                                                                                                  'infoTF': cls.FADE_OUT,
                                                                                                  'timeAlert': cls.FADE_OUT},
                                             FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE: {'yellowVignette': cls.FADE_IN,
                                                                                                     'descrTextMove': cls.MOVE_DOWN,
                                                                                                     'statsBtn': cls.FADE_OUT if isClanProfileDisabled else cls.INVISIBLE,
                                                                                                     'clanListBtn': cls.FADE_OUT,
                                                                                                     'clanProfileBtn': cls.FADE_OUT if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                                     'settingBtn': cls.FADE_OUT,
                                                                                                     'calendarBtn': cls.FADE_OUT,
                                                                                                     'transportToggle': cls.VISIBLE,
                                                                                                     'clanInfo': cls.FADE_OUT,
                                                                                                     'totalDepotQuantity': cls.VISIBLE,
                                                                                                     'footerBitmapFill': cls.FADE_OUT,
                                                                                                     'ordersPanel': cls.FADE_OUT,
                                                                                                     'orderSelector': cls.FADE_OUT,
                                                                                                     'sortieBtn': cls.FADE_OUT,
                                                                                                     'intelligenceButton': cls.FADE_OUT,
                                                                                                     'leaveModeBtn': cls.FADE_IN,
                                                                                                     'tutorialArrow': cls.INVISIBLE,
                                                                                                     'infoTF': cls.FADE_OUT,
                                                                                                     'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {FORTIFICATION_ALIASES.MODE_COMMON: {'yellowVignette': cls.FADE_OUT,
                                                                                                  'descrTextMove': cls.MOVE_UP,
                                                                                                  'statsBtn': cls.FADE_IN if isClanProfileDisabled else cls.INVISIBLE,
                                                                                                  'clanListBtn': cls.FADE_IN,
                                                                                                  'clanProfileBtn': cls.FADE_IN if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                                  'settingBtn': cls.FADE_IN,
                                                                                                  'calendarBtn': cls.FADE_IN,
                                                                                                  'transportToggle': cls.VISIBLE,
                                                                                                  'clanInfo': cls.FADE_IN,
                                                                                                  'totalDepotQuantity': cls.VISIBLE,
                                                                                                  'footerBitmapFill': cls.FADE_IN,
                                                                                                  'ordersPanel': cls.FADE_IN,
                                                                                                  'orderSelector': cls.FADE_IN,
                                                                                                  'sortieBtn': cls.FADE_IN,
                                                                                                  'intelligenceButton': cls.FADE_IN,
                                                                                                  'leaveModeBtn': cls.FADE_OUT,
                                                                                                  'tutorialArrow': cls.INVISIBLE,
                                                                                                  'infoTF': cls.FADE_IN,
                                                                                                  'timeAlert': cls.FADE_IN},
                                                              FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                  'descrTextMove': cls.DONT_MOVE,
                                                                                                                  'statsBtn': cls.INVISIBLE,
                                                                                                                  'clanListBtn': cls.INVISIBLE,
                                                                                                                  'clanProfileBtn': cls.INVISIBLE,
                                                                                                                  'settingBtn': cls.INVISIBLE,
                                                                                                                  'calendarBtn': cls.INVISIBLE,
                                                                                                                  'transportToggle': cls.VISIBLE,
                                                                                                                  'clanInfo': cls.INVISIBLE,
                                                                                                                  'totalDepotQuantity': cls.VISIBLE,
                                                                                                                  'footerBitmapFill': cls.INVISIBLE,
                                                                                                                  'ordersPanel': cls.INVISIBLE,
                                                                                                                  'orderSelector': cls.INVISIBLE,
                                                                                                                  'sortieBtn': cls.INVISIBLE,
                                                                                                                  'intelligenceButton': cls.INVISIBLE,
                                                                                                                  'leaveModeBtn': cls.VISIBLE,
                                                                                                                  'tutorialArrow': cls.INVISIBLE,
                                                                                                                  'infoTF': cls.FADE_OUT,
                                                                                                                  'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP: {FORTIFICATION_ALIASES.MODE_COMMON: {'yellowVignette': cls.FADE_OUT,
                                                                                                 'descrTextMove': cls.MOVE_UP,
                                                                                                 'statsBtn': cls.FADE_IN if isClanProfileDisabled else cls.INVISIBLE,
                                                                                                 'clanListBtn': cls.FADE_IN,
                                                                                                 'clanProfileBtn': cls.FADE_IN if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                                 'settingBtn': cls.FADE_IN,
                                                                                                 'calendarBtn': cls.FADE_IN,
                                                                                                 'transportToggle': cls.VISIBLE,
                                                                                                 'clanInfo': cls.FADE_IN,
                                                                                                 'totalDepotQuantity': cls.VISIBLE,
                                                                                                 'footerBitmapFill': cls.FADE_IN,
                                                                                                 'ordersPanel': cls.FADE_IN,
                                                                                                 'orderSelector': cls.FADE_IN,
                                                                                                 'sortieBtn': cls.FADE_IN,
                                                                                                 'intelligenceButton': cls.FADE_IN,
                                                                                                 'leaveModeBtn': cls.FADE_OUT,
                                                                                                 'tutorialArrow': cls.INVISIBLE,
                                                                                                 'infoTF': cls.FADE_IN,
                                                                                                 'timeAlert': cls.FADE_IN},
                                                             FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                  'descrTextMove': cls.DONT_MOVE,
                                                                                                                  'statsBtn': cls.INVISIBLE,
                                                                                                                  'clanListBtn': cls.INVISIBLE,
                                                                                                                  'clanProfileBtn': cls.INVISIBLE,
                                                                                                                  'settingBtn': cls.INVISIBLE,
                                                                                                                  'calendarBtn': cls.INVISIBLE,
                                                                                                                  'transportToggle': cls.VISIBLE,
                                                                                                                  'clanInfo': cls.INVISIBLE,
                                                                                                                  'totalDepotQuantity': cls.VISIBLE,
                                                                                                                  'footerBitmapFill': cls.INVISIBLE,
                                                                                                                  'ordersPanel': cls.INVISIBLE,
                                                                                                                  'orderSelector': cls.INVISIBLE,
                                                                                                                  'sortieBtn': cls.INVISIBLE,
                                                                                                                  'intelligenceButton': cls.INVISIBLE,
                                                                                                                  'leaveModeBtn': cls.VISIBLE,
                                                                                                                  'tutorialArrow': cls.INVISIBLE,
                                                                                                                  'infoTF': cls.FADE_OUT,
                                                                                                                  'timeAlert': cls.FADE_OUT},
                                                             FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE: {'yellowVignette': cls.VISIBLE,
                                                                                                                     'descrTextMove': cls.DONT_MOVE,
                                                                                                                     'statsBtn': cls.INVISIBLE,
                                                                                                                     'clanListBtn': cls.INVISIBLE,
                                                                                                                     'clanProfileBtn': cls.INVISIBLE,
                                                                                                                     'settingBtn': cls.INVISIBLE,
                                                                                                                     'calendarBtn': cls.INVISIBLE,
                                                                                                                     'transportToggle': cls.VISIBLE,
                                                                                                                     'clanInfo': cls.INVISIBLE,
                                                                                                                     'totalDepotQuantity': cls.VISIBLE,
                                                                                                                     'footerBitmapFill': cls.INVISIBLE,
                                                                                                                     'ordersPanel': cls.INVISIBLE,
                                                                                                                     'orderSelector': cls.INVISIBLE,
                                                                                                                     'sortieBtn': cls.INVISIBLE,
                                                                                                                     'intelligenceButton': cls.INVISIBLE,
                                                                                                                     'leaveModeBtn': cls.VISIBLE,
                                                                                                                     'tutorialArrow': cls.INVISIBLE,
                                                                                                                     'infoTF': cls.FADE_OUT,
                                                                                                                     'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE: {FORTIFICATION_ALIASES.MODE_COMMON: {'yellowVignette': cls.FADE_OUT,
                                                                                                     'descrTextMove': cls.MOVE_UP,
                                                                                                     'statsBtn': cls.FADE_IN if isClanProfileDisabled else cls.INVISIBLE,
                                                                                                     'clanListBtn': cls.FADE_IN,
                                                                                                     'clanProfileBtn': cls.FADE_IN if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                                     'settingBtn': cls.FADE_IN,
                                                                                                     'calendarBtn': cls.FADE_IN,
                                                                                                     'transportToggle': cls.VISIBLE,
                                                                                                     'clanInfo': cls.FADE_IN,
                                                                                                     'totalDepotQuantity': cls.VISIBLE,
                                                                                                     'footerBitmapFill': cls.FADE_IN,
                                                                                                     'ordersPanel': cls.FADE_IN,
                                                                                                     'orderSelector': cls.FADE_IN,
                                                                                                     'sortieBtn': cls.FADE_IN,
                                                                                                     'intelligenceButton': cls.FADE_IN,
                                                                                                     'leaveModeBtn': cls.FADE_OUT,
                                                                                                     'tutorialArrow': cls.INVISIBLE,
                                                                                                     'infoTF': cls.FADE_IN,
                                                                                                     'timeAlert': cls.FADE_IN},
                                                                 FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                      'descrTextMove': cls.DONT_MOVE,
                                                                                                                      'statsBtn': cls.INVISIBLE,
                                                                                                                      'clanListBtn': cls.INVISIBLE,
                                                                                                                      'clanProfileBtn': cls.INVISIBLE,
                                                                                                                      'settingBtn': cls.INVISIBLE,
                                                                                                                      'calendarBtn': cls.INVISIBLE,
                                                                                                                      'transportToggle': cls.VISIBLE,
                                                                                                                      'clanInfo': cls.INVISIBLE,
                                                                                                                      'totalDepotQuantity': cls.VISIBLE,
                                                                                                                      'footerBitmapFill': cls.INVISIBLE,
                                                                                                                      'ordersPanel': cls.INVISIBLE,
                                                                                                                      'orderSelector': cls.INVISIBLE,
                                                                                                                      'sortieBtn': cls.INVISIBLE,
                                                                                                                      'intelligenceButton': cls.INVISIBLE,
                                                                                                                      'leaveModeBtn': cls.VISIBLE,
                                                                                                                      'tutorialArrow': cls.INVISIBLE,
                                                                                                                      'infoTF': cls.FADE_OUT,
                                                                                                                      'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_DIRECTIONS: {FORTIFICATION_ALIASES.MODE_COMMON: {'yellowVignette': cls.FADE_OUT,
                                                                                     'descrTextMove': cls.MOVE_UP,
                                                                                     'statsBtn': cls.VISIBLE if isClanProfileDisabled else cls.INVISIBLE,
                                                                                     'clanListBtn': cls.VISIBLE,
                                                                                     'clanProfileBtn': cls.VISIBLE if not isClanProfileDisabled else cls.INVISIBLE,
                                                                                     'settingBtn': cls.VISIBLE,
                                                                                     'calendarBtn': cls.VISIBLE,
                                                                                     'transportToggle': cls.VISIBLE,
                                                                                     'clanInfo': cls.FADE_IN,
                                                                                     'totalDepotQuantity': cls.VISIBLE,
                                                                                     'footerBitmapFill': cls.FADE_IN,
                                                                                     'ordersPanel': cls.FADE_IN,
                                                                                     'orderSelector': cls.FADE_IN,
                                                                                     'sortieBtn': cls.FADE_IN,
                                                                                     'intelligenceButton': cls.FADE_IN,
                                                                                     'leaveModeBtn': cls.FADE_OUT,
                                                                                     'tutorialArrow': cls.INVISIBLE,
                                                                                     'infoTF': cls.FADE_IN,
                                                                                     'timeAlert': cls.FADE_IN}},
         FORTIFICATION_ALIASES.MODE_DIRECTIONS_TUTORIAL: {FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL: {'yellowVignette': cls.VISIBLE,
                                                                                                       'descrTextMove': cls.DONT_MOVE,
                                                                                                       'statsBtn': cls.INVISIBLE,
                                                                                                       'clanListBtn': cls.INVISIBLE,
                                                                                                       'clanProfileBtn': cls.INVISIBLE,
                                                                                                       'settingBtn': cls.INVISIBLE,
                                                                                                       'calendarBtn': cls.INVISIBLE,
                                                                                                       'transportToggle': cls.INVISIBLE,
                                                                                                       'clanInfo': cls.INVISIBLE,
                                                                                                       'totalDepotQuantity': cls.INVISIBLE,
                                                                                                       'footerBitmapFill': cls.INVISIBLE,
                                                                                                       'ordersPanel': cls.INVISIBLE,
                                                                                                       'orderSelector': cls.INVISIBLE,
                                                                                                       'sortieBtn': cls.INVISIBLE,
                                                                                                       'intelligenceButton': cls.INVISIBLE,
                                                                                                       'leaveModeBtn': cls.INVISIBLE,
                                                                                                       'tutorialArrow': cls.INVISIBLE,
                                                                                                       'infoTF': cls.FADE_OUT,
                                                                                                       'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL: {FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL: {'yellowVignette': cls.VISIBLE,
                                                                                                         'descrTextMove': cls.MOVE_DOWN,
                                                                                                         'statsBtn': cls.INVISIBLE,
                                                                                                         'clanListBtn': cls.INVISIBLE,
                                                                                                         'clanProfileBtn': cls.INVISIBLE,
                                                                                                         'settingBtn': cls.INVISIBLE,
                                                                                                         'calendarBtn': cls.INVISIBLE,
                                                                                                         'transportToggle': cls.VISIBLE,
                                                                                                         'clanInfo': cls.INVISIBLE,
                                                                                                         'totalDepotQuantity': cls.FADE_IN,
                                                                                                         'footerBitmapFill': cls.INVISIBLE,
                                                                                                         'ordersPanel': cls.INVISIBLE,
                                                                                                         'orderSelector': cls.INVISIBLE,
                                                                                                         'sortieBtn': cls.INVISIBLE,
                                                                                                         'intelligenceButton': cls.INVISIBLE,
                                                                                                         'leaveModeBtn': cls.INVISIBLE,
                                                                                                         'tutorialArrow': cls.FADE_IN,
                                                                                                         'infoTF': cls.FADE_OUT,
                                                                                                         'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP: {FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_NEXT_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                                    'descrTextMove': cls.DONT_MOVE,
                                                                                                                                    'statsBtn': cls.INVISIBLE,
                                                                                                                                    'clanListBtn': cls.INVISIBLE,
                                                                                                                                    'clanProfileBtn': cls.INVISIBLE,
                                                                                                                                    'settingBtn': cls.INVISIBLE,
                                                                                                                                    'calendarBtn': cls.INVISIBLE,
                                                                                                                                    'transportToggle': cls.INVISIBLE,
                                                                                                                                    'clanInfo': cls.INVISIBLE,
                                                                                                                                    'totalDepotQuantity': cls.VISIBLE,
                                                                                                                                    'footerBitmapFill': cls.INVISIBLE,
                                                                                                                                    'ordersPanel': cls.INVISIBLE,
                                                                                                                                    'orderSelector': cls.INVISIBLE,
                                                                                                                                    'sortieBtn': cls.INVISIBLE,
                                                                                                                                    'intelligenceButton': cls.INVISIBLE,
                                                                                                                                    'leaveModeBtn': cls.INVISIBLE,
                                                                                                                                    'tutorialArrow': cls.INVISIBLE,
                                                                                                                                    'infoTF': cls.FADE_OUT,
                                                                                                                                    'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_NEXT_STEP: {FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                           'descrTextMove': cls.DONT_MOVE,
                                                                                                                           'statsBtn': cls.INVISIBLE,
                                                                                                                           'clanListBtn': cls.INVISIBLE,
                                                                                                                           'clanProfileBtn': cls.INVISIBLE,
                                                                                                                           'settingBtn': cls.INVISIBLE,
                                                                                                                           'calendarBtn': cls.INVISIBLE,
                                                                                                                           'transportToggle': cls.FADE_IN,
                                                                                                                           'clanInfo': cls.INVISIBLE,
                                                                                                                           'totalDepotQuantity': cls.VISIBLE,
                                                                                                                           'footerBitmapFill': cls.INVISIBLE,
                                                                                                                           'ordersPanel': cls.INVISIBLE,
                                                                                                                           'orderSelector': cls.INVISIBLE,
                                                                                                                           'sortieBtn': cls.INVISIBLE,
                                                                                                                           'intelligenceButton': cls.INVISIBLE,
                                                                                                                           'leaveModeBtn': cls.FADE_IN,
                                                                                                                           'tutorialArrow': cls.INVISIBLE,
                                                                                                                           'infoTF': cls.FADE_OUT,
                                                                                                                           'timeAlert': cls.FADE_OUT},
                                                                      FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                                    'descrTextMove': cls.DONT_MOVE,
                                                                                                                                    'statsBtn': cls.INVISIBLE,
                                                                                                                                    'clanListBtn': cls.INVISIBLE,
                                                                                                                                    'clanProfileBtn': cls.INVISIBLE,
                                                                                                                                    'settingBtn': cls.INVISIBLE,
                                                                                                                                    'calendarBtn': cls.INVISIBLE,
                                                                                                                                    'transportToggle': cls.INVISIBLE,
                                                                                                                                    'clanInfo': cls.INVISIBLE,
                                                                                                                                    'totalDepotQuantity': cls.VISIBLE,
                                                                                                                                    'footerBitmapFill': cls.INVISIBLE,
                                                                                                                                    'ordersPanel': cls.INVISIBLE,
                                                                                                                                    'orderSelector': cls.INVISIBLE,
                                                                                                                                    'sortieBtn': cls.INVISIBLE,
                                                                                                                                    'intelligenceButton': cls.INVISIBLE,
                                                                                                                                    'leaveModeBtn': cls.INVISIBLE,
                                                                                                                                    'tutorialArrow': cls.INVISIBLE,
                                                                                                                                    'infoTF': cls.FADE_OUT,
                                                                                                                                    'timeAlert': cls.FADE_OUT},
                                                                      FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE: {'yellowVignette': cls.VISIBLE,
                                                                                                                              'descrTextMove': cls.DONT_MOVE,
                                                                                                                              'statsBtn': cls.INVISIBLE,
                                                                                                                              'clanListBtn': cls.INVISIBLE,
                                                                                                                              'clanProfileBtn': cls.INVISIBLE,
                                                                                                                              'settingBtn': cls.INVISIBLE,
                                                                                                                              'calendarBtn': cls.INVISIBLE,
                                                                                                                              'transportToggle': cls.FADE_IN,
                                                                                                                              'clanInfo': cls.INVISIBLE,
                                                                                                                              'totalDepotQuantity': cls.VISIBLE,
                                                                                                                              'footerBitmapFill': cls.INVISIBLE,
                                                                                                                              'ordersPanel': cls.INVISIBLE,
                                                                                                                              'orderSelector': cls.INVISIBLE,
                                                                                                                              'sortieBtn': cls.INVISIBLE,
                                                                                                                              'intelligenceButton': cls.INVISIBLE,
                                                                                                                              'leaveModeBtn': cls.VISIBLE,
                                                                                                                              'tutorialArrow': cls.INVISIBLE,
                                                                                                                              'infoTF': cls.FADE_OUT,
                                                                                                                              'timeAlert': cls.FADE_OUT}},
         FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL: {FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP: {'yellowVignette': cls.VISIBLE,
                                                                                                                          'descrTextMove': cls.DONT_MOVE,
                                                                                                                          'statsBtn': cls.INVISIBLE,
                                                                                                                          'clanListBtn': cls.INVISIBLE,
                                                                                                                          'clanProfileBtn': cls.INVISIBLE,
                                                                                                                          'settingBtn': cls.INVISIBLE,
                                                                                                                          'calendarBtn': cls.INVISIBLE,
                                                                                                                          'transportToggle': cls.FADE_OUT,
                                                                                                                          'clanInfo': cls.INVISIBLE,
                                                                                                                          'totalDepotQuantity': cls.VISIBLE,
                                                                                                                          'footerBitmapFill': cls.INVISIBLE,
                                                                                                                          'ordersPanel': cls.INVISIBLE,
                                                                                                                          'orderSelector': cls.INVISIBLE,
                                                                                                                          'sortieBtn': cls.INVISIBLE,
                                                                                                                          'intelligenceButton': cls.INVISIBLE,
                                                                                                                          'leaveModeBtn': cls.INVISIBLE,
                                                                                                                          'tutorialArrow': cls.FADE_OUT,
                                                                                                                          'infoTF': cls.FADE_OUT,
                                                                                                                          'timeAlert': cls.FADE_OUT}}}


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleDirectionPopover import FortBattleDirectionPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortCalendarWindow import FortCalendarWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortCombatReservesIntroWindow import FortCombatReservesIntroWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortDatePickerPopover import FortDatePickerPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortChoiceDivisionWindow import FortChoiceDivisionWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortClanBattleRoom import FortClanBattleRoom
    from gui.Scaleform.daapi.view.lobby.fortifications.StrongholdBattleRoom import StrongholdBattleRoom
    from gui.Scaleform.daapi.view.lobby.fortifications.FortDeclarationOfWarWindow import FortDeclarationOfWarWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortDisableDefencePeriodWindow import FortDisableDefencePeriodWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceWindow import FortIntelligenceWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceNotAvailableWindow import FortIntelligenceNotAvailableWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderInfoWindow import FortOrderInfoWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortOrdersPanelComponent import FortOrdersPanelComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleRoomOrdersPanelComponent import FortBattleRoomOrdersPanelComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.FortRosterIntroWindow import FortRosterIntroWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSortieOrdersPanelComponent import FortSortieOrdersPanelComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsDayoffPopover import FortSettingsDayoffPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsWindow import FortSettingsWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelligenceClanDescription import FortIntelligenceClanDescription
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesListView import FortBattlesListView
    from gui.Scaleform.daapi.view.lobby.fortifications.FortPeriodDefenceWindow import FortPeriodDefenceWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortDisconnectViewComponent import FortDisconnectViewComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelFilter import FortIntelFilter
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesIntroView import FortBattlesIntroView
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesSortieListView import FortBattlesSortieListView
    from gui.Scaleform.daapi.view.lobby.fortifications.components.StrongholdBattlesListView import StrongholdBattlesListView
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortMainViewComponent import FortMainViewComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesRoomView import FortBattlesRoomView
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortWelcomeViewComponent import FortWelcomeViewComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.components.FortWelcomeInfoView import FortWelcomeInfoView
    from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceClanFilterPopover import FortIntelligenceClanFilterPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsPeripheryPopover import FortSettingsPeripheryPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsDefenceHourPopover import FortSettingsDefenceHourPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsVacationPopover import FortSettingsVacationPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleResultsWindow import FortBattleResultsWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingProcessWindow import FortBuildingProcessWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortFixedPlayersWindow import FortFixedPlayersWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortificationsView import FortificationsView
    from gui.Scaleform.daapi.view.lobby.fortifications.FortModernizationWindow import FortModernizationWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleRoomWindow import FortBattleRoomWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.StrongholdBattleRoomWindow import StrongholdBattleRoomWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingCardPopover import FortBuildingCardPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortClanListWindow import FortClanListWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortClanStatisticsWindow import FortClanStatisticsWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortCreateDirectionWindow import FortCreateDirectionWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortCreationCongratulationsWindow import FortCreationCongratulationsWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortNotCommanderFirstEnterWindow import FortNotCommanderFirstEnterWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderConfirmationWindow import FortOrderConfirmationWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderPopover import FortOrderPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortTransportConfirmationWindow import FortTransportConfirmationWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingComponent import FortBuildingComponent
    from gui.Scaleform.daapi.view.lobby.fortifications.FortDemountBuildingWindow import FortDemountBuildingWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderSelectPopover import FortOrderSelectPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.FortReserveSelectPopover import FortReserveSelectPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.StrongholdSendInvitesWindow import StrongholdSendInvitesWindow
    return (ViewSettings(FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, FortificationsView, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_UI, ViewTypes.LOBBY_SUB, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, StrongholdSendInvitesWindow, 'sendInvitesWindow.swf', ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, FortTransportConfirmationWindow, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, FortPeriodDefenceWindow, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, FortRosterIntroWindow, FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortOrderPopover, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FortBattleDirectionPopover, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, FortReserveSelectPopover, FORTIFICATION_ALIASES.FORT_FITTING_SELECT_POPOVER_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FortSettingsPeripheryPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FortSettingsDefenceHourPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FortSettingsVacationPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FortDatePickerPopover, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FortOrderSelectPopover, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, FortOrderConfirmationWindow, FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_UI, ViewTypes.TOP_WINDOW, ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, FortCreationCongratulationsWindow, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, FortCreateDirectionWindow, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, FortDeclarationOfWarWindow, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, FortClanStatisticsWindow, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, FortCalendarWindow, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, FortClanListWindow, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, FortNotCommanderFirstEnterWindow, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortBuildingCardPopover, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FortIntelligenceClanFilterPopover, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FortSettingsDayoffPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, FortBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, StrongholdBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, FortModernizationWindow, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, FortFixedPlayersWindow, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, FortBuildingProcessWindow, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, FortIntelligenceWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, FortIntelligenceNotAvailableWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, FortDemountBuildingWindow, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, FortDisableDefencePeriodWindow, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, FortSettingsWindow, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, FortOrderInfoWindow, FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, FortBattleResultsWindow, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, FortCombatReservesIntroWindow, FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_COMPONENT_ALIAS, FortBuildingComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_ORDERS_PANEL_COMPONENT_ALIAS, FortOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_SORTIE_ORDERS_PANEL_COMPONENT_ALIAS, FortSortieOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.MAIN_VIEW_ALIAS, FortMainViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.WELCOME_VIEW_ALIAS, FortWelcomeViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.DISCONNECT_VIEW_ALIAS, FortDisconnectViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_PY, FortBattlesIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_PY, FortBattlesSortieListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_LIST_VIEW_PY, StrongholdBattlesListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_LIST_VIEW_PY, FortBattlesListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, FortBattlesRoomView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_PY, FortClanBattleRoom, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_VIEW_PY, StrongholdBattleRoom, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTEL_FILTER_ALIAS, FortIntelFilter, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.FORT_WELCOME_INFO, FortWelcomeInfoView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, FortChoiceDivisionWindow, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_DESCRIPTION, FortIntelligenceClanDescription, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_FortsBusinessHandler(), _FortsDialogsHandler())


class _FortsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, self.__showFortBattleResultsWindow),
         (FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, self.__showFortBattleRoomWindow),
         (FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, self.__showStrongholdBattleRoomWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, self.__showFortBuildingProcessWindow),
         (FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, self.__showAsyncDataView),
         (FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, self.__showOrUpdateWindow),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, self.__showOrUpdateWindow),
         (FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, self.__showOrderInfo),
         (FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, self.__showPrebattleWindow))
        super(_FortsBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
        self.__fortClanInfoNameInc = 0

    def _loadUniqueWindow(self, alias, ctx=None):
        return self.loadViewWithDefName(alias, alias, ctx) if ctx is not None else self.loadViewWithDefName(alias, alias)

    def __showMultipleViews(self, event):
        self.loadViewWithDefName(event.eventType, event.name + str(self.__fortClanInfoNameInc), event.ctx)
        self.__fortClanInfoNameInc += 1

    def __showOrderInfo(self, event):
        orderID = event.ctx.get('orderID', None)
        self.loadViewWithDefName(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, str(orderID), event.ctx)
        return

    def __showOrUpdateWindow(self, event):
        self.__loadOrUpdateWindow(event.eventType, event.name, event.ctx)

    def __loadOrUpdateWindow(self, name, alias, ctx):
        window = self.findViewByAlias(ViewTypes.WINDOW, alias)
        if window is not None:
            window.updateWindow(ctx)
            self.bringViewToFront(name)
        else:
            self.loadViewWithDefName(alias, name, ctx)
        return

    def __showFortBattleResultsWindow(self, event):
        ctx = event.ctx['data']
        self.loadViewWithDefName(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, getViewName(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx['battleID']), ctx)

    def __showFortBattleRoomWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS
        window = self.findViewByAlias(ViewTypes.WINDOW, alias)
        if window is not None:
            if event.ctx.get('modeFlags') == FUNCTIONAL_FLAG.UNIT_BROWSER:
                window.onBrowseRallies()
        self.loadViewWithDefName(alias, name, event.ctx)
        return

    def __showStrongholdBattleRoomWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS
        window = self.findViewByAlias(ViewTypes.WINDOW, alias)
        if window is not None:
            if event.ctx.get('modeFlags') == FUNCTIONAL_FLAG.UNIT_BROWSER:
                window.onBrowseRallies()
        self.loadViewWithDefName(alias, name, event.ctx)
        return

    def __showFortBuildingProcessWindow(self, event):
        alias = FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS
        dir = event.ctx.get('buildingDirection')
        pos = event.ctx.get('buildingPosition')
        name = '%s%d%d' % (alias, dir, pos)
        self.loadViewWithDefName(alias, name, event.ctx)

    @process
    def __showAsyncDataView(self, event):
        data = yield FortClanStatisticsData.getDataObject()
        if data is not None:
            self.loadViewWithDefName(event.eventType, event.name, data)
        return

    def __showPrebattleWindow(self, event):
        alias = name = event.eventType
        self.loadViewWithDefName(alias, name, event.ctx)


class _FortsDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(_FortsDialogsHandler, self).__init__([(ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, self.__showFortOrderConfirmationWindow)], APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.DEFAULT)

    def __showFortOrderConfirmationWindow(self, event):
        self.loadViewWithGenName(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, event.meta, event.handler)
