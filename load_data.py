# ---------------------- Libraries ----------------------
from scraper import regular_season_totals, adp_data, season_projections_qb, season_projections_rb
from scraper import season_projections_wr, season_projections_te, season_projections_k, season_projections_dst
# ---------------------- Libraries ----------------------


def get_adp_data():
    return adp_data()

def get_season_projections_qb():
    return season_projections_qb()

def get_season_projections_rb():
    return season_projections_rb()

def get_season_projections_wr():
    return season_projections_wr()

def get_season_projections_te():
    return season_projections_te()

def get_season_projections_k():
    return season_projections_k()

def get_season_projections_dst():
    return season_projections_dst()

def get_regular_season_totals(seasons): # Fetch regular season stats for the requested timeframe
    return regular_season_totals(seasons)