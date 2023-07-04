import json
import traceback
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
#from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_argument('disable-notifications')
    options.add_argument("incognito")

    # Use ChromeDriverManager to install the appropriate chromedriver binary
    webdriver_path = ChromeDriverManager().install()

    # Initialize the webdriver with the configured options and webdriver path
    driver = webdriver.Chrome(webdriver_path, options=options)

    wait = WebDriverWait(driver, 10)
    # Got to the webpage
    driver.get("https://www.klm.com.mx/")
    # click en botón rechazar cookies
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'bw-cookie-banner__button-basic'))).click()
    time.sleep(2)

    return driver


def look_in_kml(origen, destino, fecha, meses, driver, dict):
    origen = origen
    destino = destino
    fecha = fecha

    wait = WebDriverWait(driver, 10)
    # encontrar campo tipo de viaje (ida y vuelta, sólo ida)
    select_element = wait.until(EC.visibility_of_element_located((By.ID, "mat-input-0")))
    # Create a Select object from the element
    select = Select(select_element)

    # Select an option by its visible text
    select.select_by_visible_text("Sólo ida")  # Replace with the desired option

    # Alternatively, you can select an option by its value
    # select.select_by_value("roundtrip")

    # origen
    campo1 = driver.find_element(by="id", value="mat-input-1")
    campo1.clear()
    campo1.send_keys(origen)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'bw-search-station-item__station-subheading'))).click()
    time.sleep(1)
    # destino
    campo2 = driver.find_element(by="id", value="mat-input-2")
    campo2.clear()
    campo2.send_keys(destino)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'bw-search-station-item__station-subheading'))).click()
    time.sleep(1)
    # Click en continue (si hay)
    try:
        driver.find_element(by="xpath", value="/html/body/bw-app/bwc-page-template/mat-sidenav-container/mat-sidenav-content/div/main/div/bw-homepage-app-root/div/bw-homepage-promotion-slideshow/div/div[1]/div/bw-search-widget/mat-card/form/div[1]/div/div/div/div/button").click()
        time.sleep(1)
    except Exception as e:
        pass
    # click on buscar
    #wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-test='bwsfe-widget__search-button']"))).click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-test='bwsfe-widget__search-button']"))).click()
    time.sleep(7)

    for mes in range(meses):
        if mes > 0:
            try:
                # click on next month
                driver.find_element(by="xpath",
                                    value="//button[@aria-label='Mostrar tarifas del mes siguiente']").click()
                # make sure the page is fully loaded by looking for the visibility of an element
                # css_selector = 'button[data-test="bwsfe-month__day-inner"]'
                # wait = WebDriverWait(driver, 10)
                # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
                time.sleep(3)

            except Exception as e:
                print(f"an error occurred while clicking on next month button for {destino}")
                traceback.print_exc()
                break

        try:
            # get the code
            html_code = driver.page_source
            soup = BeautifulSoup(html_code, 'html.parser')

            # Extracting the data-price pairs
            data_price_elements = soup.find_all('button', class_='bw-month__day-inner')
        except Exception as e:
            print("an error occurred while getting the html code")
            traceback.print_exc()
            continue

        try:
            for element in data_price_elements:
                # Extracting the date
                date_element = element.find('span', class_='bwc-o-subheading bw-month__day-date')
                price_element = element.find('span', class_='bwc-o-caption bw-month__day-price')

                # Check if both date_element and price_element are None
                if date_element is None or price_element is None:
                    continue  # Skip this iteration if either element is None

                date = date_element['aria-label'].strip()
                price = price_element.text.strip()

                # Process the data-price pair (date and price)
                dict[destino][date] = price
        except Exception as e:
            print("an error occurred while scraping date/prices")
            traceback.print_exc()


def main():
    dict = {}
    origen = "Mexico"
    destinos = [ "Milan", "Amsterdam", "Praga", "Bremen", "Oslo", "Copenhague", "Budapest", "Bucarest", "Varsovia", "Cracovia", "Sarajevo", "Roma", "Riga", "Madrid"]
    fecha = "24 de junio de 2023"
    meses = 4

    driver = get_driver()
    for item in destinos:
        dict[item] = {}
        try:
            look_in_kml(origen, item, fecha, meses, driver, dict)
            driver.find_element(By.CSS_SELECTOR, "a.bwc-logo-header__logo-container-link").click()
            time.sleep(2)
            driver.refresh()
            time.sleep(2)
        except Exception as e:
            print("Maybe an error occurred while looking for the destine: ", item)
            # Extract data from the exception
            traceback.print_exc()

    # Close the browser
    driver.quit()

    # Convert the dictionary to JSON
    json_data = json.dumps(dict, indent=4)
    # Write JSON data to a file
    with open(f"from_{origen}", "w") as json_file:
        json_file.write(json_data)


main()