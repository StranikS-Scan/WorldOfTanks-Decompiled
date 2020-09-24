# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/bootcamp/lobby/settings.py
from frameworks.wulf import WindowLayer, WindowFlags
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.daapi.view.bootcamp.BCMessageWindow import BCMessageWindow
from gui.Scaleform.daapi.view.bootcamp.BCNationsWindow import BCNationsWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
BOOTCAMP_LOBBY_VIEW_SETTINGS = (GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW, BCMessageWindow, 'BCMessageWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.TOP_WINDOW_SCOPE, canClose=False, canDrag=True, flags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW_MODAL), GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW, BCNationsWindow, 'BCNationsWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.WINDOW_SCOPE, canClose=False))
DIALOG_ALIAS_MAP = {'bootcampMessage': VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW,
 'bootcampSelectNation': VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW,
 'bootcampVideo': VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO}
WINDOW_ALIAS_MAP = {'bootcampSubtitle': VIEW_ALIAS.SUBTITLES_WINDOW}
