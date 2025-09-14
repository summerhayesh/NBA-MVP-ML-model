import requests, pandas as pd, time, Utils
from ftfy import fix_text
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pathlib2 import Path
from bs4 import BeautifulSoup as bs
from io import StringIO

def run():
    start_year, end_year = Utils.year_input("scraping")
    user_years = list(range(start_year, end_year+1))
    MVP_scrape = MVPScraper(user_years)
    MVP_scrape.scrape()
    pg_scrape = PerGameScraper(user_years)
    pg_scrape.scrape()
    team_scrape = TeamScraper(user_years)
    team_scrape.scrape()

class Scraper:
    """
    A class which functions as the webscraper, as well as for saving data locally

    The code is structured using inheritance, to allow ease of variation between
    web scraping processes that is required, due to the type of data being scraped

    E.g. HTML Tables that contain each type of data, have different elements that need removing
    before they're turned into a dataframe.

        MVP data: Only a header needs removing
        Per-game data: A header, and a selection of headers within  the table
        Team data: A selection of headers need removing

    Child classes simply override the parent class method, when there are one of these variations
    """
    def __init__(self, years):
        """
        A selection of these variables are overridden, depending on the type of data web scraping
        :param years: list,
            a list of the years to scrape data from
        """
        self.years = years
        self.directory_name = None # The directory name for the current type of data being scraped
        self.URL = None
        self.table_CSS = None # CSS selector for the table containing the desired data
        self.header_CSS = None # CSS selector for the unwanted table headers
        self.unwanted_tr_CSS = None # CSS selector for unwanted table rows
        self.unwanted_column = None # CSS selector for unwanted columns

    def scrape(self):
        """
        Iterates through each year in the specified range (list), scraping specified data
        and saving into a DataFrame. Appends all dataframes into a list, then
        concatenates them and saves to a .csv file
        """
        dfs = []

        # Sees if directory for data type already exists
        self.directory_exists()
        for year in self.years:

            # Checking if directory already has this year's data
            data_exists = Utils.data_exists(self.file_path(year))
            if not data_exists:

                # Scrapes website's HTML containing desired data
                self.html_saver(year)

            # Gets df of data from HTML
            df = self.dataframe_retriever(year)
            dfs.append(df)
        complete_df = pd.concat(dfs)
        complete_df.to_csv('../csvFiles/{}.csv'.format(self.directory_name), index=False)
        print(f"Done processing {self.directory_name} data! \n")

    def dataframe_retriever(self, year):
        """
        Gets a dataframe from the raw HTML, and it's modifies columns
        :param year: int,
            integer representing current year of data being scraped
        :return: dataframe,
            A dataframe containing data for the current year.
        """

        # Finds the desired table from HTML
        table = self.table_retriever(year)

        # Turns table into a dataframe
        df = pd.read_html(StringIO(str(table)))[0]
        self.column_modifier(df, year)
        return df

    def directory_exists(self):
        """
        Checks if directory to hold data already exists, and creates it if not
        """
        directory_path = Path(f'../rawHTML/{self.directory_name}')
        if directory_path.exists():
            pass
        else:
            directory_path.mkdir()

    def file_path(self, year):
        """
        :param year: int,
            integer representing current year of data being scraped
        :return: str,
            file path to store data in, based on current year
        """
        return f'../rawHTML/{self.directory_name}/{year}.html'

    def table_retriever(self, year):
        """
        Parses the file for the desired table (HTML element), and fixes moji-bake in raw HTML
        :param year: int,
            integer representing current year of data being scraped
        :return: HTML element,
            table from raw HTML
        """

        # encoding='utf-8' specifies what to use to encode/decode the file
        with open(self.file_path(year), encoding='utf-8') as f:

            # Fixes any moji-bake
            fixed = fix_text(f.read())

            # Turn into a soup for parsing
            soup = bs(fixed, features='html.parser')
            print(f'Processing {year} data...')
            return self.table_selector(soup)

    def html_saver(self, year):
        """
        Retrieves HTML from target website and writes to a file
        :param year: int,
            integer representing current year of data being scraped
        """
        webpage = self.webpage_retriever(year)

        # Pause in-between requests, to not overload target website
        time.sleep(3)

        # Opening with 'w+' means a new file will be created/an existing one will be overwritten
        with open(self.file_path(year), 'w+', encoding='utf-8') as f:
            f.write(webpage.text)

    def tr_remover(self, soup):
        """
        Removes any unwanted HTML elements
        :param soup: bs4 object,
            beautiful soup of the raw HTML
        """
        unwanted_trs = self.unwanted_elements_sel(soup)
        for tr in unwanted_trs:
            tr.decompose() # Removes unwanted HTML elements from soup

    def table_selector(self, soup):
        self.tr_remover(soup) # Removes unwanted HTML elements inside the table
        return soup.select_one(self.table_CSS) # Uses CSS selectors to retrieve table from raw HTML

    def webpage_retriever(self, year):
        return requests.get(self.URL.format(year))


    @staticmethod
    def column_modifier(df, year):
        df['year'] = year # Adds a "year" column to df

    def unwanted_elements_sel(self, soup):
        """
        Just selects the unwanted header from the soup
        :param soup: bs4 object,
            bs4 object of raw HTML
        :return: list,
            a list of unwanted HTML elements
        """
        return soup.select(self.header_CSS)

class MVPScraper(Scraper):
    """
    A class for functions that are specific to web scraping MVP data
    """
    def __init__(self, years):
        """
        overrides variables (that are initialized in the parent class)
        that are required for scraping MVP data
        :param years: list,
            a list of the years to scrape data from
        """
        super().__init__(years)
        self.years = years
        self.directory_name = 'MVPs'
        self.URL = 'https://www.basketball-reference.com/awards/awards_{}.html'
        self.table_CSS = 'table#mvp'
        self.header_CSS = 'tr.over_header'

# Removes the single unwanted element

class PerGameScraper(Scraper):
    """
    A class for functions that are specific to web scraping Per-game data
    """
    def __init__(self, years):
        """
        Overrides variables required for scraping Per-game data
        :param years: list,
            a list of the years to scrape data from
        """
        super().__init__(years)
        self.directory_name = 'Per-game'
        self.URL = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'
        self.table_CSS = 'table#per_game_stats'
        self.header_CSS = 'tr.thead'
        self.unwanted_tr = 'tr.norank'

    def webpage_retriever(self, year):
        """
        Scrapes the rendered HTML of the page using Selenium
        :param year: int,
            integer representing current year of data being scraped
        :return: HTML,
            HTML of fully rendered webpage
        """

        # Launches a selenium service object to control the chrome webpage
        service = Service(r"C:\Users\summe\PyCharmProjects\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.get(self.URL.format(year))

        # Scrolls down in the explorer to render lazy HTML content
        driver.execute_script("window.scrollTo(1, 10000)")

        # Captures the HTML of our page after content is loaded
        html = driver.page_source
        driver.quit()
        return html

    def unwanted_elements_sel(self, soup):
        """
        Selects unwanted HTML elements from per-game raw HTML
        :param soup: bs4 object,
            bs4 object of raw HTML
        :return: list,
            a list of unwanted HTML elements
        """
        unwanted = soup.select(self.header_CSS)
        unwanted.append(soup.select_one(self.unwanted_tr))
        return unwanted

class TeamScraper(Scraper):
    """
    A class for functions that are specific to web scraping team data
    """

    def __init__(self, years):
        """
        Overrides variables required for scraping team data
        :param years: list,
            a list of the years to scrape data from
        """
        super().__init__(years)
        self.directory_name = 'Team-stats'
        self.URL = 'https://www.basketball-reference.com/leagues/NBA_{}_standings.html'
        self.table_CSS = 'table#divs_standings_{}'
        self.header_CSS = 'tr.thead'
        self.unwanted_column = '{} conference'


    def table_selector(self, soup):
        """
        Selects desired tables for team data
        :param soup: bs4 object,
             bs4 object of the raw HTML,
        :return: HTML elements,
            table elements from soup of HTML
        """
        self.tr_remover(soup)
        East_conf = soup.select_one(self.table_CSS.format('E'))
        West_conf = soup.select_one(self.table_CSS.format('W'))
        return East_conf, West_conf

    def column_modifier(self, dfs, year):
        """
        Modifies the columns in team dataframes to correctly display team name
        :param dfs: list,
            A list of dataframes, one for each conference (Western and Eastern)
        :param year:
        :return: integer representing current year of data being scraped
        """
        for df in dfs:
            df['year'] = year
        dfs[0]['Team'] = dfs[0]['Eastern Conference']
        dfs[1]['Team'] = dfs[1]['Western Conference']
        self.col_remover(dfs)

    @staticmethod
    def col_remover(dfs):
        """
        Simply deletes the columns named "Western Conference" and "Eastern Conference"
        :param dfs: list,
            A list of dataframes, one for each conference (Western and Eastern)
        """
        del dfs[0]['Eastern Conference']
        del dfs[1]['Western Conference']

    def dataframe_retriever(self, year):
        """
        Dataframe retriever function for scraping team data
        :param year: int,
            integer representing current year of data being scraped
        :return: dataframe
            concatenated dataframe for both Western + Eastern conference
        """

        # Finds the desired table from HTML
        tables = self.table_retriever(year)

        # Turns tables into dataframes and appends to a list
        dfs = [pd.read_html(StringIO(str(table)))[0] for table in tables]
        self.column_modifier(dfs, year)

        # Returns concatenated dataframes
        return pd.concat(dfs)