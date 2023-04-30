# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_token_popover.py
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.MissionsTokenPopoverMeta import MissionsTokenPopoverMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.server_events.events_dispatcher import showMissionDetails
from gui.server_events.events_helpers import missionsSortFunc
from gui.server_events.formatters import TOKEN_SIZES
from gui.shared import events
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as ms
from skeletons.gui.server_events import IEventsCache

class MissionsTokenPopover(MissionsTokenPopoverMeta):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx=None):
        super(MissionsTokenPopover, self).__init__()
        data = ctx.get('data')
        self._tokenId = data.tokenId
        self._questId = data.questId
        self._token = None
        return

    def onBuyBtnClick(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.TOKEN_SHOP, params={'name': self._token.getWebID()}))
        self.destroy()

    def onQuestClick(self, questID):
        quest = self.eventsCache.getQuests()[questID]
        showMissionDetails(quest.getID(), quest.getGroupID())
        self.destroy()

    def _populate(self):
        super(MissionsTokenPopover, self)._populate()
        mainQuest = self.eventsCache.getQuests()[self._questId]
        children = mainQuest.getChildren()[self._tokenId]

        def filterfunc(quest):
            return quest.getGroupID() == mainQuest.getGroupID() and quest.getID() in children

        quests = self.eventsCache.getQuests(filterfunc)
        for token in mainQuest.accountReqs.getTokens():
            if token.getID() == self._tokenId:
                self._token = token
                break

        result = []
        for quest in sorted(quests.values(), key=missionsSortFunc, reverse=True):
            header = text_styles.main(quest.getUserName())
            if quest.isCompleted():
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK
                descr = text_styles.bonusAppliedText(QUESTS.MISSIONS_TOKENPOPOVER_QUEST_DESCR_READY)
            elif not quest.isAvailable()[0]:
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_NOTAVAILABLEICON
                descr = text_styles.error(QUESTS.MISSIONS_TOKENPOPOVER_QUEST_DESCR_NOTAVAILABLE)
            else:
                icon = ''
                descr = text_styles.standard(ms(QUESTS.MISSIONS_TOKENPOPOVER_QUEST_DESCR_DATE, date=backport.getLongDateFormat(quest.getFinishTime())))
            tooltip = makeTooltip(ms(TOOLTIPS.MISSIONS_TOKENPOPOVER_QUEST_HEADER, name=quest.getUserName()), ms(TOOLTIPS.MISSIONS_TOKENPOPOVER_QUEST_BODY))
            result.append({'headerText': header,
             'descrText': descr,
             'imgSrc': icon,
             'questId': quest.getID(),
             'tooltip': tooltip})

        self.as_setListDataProviderS(result)
        buyBtnVisible = self._token.isOnSale() or mainQuest.isTokensOnSale()
        if buyBtnVisible:
            descrText = ms(QUESTS.MISSIONS_TOKENPOPOVER_DESCR_SHOP, name=text_styles.neutral(ms(self._token.getUserName())))
        else:
            descrText = ms(QUESTS.MISSIONS_TOKENPOPOVER_DESCR, name=text_styles.neutral(ms(self._token.getUserName())))
        if not GUI_SETTINGS.tokenShopURL:
            buyBtnVisible = False
        self.as_setStaticDataS({'headerText': text_styles.highTitle(ms(QUESTS.MISSIONS_TOKENPOPOVER_HEADER, name=ms(self._token.getUserName()))),
         'descrText': text_styles.main(descrText),
         'imageSrc': self._token.getImage(TOKEN_SIZES.MEDIUM),
         'buyBtnLabel': QUESTS.MISSIONS_TOKENPOPOVER_BUYBTN_LABEL,
         'buyBtnVisible': buyBtnVisible})
