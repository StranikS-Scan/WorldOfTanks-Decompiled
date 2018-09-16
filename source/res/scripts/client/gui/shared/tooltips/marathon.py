# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/marathon.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.marathon.marathon_constants import MARATHON_STATE, MARATHON_WARNING
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IMarathonEventController

class MarathonEventTooltipData(BlocksTooltipData):
    _marathonCtrl = dependency.descriptor(IMarathonEventController)

    def __init__(self, context):
        super(MarathonEventTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, bottom=3, left=1, right=1)
        self._setMargins(afterBlock=0)
        self._setWidth(297)

    def _packBlocks(self, *args, **kwargs):
        items = super(MarathonEventTooltipData, self)._packBlocks()
        state = self._marathonCtrl.getState()
        items.append(self._getHeader(state))
        items.append(self._getBody(state))
        if state != MARATHON_STATE.NOT_STARTED:
            items.append(self._getBottom(state))
        return items

    def _getHeader(self, _):
        icon, text = self._marathonCtrl.getFormattedRemainingTime()
        formattedText = '{} {}'.format(icons.makeImageTag(icon, width=16, height=16), text_styles.main(text))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(_ms(TOOLTIPS.MARATHON_HEADER)), img=RES_ICONS.MAPS_ICONS_QUESTS_MARATHONTOOLTIPHEADER, txtPadding=formatters.packPadding(top=25), txtOffset=20, txtGap=-8, desc=formattedText)

    def _getBody(self, state):
        if state == MARATHON_STATE.FINISHED:
            text = text_styles.main(_ms(TOOLTIPS.MARATHON_BODY_EXTRA, day=self._marathonCtrl.getExtraDaysToBuy()))
        else:
            text = text_styles.main(TOOLTIPS.MARATHON_BODY)
        return formatters.packTextBlockData(text=text, padding=formatters.packPadding(left=20, top=10, bottom=20, right=10))

    def _getBottom(self, state):
        vehicle = g_currentVehicle.item
        isObtained = self._marathonCtrl.isVehicleObtained()
        if isObtained:
            statusLabel = text_styles.bonusAppliedText(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, vSpace=-2) + ' ' + _ms(TOOLTIPS.MARATHON_EXTRA_STATE_COMPLETED))
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': statusLabel}), padding=formatters.packPadding(bottom=20))
        if state == MARATHON_STATE.IN_PROGRESS:
            warning = self._marathonCtrl.checkForWarnings(vehicle)
            if warning == MARATHON_WARNING.WRONG_BATTLE_TYPE:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.critical(_ms(TOOLTIPS.MARATHON_ERROR_BATTLE_TYPE))}), padding=formatters.packPadding(bottom=20))
            if warning == MARATHON_WARNING.WRONG_VEH_TYPE:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.critical(_ms(TOOLTIPS.MARATHON_ERROR_VEH_TYPE))}), padding=formatters.packPadding(bottom=20))
            currentStep, allStep = self._marathonCtrl.getMarathonProgress()
            if allStep:
                return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                 'message': text_styles.middleTitle(_ms(TOOLTIPS.MARATHON_EXTRA_STATE_STEPS, currentStep=currentStep, allStep=text_styles.main(allStep)))}), padding=formatters.packPadding(bottom=20))
        else:
            discount = self._marathonCtrl.getMarathonDiscount()
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': text_styles.bonusPreviewText(_ms(TOOLTIPS.MARATHON_EXTRA_STATE_DISCOUNT, discount=discount))}), padding=formatters.packPadding(bottom=20))
