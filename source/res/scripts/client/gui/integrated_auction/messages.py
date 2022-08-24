# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/integrated_auction/messages.py
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushRateErrorMessage(systemMessages=None):
    text = backport.text(R.strings.messenger.serviceChannelMessages.integratedAuction.rateError.text())
    systemMessages.pushMessage(text=text, type=SM_TYPE.IntegratedAuctionRateError)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushBelowCompetitiveRateMessage(systemMessages=None):
    text = backport.text(R.strings.messenger.serviceChannelMessages.integratedAuction.belowCompetitiveRate.text())
    systemMessages.pushMessage(text=text, type=SM_TYPE.IntegratedAuctionBelowCompetitiveRate)
