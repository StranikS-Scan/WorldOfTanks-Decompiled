# Embedded file name: scripts/client/gui/Scaleform/PlayersPanel.py
from debug_utils import LOG_ERROR
from windows import UIInterface
from weakref import proxy
from external_strings_utils import normalized_unicode_trim, unicode_from_utf8
from gui.arena_info import isEventBattle

class PlayersPanel(UIInterface):

    def __init__(self, parentUI, isLeft, isColorBlind = False):
        super(PlayersPanel, self).__init__()
        self.proxy = proxy(self)
        self.GUICtrl = None
        self.__parentUI = parentUI
        self.__isLeft = isLeft
        self.defineColorFlags(isColorBlind=isColorBlind)
        return

    def populateUI(self, proxy):
        super(PlayersPanel, self).populateUI(proxy)
        if self.__isLeft:
            self.GUICtrl = self.uiHolder.getMember('_level0.leftPanel')
        else:
            self.GUICtrl = self.uiHolder.getMember('_level0.rightPanel')
        self.GUICtrl.script = self

    def setTeamValuesData(self, data):
        self.GUICtrl.setTeamValues(data)

    def defineColorFlags(self, isColorBlind = False):
        self.__colorGroup = 'color_blind' if isColorBlind else 'default'

    def getFormattedStrings(self, vInfoVO, vStatsVO, ctx, fullPlayerName):
        format = self.__findHTMLFormat(vInfoVO, ctx)
        unicodeStr, _ = unicode_from_utf8(fullPlayerName)
        if len(unicodeStr) > ctx.labelMaxLength:
            fullPlayerName = '{0}..'.format(normalized_unicode_trim(fullPlayerName, ctx.labelMaxLength - 2))
        fragsString = format % ' '
        if not isEventBattle() and vStatsVO.frags:
            fragsString = format % str(vStatsVO.frags)
        return (format % fullPlayerName, fragsString, format % vInfoVO.vehicleType.shortName)

    def getPlayerNameLength(self):
        return self.GUICtrl.getPlayerNameLength()

    def __findHTMLFormat(self, item, ctx):
        if ctx.isPlayerSelected(item):
            return self.__getHTMLString('selected' if item.isReady() else 'selected_dead')
        isAliveAndIntoArena = item.isAlive() and item.isReady()
        if ctx.isSquadMan(item):
            return self.__getHTMLString('squad' if isAliveAndIntoArena else 'squad_dead')
        elif ctx.isTeamKiller(item):
            return self.__getHTMLString('teamkiller' if isAliveAndIntoArena else 'teamkiller_dead')
        else:
            return self.__getHTMLString('normal' if isAliveAndIntoArena else 'normal_dead')

    def __getHTMLString(self, colorScheme):
        csManager = self.__parentUI.colorManager
        scheme = csManager.getScheme(colorScheme)
        makeRGB = csManager._makeRGB
        if self.__colorGroup in scheme:
            color = makeRGB(scheme[self.__colorGroup])
        elif csManager.DEFAULT_TAG in scheme:
            color = makeRGB(scheme[csManager.DEFAULT_TAG])
        else:
            LOG_ERROR('Current color scheme not found', scheme, self.__colorGroup)
            color = 0
        if color:
            result = "<font color='#{0:06x}'>%s</font><br/>".format(color)
        else:
            result = '<font>%s</font><br/>'
        return result
