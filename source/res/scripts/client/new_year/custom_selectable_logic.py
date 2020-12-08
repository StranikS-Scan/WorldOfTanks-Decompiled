# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/custom_selectable_logic.py
from HangarPoster import HangarPoster
from NewYearCelebrityEntryObject import NewYearCelebrityEntryObject
from NewYearCelebrityObject import NewYearCelebrityObject
from NewYearIcicleObject import NewYearIcicleObject
from NewYearIciclesIllumination import NewYearIciclesIllumination
from hangar_selectable_objects import HangarSelectableLogic
from PianoMusician import PianoMusician
from NewYearSelectableObject import NewYearSelectableObject
from NewYearTalismanEntryObject import NewYearTalismanEntryObject

class PianoSelectableLogic(HangarSelectableLogic):
    __slots__ = ()

    def _filterEntity(self, entity):
        return False if not isinstance(entity, PianoMusician) else super(PianoSelectableLogic, self)._filterEntity(entity)


class IciclesSelectableLogic(HangarSelectableLogic):
    __slots__ = ()

    def _filterEntity(self, entity):
        return False if not isinstance(entity, (NewYearIcicleObject, NewYearIciclesIllumination)) else super(IciclesSelectableLogic, self)._filterEntity(entity)


class WithoutNewYearObjectsSelectableLogic(HangarSelectableLogic):
    __slots__ = ()

    def _filterEntity(self, entity):
        if isinstance(entity, NewYearSelectableObject):
            return False
        if isinstance(entity, NewYearTalismanEntryObject):
            return False
        if isinstance(entity, (NewYearCelebrityObject, NewYearCelebrityEntryObject)):
            return False
        if isinstance(entity, PianoMusician):
            return False
        if isinstance(entity, (NewYearIcicleObject, NewYearIciclesIllumination)):
            return False
        return False if isinstance(entity, HangarPoster) else super(WithoutNewYearObjectsSelectableLogic, self)._filterEntity(entity)
