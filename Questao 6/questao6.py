import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_author_quotes(author_name: str):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "http://quotes.toscrape.com/"
    driver.get(base_url)

    quotes_data = []

    
    while True:
        time.sleep(1)

        quotes = driver.find_elements(By.CLASS_NAME, "quote")

        for q in quotes:
            author = q.find_element(By.CLASS_NAME, "author").text.strip()

            
            if author.lower() == author_name.lower():
                text = q.find_element(By.CLASS_NAME, "text").text.strip()
                tag_elements = q.find_elements(By.CLASS_NAME, "tag")
                tags = [t.text for t in tag_elements]

                quotes_data.append({"text": text, "tags": tags})

        
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            next_btn.click()
        except:
            break  

    
    driver.get(base_url)

    while True:
        time.sleep(1)
        quotes = driver.find_elements(By.CLASS_NAME, "quote")

        for q in quotes:
            author = q.find_element(By.CLASS_NAME, "author").text.strip()

            if author.lower() == author_name.lower():
                about_link = q.find_element(By.TAG_NAME, "a").get_attribute("href")
                driver.get(about_link)
                time.sleep(1)

                
                born_date = driver.find_element(By.CLASS_NAME, "author-born-date").text
                born_location = driver.find_element(By.CLASS_NAME, "author-born-location").text
                description = driver.find_element(By.CLASS_NAME, "author-description").text

                driver.quit()

                return {
                    "author": {
                        "name": author_name,
                        "birth_date": born_date,
                        "birth_location": born_location,
                        "description": description.strip()
                    },
                    "quotes": quotes_data
                }

        
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            next_btn.click()
        except:
            break

    driver.quit()
    return None



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py \"J.K. Rowling\"")
        sys.exit(1)

    author_name = sys.argv[1]
    result = scrape_author_quotes(author_name)

    if result:
        import json
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print("Autora não encontrada.")
