from ..config import PRETAX_COST_OF_DEBT

def project_debt_schedule(years, initial_debt=8318.0, initial_current=499.0):
    debt_outstanding = {}
    current_debt_maturing = {}
    net_debt_change = {}
    interest_expense = {}

    for y in years:
        # Simple refinance logic: refinance maturing debt flatly
        debt_outstanding[y] = initial_debt
        current_debt_maturing[y] = initial_current
        net_debt_change[y] = 0.0 # flat refinancing means no net debt change
        
        # Interest expense
        interest_expense[y] = debt_outstanding[y] * PRETAX_COST_OF_DEBT

    return debt_outstanding, current_debt_maturing, net_debt_change, interest_expense
