from ..config import OIL_DIFF, GAS_DIFF, NGL_REALIZATION

def calculate_realized_prices(years, strip_wti, strip_hh, hedge_coverage, hedge_floor):
    realized_oil = {}
    realized_gas = {}
    realized_ngl = {}

    for y in years:
        market_wti = strip_wti[y]
        market_hh = strip_hh[y]

        # Hedge book clip formula
        cov = hedge_coverage[y]
        floor = hedge_floor[y]
        
        if cov > 0:
            hedged_price = max(market_wti, floor)
            unhedged_price = market_wti
            realized_oil_wti = (cov * hedged_price) + ((1 - cov) * unhedged_price)
        else:
            realized_oil_wti = market_wti

        # Adjust for differential basis
        realized_oil[y] = realized_oil_wti * (1 + OIL_DIFF)
        realized_gas[y] = market_hh * (1 + GAS_DIFF)
        realized_ngl[y] = market_wti * NGL_REALIZATION

    return realized_oil, realized_gas, realized_ngl

def calculate_revenues(years, oil_prod, gas_prod, ngl_prod, realized_oil, realized_gas, realized_ngl):
    revenues = {}
    total_boe = {}
    
    for y in years:
        rev_oil = oil_prod[y] * realized_oil[y]
        rev_gas = gas_prod[y] * realized_gas[y] / 1000.0 # Gas is in Mcf, convert to MMcf or keep consistent
        rev_ngl = ngl_prod[y] * realized_ngl[y]
        
        revenues[y] = rev_oil + rev_gas + rev_ngl
        total_boe[y] = oil_prod[y] + (gas_prod[y] / 6000.0) + ngl_prod[y] # 6000 Mcf = 1 boe
        
    return revenues, total_boe
