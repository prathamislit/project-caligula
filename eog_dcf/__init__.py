from .valuation.valuator import run_dcf_valuation
from .schedules.revenue import calculate_realized_prices, calculate_revenues
from .schedules.capex_dda import project_capex_and_dda
from .schedules.debt import project_debt_schedule
from .schedules.working_capital import project_working_capital

def run_full_dcf(ticker="EOG", val_date="2026-06-10"):
    years = [2026, 2027, 2028, 2029, 2030]
    
    # 1. Inputs
    strip_wti = {2026: 72.0, 2027: 69.0, 2028: 67.0, 2029: 65.0, 2030: 65.0}
    strip_hh = {2026: 2.80, 2027: 3.00, 2028: 3.20, 2029: 3.20, 2030: 3.20}
    
    hedge_coverage = {2026: 0.52, 2027: 0.20, 2028: 0.0, 2029: 0.0, 2030: 0.0}
    hedge_floor = {2026: 62.0, 2027: 62.0, 2028: 0.0, 2029: 0.0, 2030: 0.0}
    
    oil_prod = {2026: 13.2, 2027: 13.5, 2028: 13.5, 2029: 13.5, 2030: 13.5}
    gas_prod = {2026: 19800.0, 2027: 20000.0, 2028: 20000.0, 2029: 20000.0, 2030: 20000.0}
    ngl_prod = {2026: 5.5, 2027: 5.5, 2028: 5.5, 2029: 5.5, 2030: 5.5}

    # 2. Schedules
    realized_oil, realized_gas, realized_ngl = calculate_realized_prices(
        years=years,
        strip_wti=strip_wti,
        strip_hh=strip_hh,
        hedge_coverage=hedge_coverage,
        hedge_floor=hedge_floor
    )
    
    revenues, total_production_boe = calculate_revenues(
        years=years,
        oil_prod=oil_prod,
        gas_prod=gas_prod,
        ngl_prod=ngl_prod,
        realized_oil=realized_oil,
        realized_gas=realized_gas,
        realized_ngl=realized_ngl
    )
    
    capex, sustaining_capex, growth_capex, dda = project_capex_and_dda(
        years=years,
        total_production_boe=total_production_boe
    )
    
    debt_outstanding, current_debt_maturing, net_debt_change, interest_expense = project_debt_schedule(
        years=years
    )
    
    # Cost of revenue in schedules
    cost_of_revenues = {y: revenues[y] * 0.35 for y in years}
    
    ar, inventory, ap, delta_wc = project_working_capital(
        years=years,
        revenues=revenues,
        cost_of_revenues=cost_of_revenues
    )
    
    # 3. Valuation
    res = run_dcf_valuation(
        years=years,
        ebit={y: revenues[y] - cost_of_revenues[y] - (revenues[y] * 0.25) - dda[y] - (revenues[y] * 0.01) for y in years}, # Gross - SG&A - DD&A - Other
        dda=dda,
        capex=capex,
        delta_wc=delta_wc,
        total_production_boe=total_production_boe,
        revenue=revenues
    )
    
    return res
