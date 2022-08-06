# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/types.py
import typing
from enum import Enum
FeatureType = typing.Union[str, Enum]
GroupType = typing.Union[str, Enum]
ActionType = typing.Union[str, Enum]
LogLevelType = typing.Union[int, Enum]
TimeLimitType = float
PartnerIdType = typing.Optional[str]
ItemType = typing.Union[str, Enum]
ItemStateType = typing.Optional[typing.Union[str, Enum]]
ParentScreenType = typing.Optional[typing.Union[str, Enum]]
InfoType = typing.Optional[typing.Union[str, Enum]]
SourceItemType = typing.Union[str, Enum]
DestinationItemType = typing.Union[str, Enum]
TransitionMethodType = typing.Union[str, Enum]
