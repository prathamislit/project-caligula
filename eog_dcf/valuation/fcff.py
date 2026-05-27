from ..config import TAX_RATE

def calculate_fcff(years, ebit, dda, capex, delta_wc, wacc):
    fcff = {}
    discount_periods = {}
    discount_factors = {}
    pv_fcff = {}

    for idx, y in enumerate(years):
        nopat = ebit[y] * (1 - TAX_RATE)
        fcff[y] = nopat + dda[y] - capex[y] - delta_wc[y]
        
        # Mid-year convention: t - 0.5
        t = (idx + 1) - 0.5
        discount_periods[y] = t
        discount_factors[y] = 1.0 / ((1 + wacc) ** t)
        pv_fcff[y] = fcff[y] * discount_factors[y]

    sum_pv_fcff = sum(pv_fcff.values())
    return fcff, discount_periods, discount_factors, pv_fcff, sum_pv_fcff
