import pandas as pd
from ..config import TAX_RATE

class IncomeStatement:
    def __init__(self):
        # Historicals
        self.years = [2023, 2024, 2025]
        self.total_revenue = {2023: 23182.0, 2024: 23378.0, 2025: 22582.0}
        self.cost_of_revenue = {2023: 6566.0, 2024: 7402.0, 2025: 8270.0}
        self.gross_profit = {2023: 16616.0, 2024: 15976.0, 2025: 14312.0}
        self.sga = {2023: 6349.0, 2024: 6386.0, 2025: 5615.0}
        self.dda = {2023: 3492.0, 2024: 4108.0, 2025: 4461.0}
        self.opex_other = {2023: 91.0, 2024: 88.0, 2025: 213.0}
        self.ebit = {2023: 6597.0, 2024: 8356.0, 2025: 6597.0}
        self.interest_expense = {2023: 148.0, 2024: 138.0, 2025: 235.0}
        self.interest_income = {2023: 240.0, 2024: 277.0, 2025: 210.0}
        self.other_inc_exp = {2023: 705.0, 2024: -174.0, 2025: -863.0}
        self.pretax_income = {2023: 9689.0, 2024: 8218.0, 2025: 6362.0}
        self.tax_provision = {2023: 2095.0, 2024: 1815.0, 2025: 1382.0}
        self.net_income = {2023: 7594.0, 2024: 6403.0, 2025: 4980.0}

    def project(self, proj_revenues, proj_dda, proj_interest):
        proj_years = [2026, 2027, 2028, 2029, 2030]
        for idx, y in enumerate(proj_years):
            rev = proj_revenues[y]
            self.total_revenue[y] = rev
            self.cost_of_revenue[y] = rev * 0.35
            self.gross_profit[y] = self.total_revenue[y] - self.cost_of_revenue[y]
            self.sga[y] = rev * 0.25
            self.dda[y] = proj_dda[y]
            self.opex_other[y] = rev * 0.01
            self.ebit[y] = self.gross_profit[y] - self.sga[y] - self.dda[y] - self.opex_other[y]
            self.interest_expense[y] = proj_interest[y]
            self.interest_income[y] = rev * 0.005
            self.other_inc_exp[y] = 0.0
            self.pretax_income[y] = self.ebit[y] - self.interest_expense[y] + self.interest_income[y]
            self.tax_provision[y] = self.pretax_income[y] * TAX_RATE
            self.net_income[y] = self.pretax_income[y] - self.tax_provision[y]

    def to_dataframe(self):
        all_years = sorted(self.total_revenue.keys())
        data = []
        for y in all_years:
            data.append({
                "Year": y,
                "Revenue": self.total_revenue[y],
                "Cost of Revenue": self.cost_of_revenue[y],
                "Gross Profit": self.gross_profit[y],
                "SG&A": self.sga[y],
                "DD&A": self.dda[y],
                "EBIT": self.ebit[y],
                "Interest Expense": self.interest_expense[y],
                "Pretax Income": self.pretax_income[y],
                "Tax Provision": self.tax_provision[y],
                "Net Income": self.net_income[y]
            })
        return pd.DataFrame(data).set_index("Year")
