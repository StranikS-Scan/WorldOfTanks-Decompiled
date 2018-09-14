# Embedded file name: scripts/client/gui/miniclient/lobby/header/battle_type_selector/__init__.py
import pointcuts as _pointcuts

def configure_pointcuts():
    _pointcuts.CommandBattle()
    _pointcuts.SortieBattle()
    _pointcuts.TrainingBattle()
    _pointcuts.SpecialBattle()
    _pointcuts.CompanyBattle()
    _pointcuts.FalloutBattle()
    _pointcuts.OnBattleTypeSelectorPopulate()
