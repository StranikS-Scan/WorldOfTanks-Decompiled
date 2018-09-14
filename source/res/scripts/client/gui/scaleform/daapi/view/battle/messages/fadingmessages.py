# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/messages/FadingMessages.py
from account_helpers.settings_core import g_settingsCore
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui.battle_control import g_sessionProvider
from gui.doc_loaders import messages_panel_reader
_EXTRA_COLOR_FORMAT = '<font color="#{0:02X}{1:02X}{2:02X}">{3:>s}</font>'

class FadingMessages(object):

    def __init__(self, parentUI, name, cfgFileName):
        self.__name = name
        self.__cfgFileName = cfgFileName
        self.__isColorBlind = g_settingsCore.getSetting('isColorBlind')
        self.__messages = {}
        self.__ui = parentUI
        self.__name = name
        self.__pathPrefix = 'battle.{0}.%s'.format(name)
        self.__ui.addExternalCallbacks({'battle.%s.PopulateUI' % name: self.__onPopulateUI})

    def start(self):
        self.__callFlash('RefreshUI')

    def destroy(self):
        self._removeGameListeners()
        self.__ui = None
        return

    def clear(self):
        self.__callFlash('Clear')

    def showMessage(self, key, args = None, extra = None, postfix = ''):
        if postfix:
            extKey = '{0}_{1}'.format(key, postfix)
            if extKey in self.__messages:
                self.__doShowMessage(extKey, args, extra)
                return
        if key in self.__messages:
            self.__doShowMessage(key, args, extra)
            return
        LOG_DEBUG('Message was not processed', key, args, extra, postfix)

    def _addGameListeners(self):
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged

    def _removeGameListeners(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __showMessage(self, key, msgText, color):
        LOG_DEBUG('%s: show message with key = %s' % (self.__name, key))
        self.__callFlash('ShowMessage', [key, msgText, color])

    def __formatEntitiesEx(self, args, extra = None):
        if extra is None:
            extra = ()
        manager = self.__ui.colorManager
        battleCtx = g_sessionProvider.getCtx()
        isTeamKiller = battleCtx.isTeamKiller
        isSquadMan = battleCtx.isSquadMan
        for argName, vID in extra:
            arg = args.get(argName)
            rgba = None
            if isTeamKiller(vID=vID):
                rgba = manager.getRGBA('teamkiller')
            elif isSquadMan(vID=vID):
                rgba = manager.getRGBA('squad')
            if arg and rgba:
                args[argName] = _EXTRA_COLOR_FORMAT.format(int(rgba[0]), int(rgba[1]), int(rgba[2]), arg)

        return

    def __doShowMessage(self, key, args = None, extra = None):
        msgText, colors = self.__messages[key]
        if args is not None:
            self.__formatEntitiesEx(args, extra=extra)
            try:
                msgText = msgText % args
            except TypeError:
                LOG_CURRENT_EXCEPTION()

        if self.__isColorBlind:
            color = colors[1]
        else:
            color = colors[0]
        LOG_DEBUG('Show message in a battle', self.__name, key)
        self.__callFlash('ShowMessage', [key, msgText, color])
        return

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__isColorBlind = diff['isColorBlind']

    def __onPopulateUI(self, requestID):
        settings, self.__messages = messages_panel_reader.readXML(self.__cfgFileName)
        args = [requestID]
        args.extend(settings)
        self.__ui.respond(args)
        self._addGameListeners()

    def __callFlash(self, funcName, args = None):
        self.__ui.call(self.__pathPrefix % funcName, args)
