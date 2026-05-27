from ..config import EXIT_MULTIPLE

def calculate_exit_multiple_tv(y5_ebit, y5_dda, wacc):
    y5_ebitda = y5_ebit + y5_dda
    tv_undiscounted = y5_ebitda * EXIT_MULTIPLE
    
    # Discounted under Year 5 discount factor: (1 + WACC)^5
    discount_factor = 1.0 / ((1 + wacc) ** 5)
    tv_pv = tv_undiscounted * discount_factor
    
    return tv_undiscounted, tv_pv
