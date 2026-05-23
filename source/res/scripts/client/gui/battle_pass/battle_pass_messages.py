# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_messages.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from messenger import g_settings
from battle_pass_common import isBattlePassPassToken

def getBattlePassBuyShopFormattedMsg(data):
    _template = 'battlePassBuyShopInvoiceReceived'
    tags = data.get('tags', ())
    if 'battlePassBuyChapter' in tags:
        chaptersNames = []
        dataEx = data.get('data', {})
        for tokenName in dataEx.get('tokens', {}).iterkeys():
            if isBattlePassPassToken(tokenName):
                chapterID = int(tokenName.split(':')[-1])
                chaptersNames.append(text_styles.credits(backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)())))

        if chaptersNames:
            chapterInBundle = 'several' if len(chaptersNames) > 1 else 'single'
            return (_template, g_settings.msgTemplates.format(_template, ctx={'header': backport.text(R.strings.battle_pass.ingameShop.notification.title()),
              'description': backport.text(R.strings.battle_pass.ingameShop.notification.dyn(chapterInBundle).description(), chapter=', '.join(chaptersNames))}))
    return (None, None)
