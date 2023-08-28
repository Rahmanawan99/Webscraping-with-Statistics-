import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# Preprocess the 'Price' column in case the values are non-int values, we do this to get accurate stats of the prices.
def preprocess_price(price):
    # Handle missing values
    if pd.isna(price):
        return None

    # Remove non-numeric characters and convert to float
    price = price.replace('$', '').replace(',', '').strip()
    try:
        return float(price)
    except ValueError:
        return None
    
#Scraping starts here
def scrape_rolex_listings(reference_numbers, num_pages=1):
    """Scrape listings from eBay and calculate statistics.

    Args:
        reference_numbers: ITEM YOU WANT TO SEARCH CAN TAKE AN ARRAY INPUT AS WELL.
        num_pages: Number of pages to scrape (default and recommended is 3).

    Returns:
        A list in a csv file, containing the following information of the listing:
        * Title (does not work on beautiful soup since its dynamic, for titles you need to use scrappy however scraping titles are uselsss)
        * Price
        * Mean Median StdDv printed in console
    """

    listings = []

    for reference_number in reference_numbers:
        for page_number in range(1, num_pages + 1):
            #DO NOT CHANGE THE URL INSTEAD GO THE REFERENCE_NUMBER INPUT BELOW AND INSERT YOUR SEARCH QUERY THERE!
            url = f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw={reference_number}&_sacat=0&_pgn={page_number}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            items = soup.find_all("div", class_="s-item__info")

            for item in items:
                listing = {}
#DO NOT CHANGE THIS PART THIS IS DONE TO ACCORDINGLY TO EBAY LISTINGS PAGE. IN FUTURE THIS CODE DOESNT WORK THIS BLOCK MIGHT BE THE REASON AS PAGES CHANGE DYNAMICALLY
                title = item.find("h3", class_="s-item__title")
                if title is not None:
                    listing["title"] = title.text

                price = item.find("span", class_="s-item__price")
                if price is not None:
                    listing["price"] = price.text

                listings.append(listing)

    return listings

if __name__ == "__main__":
    #THE MOST IMPORTANT PART IS HERE, THE REFERENCE NUMBER IS WHAT YOU WANT TO SCRAPE OR WHAT YOU TYPE IN EBAY SEARCH BAR, IT COULD BE A SERIAL NUMBER A NAME I.E. ROLEX OR IPHONE 14 A6231 OR ANYTHING 
    reference_numbers = ["A2651"] #FOR MULTIPLE LISTINGS YOU CAN ADD MORE ITEMS AS AN ARRAY
    
    num_pages = 3  # Number of pages to scrape, top 3 pages are more than enough
    listings = scrape_rolex_listings(reference_numbers, num_pages)

    # Specify the CSV filename, you can change this accordingly
    csv_filename = "listings_iphone.csv"

    # Write the listings to a CSV file
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        #p.s. this code doesnt print the title as it is protected by ebay, try scrappy to get the titles, beautiful soup cannot do dynamic webpages
        csv_writer.writerow(["Title", "Price"])

        for listing in listings:
            csv_writer.writerow([listing.get("title", ""),
                                 listing.get("price", "")])

    print(f"Listings saved to {csv_filename}")

    # Now we read the CSV file and perform statistics
    df = pd.read_csv(csv_filename)
    
    # Preprocess the 'Price' column
    df['Price'] = df['Price'].apply(preprocess_price)
    
    # Prices filtered so that you can do this to get accurate results i.e. a ROlex cannot be under 300 
    filtered_prices = df[(df['Price'] > 300) ] #& (df['Price'] < 2000)]['Price']    #this code is for prices you want to keep under

    # Calculate statistics
    mean_price = filtered_prices.mean()
    median_price = filtered_prices.median()
    std_deviation = filtered_prices.std()
    
    # Print the statistics
    print(f"Mean Price: {mean_price}")
    print(f"Median Price: {median_price}")
    print(f"Standard Deviation: {std_deviation}")
