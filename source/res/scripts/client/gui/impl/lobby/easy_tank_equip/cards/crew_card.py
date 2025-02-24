# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/cards/crew_card.py
import typing
import nations
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.crew_preset_model import CrewPresetModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setTmanSkillsModel
from gui.impl.lobby.easy_tank_equip.cards.base_card import BaseCard, BasePreset
if typing.TYPE_CHECKING:
    from gui.impl.lobby.easy_tank_equip.data_providers.crew_data_provider import CrewPresetInfo
    from gui.shared.money import Money
    from typing import Optional

class CrewCard(BaseCard):

    def _getPreset(self):
        return CrewPreset

    def _onPricesUpdated(self, balance):
        pass


class CrewPreset(BasePreset):

    @classmethod
    def getPresetModel(cls):
        return CrewPresetModel()

    @classmethod
    def fillPresetModel(cls, model, presetInfo, balance=None):
        super(CrewPreset, cls).fillPresetModel(model, presetInfo, balance)
        model.setType(presetInfo.presetType)
        model.setRecruitsCount(presetInfo.recruitsCount)
        cls.__fillPresetTankmenModel(model, presetInfo)

    @classmethod
    def __fillPresetTankmenModel(cls, model, presetInfo):
        tankmenModels = model.getTankmen()
        tankmanModel = model.getTankmenType()
        tankmenModels.clear()
        for tankmanIndex, tankman in enumerate(presetInfo.tankmen):
            if tankman is not None:
                tm = tankmanModel()
                setTankmanModel(tm, tankman, tmanNativeVeh=presetInfo.tankmenNativeVeh[tankmanIndex])
                setTmanSkillsModel(tm.skills, tankman, fillBonusSkills=True)
                tm.setNation(nations.NAMES[tankman.nationID])
                tankmenModels.addViewModel(tm)

        tankmenModels.invalidate()
        return
