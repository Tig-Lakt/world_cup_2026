def result_to_dict(r) -> dict:
    return {
        "id":            r.id,
        "home_team":     r.home_team,
        "away_team":     r.away_team,
        "home_score":    r.home_score,
        "away_score":    r.away_score,
        "match_date":    r.match_date.isoformat() if r.match_date else None,
        "group_name":    r.group_name,
        "tour_number":   r.tour_number,
        "match_url":     r.match_url,
        "stats":         r.stats,
    }