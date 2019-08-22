# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/royale_server_prime_time.py
from helpers import time_utils
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from predefined_hosts import g_preDefinedHosts
from skeletons.gui.game_control import IBattleRoyaleController

class RoyaleServerPrimeTime(ToolTipBaseData):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(RoyaleServerPrimeTime, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, peripheryID):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        serverName = ''
        for _, serverData in enumerate(hostsList):
            _, serverName, _, _, pID = serverData
            if pID == peripheryID:
                break

        timeLeftStr = '-'
        isNow = False
        primeTime = self.__battleRoyaleController.getPrimeTimes().get(peripheryID)
        if primeTime:
            currentCycleEnd = self.__battleRoyaleController.getCurrentSeason().getCycleEndDate()
            isNow, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), currentCycleEnd)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.battle_royale.tooltips.timeLeft)
        formattedTime = text_styles.neutral(timeLeftStr)
        descriptionID = R.strings.battle_royale.tooltips.server.unavailable.inTime()
        if isNow:
            descriptionID = R.strings.battle_royale.tooltips.server.available.untill()
        sName = text_styles.expText(backport.text(R.strings.battle_royale.tooltips.server.onServer(), server=serverName))
        description = text_styles.expText(backport.text(descriptionID, time=formattedTime))
        return {'body': '{}\n{}'.format(sName, description)}
