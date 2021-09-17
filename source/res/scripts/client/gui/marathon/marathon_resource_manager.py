# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_resource_manager.py
import time
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_constants import MarathonState, R_TITLE_TOOLTIP, R_BUYING_PANEL, BUYING_BUTTON_ICON_ALIGN, MarathonFlagTooltip
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.time_utils import ONE_DAY, getTimeStructInLocal, ONE_HOUR
MarathonEventTooltipData = namedtuple('MarathonEventTooltipData', ('header', 'body', 'bodyExtra', 'bodyExtraSmart', 'errorBattleType', 'errorVehType', 'extraStateSteps', 'extraStateDiscount', 'extraStateCompleted', 'stateStart', 'stateEnd', 'stateProgress', 'stateComplete', 'daysShort', 'hoursShort', 'minutesShort', 'previewAnnounce', 'previewInProgress'))
MarathonEventIconsData = namedtuple('MarathonEventIconsData', ('tooltipHeader', 'okIcon', 'timeIcon', 'timeIconGlow', 'alertIcon', 'iconFlag', 'saleIcon', 'mapFlagHeaderIcon'))

class MarathonResourceManager(object):

    def __init__(self, dataContainer):
        self._data = dataContainer
        self._initialize()

    def getBuyBtnEnabledData(self, hasIgbLink):
        return {'enabled': True,
         'label': backport.text(R_BUYING_PANEL.buyBtn.label.buy()),
         'btnIcon': None if hasIgbLink else backport.image(R.images.gui.maps.icons.library.buyInWeb()),
         'btnIconAlign': BUYING_BUTTON_ICON_ALIGN,
         'btnTooltip': makeTooltip(body=backport.text(R_BUYING_PANEL.buyBtn.tooltip.active.body())),
         'customOffer': None}

    def getBuyBtnDiscountData(self, discount, hasIgbLink):
        discountText = text_styles.stats(backport.text(R_BUYING_PANEL.customOffer.discount()))
        discountValue = text_styles.promoTitle(backport.text(R.strings.quests.action.discount.percent(), value=backport.getIntegralFormat(discount)))
        return {'enabled': True,
         'label': backport.text(R_BUYING_PANEL.buyBtn.label.buyWithDiscount()),
         'btnIcon': None if hasIgbLink else backport.image(R.images.gui.maps.icons.library.buyInWeb()),
         'btnIconAlign': BUYING_BUTTON_ICON_ALIGN,
         'btnTooltip': makeTooltip(body=backport.text(R_BUYING_PANEL.buyBtn.tooltip.active.body())),
         'customOffer': ' '.join((discountText, discountValue))}

    def getBuyBtnDisabledData(self, hasIgbLink):
        questStartTime, _ = self._data.getQuestStartFinishTime()
        addInfo = backport.text(self._data.tooltips.previewAnnounce, marathonStartDate=text_styles.neutral(self._getDateTimeText(questStartTime)))
        tooltip = makeTooltip(header=backport.text(R_BUYING_PANEL.buyBtn.tooltip.inactive.header()), body=backport.text(R_BUYING_PANEL.buyBtn.tooltip.inactive.body(), addInfo=addInfo, event_name=backport.text(self._data.label)))
        return {'enabled': False,
         'label': backport.text(R_BUYING_PANEL.buyBtn.label.buy()),
         'btnIcon': None if hasIgbLink else backport.image(R.images.gui.maps.icons.library.buyInWeb()),
         'btnIconAlign': BUYING_BUTTON_ICON_ALIGN,
         'btnTooltip': tooltip,
         'customOffer': None}

    def getEmptyTooltip(self):
        return makeTooltip()

    def getExtraTimeToBuy(self):
        _, groupFinishTimeLeft = self._data.getGroupTimeInterval()
        gmtime = time.gmtime(groupFinishTimeLeft)
        if groupFinishTimeLeft >= ONE_DAY:
            text = backport.text(self._data.tooltips.daysShort, value=str(gmtime.tm_yday))
        elif groupFinishTimeLeft >= ONE_HOUR:
            text = backport.text(self._data.tooltips.hoursShort, value=str(gmtime.tm_hour + 1))
        else:
            text = backport.text(self._data.tooltips.minutesShort, value=str(gmtime.tm_min + 1))
        return text_styles.neutral(text)

    def getHangarFlagTooltip(self):
        return MarathonFlagTooltip.COUNTDOWN(self._data).create()

    def getTitleNotStartedTooltip(self):
        questStartTime, _ = self._data.getQuestStartFinishTime()
        tooltipBody = self._data.infoBody.announce()
        addInfo = backport.text(self._data.bodyAddInfo.announce(), addInfo=backport.text(self._data.tooltips.previewAnnounce, marathonStartDate=text_styles.neutral(self._getDateTimeText(questStartTime))))
        return self._getTitleMakeTooltip(tooltipBody, addInfo)

    def getTitleTooltip(self, finishSaleTime, discount):
        if discount:
            tooltipBody = self._data.infoBody.progress.withDiscount()
        else:
            tooltipBody = self._data.infoBody.progress()
        addInfo = backport.text(self._data.bodyAddInfo.progress(), endVehicleSellDate=text_styles.neutral(self._getDateTimeText(finishSaleTime)), addInfo=backport.text(self._data.tooltips.previewInProgress))
        return self._getTitleMakeTooltip(tooltipBody, addInfo)

    def _initialize(self):
        marathonBody = R_TITLE_TOOLTIP.info.dyn(self._data.prefix)
        self._data.infoBody = marathonBody.body if marathonBody.isValid() else R_TITLE_TOOLTIP.info.body
        self._data.label = self._getLabelObject(R.strings.quests.missions.tab.label)()
        self._data.backBtnLabel = self._getLabelObject(R.strings.vehicle_preview.header.backBtn.descrLabel)()
        self._data.tooltips = self._getTooltips()
        self._data.icons = self._getIcons()

    def getHangarFlag(self):
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.dyn(self._data.hangarFlagName)())

    def _getDateTimeText(self, timestamp):
        localDateTime = getTimeStructInLocal(timestamp)
        monthName = backport.text(R.strings.menu.dateTime.months.dyn('c_{}'.format(localDateTime.tm_mon))())
        dateTimeText = backport.text(R.strings.marathon.vehiclePreview.tooltip.dateTime(), day=localDateTime.tm_mday, monthName=monthName, year=localDateTime.tm_year, hour=localDateTime.tm_hour, min='{min:02d}'.format(min=localDateTime.tm_min))
        return dateTimeText.replace(' ', '&nbsp;')

    def _getTitleMakeTooltip(self, tooltipBody, addInfo):
        label = backport.text(self._data.label)
        return makeTooltip(header=backport.text(R.strings.marathon.vehiclePreview.title.tooltip.header(), event_name=label), body=backport.text(tooltipBody, event_name=label, addInfo=addInfo))

    def _getTooltips(self):
        body = self._getTooltipString('body')
        error = self._getTooltipString('error')
        state = self._getTooltipString('state')
        extraState = self._getTooltipString('extra_state')
        return MarathonEventTooltipData(header=self._getTooltipString('header')(), body=body(), bodyExtra=body.extra(), bodyExtraSmart=body.extra_smart(), errorBattleType=error.battle_type(), errorVehType=error.veh_type(), extraStateSteps=extraState.steps(), extraStateDiscount=extraState.discount(), extraStateCompleted=extraState.completed(), stateStart=state.start(), stateEnd=state.end(), stateProgress=extraState(), stateComplete=state.complete(), daysShort=R.strings.tooltips.template.days.short(), hoursShort=R.strings.tooltips.template.hours.short(), minutesShort=R.strings.tooltips.template.minutes.short(), previewAnnounce=self._getVehiclePreviewBodyString('announce')(), previewInProgress=self._getVehiclePreviewBodyString('inprogress')())

    def _getIcons(self):
        return MarathonEventIconsData(tooltipHeader=backport.image(R.images.gui.maps.icons.quests.dyn(self._data.marathonTooltipHeader)()), okIcon=backport.image(self._getIconsResource('ok_icon')()), timeIcon=backport.image(self._getIconsResource('time_icon')()), timeIconGlow=backport.image(self._getIconsResource('time_icon_glow')()), alertIcon=backport.image(self._getIconsResource('alert_icon')()), iconFlag=backport.image(self._getIconsResource('icon_flag')()), saleIcon=backport.image(self._getIconsResource('sale_icon')()), mapFlagHeaderIcon={MarathonState.ENABLED_STATE: backport.image(self._getIconsResource('cup_icon')()),
         MarathonState.DISABLED_STATE: backport.image(self._getIconsResource('cup_disable_icon')())})

    def _getLabelObject(self, obj):
        resourceObj = obj.dyn(self._data.prefix)
        return resourceObj if resourceObj.isValid() else obj.marathon

    def _getResouce(self, obj, attr):
        resourceObj = obj.dyn(self._data.prefix)
        if resourceObj.isValid():
            string = resourceObj.dyn(attr)
            if string.isValid():
                return string
        return obj.marathon.dyn(attr)

    def _getTooltipString(self, attr):
        return self._getResouce(R.strings.tooltips, attr)

    def _getVehiclePreviewBodyString(self, attr):
        return self._getResouce(R.strings.marathon.vehiclePreview.title.tooltip.body, attr)

    def _getIconsResource(self, attr):
        return self._getResouce(R.images.gui.maps.icons.library, attr)
