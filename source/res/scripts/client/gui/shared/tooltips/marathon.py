# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/marathon.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.impl import backport
from gui.marathon.marathon_constants import MarathonState, MarathonWarning
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
        self.__tooltipData = self._marathonEvent.tooltips
        self.__iconsData = self._marathonEvent.icons
        items = super(MarathonEventTooltipData, self)._packBlocks()
        state = self._marathonEvent.getState()
        items.append(self._getHeader(state))
        items.append(self._getBody(state))
        if state != MarathonState.NOT_STARTED and self._marathonEvent.showFlagTooltipBottom:
            items.append(self._getBottom(state))
        return items

    def _getHeader(self, _):
        icon, text = self._marathonEvent.getTooltipHeader()
        if icon:
            formattedText = '{}{}'.format(icons.makeImageTag(icon, width=32, height=32, vSpace=-10, hSpace=-10), text_styles.main(text))
        else:
            formattedText = '{}'.format(text_styles.main(text))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self.__tooltipData.header)), img=self.__iconsData.tooltipHeader, imgPadding=formatters.packPadding(top=-1, left=1), txtPadding=formatters.packPadding(top=25), txtOffset=20, txtGap=-8, desc=formattedText, descPadding=formatters.packPadding(top=25, left=-8))

    def _getBody(self, state):
        if state == MarathonState.FINISHED:
            if self._marathonEvent.isRewardObtained():
                text = text_styles.main(backport.text(self.__tooltipData.bodyExtraSmart))
            else:
                text = text_styles.main(backport.text(self.__tooltipData.bodyExtra, hours=self._marathonEvent.getExtraTimeToBuy()))
        else:
            text = text_styles.main(backport.text(self.__tooltipData.body))
        return formatters.packTextBlockData(text=text, padding=formatters.packPadding(left=20, top=10, bottom=20, right=10))

    def _getBottom(self, state):
        vehicle = g_currentVehicle.item
        isObtained = self._marathonEvent.isRewardObtained()
        if isObtained:
            statusLabel = text_styles.bonusAppliedText(icons.makeImageTag(self.__iconsData.okIcon, width=32, height=32, vSpace=-10, hSpace=-10) + backport.text(self.__tooltipData.extraStateCompleted))
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': statusLabel}), padding=formatters.packPadding(bottom=20))
        if state == MarathonState.IN_PROGRESS:
            warning = self._marathonEvent.checkForWarnings(vehicle)
            if warning == MarathonWarning.WRONG_BATTLE_TYPE:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.critical(backport.text(self.__tooltipData.errorBattleType))}), padding=formatters.packPadding(bottom=20))
            if warning == MarathonWarning.WRONG_VEH_TYPE:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.critical(backport.text(self.__tooltipData.errorVehType))}), padding=formatters.packPadding(bottom=20))
            currentStep, allStep = self._marathonEvent.getMarathonProgress()
            if allStep:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.middleTitle(backport.text(self.__tooltipData.extraStateSteps, currentStep=currentStep, allStep=text_styles.main(allStep)))}), padding=formatters.packPadding(bottom=20))
        else:
            discount = self._marathonEvent.getMarathonDiscount()
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': text_styles.bonusPreviewText(backport.text(self.__tooltipData.extraStateDiscount, discount=discount))}), padding=formatters.packPadding(bottom=20))
