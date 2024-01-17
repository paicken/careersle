import json
import requests
from bs4 import BeautifulSoup
from time import sleep

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}


def scrape_football_data(url, load_transfers: bool = True):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        name_tag = soup.find("h1", class_="data-header__headline-wrapper")
        name = name_tag.get_text().strip() if name_tag else None

        player_info = soup.find_all("span", class_="info-table__content")
        position = None
        full_name = None
        citizenship = None
        for i in range(0, len(player_info) - 1):
            player_info_text: str = player_info[i].get_text().strip()
            player_info_text_plus_one: str = player_info[i + 1].get_text().strip()

            if player_info_text == "Position:":
                position = player_info_text_plus_one
            if player_info_text == "Full name:":
                full_name = player_info_text_plus_one
            if player_info_text == "Citizenship:":
                citizenship = player_info_text_plus_one.split("\xa0")[0]

        # Extracting Youth Clubs
        youth_clubs_section = soup.find(
            "div",
            class_="box tm-player-additional-data viewport-tracking",
            attrs={"data-viewport": "Jugendvereine"},
        )
        youth_clubs_text = (
            youth_clubs_section.find("div", class_="content").get_text().strip()
            if youth_clubs_section
            else ""
        )
        
        info_dict = {
            "name": name,
            "full_name": full_name,
            "citizenship": citizenship,
            "position": position
        }

        if load_transfers:
            youth_clubs = []
            if youth_clubs_text:
                clubs = youth_clubs_text.split("), ")
                for club in clubs:
                    club_details = club.strip(")").split(" (")
                    if len(club_details) == 2:
                        club_name, time_frame = club_details
                        youth_clubs.append({"club": club_name, "time_frame": time_frame})

            info_dict["youth_clubs"] = youth_clubs
        
        if not name and not full_name:
            return None
        
        return info_dict
        

    except requests.HTTPError as e:
        return f"HTTP Error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


# Example usage
print(
    json.dumps(
        scrape_football_data(
            "https://www.example.com"
        ),
        ensure_ascii=False,
        indent=2,
    )
)
# print(
    # json.dumps(
        # scrape_football_data(
            # "https://www.transfermarkt.co.uk/ronaldo/profil/spieler/3140"
        # ),
        # ensure_ascii=False,
        # indent=2,
    # )
# )
# sleep(6.87)
# print(
    # json.dumps(
        # scrape_football_data(
            # "https://www.transfermarkt.co.uk/zlatan-ibrahimovic/profil/spieler/3455"
        # ),
        # ensure_ascii=False,
        # indent=2,
    # )
# )
