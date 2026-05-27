def project_opex(years, revenues):
    # OpEx lines are projected as % of revenues or flat growth rates
    cost_of_revenue = {}
    sga = {}
    opex_other = {}
    
    for y in years:
        rev = revenues[y]
        cost_of_revenue[y] = rev * 0.35
        sga[y] = rev * 0.25
        opex_other[y] = rev * 0.01
        
    return cost_of_revenue, sga, opex_other
