from .income import IncomeStatement
from .balance import BalanceSheet
from .cashflow import CashFlowStatement

class ThreeStatementLinker:
    def __init__(self):
        self.income_stmt = IncomeStatement()
        self.balance_sheet = BalanceSheet()
        self.cash_flow = CashFlowStatement()

    def run_projection(self, proj_years, proj_revenues, proj_dda, proj_interest, proj_ar, proj_inv, proj_ap, proj_capex, proj_div, proj_buyback, proj_net_debt_change):
        # 1. Project the income statement
        self.income_stmt.project(proj_revenues, proj_dda, proj_interest)

        # 2. Iterate year-by-year to link the balance sheet and cash flow statement dynamically
        proj_ending_cash = {}
        for idx, y in enumerate(proj_years):
            prior_y = proj_years[idx-1] if idx > 0 else 2025
            beg_cash = self.cash_flow.ending_cash[prior_y]

            # CFO components
            net_inc = self.income_stmt.net_income[y]
            dda_val = self.income_stmt.dda[y]
            def_tax = net_inc * 0.06 # proxy
            
            # Change in WC
            prior_ar = self.balance_sheet.ar[prior_y]
            prior_inv = self.balance_sheet.inventory[prior_y]
            prior_ap = self.balance_sheet.ap[prior_y]
            
            dwc = (prior_ar - proj_ar[y]) + (prior_inv - proj_inv[y]) - (prior_ap - proj_ap[y])
            cfo_val = net_inc + dda_val + def_tax + dwc

            # CFI components
            cfi_val = -proj_capex[y]

            # CFF components
            cff_val = -proj_div[y] - proj_buyback[y] + proj_net_debt_change[y]

            # Ending Cash
            change_cash = cfo_val + cfi_val + cff_val
            end_cash = beg_cash + change_cash
            proj_ending_cash[y] = end_cash

        # 3. Project the cash flow statement with calculated cash balances
        self.cash_flow.project(
            proj_years=proj_years,
            proj_net_income=self.income_stmt.net_income,
            proj_dda=self.income_stmt.dda,
            proj_deferred_tax={y: self.income_stmt.net_income[y] * 0.06 for y in proj_years},
            proj_dwc={y: (self.balance_sheet.ar[proj_years[idx-1] if idx > 0 else 2025] - proj_ar[y]) + 
                          (self.balance_sheet.inventory[proj_years[idx-1] if idx > 0 else 2025] - proj_inv[y]) - 
                          (self.balance_sheet.ap[proj_years[idx-1] if idx > 0 else 2025] - proj_ap[y]) for idx, y in enumerate(proj_years)},
            proj_capex=proj_capex,
            proj_div=proj_div,
            proj_buyback=proj_buyback,
            proj_net_debt_change=proj_net_debt_change
        )

        # 4. Project the balance sheet using ending cash balances from the cash flow statement
        self.balance_sheet.project(
            proj_years=proj_years,
            proj_ar=proj_ar,
            proj_inv=proj_inv,
            proj_ap=proj_ap,
            proj_capex=proj_capex,
            proj_dda=self.income_stmt.dda,
            proj_ending_cash=self.cash_flow.ending_cash,
            proj_debt={y: self.balance_sheet.long_term_debt[proj_years[idx-1] if idx > 0 else 2025] + proj_net_debt_change[y] for idx, y in enumerate(proj_years)},
            proj_debt_current={y: proj_debt_current[y] for y in proj_years} if 'proj_debt_current' in locals() else {y: 499.0 for y in proj_years},
            proj_net_income=self.income_stmt.net_income,
            proj_div=proj_div,
            proj_buyback=proj_buyback
        )
