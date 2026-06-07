.PHONY: setup lint test run-scans run-pipeline run-valuation all

setup:
	pip install -r requirements.txt
	mkdir -p data/audit data/raw data/interim data/processed data/ledgers
	mkdir -p outputs/tables outputs/charts outputs/memos outputs/website

lint:
	black caligula tests
	flake8 caligula tests

test:
	pytest tests/ -v

run-scans:
	python -m caligula.validation.inventory_scan
	python -m caligula.validation.no_stub_scan

run-pipeline:
	python generate_proof_ledgers.py
	python -m caligula.scoring.rankings
	python -m caligula.backtest.universe
	python -m caligula.backtest.performance_ledger
	python -m caligula.backtest.audit_example
	python -m caligula.exports.website_public

run-valuation:
	python -m caligula.valuation.eog_dcf

all: lint test run-scans run-pipeline run-valuation
