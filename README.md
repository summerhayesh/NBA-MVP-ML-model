# NBA MVP Machine Learning model


**This code is a fully functioning version of the project. Future potential improvements are detailed below**  

**This code is based off an online tutorial by [Dataquest](https://www.youtube.com/@Dataquestio). I adapted the 3 videos into a reuseable OOP-based pipeline  
[Webscraping,](https://www.youtube.com/watch?v=JGQGd-oa0l4&ab_channel=Dataquest)[ Data cleaning,](https://www.youtube.com/watch?v=LobWMsz35NM&ab_channel=Dataquest)[ Machine Learning model](https://www.youtube.com/watch?v=3cn1nHlbFVw&t=1560s&ab_channel=Dataquest)**  

This program is an end-to-end reuseable Python data pipeline that predicts the NBA MVP in a given season, given a set of data for that season.  

## Features  
- Webscraping: retrieves data from an online source (whilst conforming to the websites t&c's about webscraping)
  
- Data cleaning: cleans formats the data to make it ready for training, which includes labelling data, dealing with duplicate entries, and merging datasets to maximise the data diversity
  
- ML algorithms: implements linear regression and random forests to predict the MVP, whilst simultaneously using evaluation stratergies such as backtesting and designing error metrics

- EDA: also includes a very brief EDA (Exploratory Data Analysis) which to find some trends in the data and answer some questions
  
**Due to high rates of request activity on the target website [(Basketball Reference)](https://www.basketball-reference.com/), the webscraper may not function.   
In this event, the files that were scraped whilst website was still up and that were used to train the model have been included in the repository.**

## Quick demo:

Executing the program firstly will ask the user from which years they want to scrape data from  :

![Webscraper](https://github.com/summerhayesh/NBA-MVP-ML-model/blob/main/Webscraper_1.png)

The program then scrapes data, and stores it locally:

<img src="https://github.com/summerhayesh/NBA-MVP-ML-model/blob/main/File_storage.png" height="850">
