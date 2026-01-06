import requests
from backend.matches_repo import create_match, create_matches, get_match_by_event_id
from backend.scrape import get_game_ids, get_links, get_odds, get_win_probs_football
from rapidfuzz import fuzz, process
from constants.teamNames import fullNameNCAA, fullNameSoccer
from backend.exceptions import NoWinProbDataError
from backend.utils import american_to_decimal


def get_events(sport, date_range):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard?limit=1000&dates={date_range}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if request failed
    data = response.json()

    for event in data.get("events", []):
        yield event["id"]


def get_nfl_result(event_id):
    """
    Fetch NFL result and win probability from ESPN API for a given event_id.
    
    Returns a dictionary with:
        - teams: list of dicts with team info (team name, home/away, score, winner)
        - startingWinProbability: dict with homeWinPct
    """
    sport = "football/nfl"

    # event
    event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/summary?event={event_id}"
    event_response = requests.get(event_url)
    event_response.raise_for_status()  # Raise an error if request failed
    event_data = event_response.json()

    # odds
    odds_url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{event_id}/competitions/{event_id}/odds"
    odds_response = requests.get(odds_url)
    odds_response.raise_for_status()  # Raise an error if request failed
    odds_data = odds_response.json()

    

    # parse, format, and return
    return parse_data(sport, event_data, odds_data)

def get_nba_result(event_id):
    """
    Fetch NBA result and win probability from ESPN API for a given event_id.
    
    Returns a dictionary with:
        - teams: list of dicts with team info (team name, home/away, score, winner)
        - startingWinProbability: dict with homeWinPct
    """
    sport = "basketball/nba"

    # event
    event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/summary?event={event_id}"
    event_response = requests.get(event_url)
    event_response.raise_for_status()  # Raise an error if request failed
    event_data = event_response.json()

    # odds
    odds_url = f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/{event_id}/competitions/{event_id}/odds"
    odds_response = requests.get(odds_url)
    odds_response.raise_for_status()  # Raise an error if request failed
    odds_data = odds_response.json()
    
    # parse, format, and return
    return parse_data(sport, event_data, odds_data)

def get_mlb_result(event_id):
    """
    Fetch MLB result and win probability from ESPN API for a given event_id.
    
    Returns a dictionary with:
        - teams: list of dicts with team info (team name, home/away, score, winner)
        - startingWinProbability: dict with homeWinPct
    """
    sport = "baseball/mlb"

    # event
    event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/summary?event={event_id}"
    event_response = requests.get(event_url)
    event_response.raise_for_status()  # Raise an error if request failed
    event_data = event_response.json()

    # odds
    odds_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/events/{event_id}/competitions/{event_id}/odds"
    odds_response = requests.get(odds_url)
    odds_response.raise_for_status()  # Raise an error if request failed
    odds_data = odds_response.json()
    
    # parse, format, and return
    return parse_data(sport, event_data, odds_data)
    


def get_ncaa_result(sport, event_id):
    """
    Fetch NCAA result and win probability from ESPN API for a given event_id.
    
    Returns a dictionary with:
        - teams: list of dicts with team info (team name, home/away, score, winner)
        - startingWinProbability: dict with homeWinPct
    """

    # event
    event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/summary?event={event_id}"
    event_response = requests.get(event_url)
    event_response.raise_for_status()  # Raise an error if request failed
    event_data = event_response.json()
    
    # parse, format, and return
    return parse_data(sport, event_data)

def create_ncaaf_entry(game_ids: list[str]=None):
    sport = "football"
    league = "college-football"

    if not game_ids:
        # step 1: scrape espn for a certain dates' game ids
        game_ids = get_game_ids(sport=league, date="20251210-20260105")
    else:
        assert isinstance(game_ids, list), "game_ids must be a list of strings"

    # step 2: get dictionary of espn game data for each game id
    matches_list = []
    for event_id in game_ids:
        print(f'Processing event {event_id}')

        try: 
            summary = get_ncaa_result(f'{sport}/{league}', event_id)
            matches_list.append(summary)
        except NoWinProbDataError as e:
            print(f"Skipping event {event_id} due to missing win probability data.")

    # step 3: scrape oddsportal for betting odds for each game
    ids = get_links("https://www.oddsportal.com/american-football/usa/ncaa/results/")
    

    for id in ids:
        try:
            get_odds(id)
        except Exception as e:
            print(f"Error fetching odds for id {id}: {e}")

        home_team, away_team, date, odds = get_odds(id)
        home_team, away_team = fullNameNCAA(home_team), fullNameNCAA(away_team)
        for match in matches_list:
            match_team1 = match["team_1"]
            match_team2 = match["team_2"]
            
            if fuzz.ratio(away_team, match_team1) > 90 and fuzz.ratio(home_team, match_team2) > 90:
                print(away_team, match_team1, fuzz.ratio(away_team, match_team1))
                print(home_team, match_team2, fuzz.ratio(home_team, match_team2))  
                
                match["oddsPortalLink"] = f"https://www.oddsportal.com/basketball/usa/ncaa/{id}/"
                for bookmaker, odd in odds.items():
                    try: 
                        odd_home, odd_away = float(odd[0]), float(odd[1])
                        if bookmaker == 'bet365' or bookmaker == "Cloudbet":

                            print('here')
                            match['bookmaker'] = bookmaker
                            match[bookmaker] = {
                                "team_1": { "moneyline": odd_away },
                                "team_2": { "moneyline": odd_home }
                            }
                            match['bet'] = {}

                            implied_odds_1 = 1 / odd_away
                            implied_odds_2 = 1 / odd_home

                            if implied_odds_1 < float(match["ESPN"]["team_1"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team1
                                match['bet']["line"] = odd_away
                                match['bet']["implied_odds"] = implied_odds_1
                                match['bet']["winProb"] = match["ESPN"]["team_1"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else -1

                            elif implied_odds_2 < float(match["ESPN"]["team_2"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team2
                                match['bet']["line"] = odd_home
                                match['bet']["implied_odds"] = implied_odds_2
                                match['bet']["winProb"] = match["ESPN"]["team_2"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else -1
                            
                            else:
                                match['bet']["team"] = "No Bet"
                                match['bet']["line"] = "-"
                                match['bet']["implied_odds"] = "-"
                                match['bet']["winProb"] = "-"
                                match['bet']["EV"] = 0
                                match['bet']["EW"] = 0
                                match['bet']["result"] = "-"
                                match['bet']["actual_value"] = 0

                            break
                    except ValueError:
                        print(f"Invalid odds value for bookmaker {bookmaker}: {odd}")
                        continue


    # step 4: create matches where bet isn't empty
    print(matches_list)
    matches_list = [m for m in matches_list if m.get("bet")]
    create_matches(matches_list)



def create_ncaab_entry():
    sport = "basketball"
    league = "mens-college-basketball"

    # step 1: scrape espn for a certain dates' game ids
    game_ids = get_game_ids(sport=league, date="20260105")

    # step 2: get dictionary of espn game data for each game id
    matches_list = []
    for event_id in game_ids:
        print(f'Processing event {event_id}')
        summary = get_ncaa_result(f"{sport}/{league}", event_id)
        matches_list.append(summary)

    # step 3: scrape oddsportal for betting odds for each game
    ids = get_links("https://www.oddsportal.com/basketball/usa/ncaa/results/")
    # ids = get_links("https://www.oddsportal.com/basketball/usa/ncaa/results/#/page/2/")

    

    for id in ids:

        try:
            get_odds(id)
        except Exception as e:
            print(f"Error fetching odds for id {id}: {e}")

        home_team, away_team, date, odds = get_odds(id)
        home_team, away_team = fullNameNCAA(home_team), fullNameNCAA(away_team)
        for match in matches_list:
            match_team1 = match["team_1"]
            match_team2 = match["team_2"]
            
            if fuzz.ratio(away_team, match_team1) > 90 and fuzz.ratio(home_team, match_team2) > 90:
                print(away_team, match_team1, fuzz.ratio(away_team, match_team1))
                print(home_team, match_team2, fuzz.ratio(home_team, match_team2))  
                
                match["oddsPortalLink"] = f"https://www.oddsportal.com/basketball/usa/ncaa/{id}/"
                for bookmaker, odd in odds.items():
                    try: 
                        odd_home, odd_away = float(odd[0]), float(odd[1])
                        if bookmaker == 'bet365' or bookmaker == "Cloudbet":

                            print('here')
                            match['bookmaker'] = bookmaker
                            match[bookmaker] = {
                                "team_1": { "moneyline": odd_away },
                                "team_2": { "moneyline": odd_home }
                            }
                            match['bet'] = {}

                            implied_odds_1 = 1 / odd_away
                            implied_odds_2 = 1 / odd_home

                            if implied_odds_1 < float(match["ESPN"]["team_1"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team1
                                match['bet']["line"] = odd_away
                                match['bet']["implied_odds"] = implied_odds_1
                                match['bet']["winProb"] = match["ESPN"]["team_1"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else -1

                            elif implied_odds_2 < float(match["ESPN"]["team_2"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team2
                                match['bet']["line"] = odd_home
                                match['bet']["implied_odds"] = implied_odds_2
                                match['bet']["winProb"] = match["ESPN"]["team_2"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else -1
                            
                            else:
                                match['bet']["team"] = "No Bet"
                                match['bet']["line"] = "-"
                                match['bet']["implied_odds"] = "-"
                                match['bet']["winProb"] = "-"
                                match['bet']["EV"] = 0
                                match['bet']["EW"] = 0
                                match['bet']["result"] = "-"
                                match['bet']["actual_value"] = 0

                            break
                    except ValueError:
                        print(f"Invalid odds value for bookmaker {bookmaker}: {odd}")
                        continue


    # step 4: create matches where bet isn't empty
    print(matches_list)
    matches_list = [m for m in matches_list if m.get("bet")]
    create_matches(matches_list)
                  

def create_ncaaw_entry():
    sport = "basketball"
    league = "womens-college-basketball"

    # step 1: scrape espn for a certain dates' game ids
    game_ids = get_game_ids(sport=league, date="20260102")

    # step 2: get dictionary of espn game data for each game id
    matches_list = []
    for event_id in game_ids:
        print(f'Processing event {event_id}')
        summary = get_ncaa_result(f"{sport}/{league}", event_id)
        matches_list.append(summary)

    # step 3: scrape oddsportal for betting odds for each game
    ids = get_links("https://www.oddsportal.com/basketball/usa/ncaa-women/results/")

    for id in ids:

        try:
            get_odds(id)
        except Exception as e:
            print(f"Error fetching odds for id {id}: {e}")

        home_team, away_team, date, odds = get_odds(id)
        home_team, away_team = fullNameNCAA(home_team), fullNameNCAA(away_team)
        for match in matches_list:
            match_team1 = match["team_1"]
            match_team2 = match["team_2"]
            
            if fuzz.ratio(away_team, match_team1) > 90 and fuzz.ratio(home_team, match_team2) > 90:
                print(away_team, match_team1, fuzz.ratio(away_team, match_team1))
                print(home_team, match_team2, fuzz.ratio(home_team, match_team2))  
                
                match["oddsPortalLink"] = f"https://www.oddsportal.com/basketball/usa/ncaa/{id}/"
                for bookmaker, odd in odds.items():
                    try: 
                        odd_home, odd_away = float(odd[0]), float(odd[1])
                        if bookmaker == 'bet365' or bookmaker == "Cloudbet":

                            print('here')
                            match['bookmaker'] = bookmaker
                            match[bookmaker] = {
                                "team_1": { "moneyline": odd_away },
                                "team_2": { "moneyline": odd_home }
                            }
                            match['bet'] = {}

                            implied_odds_1 = 1 / odd_away
                            implied_odds_2 = 1 / odd_home

                            if implied_odds_1 < float(match["ESPN"]["team_1"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team1
                                match['bet']["line"] = odd_away
                                match['bet']["implied_odds"] = implied_odds_1
                                match['bet']["winProb"] = match["ESPN"]["team_1"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_1_score", 0)) > int(match.get("team_2_score", 0)) else -1

                            elif implied_odds_2 < float(match["ESPN"]["team_2"].get("winPct", -0.1)):
                                match['bet']["team"] = match_team2
                                match['bet']["line"] = odd_home
                                match['bet']["implied_odds"] = implied_odds_2
                                match['bet']["winProb"] = match["ESPN"]["team_2"].get("winPct", -0.1)
                                match['bet']["EV"] = (match['bet']["winProb"] * match['bet']["line"]) - 1
                                match['bet']["EW"] = match['bet']["winProb"]
                                match['bet']["result"] = "W" if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else "L"
                                match['bet']["actual_value"] = match['bet']["line"] - 1 if int(match.get("team_2_score", 0)) > int(match.get("team_1_score", 0)) else -1
                            
                            else:
                                match['bet']["team"] = "No Bet"
                                match['bet']["line"] = "-"
                                match['bet']["implied_odds"] = "-"
                                match['bet']["winProb"] = "-"
                                match['bet']["EV"] = 0
                                match['bet']["EW"] = 0
                                match['bet']["result"] = "-"
                                match['bet']["actual_value"] = 0

                            break
                    except ValueError:
                        print(f"Invalid odds value for bookmaker {bookmaker}: {odd}")
                        continue

    # step 4: create matches where bet isn't empty
    print(matches_list)
    matches_list = [m for m in matches_list if m.get("bet")]
    create_matches(matches_list)
                  
def record_soccer_winprob(league = "eng.1", league_opta = "premier-league", click=False, espn_date_range = "20260105"):
    sport = "soccer"
    
    # f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event=740789"
    # f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/740789/competitions/740789/odds"

    
    matches, probs = get_win_probs_football(league_opta, click=click)
    print(matches, probs)
    matches_list = []
    for match, prob in zip(matches, probs):
        match = match.split("\n")
        home_team, away_team = match[0], match[2]

        homeWinProb, drawProb, awayWinProb = prob[0], prob[1], prob[2]

        game = {
            "sport": sport,
            "league": league,
            "team_1": fullNameSoccer(home_team),
            "team_1_homeAway": "home",
            "team_2": fullNameSoccer(away_team),
            "team_2_homeAway": "away",
            "Opta": {
                "team_1": {
                    "winPct": homeWinProb,
                },
                "team_2": {
                    "winPct": awayWinProb,
                },
                "drawPct": drawProb
            },

            "bet": {
                "team": "",
                "line": "",
                "implied_odds": "",
                "winProb": "",
                "EV": "",
                "EW": "",
                "result": "",
                "actual_value": "",
            },

            "bookmaker": "",
        }

        for id in get_events(f"{sport}/{league}", espn_date_range):
            event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={id}"
            event_response = requests.get(event_url)
            event_response.raise_for_status()
            event_data = event_response.json()

            match_team1 = event_data["header"]["competitions"][0]["competitors"][0]["team"]["displayName"]
            match_team2 = event_data["header"]["competitions"][0]["competitors"][1]["team"]["displayName"]

             

            if fuzz.ratio(fullNameSoccer(home_team), match_team1) > 90 and fuzz.ratio(fullNameSoccer(away_team), match_team2) > 90:
                print(fullNameSoccer(home_team), match_team1, fuzz.ratio(fullNameSoccer(home_team), match_team1))
                print(fullNameSoccer(away_team), match_team2, fuzz.ratio(fullNameSoccer(away_team), match_team2)) 

                game["date"] = event_data["header"]["competitions"][0]["date"]
                game["event_id"] = event_data["header"]["id"]
                
                matches_list.append(game)

                break
    print(matches_list)
    create_matches(matches_list)

def get_soccer_result(event_id, league):
    sport = "soccer"
    game = get_match_by_event_id(str(event_id))

    game['ESPN'] = {
        'team_1': {},
        'team_2': {}
    }

    # event
    event_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={event_id}"
    event_response = requests.get(event_url)
    event_response.raise_for_status()  # Raise an error if request failed
    event_data = event_response.json()

    for comp in event_data["header"]["competitions"][0]["competitors"]:
        if comp["homeAway"] == "home":
            game["team_1_score"] = comp.get("score")
        elif comp["homeAway"] == "away":
            game["team_2_score"] = comp.get("score")
        else:
            raise ValueError("Unknown homeAway value")
        
    game['date'] = event_data["header"]["competitions"][0]["date"]

    extra_time = False
    if event_data["header"]["competitions"][0]["status"]["type"]["detail"] in ["AET", "FT-Pens"]:
        extra_time = True
        game['extra_time'] = True

    # odds
    odds_url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{event_id}/odds"
    odds_response = requests.get(odds_url)
    odds_response.raise_for_status()  # Raise an error if request failed
    odds_data = odds_response.json()

    if odds_data:
        odds = odds_data['items'][0]  # the first (and only) event

        game['bookmaker'] = odds['provider']['name']

        home = odds['homeTeamOdds']['close']
        away = odds['awayTeamOdds']['close']

        game['ESPN']["team_1"]["moneyline"] = home.get('moneyLine', {}).get('decimal')
        game['ESPN']["team_1"]["spread_odds"] = home.get('spread', {}).get('decimal')
        game['ESPN']["team_1"]["point_spread"] = home.get('pointSpread', {}).get('alternateDisplayValue')
        game['ESPN']["team_2"]["moneyline"] = away.get('moneyLine', {}).get('decimal')
        game['ESPN']["team_2"]["spread_odds"] = away.get('spread', {}).get('decimal')
        game['ESPN']["team_2"]["point_spread"] = away.get('pointSpread', {}).get('alternateDisplayValue')

        game['ESPN']['draw'] = american_to_decimal(odds['drawOdds']['moneyLine'])

        implied_odds_1 = 1 / game["ESPN"]["team_1"]["moneyline"]
        implied_odds_draw = 1 / game["ESPN"]["draw"]
        implied_odds_2 = 1 / game["ESPN"]["team_2"]["moneyline"]


        if implied_odds_1 < float(game["Opta"]["team_1"].get("winPct", -0.1)):
            game['bet']["team"] = game["team_1"]
            game['bet']["line"] = game["ESPN"]["team_1"]["moneyline"]
            game['bet']["implied_odds"] = implied_odds_1
            game['bet']["winProb"] = game["Opta"]["team_1"].get("winPct", -0.1)
            game['bet']["EV"] = (game['bet']["winProb"] * game['bet']["line"]) - 1
            game['bet']["EW"] = game['bet']["winProb"]
            game['bet']["result"] = "W" if int(game.get("team_1_score", 0)) > int(game.get("team_2_score", 0)) and (not extra_time) else "L"
            game['bet']["actual_value"] = game['bet']["line"] - 1 if int(game.get("team_1_score", 0)) > int(game.get("team_2_score", 0)) and (not extra_time) else -1

        elif implied_odds_2 < float(game["Opta"]["team_2"].get("winPct", -0.1)):
            game['bet']["team"] = game["team_2"]
            game['bet']["line"] = game["ESPN"]["team_2"]["moneyline"]
            game['bet']["implied_odds"] = implied_odds_2
            game['bet']["winProb"] = game["Opta"]["team_2"].get("winPct", -0.1)
            game['bet']["EV"] = (game['bet']["winProb"] * game['bet']["line"]) - 1
            game['bet']["EW"] = game['bet']["winProb"]
            game['bet']["result"] = "W" if int(game.get("team_2_score", 0)) > int(game.get("team_1_score", 0)) and (not extra_time) else "L"
            game['bet']["actual_value"] = game['bet']["line"] - 1 if int(game.get("team_2_score", 0)) > int(game.get("team_1_score", 0)) and (not extra_time) else -1

        elif implied_odds_draw < float(game["Opta"].get("drawPct", -0.1)):
            game['bet']["team"] = "Draw"
            game['bet']["line"] = game["ESPN"]["draw"]
            game['bet']["implied_odds"] = implied_odds_draw
            game['bet']["winProb"] = game["Opta"].get("drawPct", -0.1)
            game['bet']["EV"] = (game['bet']["winProb"] * game['bet']["line"]) - 1
            game['bet']["EW"] = game['bet']["winProb"]
            game['bet']["result"] = "W" if int(game.get("team_1_score", 0)) == int(game.get("team_2_score", 0)) or extra_time else "L"
            game['bet']["actual_value"] = game['bet']["line"] - 1 if int(game.get("team_1_score", 0)) == int(game.get("team_2_score", 0)) or extra_time else -1

        else:
            game['bet']["team"] = "No Bet"
            game['bet']["line"] = "-"
            game['bet']["implied_odds"] = "-"
            game['bet']["winProb"] = "-"
            game['bet']["EV"] = 0
            game['bet']["EW"] = 0
            game['bet']["result"] = "-"
            game['bet']["actual_value"] = 0

    game = dict(sorted(game.items()))
    return game



def parse_data(sport, event_data, odds_data=None):
    """
    Parse the ESPN API data and format it into a dictionary.
    """
    home_winprob = event_data.get("winprobability")
    if home_winprob:
        home_winprob = home_winprob[0]
    else:
        raise NoWinProbDataError()
    
    game = {
        "date": event_data["header"]["competitions"][0]["date"],
        "event_id": event_data["header"]["id"],
        "ESPN": {
            "team_1": {
                "winPct": 1 - home_winprob.get("homeWinPercentage"),
            },
            "team_2": {
                "winPct": home_winprob.get("homeWinPercentage"),
            }
        },

        "bet": {},

        "sport": sport.split("/")[0],
        "league": sport.split("/")[1],


        # unused or currently unavailable
        "oddsPortalLink": None,
    }

    for comp in event_data["header"]["competitions"][0]["competitors"]:
        if comp["homeAway"] == "home":
            game["team_2"] = comp["team"]["displayName"]
            game["team_2_homeAway"] = comp["homeAway"]
            game["team_2_score"] = comp.get("score")
        elif comp["homeAway"] == "away":
            game["team_1"] = comp["team"]["displayName"]
            game["team_1_homeAway"] = comp["homeAway"]
            game["team_1_score"] = comp.get("score")
        else:
            raise ValueError("Unknown homeAway value")
        
    if odds_data:
        odds = odds_data['items'][0]  # the first (and only) event

        game['bookmaker'] = odds['provider']['name']

        home = odds['homeTeamOdds']['close']
        away = odds['awayTeamOdds']['close']

        game['ESPN']["team_1"]["moneyline"] = away.get('moneyLine', {}).get('decimal')
        game['ESPN']["team_1"]["spread_odds"] = away.get('spread', {}).get('decimal')
        game['ESPN']["team_1"]["point_spread"] = away.get('pointSpread', {}).get('alternateDisplayValue')
        game['ESPN']["team_2"]["moneyline"] = home.get('moneyLine', {}).get('decimal')
        game['ESPN']["team_2"]["spread_odds"] = home.get('spread', {}).get('decimal')
        game['ESPN']["team_2"]["point_spread"] = home.get('pointSpread', {}).get('alternateDisplayValue')

        implied_odds_1 = 1 / game["ESPN"]["team_1"]["moneyline"]
        implied_odds_2 = 1 / game["ESPN"]["team_2"]["moneyline"]


        if implied_odds_1 < float(game["ESPN"]["team_1"].get("winPct", -0.1)):
            game['bet']["team"] = game["team_1"]
            game['bet']["line"] = game["ESPN"]["team_1"]["moneyline"]
            game['bet']["implied_odds"] = implied_odds_1
            game['bet']["winProb"] = game["ESPN"]["team_1"].get("winPct", -0.1)
            game['bet']["EV"] = (game['bet']["winProb"] * game['bet']["line"]) - 1
            game['bet']["EW"] = game['bet']["winProb"]
            game['bet']["result"] = "W" if int(game.get("team_1_score", 0)) > int(game.get("team_2_score", 0)) else "L"
            game['bet']["actual_value"] = game['bet']["line"] - 1 if int(game.get("team_1_score", 0)) > int(game.get("team_2_score", 0)) else -1

        elif implied_odds_2 < float(game["ESPN"]["team_2"].get("winPct", -0.1)):
            game['bet']["team"] = game["team_2"]
            game['bet']["line"] = game["ESPN"]["team_2"]["moneyline"]
            game['bet']["implied_odds"] = implied_odds_2
            game['bet']["winProb"] = game["ESPN"]["team_2"].get("winPct", -0.1)
            game['bet']["EV"] = (game['bet']["winProb"] * game['bet']["line"]) - 1
            game['bet']["EW"] = game['bet']["winProb"]
            game['bet']["result"] = "W" if int(game.get("team_2_score", 0)) > int(game.get("team_1_score", 0)) else "L"
            game['bet']["actual_value"] = game['bet']["line"] - 1 if int(game.get("team_2_score", 0)) > int(game.get("team_1_score", 0)) else -1

        else:
            game['bet']["team"] = "No Bet"
            game['bet']["line"] = "-"
            game['bet']["implied_odds"] = "-"
            game['bet']["winProb"] = "-"
            game['bet']["EV"] = 0
            game['bet']["EW"] = 0
            game['bet']["result"] = "-"
            game['bet']["actual_value"] = 0


    game = dict(sorted(game.items()))
    return game



if __name__ == "__main__":

    matches_list = []
    # for event_id in get_events("football/nfl", "20260102-20260104"):
    #     print(f'Processing event {event_id}')
    #     summary = get_nfl_result(event_id)
    #     matches_list.append(summary)

    # sport = "basketball/nba"
    # for event_id in get_events(sport, "20260105"):
    #     print(f'Processing event {event_id}')
    #     summary = get_nba_result(event_id)
    #     matches_list.append(summary)

    # sport = "baseball/mlb"
    # for event_id in get_events(sport, "20250810-20250816"):
    #     print(f'Processing event {event_id}')
    #     summary = get_mlb_result(event_id)
    #     matches_list.append(summary)

    # create_matches(matches_list)

    #create_ncaaf_entry()
    # create_ncaab_entry()
    # create_ncaaw_entry()


    # record_soccer_winprob("eng.1", "premier-league", espn_date_range = "20260107", click=True)


    sport = "soccer"
    league = "caf.nations"
    for event_id in get_events(f"{sport}/{league}", "20260103-20260105"):
        print(f'Processing event {event_id}')
        try:
            summary = get_soccer_result(event_id, league)
            matches_list.append(summary)
        except (KeyError, TypeError) as e:
            print(f"Skipping event {event_id} due to missing data: {e}")
    create_matches(matches_list)

    # get_soccer_result(740789, league)
    


    # Example usage:

    # event_id = 401811100
    # summary = get_ncaab_result(event_id)
    # print(summary)
    # create_match(summary)