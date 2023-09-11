import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
import re
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PIL import Image
from io import BytesIO


def scrape_daraz_products(url):
    """Scrape data from the https://www.daraz.com.bd/smartphones/ page.
    Args:
    url: The URL
    Returns:
    A list of information.
    """
    # Set up Chrome WebDriver with options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Provide the path to your ChromeDriver executable
    # driver = webdriver.Chrome(executable_path='path/to/chromedriver', options=chrome_options)
    # Set up ChromeDriver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Maximize the browser window
    driver.maximize_window()
    driver.get(url)
    time.sleep(10)
    # Set up WebDriverWait with a timeout of 10 seconds
    wait = WebDriverWait(driver, 10)
    price_high_low_filter = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//div[@title='Best Match'])[1]")))  # Replace with your class name
    price_high_low_filter.click()
    price_high_low = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//div[normalize-space()='Price high to low'])[1]")))  # Replace with your class name
    price_high_low.click()
    time.sleep(5)

    # Initialize a list to store all product data
    products_data = []

    # Function to scrape product data from a page and append it to the global list
    def scrape_and_append_data():
        indexy = 3  # the list has 40 item for this indexy = 41
        sl_no = 1

        # Loop through indices 1 to 10
        for index in range(1, indexy):
            # Find all div elements with the specified class name using WebDriverWait
            divs = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"(//div[@class='gridItem--Yd0sa'])[{index}]")))  # Replace with your class name
            divs.click()
            time.sleep(2)
            print(sl_no)
            # Get the current URL
            product_url = driver.current_url
            # Get the HTML source of the search results page
            html = driver.page_source

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            # print(soup.prettify())
            # Extract text and image badge URL
            product_title = soup.find('span', class_='pdp-mod-product-badge-title').text.strip()
            # badge_image_url = soup.find('img', class_='pdp-mod-product-badge')['src']
            # response = requests.get(badge_image_url)
            product_review_summary = soup.find('div', class_='pdp-review-summary').text.strip()

            product_price = soup.find('div', class_='pdp-product-price').text.strip()
            product_promotion_tag = soup.find('div', class_='pdp-mod-promotion-tags')
            product_detail_title = soup.find('h2', class_='pdp-mod-section-title outer-title').text.strip()
            product_highlights = soup.find('div', class_='html-content pdp-product-highlights').text.strip()
            # Download the image
            badge_image = soup.find('img', class_='pdp-mod-product-badge')
            product_image = soup.find('img', class_='pdp-mod-common-image gallery-preview-panel__image')
            if product_image:
                product_image_url = product_image['src']
                # Download the image
                response = requests.get(product_image_url)
                products_image = Image.open(BytesIO(response.content))
                print(f"Product image found: {product_image_url}")
            else:
                products_image = "No product image found"
                product_image_url = "No product image found"
                print("No product image found")
            print(product_title)
            print(product_price)

            if product_promotion_tag:
                product_promotion = product_promotion_tag.text.strip()
                print(product_promotion)
            else:
                print("No promotion for the product")
                product_promotion = "No promotion for the product"
            print(product_review_summary)

            if badge_image:
                badge_image_url = badge_image['src']
                # Download the image
                response = requests.get(badge_image_url)
                badges_image = Image.open(BytesIO(response.content))
                print("Daraz mall badge found")
                product_badge = "Daraz mall badge found"
            else:
                print("No badge found")
                product_badge = "NO Daraz mall badge found"
                badge_image_url = "NO Daraz mall badge found"
                badges_image = "NO Daraz mall badges images found"
            print(product_detail_title)
            print(product_highlights)

            # Append extracted data to ads_data list
            product_data = {
                "Product Per Page": sl_no,
                "Product Title": product_title,
                "Product Price": product_price,
                "Product Reviews": product_review_summary,
                "Product Promotion": product_promotion,
                "Product Badge": product_badge,
                "Product Details Title": product_detail_title,
                "Product URL": product_url,
                "Product Image": product_image_url,
                "Product Highlights": product_highlights,
            }
            products_data.append(product_data)

            # Define the image URL
            image_url = product_image_url.split("_.webp")[0]  # Replace with the actual image URL
            # Folder where you want to save the image
            save_folder = r"C:\Users\PP Istiak\PycharmProjects\Scapee_Daraz\images"  # Replace with the actual folder path

            # Ensure the folder exists, create it if it doesn't
            os.makedirs(save_folder, exist_ok=True)

            # Send an HTTP GET request to download the image
            response = requests.get(image_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the file name from the URL
                # Remove all special characters except spaces
                fileName = re.sub(r'[^\w\s]', '', product_title)
                file_name = os.path.basename(f"{fileName}.jpg")

                # Specify the full path for saving
                save_path = os.path.join(save_folder, file_name)

                # Save the image to the specified folder
                with open(save_path, "wb") as file:
                    file.write(response.content)

                print(f"Image saved to {save_path}")
            else:
                print(f"Failed to download the image from {image_url}")


            # Go back to the previous page
            driver.back()  # This takes you back to the original page
            sl_no += 1

    scrape_and_append_data()

    # Define an XPath for the "See Next Reviews" button
    see_next_list_xpath = "(//li[@class=' ant-pagination-next'])[1]"

    while True:
        try:
            # Find the "See Next Reviews" button and wait until it's clickable
            see_next_list = wait.until(EC.element_to_be_clickable((By.XPATH, see_next_list_xpath)))

            # Click the "See Next Reviews" button
            see_next_list.click()

            # Wait for some time (you can adjust this)
            time.sleep(5)

            # Scrape and append review data from the current page
            scrape_and_append_data()

        except Exception as e:
            print(f"No other product list exist")
            # print(f"An error occurred: {e}")
            break

    time.sleep(10)
    driver.quit()
    return products_data


def main():
    url = f"https://www.daraz.com.bd/smartphones/"
    products_data = scrape_daraz_products(url)

    # Create a DataFrame from the ads_data list
    product_df = pd.DataFrame(products_data)

    # Save the DataFrame to an Excel file
    existing_excel_filename = "daraz_product_data.xlsx"
    # Load the existing Excel file into a DataFrame
    try:
        existing_product_df = pd.read_excel(existing_excel_filename)
    except FileNotFoundError:
        existing_product_df = pd.DataFrame()  # Create an empty DataFrame if the file doesn't exist

    # Concatenate the new data with the existing DataFrame
    products_df = pd.concat([existing_product_df, product_df], ignore_index=True)

    # Save the concatenated DataFrame back to the Excel file
    products_df.to_excel(existing_excel_filename, index=False)
    print(f"Product Data appended to {existing_excel_filename}")


if __name__ == "__main__":
    main()
