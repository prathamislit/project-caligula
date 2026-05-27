import pandas as pd

class CashFlowStatement:
    def __init__(self):
        # Historicals
        self.years = [2023, 2024, 2025]
        self.net_income = {2023: 7594.0, 2024: 6403.0, 2025: 4980.0}
        self.dda = {2023: 3492.0, 2024: 4108.0, 2025: 4461.0}
        self.deferred_taxes = {2023: 683.0, 2024: 467.0, 2025: 343.0}
        self.impairments = {2023: 202.0, 2024: 391.0, 2025: 843.0}
        self.change_in_wc = {2023: 191.0, 2024: 550.0, 2025: -840.0}
        self.other_operating = {2023: -822.0, 2024: 224.0, 2025: 257.0}
        self.cfo = {2023: 11340.0, 2024: 12143.0, 2025: 10044.0}

        self.capex = {2023: -6185.0, 2024: -6372.0, 2025: -6594.0}
        self.business_purchase = {2023: 0.0, 2024: 0.0, 2025: -4451.0}
        self.other_investing = {2023: -155.0, 2024: 405.0, 2025: 109.0}
        self.cfi = {2023: -6340.0, 2024: -5967.0, 2025: -10936.0}

        self.dividends_paid = {2023: -3386.0, 2024: -2087.0, 2025: -2161.0}
        self.buybacks = {2023: -1038.0, 2024: -3246.0, 2025: -2564.0}
        self.net_debt_change = {2023: -1282.0, 2024: 952.0, 2025: 1923.0}
        self.other_financing = {2023: 12.0, 2024: 20.0, 2025: -2.0}
        self.cff = {2023: -5694.0, 2024: -4361.0, 2025: -2804.0}

        self.change_in_cash = {2023: -694.0, 2024: 1815.0, 2025: -3696.0}
        self.beginning_cash = {2023: 5972.0, 2024: 5278.0, 2025: 7092.0}
        self.ending_cash = {2023: 5278.0, 2024: 7092.0, 2025: 3396.0}

    def project(self, proj_years, proj_net_income, proj_dda, proj_deferred_tax, proj_dwc, proj_capex, proj_div, proj_buyback, proj_net_debt_change):
        for idx, y in enumerate(proj_years):
            prior_y = proj_years[idx-1] if idx > 0 else 2025
            self.beginning_cash[y] = self.ending_cash[prior_y]

            self.net_income[y] = proj_net_income[y]
            self.dda[y] = proj_dda[y]
            self.deferred_taxes[y] = proj_deferred_tax[y]
            self.impairments[y] = 0.0
            self.change_in_wc[y] = proj_dwc[y]
            self.other_operating[y] = 0.0
            self.cfo[y] = self.net_income[y] + self.dda[y] + self.deferred_taxes[y] + self.change_in_wc[y]

            self.capex[y] = -proj_capex[y]
            self.business_purchase[y] = 0.0
            self.other_investing[y] = 0.0
            self.cfi[y] = self.capex[y]

            self.dividends_paid[y] = -proj_div[y]
            self.buybacks[y] = -proj_buyback[y]
            self.net_debt_change[y] = proj_net_debt_change[y]
            self.other_financing[y] = 0.0
            self.cff[y] = self.dividends_paid[y] + self.buybacks[y] + self.net_debt_change[y]

            self.change_in_cash[y] = self.cfo[y] + self.cfi[y] + self.cff[y]
            self.ending_cash[y] = self.beginning_cash[y] + self.change_in_cash[y]

    def to_dataframe(self):
        all_years = sorted(self.net_income.keys())
        data = []
        for y in all_years:
            data.append({
                "Year": y,
                "Net Income": self.net_income[y],
                "DD&A": self.dda[y],
                "CFO": self.cfo[y],
                "CFI": self.cfi[y],
                "CFF": self.cff[y],
                "Change in Cash": self.change_in_cash[y],
                "Beginning Cash": self.beginning_cash[y],
                "Ending Cash": self.ending_cash[y]
            })
        return pd.DataFrame(data).set_index("Year")
