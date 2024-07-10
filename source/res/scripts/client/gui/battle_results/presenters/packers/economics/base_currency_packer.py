# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/base_currency_packer.py
from collections import namedtuple
import logging
import typing
from frameworks.wulf.view.array import fillStringsArray
from gui.battle_results.presenters.packers.interfaces import ICurrencyPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_record_model import CurrencyRecordModel
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.battle_results.financial_details_model import FinancialDetailsModel
    from gui.battle_results.stats_ctrl import BattleResults
_logger = logging.getLogger(__name__)
CurrencyRecord = namedtuple('CurrencyRecord', ('recordNames', 'subtractRecords', 'valueExtractor', 'capsToBeChecked', 'label', 'modifiers', 'showZeroValue', 'currencyType'))
CurrencyGroup = namedtuple('CurrencyGroup', ('label', 'records'))

class BaseCurrencyPacker(ICurrencyPacker):
    __slots__ = ()
    _EARNED = None
    _EXPENSES = None
    _TOTAL = None
    _ADDITIONAL = None
    _EXTRACTORS = {}

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        recordsExtractors, recordsConfigsExtractor = cls._getExtractors(currencyType, battleResults)
        if recordsExtractors is None or recordsConfigsExtractor is None:
            _logger.error('Invalid data for currency tooltip')
            return
        else:
            records = [ extractor(battleResults.reusable) for extractor in recordsExtractors ]
            cls.__packGroup(model.earned, records, battleResults, recordsConfigsExtractor, cls._getEarnedConfig(battleResults))
            cls.__packGroup(model.expenses, records, battleResults, recordsConfigsExtractor, cls._EXPENSES)
            cls.__packGroup(model.total, records, battleResults, recordsConfigsExtractor, cls._TOTAL)
            cls.__packGroup(model.additional, records, battleResults, recordsConfigsExtractor, cls._ADDITIONAL)
            return

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        raise NotImplementedError

    @classmethod
    def _getEarnedConfig(cls, battleResults):
        return cls._EARNED

    @classmethod
    def _fillRecords(cls, recordsModel, battleResults, records, recordsConfigs):
        recordsModel.clear()
        for configs in recordsConfigs:
            if not any(configs):
                continue
            recordModel = cls.__createRecordModel(battleResults, records, configs)
            if recordModel is not None:
                recordsModel.addViewModel(recordModel)

        recordsModel.invalidate()
        return

    @classmethod
    def __createRecordModel(cls, battleResults, records, configs):
        values = cls.__getValues(battleResults, records, configs)
        if not any((v is not None for v in values)):
            return
        else:
            recordModel = CurrencyRecordModel()
            for valueModel, config, value in zip((recordModel.firstValue, recordModel.secondValue), configs, values):
                cls.__packValueModel(valueModel, config, value)

            labelRes = first(configs).label
            recordModel.setLabel(labelRes() if labelRes is not None else R.invalid())
            return recordModel

    @classmethod
    def __packGroup(cls, model, records, battleResults, recordsConfigsExtractor, sourceConfig):
        if sourceConfig is None:
            return
        else:
            recordsConfigs = recordsConfigsExtractor(sourceConfig.records)
            if not recordsConfigs:
                _logger.error('Invalid config data for currency tooltip')
                return
            model.setUseSecondValues(len(first(recordsConfigs)) > 1)
            title = sourceConfig.label
            model.setTitle(title() if title is not None else R.invalid())
            cls._fillRecords(model.getRecords(), battleResults, records, recordsConfigs)
            return

    @staticmethod
    def __packValueModel(valueModel, recordConfig, value):
        valueModel.setIsShown(value is not None)
        valueModel.setValue(value if value is not None else 0)
        if recordConfig is not None:
            valueModel.setCurrencyType(recordConfig.currencyType)
            fillStringsArray([ r.value for r in recordConfig.modifiers ], valueModel.getModifiers())
        return

    @staticmethod
    def __getValues(battleResults, records, configs):
        commonInfo = battleResults.reusable.common
        values = []
        for currencyRecords, currencyConfig in zip(records, configs):
            if currencyConfig is None:
                values.append(None)
                continue
            capsToBeChecked = currencyConfig.capsToBeChecked
            isRecordAvailable = commonInfo.checkBonusCaps(capsToBeChecked) if capsToBeChecked else True
            if not isRecordAvailable:
                values.append(None)
                continue
            valueExtractor = currencyConfig.valueExtractor
            value = valueExtractor(currencyRecords, currencyConfig, battleResults)
            if value or value == 0 and currencyConfig.showZeroValue:
                values.append(value)
            values.append(None)

        return values
