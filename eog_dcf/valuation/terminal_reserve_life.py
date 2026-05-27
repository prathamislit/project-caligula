from ..config import HYPERBOLIC_B, INITIAL_DECLINE_DI, WTI_LONG_RUN, OIL_DIFF, TAX_RATE

def calculate_reserve_life_tv(y5_production, y5_ebit, y5_revenue, wacc, max_years=25):
    # Hyperbolic decline depletion math
    # Y6 to Y30 (25 years)
    b = HYPERBOLIC_B
    di = INITIAL_DECLINE_DI
    
    tv_undiscounted = 0.0
    tv_pv = 0.0
    
    production = y5_production
    for t_step in range(1, max_years + 1):
        # Hyperbolic decline curve
        decline_factor = (1.0 + b * di * t_step) ** (-1.0 / b)
        prod_t = y5_production * decline_factor
        
        # Revenues scale with production
        rev_t = y5_revenue * decline_factor
        ebit_t = y5_ebit * decline_factor
        nopat_t = ebit_t * (1 - TAX_RATE)
        
        # In depletion phase, reinvestment (CapEx) matches DD&A, working capital change is zero
        # FCFF_t = NOPAT_t + DD&A_t - CapEx_t - dWC_t => FCFF_t = NOPAT_t
        fcff_t = nopat_t
        
        # Discount under mid-year convention from Year 5 onwards: (1 + WACC)^(5 + t - 0.5)
        t_total = 5.0 + t_step - 0.5
        discount_factor = 1.0 / ((1 + wacc) ** t_total)
        pv_fcff_t = fcff_t * discount_factor
        
        tv_undiscounted += fcff_t
        tv_pv += pv_fcff_t
        
    return tv_undiscounted, tv_pv
