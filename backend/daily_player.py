#! /home/ubuntu/careersle_backend/venv/bin/python
import argparse
import json
import random
from datetime import datetime, timedelta
from time import sleep

from playerdetailsscrape import Player, scrape_player_details

def log_write(string_to_write):
    with open('/home/ubuntu/json_gen/log.txt', 'a') as log_file:
        log_file.write(f"{datetime.now()}: {string_to_write}")

def newer_than_180_days(date_str):
    if date_str is None:
        return False

    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d")
        days_ago = datetime.now() - timedelta(days=180)
        return input_date > days_ago
    except ValueError:
        return False

def chosen_date_string(is_today: bool = False) -> str:
    future_days = 0 if is_today else 1
    print(f"future days: {future_days}")
    day = datetime.now() + timedelta(days=future_days)
    return day.strftime("%Y-%m-%d")

def generate_player_json(is_today: bool = False, run_now: bool = False):
    if not run_now:
        min_sleep = 10
        max_sleep = 58 * 60
        random_sleep_duration = random.randint(min_sleep, max_sleep)
        print(f"Sleeping {random_sleep_duration} seconds ({random_sleep_duration/60} minutes)")
        sleep(random_sleep_duration)
    else:
        print("skipping sleep")

    players_track_file_path = 'players_tracker.json'
    with open(players_track_file_path, 'r') as players_track_file:
        players_track_dict = json.load(players_track_file)

    player_chosen = False
    json_generated = False
    chosen_date = None
    random_player_id = None
    for json_gen_attempts in range(0,1000):
        if json_generated:
            break
        try:
            player_chosen = False
            for player_choose_attempts in range(0,1000):
                if player_chosen:
                    break
                random_player_id = random.choice(list(players_track_dict.keys()))
                player_meta = players_track_dict[random_player_id]
                if not newer_than_180_days(player_meta['last_featured']):
                    player_chosen = True

            chosen_date = chosen_date_string(is_today)

            player_details = scrape_player_details(player_meta['url'])

            with open(f'/var/www/piersaicken.com/html/careersle/api/{chosen_date}.json', 'w') as daily_json:
                json.dump(player_details.info_dict(), daily_json, indent=2)

            players_track_dict[random_player_id]['last_featured'] = chosen_date

            with open(players_track_file_path, 'w') as players_track_file:
                json.dump(players_track_dict, players_track_file, sort_keys=True, indent=2)
            json_generated = True
            log_write(f"SUCCESS. Player ID: {random_player_id}")
        except Exception as e:
            log_write(datetime.now())
            if player_chosen:
                log_write(f"ERROR. Player ID: {random_player_id}")
            log_write(f"Exception ocurred: {e}")
            random_player_id = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Career JSON')
    parser.add_argument('-n', '--run-now', action='store_true')
    parser.add_argument('-t', '--is-today', action='store_true')
    args = parser.parse_args()
    run_now = args.run_now
    is_today = args.is_today
    generate_player_json(is_today, run_now)
