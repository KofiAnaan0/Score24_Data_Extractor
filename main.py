import json
import os
import re  # For sanitizing filenames
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dataclasses import asdict, dataclass, field

# Define the data structures to match the desired JSON format
@dataclass
class HeadToHead:
    teams: dict = field(default_factory=dict)
    goals: dict = field(default_factory=dict)
    x_goals: dict = field(default_factory=dict)
    corners: dict = field(default_factory=dict)
    fouls: dict = field(default_factory=dict)
    HT_cards: dict = field(default_factory=dict)
    FT_cards: dict = field(default_factory=dict)

@dataclass
class FixtureData:
    fixture: str
    head_to_head: HeadToHead

def save_to_json(data: FixtureData, filename: str):
    """Save data as JSON file with sanitized filename."""
    if not os.path.exists("output"):
        os.makedirs("output")
    # Sanitize filename by removing invalid characters
    sanitized_filename = re.sub(r'[\\/:"*?<>|]+', "", filename)
    with open(f"output/{sanitized_filename}.json", "w", encoding='utf-8') as file:
        json.dump(asdict(data), file, indent=4, ensure_ascii=False)

def main():
    with sync_playwright() as p:
        try:
            # Launch browser
            browser = p.chromium.launch(headless=True)  # Set headless=True for faster performance
            page = browser.new_page()

            # Base URL
            page.goto("https://www.soccer24.com/england/premier-league/fixtures/", timeout=1800000)
            page.wait_for_timeout(2000)  # Wait for the page to load completely

            # Locate the specific div containing "Round 7"
            round_7_div = page.query_selector('//div[contains(text(),"Round 8")]')

            if round_7_div:
                # Find all sibling divs after "Round 7" containing match data
                match_links_handle = round_7_div.evaluate_handle(""" 
                    (round7) => {
                        let links = [];
                        let nextSibling = round7.nextElementSibling;
                        while (nextSibling && nextSibling.classList.contains('event__match')) {
                            let linkElement = nextSibling.querySelector('a.eventRowLink');
                            if (linkElement) {
                                links.push(linkElement.href);
                            }
                            nextSibling = nextSibling.nextElementSibling;
                        }
                        return links;
                    }
                """)
                links = match_links_handle.json_value()

                # Iterate through each match link, click it, and extract the required text
                for link in links:
                    page.goto(link)

                    # Extract the home team, away team, and divider ("-")
                    home_team_element = page.query_selector('a.participant__participantName.participant__overflow')
                    divider_element = page.query_selector('span.detailScore__divider')
                    away_team_element = page.query_selector('div.duelParticipant__away a.participant__participantName.participant__overflow')

                    if home_team_element and divider_element and away_team_element:
                        home_team = home_team_element.inner_text().strip()
                        divider = divider_element.inner_text().strip()
                        away_team = away_team_element.inner_text().strip()

                        # Store in variable 'fixture' and print
                        fixture = f"{home_team} vs {away_team}"
                        print(f"Fixture: {fixture}")
                    else:
                        print("Could not extract fixture details.")
                        continue  # Skip to the next link if fixture details are missing

                    # Initialize FixtureData instance
                    fixture_data = FixtureData(
                        fixture=fixture,
                        head_to_head=HeadToHead()
                    )

                    # Click on the "H2H" tab
                    try:
                        # Ensure the selector accurately targets the H2H tab
                        page.click('a[href*="#/h2h"] button[data-testid="wcl-tab"]')
                        page.wait_for_timeout(2000)  # Wait for H2H section to load

                        # Locate the "Head-to-head matches" section using XPath
                        h2h_section = page.query_selector('//div[contains(@class, "h2h__section") and .//div[contains(@class, "section__title") and normalize-space(text())="Head-to-head matches"]]')

                        if h2h_section:
                            # Within this section, select all h2h__row divs
                            h2h_rows = h2h_section.query_selector_all('div.h2h__row')

                            # Filter h2h_rows to include only those with year >= 20
                            filtered_h2h_rows = []
                            for row in h2h_rows:
                                date_element = row.query_selector('span.h2h__date')
                                if date_element:
                                    date_text = date_element.inner_text().strip()
                                    # Assuming date format is DD.MM.YY
                                    try:
                                        year = int(date_text.split('.')[-1])
                                        if year >= 20:
                                            filtered_h2h_rows.append(row)
                                            print(f"Including match from year: {year}")
                                        else:
                                            print(f"Excluding match from year: {year}")
                                    except ValueError:
                                        print(f"Invalid date format: {date_text}")
                                else:
                                    print("Date element not found in h2h__row.")
                            
                            # Now, use filtered_h2h_rows for further processing
                            # Limit to first five matches if necessary
                            for idx, row in enumerate(filtered_h2h_rows[:5], start=1):
                                match_key = f"match_{['one','two','three','four','five'][idx-1]}"

                                row_title = row.get_attribute('title')  # Optional: Get the title for logging
                                row.click()  # Click on the H2H match detail
                                print(f"Clicked on match detail: {row_title}")

                                # Wait for the new page to open
                                with page.context.expect_page() as new_page_event:
                                    pass  # No action needed here; the context manager handles it

                                new_page = new_page_event.value  # The newly opened page

                                # Wait for the new page to load completely
                                new_page.wait_for_load_state('domcontentloaded')

                                # Extract team names 
                                new_home_team_element = new_page.query_selector('div.duelParticipant__home a.participant__participantName.participant__overflow')
                                new_away_team_element = new_page.query_selector('div.duelParticipant__away a.participant__participantName.participant__overflow')

                                # Extract score
                                score_element = new_page.query_selector('div.detailScore__wrapper')
                                if score_element:
                                    try:
                                        score_spans = score_element.query_selector_all('span')
                                        score_home = int(score_spans[0].inner_text().strip())
                                        score_away = int(score_spans[2].inner_text().strip())
                                        goals = [score_home, score_away]
                                        fixture_data.head_to_head.goals[match_key] = goals
                                        print(f"goals = {goals}")
                                    except (IndexError, ValueError) as e:
                                        print(f"Error extracting goals: {e}")
                                        fixture_data.head_to_head.goals[match_key] = []
                                else:
                                    print("Could not extract score.")
                                    fixture_data.head_to_head.goals[match_key] = []

                                # Extract team names if available
                                if new_home_team_element and new_away_team_element:
                                    new_home_team = new_home_team_element.inner_text().strip()
                                    new_away_team = new_away_team_element.inner_text().strip()
                                    fixture_data.head_to_head.teams[match_key] = [new_home_team, new_away_team]
                                    print(f"Teams: {[new_home_team, new_away_team]}")
                                else:
                                    print("Could not extract team names.")
                                    fixture_data.head_to_head.teams[match_key] = []

                                # **Extract x_goals, corner kicks, fouls, and FT_cards from the stats section**
                                # Initialize statistics
                                fixture_data.head_to_head.x_goals[match_key] = []
                                fixture_data.head_to_head.corners[match_key] = []
                                fixture_data.head_to_head.fouls[match_key] = []
                                fixture_data.head_to_head.FT_cards[match_key] = []
                                # **Initialize HT_cards to ensure it's always set, even if extraction fails**
                                fixture_data.head_to_head.HT_cards[match_key] = []

                                # Click on the "Stats" button
                                try:
                                    # Define the selector for the Stats button
                                    stats_button_selector = 'a[href="#/match-summary/match-statistics"] button[data-testid="wcl-tab"]'

                                    # Wait for the Stats button to be available and click it
                                    stats_button = new_page.wait_for_selector(stats_button_selector, timeout=3000)
                                    if stats_button:
                                        stats_button.click()
                                        print("Clicked on the Stats button.")

                                        # Optionally, wait for the Stats section to load
                                        new_page.wait_for_timeout(2000)  # Adjust the timeout as needed

                                        # **Extract x_goals, corner kicks, fouls, and FT_cards from the stats section**
                                        # Locate all statistics rows
                                        stats_rows = new_page.query_selector_all('div._row_18zuy_8[data-testid="wcl-statistics"]')

                                        for stat_row in stats_rows:
                                            # Extract the category name
                                            category_element = stat_row.query_selector('div._category_1haer_4 strong')
                                            if not category_element:
                                                continue  # Skip if category not found

                                            category = category_element.inner_text().strip()

                                            # Extract home and away values
                                            home_value_element = stat_row.query_selector('div._value_7ptpb_4._homeValue_7ptpb_9[data-testid="wcl-statistics-value"] strong')
                                            away_value_element = stat_row.query_selector('div._value_7ptpb_4._awayValue_7ptpb_13[data-testid="wcl-statistics-value"] strong')

                                            if home_value_element and away_value_element:
                                                home_value_text = home_value_element.inner_text().strip()
                                                away_value_text = away_value_element.inner_text().strip()

                                                if category == "Expected Goals (xG)":
                                                    try:
                                                        home_xg = float(home_value_text)
                                                        away_xg = float(away_value_text)
                                                        fixture_data.head_to_head.x_goals[match_key] = [home_xg, away_xg]
                                                        print(f"x_goals = {[home_xg, away_xg]}")
                                                    except ValueError:
                                                        print(f"Error converting xG values: '{home_value_text}', '{away_value_text}'")
                                                        fixture_data.head_to_head.x_goals[match_key] = []

                                                elif category == "Corner Kicks":
                                                    try:
                                                        home_corners = int(home_value_text)
                                                        away_corners = int(away_value_text)
                                                        fixture_data.head_to_head.corners[match_key] = [home_corners, away_corners]
                                                        print(f"corners = {[home_corners, away_corners]}")
                                                    except ValueError:
                                                        print(f"Error converting Corner Kick values: '{home_value_text}', '{away_value_text}'")
                                                        fixture_data.head_to_head.corners[match_key] = []

                                                elif category == "Fouls":
                                                    try:
                                                        home_fouls = int(home_value_text)
                                                        away_fouls = int(away_value_text)
                                                        fixture_data.head_to_head.fouls[match_key] = [home_fouls, away_fouls]
                                                        print(f"fouls = {[home_fouls, away_fouls]}")
                                                    except ValueError:
                                                        print(f"Error converting Fouls values: '{home_value_text}', '{away_value_text}'")
                                                        fixture_data.head_to_head.fouls[match_key] = []

                                                elif category == "Yellow Cards":
                                                    try:
                                                        home_cards = int(home_value_text)
                                                        away_cards = int(away_value_text)
                                                        fixture_data.head_to_head.FT_cards[match_key] = [home_cards, away_cards]
                                                        print(f"FT_cards = {[home_cards, away_cards]}")
                                                    except ValueError:
                                                        print(f"Error converting Yellow Cards values: '{home_value_text}', '{away_value_text}'")
                                                        fixture_data.head_to_head.FT_cards[match_key] = []

                                except PlaywrightTimeoutError:
                                    print("Stats button not found or failed to load in time.")
                                except Exception as e:
                                    print(f"An error occurred while clicking the Stats button: {e}")
                                # **Extract HT_cards (Yellow Cards in 1st Half)**
                                try:
                                    # Define the selector for the "1st Half" button
                                    first_half_button_selector = 'a[title="1st Half"] button[data-testid="wcl-tab"]'

                                    # Wait for the "1st Half" button to be available and click it
                                    first_half_button = new_page.wait_for_selector(first_half_button_selector, timeout=3000)
                                    if first_half_button:
                                        first_half_button.click()
                                        print("Clicked on the 1st Half button.")

                                        # Optionally, wait for the 1st Half stats to load
                                        new_page.wait_for_timeout(2000)  # Adjust the timeout as needed

                                        # **Extract HT_cards (Yellow Cards in 1st Half)**
                                        # Locate all statistics rows in 1st Half
                                        first_half_stats_rows = new_page.query_selector_all('div._row_18zuy_8[data-testid="wcl-statistics"]')

                                        for fh_stat_row in first_half_stats_rows:
                                            # Extract the category name
                                            fh_category_element = fh_stat_row.query_selector('div._category_1haer_4 strong')
                                            if not fh_category_element:
                                                continue  # Skip if category not found

                                            fh_category = fh_category_element.inner_text().strip()

                                            if fh_category == "Yellow Cards":
                                                # Extract home and away values
                                                fh_home_value_element = fh_stat_row.query_selector('div._value_7ptpb_4._homeValue_7ptpb_9[data-testid="wcl-statistics-value"] strong')
                                                fh_away_value_element = fh_stat_row.query_selector('div._value_7ptpb_4._awayValue_7ptpb_13[data-testid="wcl-statistics-value"] strong')

                                                if fh_home_value_element and fh_away_value_element:
                                                    fh_home_value_text = fh_home_value_element.inner_text().strip()
                                                    fh_away_value_text = fh_away_value_element.inner_text().strip()

                                                    try:
                                                        home_ht_cards = int(fh_home_value_text)
                                                        away_ht_cards = int(fh_away_value_text)
                                                        fixture_data.head_to_head.HT_cards[match_key] = [home_ht_cards, away_ht_cards]
                                                        print(f"HT_cards = {[home_ht_cards, away_ht_cards]}")
                                                    except ValueError:
                                                        print(f"Error converting HT_cards values: '{fh_home_value_text}', '{fh_away_value_text}'")
                                                        # HT_cards[match_key] is already initialized to [] before extraction
                                                else:
                                                    print("Could not extract HT_cards values.")
                                                    # HT_cards[match_key] is already initialized to []
                                    else:
                                        print("1st Half button not found.")
                                        # HT_cards[match_key] remains as [] (initialized earlier)
                                except PlaywrightTimeoutError:
                                    print("1st Half button not found or failed to load in time.")
                                    # HT_cards[match_key] remains as [] (initialized earlier)
                                except Exception as e:
                                    print(f"An error occurred while clicking the 1st Half button: {e}")
                                    # HT_cards[match_key] remains as [] (initialized earlier)

                                # Close the new page after processing
                                new_page.close()
                                print(f"Closed tab after scraping match detail: {row_title}")

                                # Wait before continuing to the next row
                                page.wait_for_timeout(1000)  # Wait for the H2H section to reload

                        else:
                            print("Head-to-head matches section not found.")
                            continue  # Skip to the next match link
                    except PlaywrightTimeoutError:
                        print("H2H tab not found or failed to click.")
                        continue  # Skip to the next match link
                    except Exception as e:
                        print(f"An error occurred while processing H2H: {e}")
                        continue  # Skip to the next match link

                    # After collecting all head-to-head data, save to JSON
                    save_to_json(fixture_data, fixture)
                    print(f"Saved data for fixture: {fixture}")
            else:
                print("Round 7 not found.")

        except PlaywrightTimeoutError as e:
            print(f"Playwright Timeout Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Close browser instance when the job is done
            browser.close()

if __name__ == "__main__":
    main()
