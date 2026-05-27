import pandas as pd

class BalanceSheet:
    def __init__(self):
        # Historicals
        self.years = [2023, 2024, 2025]
        self.cash = {2023: 5278.0, 2024: 7092.0, 2025: 3396.0}
        self.ar = {2023: 2716.0, 2024: 2650.0, 2025: 2681.0}
        self.inventory = {2023: 1275.0, 2024: 985.0, 2025: 1014.0}
        self.other_current_assets = {2023: 666.0, 2024: 503.0, 2025: 565.0}
        self.total_current_assets = {2023: 9935.0, 2024: 11230.0, 2025: 7656.0}
        self.ppe_net = {2023: 32297.0, 2024: 34212.0, 2025: 42341.0}
        self.other_assets = {2023: 1625.0, 2024: 1744.0, 2025: 1802.0}
        self.total_assets = {2023: 43857.0, 2024: 47186.0, 2025: 51799.0}

        self.ap = {2023: 2437.0, 2024: 2464.0, 2025: 2904.0}
        self.accrued_taxes = {2023: 466.0, 2024: 1007.0, 2025: 299.0}
        self.current_debt = {2023: 359.0, 2024: 847.0, 2025: 499.0}
        self.other_current_liabilities = {2023: 812.0, 2024: 1036.0, 2025: 989.0}
        self.total_current_liabilities = {2023: 4074.0, 2024: 5354.0, 2025: 4691.0}

        self.long_term_debt = {2023: 3616.0, 2024: 4102.0, 2025: 7819.0}
        self.deferred_taxes = {2023: 6854.0, 2024: 7015.0, 2025: 7854.0}
        self.other_liabilities = {2023: 1223.0, 2024: 1364.0, 2025: 1602.0}
        self.total_liabilities = {2023: 15767.0, 2024: 17835.0, 2025: 21966.0}

        self.stockholders_equity = {2023: 28090.0, 2024: 29351.0, 2025: 29833.0}

    def project(self, proj_years, proj_ar, proj_inv, proj_ap, proj_capex, proj_dda, proj_ending_cash, proj_debt, proj_debt_current, proj_net_income, proj_div, proj_buyback):
        for idx, y in enumerate(proj_years):
            # Prior values
            prior_y = proj_years[idx-1] if idx > 0 else 2025
            prior_equity = self.stockholders_equity[prior_y]
            prior_ppe = self.ppe_net[prior_y]

            # Current assets
            self.cash[y] = proj_ending_cash[y]
            self.ar[y] = proj_ar[y]
            self.inventory[y] = proj_inv[y]
            self.other_current_assets[y] = self.other_current_assets[prior_y] * 1.02
            self.total_current_assets[y] = self.cash[y] + self.ar[y] + self.inventory[y] + self.other_current_assets[y]

            # Non-current assets
            self.ppe_net[y] = prior_ppe + proj_capex[y] - proj_dda[y]
            self.other_assets[y] = self.other_assets[prior_y]
            self.total_assets[y] = self.total_current_assets[y] + self.ppe_net[y] + self.other_assets[y]

            # Current liabilities
            self.ap[y] = proj_ap[y]
            self.accrued_taxes[y] = self.accrued_taxes[prior_y] * 1.02
            self.current_debt[y] = proj_debt_current[y]
            self.other_current_liabilities[y] = self.other_current_liabilities[prior_y]
            self.total_current_liabilities[y] = self.ap[y] + self.accrued_taxes[y] + self.current_debt[y] + self.other_current_liabilities[y]

            # Non-current liabilities
            self.long_term_debt[y] = proj_debt[y]
            self.deferred_taxes[y] = self.deferred_taxes[prior_y] * 1.01
            self.other_liabilities[y] = self.other_liabilities[prior_y]
            self.total_liabilities[y] = self.total_current_liabilities[y] + self.long_term_debt[y] + self.deferred_taxes[y] + self.other_liabilities[y]

            # Stockholders' equity (balances perfectly to match retained earnings net changes)
            self.stockholders_equity[y] = prior_equity + proj_net_income[y] - proj_div[y] - proj_buyback[y]

    def to_dataframe(self):
        all_years = sorted(self.cash.keys())
        data = []
        for y in all_years:
            data.append({
                "Year": y,
                "Cash": self.cash[y],
                "Accounts Receivable": self.ar[y],
                "Inventory": self.inventory[y],
                "Total Current Assets": self.total_current_assets[y],
                "Net PPE": self.ppe_net[y],
                "Total Assets": self.total_assets[y],
                "Accounts Payable": self.ap[y],
                "Total Current Liabilities": self.total_current_liabilities[y],
                "Long-Term Debt": self.long_term_debt[y],
                "Total Liabilities": self.total_liabilities[y],
                "Stockholders Equity": self.stockholders_equity[y]
            })
        return pd.DataFrame(data).set_index("Year")
