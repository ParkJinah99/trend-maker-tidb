import pandas as pd
import math
from typing import Dict
import json

from src.config import logger  # Import the logger


class StatProcessor:
    def __init__(self, queries: dict, data: dict):
        """
        Initialize the StatProcessor class with the input data.

        :param data: A dictionary containing the input data with keys:
                     - ComparedBreakdownByRegion
                     - InterestByRegion
                     - InterestOverTime
        """
        self.data = data
        self.keywords = queries["q"].split(",")
        self.main_keyword = self.keywords[0]

    def process_data(self) -> dict:
        """
        Process all the data by merging the outputs of the different generation functions.

        :return: A dictionary containing all the merged data.
        """
        # Initialize an empty dictionary to store the processed data
        processed_data = {
            "queries": self.keywords,
            "ComparedBreakdownByRegion": self.generate_ComparedBreakdownByRegion(),
            "InterestByRegion": self.generate_interest_by_region(),
            "InterestOverTime": self.generate_interest_over_time(),
            "RelatedQueries": self.generate_related_queries(),
            "YouTubeSearch": self.generate_top_10_youtube_videos(),
            "ShoppingResults": self.generate_shopping(),
        }
        return processed_data

    def generate_ComparedBreakdownByRegion(self) -> Dict:
        """
        Produce a dictionary for the top seven and world aggregated locations by the percentage of the main query.

        :return: A dictionary containing the top seven locations and the world aggregated data.
        """
        compared_data = json.loads(self.data["ComparedBreakdownByRegion"])
        if compared_data:
            # Sort the compared data by the main query percentage in descending order
            sorted_data = sorted(
                compared_data, key=lambda x: x[self.main_keyword], reverse=True
            )

            # Get the top 7 locations
            top_7 = sorted_data[:7]

            # Calculate the "World" category by summing the values across all regions
            world_aggregated = {
                key: sum(entry[key] for entry in compared_data)
                for key in top_7[0]
                if key != "Location"
            }
            world_aggregated["Location"] = "World"

            # Combine the top 7 with the "World" category
            combined_data = top_7 + [world_aggregated]
            return combined_data
        return None

    def generate_interest_by_region(self) -> Dict:
        """
        Produce a dictionary for the top 10 most interested countries by total interest.

        :return: A dictionary containing the top 10 countries by total interest.
        """
        interest_data = json.loads(self.data["InterestByRegion"])
        df_interest = pd.DataFrame(interest_data)
        if df_interest.empty:
            return None
        df_interest.set_index("Location", inplace=True)

        # Calculate the total interest for each country
        df_interest["Total_Interest"] = df_interest.sum(axis=1)

        # Get the top 10 countries by total interest
        top_10 = df_interest.nlargest(10, "Total_Interest")

        # Convert to dictionary
        return top_10[["Total_Interest"]].to_dict()

    def generate_interest_over_time(self) -> Dict:
        """
        Produce a dictionary for the interest over time for the dynamically handled keywords.

        :return: A dictionary containing the interest over time data.
        """
        interest_time_data = json.loads(self.data["InterestOverTime"])
        df_time = pd.DataFrame(interest_time_data)
        if df_time.empty:
            return
        # Convert the 'Timestamp' to a readable date format
        df_time["Date"] = pd.to_datetime(df_time["Timestamp"], unit="s")
        df_time["Date"] = df_time["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Set the 'Date' as the index for the time series plot
        df_time.set_index("Date", inplace=True)

        # Dynamically select the columns to plot based on the keywords
        dynamic_columns = self.keywords

        # Convert to dictionary
        return df_time[dynamic_columns].to_dict()

    def generate_top_10_youtube_videos(self) -> Dict:
        """
        Produce a dictionary for the top 10 YouTube videos based on keyword scoring.

        :return: A dictionary containing the top 10 YouTube videos.
        """
        # Convert the video results into a DataFrame

        # Filter out rows where the first word in 'Published Date' is a number greater than 12 and contains "months"
        def filter_date(date_str):
            parts = date_str.split()
            if (
                len(parts) > 1
                and parts[0].isdigit()
                and int(parts[0]) > 12
                and "months" in date_str.lower()
            ):
                return False
            return True

        youtube_data = json.loads(self.data["YouTubeSearch"])
        df = pd.DataFrame(youtube_data)
        if df.empty:
            return None
        df = df[df["Published Date"].apply(filter_date)]

        # Initialize the trend_score with the views
        df["trend_score"] = df["Views"]

        # Increment the trend_score based on keyword matches in the title
        for keyword in self.keywords:
            df.loc[
                df["Title"].str.contains(keyword, case=False, na=False),
                "trend_score",
            ] += df["Views"]

        # Sort the DataFrame by trend_score
        df_sorted = df.sort_values(by="trend_score", ascending=False).head(10)

        # Select relevant columns to display
        df_display = df_sorted[["Title", "Published Date", "Views", "trend_score"]]

        # Convert to dictionary
        return df_display.to_dict()

    def generate_related_queries(self) -> Dict:
        """
        Produce a dictionary for the top 10 rising related queries by search volume.

        :return: A dictionary containing the top 10 rising related queries.
        """
        related_queries = json.loads(self.data["RelatedQueries"])
        df_related = pd.DataFrame(related_queries)
        if df_related.empty:
            return None
        # Filter out only the rising queries
        df_rising = df_related[df_related["Type"] == "rising"]

        # Sort the rising queries by search volume in descending order
        df_sorted = df_rising.sort_values(by="Extracted Value", ascending=False).head(
            10
        )

        # Convert to dictionary
        return df_sorted[["Query", "Extracted Value"]].to_dict()

    def generate_shopping(self) -> Dict:
        """
        Produce a dictionary for the top 10 products based on an improved trend score
        that considers both rating and the number of reviews, with logarithmic scaling
        applied to the review count.

        :return: A dictionary containing the top 10 products.
        """
        all_products = []
        # Check if self.data is a list of multiple datasets

        shopping_results = json.loads(self.data["ShoppingResults"])

        if shopping_results != None or shopping_results == []:
            # Process each product in the shopping results
            for product in shopping_results:
                title = product.get("Title", "")
                price = product.get("Price", "")
                source = product.get("Source", "")

                # Check if Rating and Reviews are not empty
                if product.get("Rating") and product.get("Reviews"):
                    rating = float(product.get("Rating", 0))
                    reviews = int(product.get("Reviews", 0))

                    # Apply logarithmic scaling to reviews
                    scaled_reviews = math.log1p(
                        reviews
                    )  # log1p(reviews) = log(1 + reviews)

                    # Calculate the trend score considering both rating and review influence
                    trend_score = rating * (1 + scaled_reviews)
                else:
                    rating = 0
                    reviews = 0
                    trend_score = 0
                # Append to the all_products list
                all_products.append(
                    {
                        "Title": title,
                        "Price": price,
                        "Rating": rating,
                        "Reviews": reviews,
                        "Source": source,
                        "Trend Score": trend_score,
                    }
                )

            # Convert all_products list to a pandas DataFrame
            df = pd.DataFrame(all_products)
            if df.empty:
                return None

            # Sort the products by trend score in descending order
            df_sorted = df.sort_values(by="Trend Score", ascending=False)

            # Get the top 10 products
            top_10_products_df = df_sorted.head(10)

            # Convert to dictionary
            return top_10_products_df.to_dict()
        return None
