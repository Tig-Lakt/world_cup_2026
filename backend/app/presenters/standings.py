def build_standings_list(grouped) -> list[dict]:
    return [
        {
            "group": g["group"],
            "teams": [
                {
                    "position":      t.position,
                    "team":          {"name": t.team_name},
                    "played":        t.played,
                    "won":           t.won,
                    "drawn":         t.drawn,
                    "lost":          t.lost,
                    "goals_for":     t.goals_for,
                    "goals_against": t.goals_against,
                    "goal_diff":     t.goals_for - t.goals_against,
                    "points":        t.points,
                }
                for t in g["teams"]
            ],
        }
        for g in grouped
    ]


def standing_to_dict(s) -> dict:
    return {
        "position":      s.position,
        "team_name":     s.team_name,
        "played":        s.played,
        "won":           s.won,
        "drawn":         s.drawn,
        "lost":          s.lost,
        "goals_for":     s.goals_for,
        "goals_against": s.goals_against,
        "points":        s.points,
        "points_pct":    s.points_pct,
    }