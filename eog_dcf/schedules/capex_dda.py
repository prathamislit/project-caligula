from ..config import SUSTAINING_CAPEX_PCT, DDA_PER_BOE

def project_capex_and_dda(years, total_production_boe, guided_capex=None):
    capex = {}
    sustaining_capex = {}
    growth_capex = {}
    dda = {}

    default_guided = {2026: 6594.0, 2027: 6725.0, 2028: 6860.0, 2029: 6997.0, 2030: 7137.0}
    if guided_capex is None:
        guided_capex = default_guided

    for y in years:
        capex[y] = guided_capex[y]
        sustaining_capex[y] = capex[y] * SUSTAINING_CAPEX_PCT
        growth_capex[y] = capex[y] - sustaining_capex[y]
        
        # DD&A = $/Boe * Total production boe
        dda[y] = DDA_PER_BOE * total_production_boe[y]

    return capex, sustaining_capex, growth_capex, dda
