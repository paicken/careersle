import requests
import csv
from bs4 import BeautifulSoup
import re
import json
import datetime
# from datetime import datetime
from time import sleep
from typing import List
from constants import DOMESTIC_LEAGUES, CONTRACTS_TO_DELETE, CONTRACTS_TO_DELETE_REGEX, IGNORE_STATED_YOUTH_CLUBS

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9",
}

NO_GOALS_APPEARANCES = "0"

class PlayerRequirementsNotMet(Exception):
    pass

class Transfer:
    date = None
    season = None
    old_club = None
    new_club = None
    new_club_id = None
    fee = None

    def __init__(self, season, date, old_club, new_club, new_club_id, fee) -> None:
        self.season = season
        self.date = date
        self.old_club = old_club
        self.new_club = new_club
        self.new_club_id = new_club_id
        self.fee = fee


class Contract:
    start = datetime.date(1900, 1, 1)
    start_season = None
    end = None
    end_season = None
    club = "placeholder"
    club_id = -1
    is_loan = False
    appearances = NO_GOALS_APPEARANCES
    goals = NO_GOALS_APPEARANCES
    seasons = []
    missing_stats = False

    def __init__(self, start, start_season, club, club_id, is_loan: False) -> None:
        self.start = start
        self.start_season = start_season
        self.club = club
        self.is_loan = is_loan
        self.club_id = club_id

    def add_start(self, start: datetime.date) -> None:
        self.start = start

    def add_appearances(self, appearances: datetime.date) -> None:
        self.appearances = appearances

    def add_goals(self, goals: datetime.date) -> None:
        self.goals = goals

    def list_out(self):
        return [self.start, self.end, self.club, self.is_loan, self.appearances, self.goals]
    
    def year_string(self) -> str:
        if self.end:
            if self.start.year == self.end.year:
                return f"{self.start.year}"
            else:
                return f"{self.start.year}-{self.end.year}"
        else:
            return f"{self.start.year}-"
    
    def club_string(self) -> str:
        if self.is_loan:
            return f"→ {self.club} (loan)"
        else:
            return f"{self.club}"

    def stats_string(self) -> str:
        if self.missing_stats:
            appearances_str = f"{self.appearances}*"
            goals_str = f"({self.goals})*"
        else:
            appearances_str = f"{self.appearances}"
            goals_str = f"({self.goals})"
        return f"{appearances_str.rjust(4)}{goals_str.rjust(6)}"

    def quiz_rep(self):
        return f"{self.year_string().ljust(12)}{self.club_string().ljust(48)}{self.stats_string()}"


class Player:
    name: str
    nationality: str
    position: str
    contracts: List[Contract]
    clubs: List[str]
    years: List[str]
    appearances_and_goals: List[str]

    def __init__(self, name, nationality, position, contracts: List[Contract]) -> None:
        self.name = name
        self.nationality = nationality
        self.position = position
        self.contracts = contracts
        self.clubs = []
        self.years = []
        self.appearances_and_goals = []
        self.extract_clubs_years_and_stats()
    
    def extract_clubs_years_and_stats(self) -> None:
        for contract in self.contracts:
            self.clubs.append(contract.club_string())
            self.years.append(contract.year_string())
            self.appearances_and_goals.append(contract.stats_string())

    def display(self):
        print(f"Name:         {self.name}")
        print(f"Nationality:  {self.nationality}")
        print(f"Postion:      {self.position}")
        print("-------")
        for contract in self.contracts:
            print(contract.quiz_rep())
    
    def info_dict(self) -> dict:
        return {
            "name": self.name,
            "nationality": self.nationality,
            "position": self.position,
            "clubs": self.clubs,
            "years": self.years,
            "appearances_and_goals": self.appearances_and_goals
        }


class StatsTableRow:
    cells = None
    season = None
    club_id = None
    appearances = None
    goals = None
    def __init__(self, cells):
        self.cells = cells
        self.season = cells[0].text.strip()
        club_link = cells[3].find("a")
        if club_link:
            club_url = club_link["href"].split('/')
            self.club_id = club_url[-3]
        appearances_cell_text = cells[4].text.strip()
        goals_cell_text = cells[5].text.strip()
        if appearances_cell_text == '-':
            self.appearances = 0
        else:
            self.appearances = int(appearances_cell_text)
        if goals_cell_text == '-':
            self.goals = 0
        else:
            self.goals = int(goals_cell_text)
    
    def __repr__(self):
        return str(self.cells)


def get_player_names_and_urls_from_file(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file)
        # urls = [row[1] for row in reader]
        player_names = []
        player_urls = []
        for row in reader:
            player_names.append(row[0])
            player_urls.append(row[1])
    return player_names, player_urls


def get_player_id_and_name_from_url(url):
    split_url = url.split('/')
    player_id = split_url[-1]
    player_name = split_url[-4]
    return player_id, player_name


def get_transfer_soup(player_name, player_id, headers):
    transfers_url = f"https://www.transfermarkt.co.uk/{player_name}/transfers/spieler/{player_id}"
    response = requests.get(transfers_url, headers=headers)
    transfer_soup = BeautifulSoup(response.text, "html.parser")
    # with open("messi.html", "r") as msi:
    #     response = msi.read()
    # transfer_soup = BeautifulSoup(response, "html.parser")
    return transfer_soup


def get_stats_soup(player_name, player_id, headers):
    stats_url = f"https://www.transfermarkt.co.uk/{player_name}/leistungsdatendetails/spieler/{player_id}"
    response = requests.get(stats_url, headers=headers)
    stats_soup = BeautifulSoup(response.text, "html.parser")
    return stats_soup


def get_nationality_and_position_from_soup(transfer_soup):
    infobox = transfer_soup.find("div", class_="data-header__info-box")
    data_points = infobox.find_all("li", class_="data-header__label")
    for data_point in data_points:
        if re.search('Citizenship', data_point.text):
            nationality = data_point.find(
                "span", class_="data-header__content").text.strip()
        if re.search('Position', data_point.text):
            position = data_point.find(
                "span", class_="data-header__content").text.strip()
    return nationality, position


def get_final_youth_year_from_soup(transfer_soup, player_id):
    youth_teams_div = transfer_soup.find(
        "div", class_="tm-player-additional-data")
    if youth_teams_div and not IGNORE_STATED_YOUTH_CLUBS.get(player_id):
        youth_teams = youth_teams_div.find(
            "div", class_="content").text.strip()
        youth_team_years = re.findall('[0-9]{4}', youth_teams)
        if youth_team_years == []:
            final_youth_year = datetime.date(1900, 1, 1)
        else:
            youth_team_years_ints = [int(x) for x in youth_team_years]
            final_youth_year = datetime.date(max(youth_team_years_ints), 1, 1)
    else:
        final_youth_year = datetime.date(1900, 1, 1)
    return final_youth_year


def load_club_history_from_transfer_divs(transfer_soup):
    transfer_divs = transfer_soup.find_all(
        "div", class_="tm-player-transfer-history-grid")
    fer_divs = transfer_soup.find_all(
        "div")
    print(transfer_soup.text)
    div_num = -2
    club_history = []
    # loan_offset = 0
    for transfer_div in transfer_divs:
        div_num += 1
        # ignore first and last divs
        if div_num == -1 or div_num == len(transfer_divs) - 2:
            continue
        date_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__date")
        if not date_div:
            continue
        date_str = date_div.text.strip()
        if date_str == "-":
            continue
        datetime_date = datetime.datetime.strptime(
            date_str, '%b %d, %Y').date()
        # if date in future (i.e. loan ending) ignore
        if datetime_date > datetime.date.today():
            continue
        season_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__season")
        season = int(season_div.text.strip().split('/')[0])
        date_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__date")
        date_str = date_div.text.strip()
        datetime_date = datetime.datetime.strptime(
            date_str, '%b %d, %Y').date()
        old_club_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__old-club")
        old_club = old_club_div.text.strip()
        new_club_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__new-club")
        new_club = new_club_div.text.strip()
        new_club_link = new_club_div.find("a")
        if new_club_link:
            new_club_url = new_club_link["href"].split('/')
            new_club_id = new_club_url[-3]
        else:
            new_club_id = new_club
        fee_div = transfer_div.find(
            "div", class_="tm-player-transfer-history-grid__fee")
        fee = fee_div.text.strip()
        club_history.insert(
            0, [season, datetime_date, old_club, new_club, new_club_id, fee])
        print(club_history)
        """
        season first year int, datetime date of transfer, old club, new club, new club id, fee
        """
    return club_history


def load_club_history_from_json_call(player_id):
    transfer_json = requests.get(f"https://www.transfermarkt.co.uk/ceapi/transferHistory/list/{player_id}", headers=headers).json()
    club_history = []
    for transfer in transfer_json["transfers"]:
        datetime_date = datetime.datetime.strptime(
            transfer["dateUnformatted"], '%Y-%m-%d').date()
        # if date in future (i.e. loan ending) ignore
        if datetime_date > datetime.date.today():
            continue
        season = int(transfer["season"].replace('\/', '/').split('/')[0])
        old_club = transfer["from"]["clubName"]
        new_club = transfer["to"]["clubName"]
        if transfer["to"]["isSpecial"]:
            new_club_id = new_club
        else:
            new_club_url = transfer["to"]["href"].replace('\/', '/').split('/')
            new_club_id = new_club_url[-3]
        fee = transfer["fee"]
        club_history.insert(
            0, [season, datetime_date, old_club, new_club, new_club_id, fee])
    print(club_history)
    """
    season first year int, datetime date of transfer, old club, new club, new club id, fee
    """
    return club_history


def determine_transfer_type(transfer: Transfer):
    if transfer.fee == "End of loan":
        transfer_type = "loan_end"
    elif re.search('loan', transfer.fee, re.IGNORECASE):
        transfer_type = "new_loan"
    elif transfer.new_club == "Retired":
        transfer_type = "retirement"
    # elif transfer.new_club == "Without Club":
    #     transfer_type = "contractless"
    else:
        transfer_type = "sale"

    return transfer_type


def convert_club_history_to_transfers(club_history, final_youth_year):
    transfers = []
    for entry in club_history:
        if entry[1] < final_youth_year:
            continue
        else:
            transfers.append(
                Transfer(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
    return transfers


def add_new_contract_to_list(contract_list: List[Contract], transfer: Transfer, is_new_loan: bool) -> List[Contract]:
    contract = Contract(transfer.date, transfer.season,
                        transfer.new_club, transfer.new_club_id, is_new_loan)
    contract_list.append(contract)
    return contract_list


def update_contract_with_end_date(contract_list: List[Contract], index, transfer: Transfer) -> List[Contract]:
    contract_list[index].end = transfer.date
    contract_list[index].end_season = transfer.season
    return contract_list


def create_contract_list_from_transfers(transfers: List[Transfer]) -> List[Contract]:
    perm_club_index = -1
    loan_club_index = -1
    contract_index = -1
    player_contract_list = []

    # We will loop through each transfer and populate contract details from the transfers
    # The *_index variables keep track of which place in the list we need to update
    # perm_club_index is the index of the player's permanent club while loan_club_index is the
    # player's loan club. contract index tracks the player's contract whether it's perm or loan

    for transfer in transfers:
        transfer_type = determine_transfer_type(transfer)
        if transfer_type == "contractless":
            return None  # ignore players with 'without club' periods for simplicity
        elif transfer_type == "loan_end":
            player_contract_list = update_contract_with_end_date(
                player_contract_list, loan_club_index, transfer)
        elif transfer_type == "sale":
            player_contract_list = add_new_contract_to_list(
                player_contract_list, transfer, False)
            contract_index += 1
            if contract_index > 0:
                player_contract_list = update_contract_with_end_date(
                    player_contract_list, perm_club_index, transfer)
            perm_club_index = contract_index
        elif transfer_type == "retirement":
            if contract_index > 0:
                player_contract_list = update_contract_with_end_date(
                    player_contract_list, perm_club_index, transfer)
            perm_club_index = contract_index
        elif transfer_type == "new_loan":
            player_contract_list = add_new_contract_to_list(
                player_contract_list, transfer, True)
            contract_index += 1
            loan_club_index = contract_index

    return player_contract_list


def find_irrelevant_contract_indices(contract_list: List[Contract]) -> List[int]:
    contracts_to_delete_indices = []
    contract_list_index = -1
    for contract in contract_list:
        contract_list_index += 1
        for regex_str in CONTRACTS_TO_DELETE_REGEX:
            # print(f"club: {contract.club}, regex_str: {regex_str}")
            if re.search(regex_str, contract.club):
                contracts_to_delete_indices.append(contract_list_index)
                # print("regex match found. appending")
            # else:
                # print("no regex match found. continuing")
        if contract.club.upper() in CONTRACTS_TO_DELETE:
            contracts_to_delete_indices.append(contract_list_index)
    return contracts_to_delete_indices


def remove_irrelevant_contracts(contract_list: List[Contract], contracts_to_remove_indices: List[int]) -> List[Contract]:
    for contract_list_index in reversed(contracts_to_remove_indices):
        contract_list.pop(contract_list_index)
    return contract_list


def find_and_remove_irrelevant_contracts(contract_list: List[Contract]) -> List[Contract]:
    contracts_to_remove_indices = find_irrelevant_contract_indices(contract_list)
    contract_list = remove_irrelevant_contracts(contract_list, contracts_to_remove_indices)
    return contract_list


def store_stats_rows_in_class_list(stats_soup) -> List[StatsTableRow]:
    table = stats_soup.find("table", {"class": "items"})
    rows = []
    tr_index = -1
    for tr in table.find_all("tr"):
        tr_index += 1
        if tr_index < 2:
            continue
        cells = [td for td in tr.find_all("td")]
        # cells = [td.text.strip() for td in tr.find_all("td")]
        league_link = cells[2].find("a")
        league_url = league_link["href"].split('/')
        league_id = league_url[-3]
        if DOMESTIC_LEAGUES.get(league_id):
            row = StatsTableRow(cells)
            rows.append(row)
    return rows


def generate_goals_and_appearances_dict(player_name, player_id, headers) -> dict:
    stats_soup = get_stats_soup(player_name, player_id, headers)
    table_rows = store_stats_rows_in_class_list(stats_soup)
    goals_and_appearances = {}
    for row in table_rows:
        if not goals_and_appearances.get(row.season):
            goals_and_appearances[row.season] = {}
        if goals_and_appearances[row.season].get(row.club_id):
            goals_and_appearances[row.season][row.club_id]["appearances"] += row.appearances
            goals_and_appearances[row.season][row.club_id]["goals"] += row.goals
        else:
            goals_and_appearances[row.season][row.club_id] = {
                "appearances": row.appearances,
                "goals": row.goals
            }
    return goals_and_appearances


def check_player_hasnt_multiple_contracts_for_same_club_in_same_season(contract, contract_list, contract_list_index, contract_season):
    if contract_list_index > 0:
        if contract_season in contract_list[contract_list_index-1].seasons and contract.club_id == contract_list[contract_list_index-1].club_id:
            if contract.club.upper() not in CONTRACTS_TO_DELETE:
                print(f"index-1: contract_season: {contract_season}, contract.club_id: {contract.club_id}")
                raise PlayerException("Multiple instances of same club in same season - stats would be inaccurate so skip")
    if contract_list_index > 1:
        if contract_season in contract_list[contract_list_index-2].seasons and contract.club_id == contract_list[contract_list_index-2].club_id:
            if contract_list[contract_list_index-1].club.upper() not in CONTRACTS_TO_DELETE:
                print(f"index-1: contract_season: {contract_season}, contract.club_id: {contract.club_id}")
                raise PlayerException("Multiple instances of same club in same season - stats would be inaccurate so skip")
            

def update_contracts_with_goals_and_appearances(contract_list: List[Contract], goals_and_appearances_dict: dict) -> List[Contract]:
    contract_list_index = 0
    for contract in contract_list:
        contract_seasons = []
        # start_season_first_year = int(contract.start_season.split('/')[0])+100
        # end_season_first_year = int(contract.end_season.split('/')[0])+100
        start_season_first_year = contract.start_season
        end_season_first_year = contract.end_season
        if end_season_first_year is None:
            # must be current contract - set end year to be current season
            current_year = int(datetime.datetime.today().strftime('%Y'))
            current_month = int(datetime.datetime.today().strftime('%m'))
            if current_month < 7:
                end_season_first_year = current_year-2001
            else:
                end_season_first_year = current_year-2000
        if start_season_first_year < 50:
            start_season_first_year += 100
        if end_season_first_year < 50:
            end_season_first_year += 100
        season_first_year = start_season_first_year
        while season_first_year <= end_season_first_year:
            contract_seasons.append(f"{str(season_first_year)[-2:]}/{str(season_first_year+1)[-2:]}") # print last 2 digits
            season_first_year += 1

        for contract_season in contract_seasons:
            try:
                check_player_hasnt_multiple_contracts_for_same_club_in_same_season(contract, contract_list, contract_list_index, contract_season)
                if contract_list[contract_list_index].appearances == NO_GOALS_APPEARANCES:
                    contract_list[contract_list_index].appearances = goals_and_appearances_dict[contract_season][contract.club_id]["appearances"]
                else:
                    contract_list[contract_list_index].appearances += goals_and_appearances_dict[contract_season][contract.club_id]["appearances"]
                if contract_list[contract_list_index].goals == NO_GOALS_APPEARANCES:
                    contract_list[contract_list_index].goals = goals_and_appearances_dict[contract_season][contract.club_id]["goals"]
                else:
                    contract_list[contract_list_index].goals += goals_and_appearances_dict[contract_season][contract.club_id]["goals"]
                # contract_list[contract_list_index].appearances += goals_and_appearances_dict[contract_season][contract.club_id]["appearances"]
                # contract_list[contract_list_index].goals += goals_and_appearances_dict[contract_season][contract.club_id]["goals"]
            except KeyError as e:
                try:
                    # Some leagues (Japan) are just 2022 instead of 2023
                    # if 22/23 fails, try 2022
                    first_year = int(contract_season[:2])
                    season = str(first_year + 2000 if first_year < 50 else first_year + 1900)
                    check_player_hasnt_multiple_contracts_for_same_club_in_same_season(contract, contract_list, contract_list_index, season)
                    if contract_list[contract_list_index].appearances == NO_GOALS_APPEARANCES:
                        contract_list[contract_list_index].appearances = goals_and_appearances_dict[season][contract.club_id]["appearances"]
                    else:
                        contract_list[contract_list_index].appearances += goals_and_appearances_dict[season][contract.club_id]["appearances"]
                    if contract_list[contract_list_index].goals == NO_GOALS_APPEARANCES:
                        contract_list[contract_list_index].goals = goals_and_appearances_dict[season][contract.club_id]["goals"]
                    else:
                        contract_list[contract_list_index].goals += goals_and_appearances_dict[season][contract.club_id]["goals"]
                except KeyError as er:
                    if not goals_and_appearances_dict.get(contract_season) and not goals_and_appearances_dict.get(season):
                        first_year_of_season = int(contract_season[:2])
                        if first_year_of_season != contract.end_season:
                            contract_list[contract_list_index].missing_stats = True
                except PlayerException:
                    print(f"clash: contract_season: {contract_season}")
                    return None
            except PlayerException:
                print(f"clash: contract_season: {contract_season}")
                return None
        contract_list[contract_list_index].seasons = contract_seasons
        contract_list_index += 1
    return contract_list


class PlayerException(Exception):
    pass

def has_played_100_games_in_a_big_5_league(player_id, player_name) -> bool:
    return True


def get_pretty_name_from_soup(transfer_soup) -> str:
    player_full_name = transfer_soup.find("title").text.split('-')[0][:-1]
    # elements = transfer_soup.find_all("tm-compare-player")
    # player_full_name = elements[0].get("player-full-name")
    return player_full_name


def scrape_player_details(player_url):
    player_id, player_name = get_player_id_and_name_from_url(player_url)
    transfer_soup = get_transfer_soup(player_name, player_id, headers)
    pretty_name = get_pretty_name_from_soup(transfer_soup)
    nationality, position = get_nationality_and_position_from_soup(
        transfer_soup)
    final_youth_year = get_final_youth_year_from_soup(transfer_soup, player_id)
    # club_history = load_club_history_from_transfer_divs(transfer_soup)
    club_history = load_club_history_from_json_call(player_id)
    transfers = convert_club_history_to_transfers(
        club_history, final_youth_year)
    contract_list = create_contract_list_from_transfers(transfers)
    if not contract_list:
        print("Contract_list is None - possible without club")
        return None
    goals_and_appearances = generate_goals_and_appearances_dict(player_name, player_id, headers)
    contract_list = update_contracts_with_goals_and_appearances(contract_list, goals_and_appearances)
    if not contract_list:
        print("Contract_list is None - multiple contracts with one club in one season")
        return None
    contract_list = find_and_remove_irrelevant_contracts(contract_list)
    # if not has_played_100_games_in_a_big_5_league(player_id, player_name):
    #     return None

    player = Player(pretty_name, nationality, position, contract_list)

    return player


def random_player_url():
    player_names, player_urls = get_player_names_and_urls_from_file(
        "player_transfermarkt_urls_subset.csv")
    player_url = player_urls[0]

    return player_url



if __name__ == "__main__":
    
    player_names, player_urls = get_player_names_and_urls_from_file(
        "curated_player_urls_small.csv")
    
    i = 0
    for player_url in player_urls:
        player = scrape_player_details(player_url)
        player.display()
        with open(f"player_stats/{player_names[i]}.json".replace(" ", ""), "w") as player_json_file:
            json.dump(player.info_dict(), player_json_file, indent=2)
        print("\n")
        i += 1
        
