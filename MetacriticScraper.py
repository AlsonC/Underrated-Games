import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import time
import openpyxl
from tqdm import tqdm
from bs4 import BeautifulSoup

def main():

    # Get dates
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    current_time_str = datetime.now().strftime("%H:%M:%S")

    title = f"Top Games on Metacritic (Data fetched as of {current_time_str}, {current_date_str})"

    # Set up the driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Scrape the data
    all_data = pd.DataFrame()
    all_links = []  # List to store all links
    for i in range(1, 6):  # Adjust the range as needed to scrape more pages
        # print('='*20)
        print(f"Scraping page {i+1}")
        url = f'https://www.metacritic.com/browse/game/all/all/current-year/metascore/?page={i}'
        driver.get(url)
        time.sleep(1)  # Wait for the page to load
        # Save the raw HTML to a file
        with open('metacritic.txt', 'a', encoding='utf-8') as file:
            file.write(driver.page_source)
            file.write('\n\n')  # Separate pages with new lines
        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Extract data from the page
        game_cards = soup.find_all('div', class_='c-finderProductCard')
        for card in game_cards:
            try:
                # Extract game name
                name_tag = card.find('h3', class_='c-finderProductCard_titleHeading')
                game_name = name_tag.find_all('span')[-1].text.strip() if name_tag else "N/A"
                
                # Extract metascore
                metascore_tag = card.find('div', class_='c-siteReviewScore')
                metascore = metascore_tag.text.strip() if metascore_tag else "N/A"
                
                # Extract link
                link_tag = card.find('a', href=True)
                link = link_tag['href'] if link_tag else "N/A"
                all_links.append(link)
                
                all_data = pd.concat([all_data, pd.DataFrame([{
                    'Title': game_name,
                    'Score': metascore
                }])], ignore_index=True)
            except Exception as e:
                print(f"Error extracting data for a game: {e}")
    # Print all links
    print("Links:")
    for link in all_links:
        print(link)

    developers = []  # List to store developers
    publishers = []  # List to store publishers

    for link in all_links:
        try:
            # Construct the full URL
            full_url = f"https://www.metacritic.com{link}"
            driver.get(full_url)
            time.sleep(0.5)  # Wait for the page to load
            if all_links.index(link) == 0:
                # Save the raw HTML to a new txt file
                with open(f'metacritic_{link.split("/")[-1]}.txt', 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract developer
            developer = soup.find('div', class_='c-gameDetails_Developer')
            developer_name = developer.find('li').get_text(strip=True) if developer and developer.find('li') else "N/A"
            developers.append(developer_name)

            # Extract publisher
            publisher = soup.find('div', class_='c-gameDetails_Distributor')
            publisher_name = publisher.find('span', class_='g-outer-spacing-left-medium-fluid g-color-gray70 u-block').get_text(strip=True) if publisher and publisher.find('span', class_='g-outer-spacing-left-medium-fluid g-color-gray70 u-block') else "N/A"
            publishers.append(publisher_name)

            print("Developer:", developer_name)
            print("Publisher:", publisher_name)

        except Exception as e:
            print(f"Error extracting additional data for link {link}: {e}")

    # Add developers and publishers to the DataFrame
    all_data['Developer'] = developers
    all_data['Publisher'] = publishers
    
    driver.quit()

    # Print the data for debugging
    # print("Scraped Data Preview:")
    # print(all_data.head())
    # Save the DataFrame to an Excel file using openpyxl
    all_data.to_excel('MetacriticResults.xlsx', index=False, engine='openpyxl')




if __name__ == "__main__":
    main()
