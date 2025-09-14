import pandas as pd, Utils
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor

def predict():
    ML_alg = int(input("\nPick model: \n"
                   "'1': linear regression\n"
                   "'2': random forest \n "))
    if ML_alg == 1:
        ML_alg = Ridge(alpha=input("Pick an alpha value: "))
    else:
        ML_alg = RandomForestRegressor(n_estimators=50, random_state=1, min_samples_split=5)
    start_yr, end_yr = Utils.year_input("training")
    Predictor = Model(start_yr, end_yr, ML_alg)
    mean_ap, aps, predictions_df = Predictor.backtest()
    print(f"\nMean Average Precision: {mean_ap}")

class Model:
    """
    A Class which initiates a machine learning model for predicting the NBA MVP
    """
    def __init__(self, start_yr, end_yr, model):

        # Initializes our the core dataframe, and then adds additional columns for diagnostics
        self.df = pd.read_csv("../csvFiles/mvp-pg-team (clean).csv")

        #  The predictors we'll use to train our model
        self.predictors = self.predictors()
        self.years = list(range(start_yr, end_yr+1))

        # The type of model we will use for our ML procedure
        self.model = model


    def backtest(self):
        """
        Backtests on previous years' worth of data for predicting the NBA MVP
        :return: the model's mean precision (int), a list of all average precisions and a dataframe of the top 5 predicted players for each season
        """
        print("\nProcessing prediciton...")

        all_predictions = []
        aps =  []

        # We start at the 5th earliest year, so we can have at least 5 years' of data for training
        for year in self.years[5:]:

            # A dataframe for all the predictions made for that year
            predictions_df = self.train(year)
            all_predictions.append(predictions_df)
            aps.append(self.error_met(predictions_df))
        return sum(aps) / len (aps), aps, pd.concat(all_predictions)


    def predictors(self):
        """
        Gives the predictors (str) to use for our back-testing
        :return: list,
            A list containing the predictor columns for training
        """

        # A list of columns which contain a numerical datatype
        number_d_types = self.df.select_dtypes(include="number")

        # Selects only column names which are not directly correlated to MVP voting, to avoid overfitting
        return [col for col in number_d_types if col not in ["First", "Share", "Pts Max", "Pts Won"]]

    def train(self, year):
        """
        Trains an ML model, and creates a dataframe of the predictions
        :param year: int,
            The current year of data we're testing on
        :return: Dataframe,
            A dataframe containing the predictions, actual rank, predicted rank and difference between them
        """

        # Creates the training and test dataframe to use
        train_df = self.df[self.df["year"] < year]
        test_df = self.df[self.df["year"] == year]

        # Trains model being used, using the predictors from the training dataset, to predict the "Share" column
        self.model.fit(train_df[self.predictors], train_df["Share"])

        # Use our regression model to make predictions for the "Share" column using test data
        predictions = self.model.predict(test_df[self.predictors])
        predictions_df = pd.DataFrame(predictions, columns=["Predictions"], index=test_df.index)

        # concatenates the test "Player" and "Share" columns from the test dataframe, with the predictions dataframe
        Sh_predictions = pd.concat([test_df[["Player", "Share"]], predictions_df], axis=1)
        return self.rk_add(Sh_predictions)


    @staticmethod
    def rk_add(df):
        """
        Adds the rank (int), predicted rank (int) and the difference to the predictions dataframe.
        :param df: dataframe,
            The dataframe being modified
        :return: dataframe,
            The modified dataframe
        """
        df = df.sort_values("Share", ascending=False)

        # Adds a rank column, for the actual MVP rankings in that year
        df["Rk"] = list(range(1, df.shape[0]+1))
        df = df.sort_values("Predictions", ascending=False)

        # Adds a column for the models ranking predictions
        df["Predicted Rk"] = list(range(1, df.shape[0]+1))

        # Gets the difference between the actual ranking and the predicted ranking
        df["Difference"] = df["Rk"] - df["Predicted Rk"]
        return df

    @staticmethod
    def error_met(df):
        """
        calculates the mean error metric (int) for a dataframe.
        :param df: Dataframe,
            the dataframe we're finding the error metric of
        :return: int,
            the mean error metric
        """

        # A dataframe of the players that ranked top 5 in the final MVP voting results
        actual = df.sort_values("Share", ascending=False).head(5)

        # A dataframe sorted by players our model predicted highest in the MVP voting results
        predicted = df.sort_values("Predictions", ascending=False)
        ps = []
        found = 0
        seen = 1

        # index references the rows index (int) and row is the row itself (pd.Series)
        for index, row in predicted.iterrows():

            # if the value in a rows "player" column is in the actual top 5 rankings
            # Add a score to the ps list describing how close the models prediction was
            if row["Player"] in actual["Player"].values:
                found+=1
                ps.append(found/seen)
            seen +=1
        return sum(ps) / len(ps)