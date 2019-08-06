# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/festival_marathon.py
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_event_dp import MarathonEvent, MarathonEventTooltipData, MarathonEventIconsData
from gui.shared.formatters import text_styles

class FestivalMarathon(MarathonEvent):

    @property
    def tokenPrefix(self):
        pass

    @property
    def urlName(self):
        pass

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.festivalMarathon()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_FESTIVALMARATHON

    @property
    def tabTooltipDisabled(self):
        return QUESTS.MISSIONS_TAB_FESTIVALMARATHON

    @property
    def vehiclePrefix(self):
        pass

    @property
    def vehicleID(self):
        pass

    @property
    def awardTokens(self):
        pass

    @property
    def questsInChain(self):
        pass

    @property
    def minVehicleLevel(self):
        pass

    @property
    def tooltips(self):
        tooltips = super(FestivalMarathon, self).tooltips._asdict()
        tooltips.update({'header': R.strings.tooltips.festivalMarathon.header(),
         'body': self.__getFormattedFlagTooltipBody(),
         'errorVehType': R.strings.tooltips.festivalMarathon.error.veh_type(),
         'extraStateSteps': R.strings.tooltips.festivalMarathon.extra_state.steps(),
         'extraStateCompleted': R.strings.tooltips.festivalMarathon.extra_state.completed()})
        return MarathonEventTooltipData(**tooltips)

    @property
    def icons(self):
        icons = super(FestivalMarathon, self).icons._asdict()
        icons.update({'tooltipHeader': backport.image(R.images.gui.maps.icons.quests.festivalMarathonHeader())})
        return MarathonEventIconsData(**icons)

    def getHangarFlag(self, state=None):
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_czech())

    def doesShowRewardVideo(self):
        return False

    def doesShowMissionsTab(self):
        return self.isEnabled()

    def __getFormattedFlagTooltipBody(self):
        vehicleText = text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.vehicle()))
        bodyText = backport.text(R.strings.tooltips.festivalMarathon.body(), levels=text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.levels())), vehicle=vehicleText, style=text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.style(), vehicle=vehicleText)))
        return bodyText
