#! /home/piers/dev/careersle/venv/bin/python
import argparse
import json
import random
from time import sleep

from player_data_scraper import scrape_football_data


def processed_url(url: str):
    print(f"Processing URL: {url}")
    player_id = f"id_{url.split('/')[-1]}"
    print(f"player id: {player_id}")
    with open("players.json", "r") as player_json_file:
        players_dict = json.load(player_json_file)
    if player_id in players_dict:
        print(f"SKIP - {player_id} already file")
        return False
    player_info = scrape_football_data(url, load_transfers=False)
    if not player_info:
        print(f"FAIL - Cannot extract player info from '{url}'")
        return True
    players_dict[player_id] = player_info
    with open("players.json", "w") as player_json_file:
        json.dump(players_dict, player_json_file, sort_keys=True, indent=2)
    print(f"PASS - Added {player_info['name']} to file")
    with open('player_names.txt', 'a') as file:
        file.write(player_info['name'] + '\n')
    return True

def sort_names_file():
    with open('player_names.txt', 'r') as file:
        lines = file.readlines()
    lines.sort()
    with open('player_names.txt', 'w') as file:
        file.writelines(lines)


def urls_from_file(file_path: str):
    urls = []
    with open(file_path, "r") as file:
        for line in file:
            urls.append(line.strip())
    
    return urls


def main(urls: list[str], file_path: str):
    urls_to_process = []
    if urls:
        urls_to_process.extend(urls)
    if file_path:
        urls_to_process.extend(urls_from_file(file_path))
    for url in urls_to_process:
        if processed_url(url):
            sleep_time = round(random.uniform(3, 7), 2)
            print(f"Sleeping {sleep_time} seconds")
            sleep(sleep_time)
    sort_names_file()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process URLs either directly or from a file."
    )

    parser.add_argument("urls", nargs="*", help="List of URLs to process")
    parser.add_argument("-f", "--file", type=str, help="File containing list of URLs")

    args = parser.parse_args()

    if not args.urls and not args.file:
        parser.error(
            "No URLs provided. Add URLs or use the '-f' option to specify a file."
        )
    # print(f"args.urls, {args.urls}, args.file {args.file}")
    main(args.urls, args.file)
