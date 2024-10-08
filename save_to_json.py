from dataclasses import asdict, dataclass, field
import json
import os

@dataclass
class RecentMatches:
    """Holds RecentMatches data"""
    teams: dict = field(default_factory=dict)
    goals: dict = field(default_factory=dict)
    x_goals: dict = field(default_factory=dict)
    corners: dict = field(default_factory=dict)
    fouls: dict = field(default_factory=dict)
    HT_cards: dict = field(default_factory=dict)
    FT_cards: dict = field(default_factory=dict)

@dataclass
class HomeTeam:
    """Holds Team data"""
    name: str = None
    recent_matches: RecentMatches = field(default_factory=RecentMatches)

@dataclass
class DataStructure:
    """Holds Home Team data"""
    home_team: HomeTeam = field(default_factory=HomeTeam)

def save_to_json(data: DataStructure, filename: str):
    """Save data as json file"""
    if not os.path.exists("output"):
        os.makedirs("output")
    with open(f"output/{filename}.json", "w") as file:
        json.dump(asdict(data), file, indent=4)

def main():
    # Sample structured data to demonstrate the format
    data = DataStructure(
        home_team=HomeTeam(
            name="Stuttgart",
            recent_matches=RecentMatches(
                teams={
                    "match_one": ["Stuttgart", "Mainz"],
                    "match_two": ["Freiburg", "Stuttgart"],
                    "match_three": ["Bayer Leverkusen", "Stuttgart"],
                    "match_four": ["Stuttgart", "B. Monchengladbach"],
                    "match_five": ["Augsburg", "Stuttgart"],
                    "match_six": ["Stuttgart", "Bayern Munich"],
                    "match_seven": ["Bayer Leverkusen", "Stuttgart"],
                },
                goals={
                    "match_one": [3, 3],
                    "match_two": [3, 1],
                    "match_three": [3, 2],
                    "match_four": [4, 0],
                    "match_five": [0, 1],
                    "match_six": [3, 1],
                    "match_seven": [2, 2],
                },
                x_goals={
                    "match_one": [5.21, 2.25],
                    "match_two": [2.66, 0.46],
                    "match_three": [2.77, 2.32],
                    "match_four": [1.84, 1.45],
                    "match_five": [0.71, 2.37],
                    "match_six": [1.97, 1.56],
                    "match_seven": [1.32, 1.76],
                },
                corners = {
                    "match_one": [11,2],
                    "match_two": [6,3],
                    "match_three": [10,3],
                    "match_four": [8,4],
                    "match_five": [5,5],
                    "match_six": [3,1],
                    "match_seven": [5,2]
                },
                fouls = {
                    "match_one": [6,12],
                    "match_two": [7,10],
                    "match_three": [10,20],
                    "match_four": [4,9],
                    "match_five": [15,9],
                    "match_six": [10,8],
                    "match_seven": [10,19]
                },
                HT_cards = {
                    "match_one": [1,0],
                    "match_two": [1,0],
                    "match_three": [1,1],
                    "match_four": [0,0],
                    "match_five": [0,1],
                    "match_six": [1,1],
                    "match_seven": [2,1]
                },
                FT_cards= {
                    "match_one": [4,2],
                    "match_two": [2,1],
                    "match_three": [5,5],
                    "match_four": [1,2],
                    "match_five": [4,2],
                    "match_six": [1,2],
                    "match_seven": [4,3]
                }
            )
        )
    )

     # Save the structured data to a JSON file
    save_to_json(data, "Stuttgart_data")

if __name__ == "__main__":
    main()
