import requests
import csv
from bs4 import BeautifulSoup
import re
import json
import random
import datetime
from copy import deepcopy

# from datetime import datetime
from time import sleep
from typing import List

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9",
}

leagues = [
    {"name": "bundesliga", "code": "L1"},
    {"name": "laliga", "code": "ES1"},
    {"name": "ligue-1", "code": "FR1"},
    {"name": "premier-league", "code": "GB1"},
    {"name": "serie-a", "code": "IT1"},
]

first_year = 2013
last_year = 2023


def sleep_rando_minute():
    random_sleep_duration = random.randint(45, 75)
    print(f".{random_sleep_duration}")
    sleep(random_sleep_duration)


def sleep_rando_second():
    random_sleep_duration = random.uniform(0.75, 1.25)
    sleep(random_sleep_duration)


def get_players_from_season(league: dict, year: int):
    season_url = f"https://www.transfermarkt.co.uk/{league['name']}/startseite/wettbewerb/{league['code']}/plus/?saison_id={year}"
    sleep_rando_minute()
    club_urls = get_clubs_for_season(season_url)
    for club_url in club_urls:
        sleep_rando_second()
        get_players_from_club(club_url, season_url)


def get_clubs_for_season(season_url: str):
    response = requests.get(season_url, headers=headers)
    league_soup = BeautifulSoup(response.text, "html.parser")
    div_yw1 = league_soup.find('div', id='yw1')
    club_urls = []
    if div_yw1:
        td_elements = div_yw1.find_all('td', class_='zentriert no-border-rechts')
        
        for td in td_elements:
            a_tag = td.find('a')
            if a_tag and a_tag.has_attr('href'):
                club_urls.append(f"https://www.transfermarkt.co.uk{a_tag['href']}")
    
    return club_urls


def get_players_from_club(club_url: str, season_url: str):
    print(f"Club: {club_url.split('/')[3]}")
    copied_headers = deepcopy(headers)
    copied_headers['Referer'] = season_url
    response = requests.get(club_url, headers=copied_headers)
    club_soup = BeautifulSoup(response.text, "html.parser")
    div_yw1 = club_soup.find('div', id='yw1')
    player_info = []
    if div_yw1:
        players_list_file = "players/players.csv"
        with open(players_list_file, 'a') as players_file:
            tables = div_yw1.find_all('table', class_="inline-table")
            
            for table in tables:
                td_hauptlink = table.find('td', class_="hauptlink")
                
                if td_hauptlink and td_hauptlink.find('a'):
                    player_id = td_hauptlink.find('a')['href'].strip().split('/')[-1]
                    text = td_hauptlink.find('a').get_text(strip=True)
                    
                    info = f"{player_id},{text}\n"
                    players_file.write(info)

                    player_info.append(info)
    
    return player_info


year = first_year
while year <= last_year:
    print(f"Year: {year}")
    for league in leagues:
        print(f"League: {league['name']}")
        get_players_from_season(league, year)
    year += 1
