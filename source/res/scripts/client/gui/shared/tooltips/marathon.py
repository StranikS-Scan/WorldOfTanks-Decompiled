# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/marathon.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_constants import MARATHON_STATE, MARATHON_WARNING
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController

class MarathonEventTooltipData(BlocksTooltipData):
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self, context):
        super(MarathonEventTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, bottom=3, left=1, right=1)
        self._setMargins(afterBlock=-1)
        self._setWidth(303)

    def _packBlocks(self, questType, prefix, *args, **kwargs):
        self._marathonEvent = self._marathonsCtrl.getMarathon(prefix)
        self.__tooltipData = self._marathonEvent.getTooltipData()
        self.__iconsData = self._marathonEvent.getIconsData()
        self.__isVehicleObtained = self._marathonEvent.isVehicleObtained()
        self.__isRewardObtained = self._marathonEvent.isRewardObtained()
        items = super(MarathonEventTooltipData, self)._packBlocks()
        state = self._marathonEvent.getState()
        items.append(self._getHeader(state))
        items.append(self._getBody(state))
        if state != MARATHON_STATE.NOT_STARTED and self._marathonEvent.data.showFlagTooltipBottom:
            items.append(self._getBottom(state))
        return items

    def _getHeader(self, _):
        icon, text = self._marathonEvent.getTooltipHeader()
        if icon:
            formattedText = '{}{}'.format(icons.makeImageTag(icon, width=32, height=32, vSpace=-10, hSpace=-10), text)
        else:
            formattedText = '{}'.format(text_styles.main(text))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self.__tooltipData.header)), img=self.__iconsData.tooltipHeader, imgPadding=formatters.packPadding(top=-1, left=1), txtPadding=formatters.packPadding(top=25), txtOffset=20, txtGap=-8, desc=formattedText, descPadding=formatters.packPadding(top=25, left=-8))

    def _getBody(self, state):
        if state == MARATHON_STATE.FINISHED:
            text = text_styles.main(backport.text(self.__tooltipData.bodyExtra, bonuses=text_styles.stats(backport.text(R.strings.tooltips.dday.bonuses())), day=self._marathonEvent.getExtraDaysToBuy()))
            return self.__getFormattedBody(text)
        if self.__isRewardObtained:
            text = text_styles.main(backport.text(R.strings.tooltips.dday.rewardsReceived.body(), bonuses=text_styles.stats(backport.text(R.strings.tooltips.dday.bonuses.capital()))))
            return self.__getFormattedBody(text)
        if self.__isVehicleObtained:
            text = text_styles.main(backport.text(R.strings.tooltips.dday.vehicleReceived.body(), bonuses=text_styles.stats(backport.text(R.strings.tooltips.dday.bonuses()))))
            return self.__getFormattedBody(text)
        text = text_styles.main(backport.text(R.strings.tooltips.dday.body(), bonuses=text_styles.stats(backport.text(R.strings.tooltips.dday.bonuses()))))
        return self.__getFormattedBody(text)

    def __getFormattedBody(self, text):
        return formatters.packTextBlockData(text=text, padding=formatters.packPadding(left=20, top=10, bottom=20, right=10))

    def _getBottom(self, state):
        vehicle = g_currentVehicle.item
        warning = self._marathonEvent.checkForWarnings(vehicle)
        if warning == MARATHON_WARNING.WRONG_BATTLE_TYPE:
            return self._getFooter(text_styles.critical(backport.text(self.__tooltipData.errorBattleType)))
        if warning == MARATHON_WARNING.WRONG_VEH_TYPE and state == MARATHON_STATE.IN_PROGRESS:
            return self._getFooter(text_styles.critical(backport.text(self.__tooltipData.errorVehType)))
        if self.__isRewardObtained:
            return self._getFooter(text_styles.bonusAppliedText(icons.makeImageTag(self.__iconsData.doubleOkIcon, width=32, height=32, vSpace=-10, hSpace=-10) + backport.text(self.__tooltipData.extraStateReward)))
        if self.__isVehicleObtained:
            return self._getFooter(text_styles.bonusAppliedText(icons.makeImageTag(self.__iconsData.okIcon, width=32, height=32, vSpace=-10, hSpace=-10) + backport.text(self.__tooltipData.extraStateVehicle)))
        currentStep, allStep = self._marathonEvent.getMarathonProgress()
        return self._getFooter(text_styles.middleTitle(backport.text(self.__tooltipData.extraStateSteps, currentStep=currentStep, allStep=text_styles.main(allStep)))) if allStep else None

    def _getFooter(self, message):
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': message}), padding=formatters.packPadding(bottom=20))


class MarathonBonusInfoTooltipData(BlocksTooltipData):
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self, context):
        super(MarathonBonusInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=1, bottom=3, left=1, right=1)
        self._setMargins(afterBlock=0)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        items = super(MarathonBonusInfoTooltipData, self)._packBlocks()
        self.__initialize()
        items.append(self._getHeader())
        items.append(self._getBonusesBlock())
        items.append(self._getBottom())
        return items

    def _getBonusesBlock(self):
        packer = formatters.packTextParameterWithManualIconBlockData
        bonusBlocks = [self._getBody(), packer(value=text_styles.stats(self.content['totalXP']), icon=self.content['totalXPIcon'], text=text_styles.main(self.content['totalXPLabel']), padding=formatters.packPadding(bottom=-5)), packer(value=text_styles.stats(self.content['tankmanXP']), icon=self.content['tankmanXPIcon'], text=text_styles.main(self.content['tankmanXPLabel']), padding=formatters.packPadding(bottom=-5))]
        return formatters.packBuildUpBlockData(blocks=bonusBlocks, padding=formatters.packPadding(bottom=8))

    def _getHeader(self):
        icon = self.content['timeIcon']
        text = self.content['headerEndTime']
        endDate = self.content['endDate']
        formattedText = '{}{} {}'.format(icons.makeImageTag(icon, width=32, height=32, vSpace=-10, hSpace=-10), text_styles.main(text), text_styles.stats(endDate))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(self.content['header']), img=self.content['headerBg'], imgPadding=formatters.packPadding(left=30), txtPadding=formatters.packPadding(top=25), txtOffset=20, txtGap=-8, desc=formattedText, descPadding=formatters.packPadding(top=25, left=-8))

    def _getBody(self):
        text = text_styles.main(backport.text(self.content['body'], name=text_styles.stats(self.content['marathonName'])))
        return formatters.packTextBlockData(text=text, padding=formatters.packPadding(left=19, bottom=14, right=28))

    def _getBottom(self):
        text = text_styles.middleTitle(backport.text(self.content['footerStr'], currentStep=text_styles.stats(self.content['completedDays']), allStep=text_styles.main(self.content['totalDays'])))
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': text}), padding=formatters.packPadding(bottom=10))

    def __getEndDate(self, finishDate):
        return backport.text(R.strings.tooltips.marathon.classicDate(), day='{:02d}'.format(finishDate.tm_mday), month='{:02d}'.format(finishDate.tm_mon), year='{:04d}'.format(finishDate.tm_year))

    def __initialize(self):
        marathon = self._marathonsCtrl.getPrimaryMarathon()
        data = marathon.data
        bonusData = marathon.getBonusData()
        currentStep, allSteps = marathon.getMarathonProgress()
        _, finishDateStruct = marathon.getGroupStartFinishDates()
        self.content = {'header': backport.text(R.strings.tooltips.dday.bonus.tooltip.header()),
         'headerBg': data.icons.tooltipHeader,
         'timeIcon': data.icons.timeIconGlow,
         'headerEndTime': backport.text(R.strings.tooltips.dday.bonus.tooltip.header.endTime()),
         'endDate': self.__getEndDate(finishDateStruct),
         'body': R.strings.tooltips.dday.bonus.tooltip.body(),
         'marathonName': backport.text(R.strings.tooltips.dday.bonus.tooltip.name()),
         'totalXP': bonusData['totalXP'],
         'tankmanXP': bonusData['tankmanXP'],
         'totalXPLabel': backport.text(R.strings.tooltips.dday.bonus.tooltip.totalXP()),
         'tankmanXPLabel': backport.text(R.strings.tooltips.dday.bonus.tooltip.tankmanXP()),
         'totalXPIcon': backport.image(R.images.gui.maps.icons.boosters.booster_xp_small_bw()),
         'tankmanXPIcon': backport.image(R.images.gui.maps.icons.boosters.booster_crew_xp_small_bw()),
         'footerStr': data.tooltips.extraStateSteps,
         'completedDays': currentStep,
         'totalDays': allSteps}
