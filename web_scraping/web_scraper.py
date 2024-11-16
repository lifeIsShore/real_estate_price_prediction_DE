from bs4 import BeautifulSoup
import csv
import logging
import requests
import re  # For sanitizing the address to be used in a filename

# Set up logging configuration
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,  # Use the dynamic log file name
        level=logging.WARNING,  # Log level: only high-level warnings will be saved
        format='%(message)s',  # only message no time or date
    )

def sanitize_filename(name):
    """
    Sanitizes the given string to make it a valid filename.
    """
    # Remove any characters that are not allowed in filenames
    return re.sub(r'[<>:"/\\|?*]', '', name).replace(" ", "_")

def scrape_immowelt(url, output_dir):
    """
    Scrapes real estate listings from Immowelt.de based on the provided URL and saves the data to a CSV file.
    The filename is dynamically created based on the first address listed.

    Args:
        url (str): The base URL of the Immowelt search page.
        output_dir (str): Directory path where the CSV file will be saved.
    """
    # Request first page and parse it
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract address from the first listing to create the file name
    first_listing = soup.find("div", class_="css-79elbk")
    first_address = first_listing.find("div", class_="css-ee7g92").text.strip() if first_listing else "Unknown"
    safe_address = sanitize_filename(first_address)  # Clean the address for use in the filename

    # Set the output CSV file path with the dynamic name
    output_csv = f"{output_dir}\\{safe_address}_ads.csv"
    
    # Set the dynamic log file name based on the address
    log_file = f"{output_dir}\\{safe_address}_scraper.log"
    
    # Setup logging with the dynamic log file
    setup_logging(log_file)

    # Find pagination and determine the last page number
    pagination = soup.find("ul", class_="css-bcim1s")
    page_numbers = []
    if pagination:
        for li in pagination.find_all("li"):
            button = li.find("button")
            if button:
                page_num = button.text.strip()
                if page_num.isdigit():
                    page_numbers.append(int(page_num))

    last_page_num = max(page_numbers) if page_numbers else 1
    logging.warning(f"Last page number: {last_page_num}")

    # Variables for tracking progress
    total_records = 0
    unknown_count = 0
    unknown_rows = []

    # Create and write to the CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # Write the header row to the CSV file
        writer.writerow(["Street", "City_Code", "Price", "Number of Rooms", "Living Area", "Land Size", "URL"])

        # Retrieve data from all pages
        for page in range(1, last_page_num + 1):
            logging.warning(f"Scraping page {page}...")
            response = requests.get(f"{url}&page={page}")
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract listings from the page
            listings = soup.find_all("div", class_="css-79elbk")

            for listing in listings:
                address = listing.find("div", class_="css-ee7g92").text.strip() if listing.find("div", class_="css-ee7g92") else "Unknown"
                price = listing.find("div", class_="css-11nox3k").text.strip() if listing.find("div", class_="css-11nox3k") else "Unknown"
                features = listing.find_all("div", class_="css-9u48bm")

                rooms = features[0].text.strip() if len(features) > 0 else "Unknown"
                living_area = features[2].text.strip() if len(features) > 2 else "Unknown"
                land_size = features[4].text.strip() if len(features) > 4 else "Unknown"
                
                # Extract URL
                address_url = "Unknown"
                link_tag = listing.find("a", class_="css-xt08q3")
                if link_tag:
                    address_url = link_tag['href']

                # Track unknown values
                unknowns = []
                if rooms == "Unknown":
                    unknowns.append("rooms")
                if living_area == "Unknown":
                    unknowns.append("living_area")
                if land_size == "Unknown":
                    unknowns.append("land_size")
                if address_url == "Unknown":
                    unknowns.append("url")
                
                if unknowns:
                    unknown_count += 1
                    unknown_rows.append((total_records + 1, unknowns))  # Add row index and unknown feature(s) to the list

                # Write data to CSV
                writer.writerow([address, price, rooms, living_area, land_size, address_url])
                total_records += 1

            # Log every 10th page for monitoring
            if page % 10 == 0:
                logging.warning(f"Finished scraping page {page}.")

    # Log summary after scraping is finished
    logging.warning(f"Total records scraped: {total_records}")
    logging.warning(f"Total unknown values found: {unknown_count}")
    for row in unknown_rows:
        logging.warning(f"Row {row[0]+1} has unknown values: {', '.join(row[1])}")

    logging.warning(f"Data has been successfully saved to '{output_csv}'.")

# Example of how to call the function with different URLs and output directory
base_url = "https://www.immowelt.de/classified-search?distributionTypes=Buy,Buy_Auction,Compulsory_Auction&estateTypes=House,Apartment&locations=AD08DE5960"
output_directory = r"C:\Users\ahmty\Desktop\web_scraping"  # The directory where you want to save the CSV and log files
scrape_immowelt(base_url, output_directory)
