from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, json, html, re


options = Options()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
options.add_argument("--headless=new")   # optional
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


def get_odds_pl():
    driver.get("https://www.oddsportal.com/football/england/premier-league/fulham-nottingham-QPr9bewR/#1X2;2s")


    wait = WebDriverWait(driver, 10)

    element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-v-037756ac]"))
    )

    print(element.text)

def get_odds(id):
    print(id)
    # driver.get("https://www.oddsportal.com/basketball/usa/ncaa/2euTifv9/")
    driver.get(f"https://www.oddsportal.com/basketball/usa/ncaa/{id}/")
    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="over-under-expanded-row"]'))
    )
    header = driver.find_element(By.ID, "react-event-header")
    raw_data = header.get_attribute("data")
    decoded_data = html.unescape(raw_data)
    data = json.loads(decoded_data)
    home_team = data["eventData"]['home']
    away_team = data["eventData"]['away']
    print(home_team, away_team)

    # date_container = driver.find_element(
    #     By.CSS_SELECTOR,
    #     'div[data-testid="game-time-item"]'
    # )
    # parts = date_container.find_elements(By.TAG_NAME, "p")
    # date_text = " ".join(p.text.strip() for p in parts)
    # print(date_text)

    odds_rows = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="over-under-expanded-row"]')

    odds_data = {}

    for row in odds_rows:
        # Get bookmaker name
        bookmaker = row.find_element(By.CSS_SELECTOR, 'p[data-testid="outrights-expanded-bookmaker-name"]').text
        
        # Get all odds in this row
        odd_containers = row.find_elements(By.CSS_SELECTOR, 'div[data-testid="odd-container"] p.odds-text')
        odds = [odd.text for odd in odd_containers]
        
        odds_data[bookmaker] = odds
        


    # Display results
    # for o in odds_data:
    #     print(o)

    return home_team, away_team, None, odds_data

def get_game_ids(sport, date):
    game_ids = []
    driver.get(f"https://www.espn.com/{sport}/schedule/_/date/{date}")
    wait = WebDriverWait(driver, 15)

    game_links = driver.find_elements("css selector", "td.teams__col a.AnchorLink")
    for link in game_links:
        href = link.get_attribute("href")
        match = re.search(r'gameId/(\d+)', href)
        if match:
            game_ids.append(match.group(1))

    return game_ids


def get_links(link):
    driver.get(link)
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.eventRow")))

    # scroll to load all events
    last_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    events = driver.find_elements(By.CSS_SELECTOR, "div.eventRow")
    ids = [event.get_attribute("id") for event in events if event.get_attribute("id")]

    print(f"Found {len(ids)} events")
    # print(ids)
    return ids

def get_win_probs_football(league, click=False):
    driver.get(f"https://theanalyst.com/competition/{league}/fixtures")
    wait = WebDriverWait(driver, 15)

    if click:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.DatePickerHeader-module_datepicker-header-button__vs2Om")))
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.DatePickerHeader-module_datepicker-header-button__vs2Om")
        buttons[1].click()
        print("clicked")


    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.FixtureTile-module_fixture-tile-link__GmKtI")))
    time.sleep(3)
    matches, probs = [], []
    matches_raw = driver.find_elements(By.CSS_SELECTOR, "div.FixtureTile-module_fixture-tile__VorIx")
    for match in matches_raw:
        matches.append(match.text)
    

    probs_raw = driver.find_elements(By.CSS_SELECTOR, "div.FixtureTile-module_probabilities-bar__8LfcA")

    for i in range(0, len(probs_raw), 3):
        first, _, third = probs_raw[i:i+3]
        
        first_val = float(first.text.strip('%'))
        third_val = float(third.text.strip('%'))
        
        middle_val = 100 - first_val - third_val
        
        probs.append((first_val/100, middle_val/100, third_val/100))

        print(probs)
        
    return matches, probs

if __name__ == "__main__":
    # get_links()
    # get_odds("04bB60vJ")
    # get_game_ids()
    get_win_probs_football()