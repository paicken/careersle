import json

players_track_file_path = 'site/backend/players_tracker.json'
with open(players_track_file_path, 'r') as players_track_file:
    players_track_dict = json.load(players_track_file)

with open('chosen_players.csv', 'r') as chosen_players:
    player_lines = chosen_players.readlines()

for player_line in player_lines:
    player_id = player_line.split('/')[-1].strip()
    dict_key = f"id_{player_id}"
    if dict_key in players_track_dict:
        continue
    line_parts = player_line.split(',')
    player_name = line_parts[0].strip()
    player_url = line_parts[1].strip()
    players_track_dict[dict_key] = {
        "name": player_name,
        "url": player_url,
        "last_featured": None
    }

with open(players_track_file_path, 'w') as players_track_file:
    json.dump(players_track_dict, players_track_file, sort_keys=True, indent=2)