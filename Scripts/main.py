import DataCleaner, Webscraper, ML

if __name__ == "__main__":
   # Commented out as webscraping functionality is down due to Basket ball reference receiving a large number of requests
   #Webscraper.run()
   DataCleaner.clean()
   ML.predict()


