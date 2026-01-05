def american_to_decimal(american_odds):
    if american_odds > 0:
        return 1 + (american_odds / 100)
    elif american_odds < 0:
        return 1 + (100 / abs(american_odds))
    else:
        raise ValueError("American odds cannot be zero")