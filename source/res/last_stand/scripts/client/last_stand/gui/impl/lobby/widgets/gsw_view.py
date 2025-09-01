# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/gsw_view.py
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from last_stand.gui.impl.lobby.gsw_cards.key_card_presenter import KeyCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.reward_path_presenter import RewardPathCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.shop_card_presenter import ShopCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter

class GswPresenter(ViewComponent):

    def _initChildren(self):
        self._registerChild(R.aliases.last_stand.shared.Shop(), ShopCardPresenter())
        self._registerChild(R.aliases.last_stand.shared.Keys(), KeyCardPresenter())
        self._registerChild(R.aliases.last_stand.shared.RewardPath(), RewardPathCardPresenter())
        self._registerChild(R.aliases.last_stand.shared.Quests(), QuestsCardPresenter())
