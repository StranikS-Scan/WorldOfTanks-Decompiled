# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/currency_packers.py
import logging
import typing
from collections import namedtuple
from soft_exception import SoftException
from shared_utils import first
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.battle_results.presenters.packers.interfaces import ICurrencyPacker
from gui.impl.gen.view_models.views.lobby.battle_results.currency_record_model import CurrencyRecordModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_details_model import CurrencyRecordsItemDetailsModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
if typing.TYPE_CHECKING:
    from typing import List, Any, Tuple
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.pbs_helpers.economics import FinancialRecordValues
    from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_model import CurrencyRecordsModel
_logger = logging.getLogger(__name__)
CurrencyRecord = namedtuple('CurrencyRecord', ('recordNames', 'subtractRecords', 'baseAccountValueExtractor', 'premiumAccountValueExtractor', 'detailsValuesExtractors', 'capsToBeChecked', 'paramName', 'label', 'modifiers', 'showZeroValue', 'currencyType'))
CurrencyGroup = namedtuple('CurrencyGroup', ('label', 'records'))

class CurrencyPacker(ICurrencyPacker):
    _EARNED = None
    _EXPENSES = None
    _TOTAL = None
    _ADDITIONAL = None
    _EXTRACTORS = {}

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        recordsExtractors, recordsConfigsExtractor = cls._getExtractors(currencyType, battleResults)
        if recordsExtractors is None or recordsConfigsExtractor is None:
            _logger.error('Invalid currency data')
            return
        else:
            records = [ extractor(battleResults.reusable) for extractor in recordsExtractors ]
            cls._packGroup(model.earned, records, battleResults, recordsConfigsExtractor, cls._getEarnedConfig(battleResults))
            cls._packGroup(model.expenses, records, battleResults, recordsConfigsExtractor, cls._EXPENSES)
            cls._packGroup(model.total, records, battleResults, recordsConfigsExtractor, cls._TOTAL)
            cls._packGroup(model.additional, records, battleResults, recordsConfigsExtractor, cls._ADDITIONAL)
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
            recordModel = cls._createRecordModel(battleResults, records, configs)
            if recordModel is not None:
                recordsModel.addViewModel(recordModel)

        recordsModel.invalidate()
        return

    @classmethod
    def _createRecordModel(cls, battleResults, records, configs):
        values = cls._getValues(battleResults, records, configs)
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
    def _packGroup(cls, model, records, battleResults, recordsConfigsExtractor, sourceConfig):
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
    def _getValues(battleResults, records, configs):
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
            value = None
            if battleResults.reusable.personal.hasAnyPremium:
                valueExtractor = currencyConfig.premiumAccountValueExtractor
                if valueExtractor:
                    value = valueExtractor(currencyRecords, currencyConfig, battleResults)
            else:
                valueExtractor = currencyConfig.baseAccountValueExtractor
                if valueExtractor:
                    value = valueExtractor(currencyRecords, currencyConfig, battleResults)
            if value or value == 0 and currencyConfig.showZeroValue:
                values.append(value)
            values.append(None)

        return values


class DetailedCurrencyPacker(ICurrencyPacker):
    _EARNED = None
    _EXPENSES = None
    _TOTAL = None
    _EXTRACTORS = {}

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        recordsExtractors, recordsConfigsExtractor = cls._getExtractors(battleResults)
        if recordsExtractors is None or recordsConfigsExtractor is None:
            raise SoftException('Invalid currency data')
        records = [ extractor(battleResults.reusable) for extractor in recordsExtractors ]
        cls._packGroup(model.getEarned(), records, battleResults, recordsConfigsExtractor, cls._EARNED)
        cls._packGroup(model.getExpenses(), records, battleResults, recordsConfigsExtractor, cls._EXPENSES)
        cls._packGroup(model.getTotal(), records, battleResults, recordsConfigsExtractor, cls._TOTAL)
        return

    @classmethod
    def _getExtractors(cls, battleResults):
        raise NotImplementedError

    @classmethod
    def _packGroup(cls, model, records, battleResults, recordsConfigsExtractor, sourceConfig):
        if sourceConfig is None:
            return
        else:
            recordsConfigs = recordsConfigsExtractor(sourceConfig)
            if not recordsConfigs:
                raise SoftException('Invalid config data for currency')
            cls._fillRecords(model, battleResults, records, recordsConfigs)
            return

    @classmethod
    def _fillRecords(cls, recordsModel, battleResults, records, recordsConfigs):
        recordsModel.clear()
        for configs in recordsConfigs:
            if not any(configs):
                continue
            for record, config in zip(records, configs):
                if not config:
                    continue
                recordModel = cls._createRecordModel(battleResults, record, config)
                recordsModel.addViewModel(recordModel)

        recordsModel.invalidate()

    @classmethod
    def _createRecordModel(cls, battleResults, record, config):
        baseAccountValue, premiumAccountValue = cls._getValues(battleResults, record, config)
        recordModel = CurrencyRecordsItemModel()
        recordModel.setBaseValue(baseAccountValue if baseAccountValue is not None else 0)
        recordModel.setPremiumValue(premiumAccountValue if premiumAccountValue is not None else 0)
        recordModel.setParamName(config.paramName)
        recordModel.setCurrencyType(config.currencyType)
        if config.detailsValuesExtractors:
            cls._packAdditionalValues(recordModel.getDetailedItemRecords(), battleResults, config)
        return recordModel

    @staticmethod
    def _getValues(battleResults, record, config):
        commonInfo = battleResults.reusable.common
        baseAccountValue = None
        premiumAccountValue = None
        if config is None:
            return (baseAccountValue, premiumAccountValue)
        else:
            capsToBeChecked = config.capsToBeChecked
            isRecordAvailable = commonInfo.checkBonusCaps(capsToBeChecked) if capsToBeChecked else True
            if not isRecordAvailable:
                return (baseAccountValue, premiumAccountValue)
            valueExtractor = config.baseAccountValueExtractor
            if valueExtractor:
                value = valueExtractor(record, config, battleResults)
                if value:
                    baseAccountValue = value
            valueExtractor = config.premiumAccountValueExtractor
            if valueExtractor:
                value = valueExtractor(record, config, battleResults)
                if value:
                    premiumAccountValue = value
            return (baseAccountValue, premiumAccountValue)

    @staticmethod
    def _packAdditionalValues(model, battleResults, config):
        model.clear()
        for extractor in config.detailsValuesExtractors:
            detailsModel = CurrencyRecordsItemDetailsModel()
            param, value = extractor(battleResults)
            detailsModel.setItemName(param)
            detailsModel.setItemValue(str(value))
            model.addViewModel(detailsModel)

        model.invalidate()
