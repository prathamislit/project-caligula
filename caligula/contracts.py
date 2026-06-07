"""Canonical data contracts for the Caligula pipeline."""

from dataclasses import dataclass
from typing import Dict
import datetime


@dataclass
class FilingRecord:
    ticker: str
    fiscal_year: int
    fiscal_period: str
    filing_type: str
    accession_number: str
    filing_date: datetime.date
    accepted_datetime: datetime.datetime
    source_url: str


@dataclass
class ExtractionRecord:
    extraction_id: str
    ticker: str
    fiscal_year: int
    filing_type: str
    accession_number: str
    filing_date: datetime.date
    accepted_datetime: datetime.datetime
    source_url: str
    source_section: str
    metric_name: str
    extracted_value: float
    reported_unit: str
    normalized_value: float
    normalized_unit: str
    raw_extracted_text: str
    model_name: str
    prompt_version: str
    confidence_score: float
    human_reviewed: bool
    human_override: bool
    validation_status: str
    audit_hash: str


@dataclass
class ReserveRecord:
    reserve_record_id: str
    ticker: str
    fiscal_year: int
    filing_type: str
    accession_number: str
    filing_date: datetime.date
    period_end_date: datetime.date
    commodity: str
    basin: str
    reserve_category: str
    measure_type: str
    value: float
    unit: str
    normalized_value: float
    normalized_unit: str
    source_extraction_id: str
    source_table: str
    source_page: str
    audit_hash: str


@dataclass
class HedgeRecord:
    ticker: str
    fiscal_year: int
    pct_oil_hedged_ntm: float
    weighted_floor: float
    swap_pct: float
    collar_pct: float
    put_pct: float


@dataclass
class PillarInputRecord:
    ticker: str
    quarter: datetime.date
    metrics: Dict[str, float]


@dataclass
class PillarScoreRecord:
    ticker: str
    quarter: datetime.date
    pillar: str
    score: float
    weight: float


@dataclass
class CompositeScoreRecord:
    ticker: str
    quarter: datetime.date
    caligula_score: float
    rank: int
    tier: str


@dataclass
class UniverseMemberRecord:
    universe_version: str
    as_of_date: datetime.date
    rebalance_quarter: datetime.date
    ticker: str
    company_name: str
    eligible: bool
    inclusion_reason: str
    exclusion_reason: str


@dataclass
class BacktestHoldingRecord:
    run_id: str
    as_of_date: datetime.date
    ticker: str
    weight: float
    bucket: str
    execution_price: float


@dataclass
class BacktestReturnRecord:
    run_id: str
    start_date: datetime.date
    end_date: datetime.date
    ticker: str
    holding_period_return: float


@dataclass
class PerformanceMetricRecord:
    run_id: str
    metric_name: str
    value: float
    unit: str


@dataclass
class DCFInputRecord:
    ticker: str
    valuation_date: datetime.date
    wacc: float
    shares_outstanding: float
    net_debt: float
    current_price: float


@dataclass
class DCFOutputRecord:
    ticker: str
    valuation_date: datetime.date
    intrinsic_price_reserve_life: float
    intrinsic_price_exit_multiple: float
    implied_upside: float
    recommendation: str
