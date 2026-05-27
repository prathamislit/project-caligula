def project_working_capital(years, revenues, cost_of_revenues, dso=43.0, dio=45.0, dpo=120.0):
    ar = {}
    inventory = {}
    ap = {}
    delta_wc = {}

    # Historical values at 2025
    prior_ar = 2681.0
    prior_inv = 1014.0
    prior_ap = 2904.0

    for idx, y in enumerate(years):
        rev = revenues[y]
        cogs = cost_of_revenues[y]
        
        ar[y] = dso * rev / 365.0
        inventory[y] = dio * cogs / 365.0
        ap[y] = dpo * cogs / 365.0
        
        # prior - current
        y_prior_ar = years[idx-1] if idx > 0 else 2025
        y_prior_inv = years[idx-1] if idx > 0 else 2025
        y_prior_ap = years[idx-1] if idx > 0 else 2025
        
        val_prior_ar = ar[y_prior_ar] if idx > 0 else prior_ar
        val_prior_inv = inventory[y_prior_inv] if idx > 0 else prior_inv
        val_prior_ap = ap[y_prior_ap] if idx > 0 else prior_ap
        
        delta_wc[y] = (val_prior_ar - ar[y]) + (val_prior_inv - inventory[y]) - (val_prior_ap - ap[y])

    return ar, inventory, ap, delta_wc
