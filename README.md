# Score24.com Fixture Scraper

A Python script that automates the extraction of League (Premier League, Ligue 1, Bundesliga, Serie A, Eredivisie & LaLiga) statistics using Playwright. This tool scrapes match data from [Soccer24](https://www.soccer24.com/), processes the information, and saves it in structured JSON files for further analysis or integration into other applications.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Automated Scraping**: Navigates to a specified League (Premier League, Ligue 1, Bundesliga, Serie A, Eredivisie & LaLiga) fixtures page and targets a specific round (e.g., Round 7) in any of the leagues to extract match data.
- **Detailed Statistics**: Retrieves comprehensive features & H2H statistics, including goals, expected goals (xG), corner kicks, fouls, and yellow cards (both first half and full time).
- **Structured Data Storage**: Saves the extracted data into sanitized JSON files, ensuring easy integration and analysis.
- **Robust Error Handling**: Implements error handling to manage potential issues during the scraping process, such as missing elements or timeout errors.
- **Configurable**: Easily adjust the target round or extend the scraper to accommodate additional data points.

## Prerequisites

- **Python 3.7+**: Ensure you have Python installed. You can download it from the [official website](https://www.python.org/downloads/).
- **Playwright**: A Python library for automating web browsers.
- **Git**: For version control (optional but recommended).

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/premier-league-h2h-scraper.git
   cd Score24_Data_Extractor
   ```
   
2. **Create a Virtual Environment (Optional but Recommended)**
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
3. **Install Dependencies**
   
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Install Dependencies**

   Playwright requires installing browser binaries. Run the following command:
   ```bash
   playwright install
   ```
   Note: If you encounter issues with Playwright installation, refer to the [official Playwright documentation](https://playwright.dev/python/docs/intro).

## Usage

### Configure the Base URL & Target Round

By default, the script targets [Premier League](https://www.soccer24.com/england/premier-league/fixtures/) & **"Round 7"**. To change the base url & round:

1. **Open `main.py` in a text editor.**

2. **Locate the following line:**

    ```python
    # Base URL
            page.goto("https://www.soccer24.com/england/premier-league/fixtures/", timeout=1800000)
    ```
    
    then

    ```python
    round_7_div = page.query_selector('//div[contains(text(),"Round 7")]')
    ```

3. **Modify the base url & round number as needed.** For example, to target [Bundesliga](https://www.soccer24.com/germany/bundesliga/fixtures/) "Round 8", update the line to:

   ```python
    # Base URL
            page.goto("https://www.soccer24.com/germany/bundesliga/fixtures/", timeout=1800000)
    ```

   then

    ```python
    round_7_div = page.query_selector('//div[contains(text(),"Round 8")]')
    ```

4. **Save the changes** and **run the script** to scrape data for the new round.

   ```bash
    python main.py
   ```

   ## The script will:

  - Launch a headless browser.
  - Navigate to the Bundesliga fixtures page on Soccer24.com.
  - Extract match links for the specified round.
  - For each match, navigate to the match details, extract H2H statistics, and save the data as JSON files in the `output/` directory.
  
  ### View the Output
  
  After successful execution, the `output/` directory will contain JSON files named after each fixture (e.g., `TeamA vs TeamB.json`).
  
  ---
  
  ## Output Structure
  
  Each JSON file follows the structure below:
  
  ```json
  {
      "fixture": "Home Team vs Away Team",
      "head_to_head": {
          "teams": {
              "match_one": ["Home Team", "Away Team"],
              "match_two": ["Home Team", "Away Team"]
              // ...
          },
          "goals": {
              "match_one": [2, 1],
              "match_two": [1, 1]
              // ...
          },
          "x_goals": {
              "match_one": [2.5, 1.8],
              "match_two": [1.7, 1.4]
              // ...
          },
          "corners": {
              "match_one": [5, 3],
              "match_two": [4, 4]
              // ...
          },
          "fouls": {
              "match_one": [10, 8],
              "match_two": [12, 9]
              // ...
          },
          "HT_cards": {
              "match_one": [1, 0],
              "match_two": [0, 2]
              // ...
          },
          "FT_cards": {
              "match_one": [2, 1],
              "match_two": [1, 3]
              // ...
          }
      }
  }
  ```

  - **`head_to_head`**: Contains various H2H statistics categorized under:
  - **`teams`**: Lists of the teams that played in each match.
  - **`goals`**: Goals scored by each team.
  - **`x_goals`**: Expected goals for each team.
  - **`corners`**: Number of corners for each team.
  - **`fouls`**: Number of fouls committed by each team.
  - **`HT_cards`**: First half yellow cards for each team.
  - **`FT_cards`**: Full-time yellow cards for each team.

  ## Project Structure

  ```lua
    BreadcrumbsScore24_Data_Extractor/
  ├── output/
  │   ├── TeamA vs TeamB.json
  │   ├── TeamC vs TeamD.json
  │   └── ...
  ├── main.py
  ├── requirements.txt
  ├── README.md
  └── .gitignore
  ```

   - `output/`: Directory where JSON files are saved.
   - `scraper.py`: Main Python script containing the scraping logic.
   - `requirements.txt`: Lists all Python dependencies.
   - `README.md`: Documentation (this file).
   - `.gitignore`: Specifies files and directories to ignore in Git.

   ### Troubleshooting

   #### Playwright Installation Issues
   
   Ensure you have the latest version of Playwright installed and that the browser binaries are correctly set up.
   
   ```bash
   pip install --upgrade playwright
   playwright install
   ```

   ### Timeout Errors

   If the script times out while loading pages or elements:
   
   - Increase the timeout duration in the script by modifying the timeout parameters.
   - Ensure a stable internet connection.
   - Verify that the website's structure hasn't changed, which might require updating the selectors.
   
   ### Missing Elements
   
   Websites often update their structures, which can break selectors. Inspect the target website to ensure that the selectors in `main.py` are still accurate.
   
   ### Contributing
   
   Contributions are welcome! Please follow these steps:
   
   #### Fork the Repository
   
   #### Create a Feature Branch
   
   ```bash
   git checkout -b feature/YourFeatureName
   ```


