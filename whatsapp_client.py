## IMPORTS ##
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import quote
from re import fullmatch
import time

# Driver Managers
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.opera import OperaDriverManager
# from webdriver_manager.utils import ChromeType

## RUNTIME VARIABLES ##
"""
Place the associated driver manager above depending on the browser you want to launch.
Selenium supports the following:
- Chrome
- Edge
- Firefox
- Opera
- Brave

Below the script is configured set to use an Edge browser. Be sure to change it according to the browser you use.
"""
browser = "Edge"

## INPUT ##
"""
Takes input related to sending a text from the recipient phone number and message.
"""
print("\n")
print("Write recipient phone number in format +[Country Code][Area Code][Rest]:")
phone_no = "+919482699499"
print("\nWrite message:")
message = str(input())

## HELPERS ##
"""
Functions that do self explanatory tasks
"""
def modify_number(phone_no):
    phone_no = phone_no.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return phone_no

def validate_number(phone_no):
    def check_number(number):
        return "+" in number or "_" in number

    if not check_number(number=phone_no):
        raise Exception("Country Code Missing in Phone Number!")

    if not fullmatch(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", phone_no):
        raise Exception("Invalid Phone Number.")
    return True

def set_browser(browser):
    install = lambda dm : dm.install()
    try:
        if (browser == "Edge"):
            bm = EdgeChromiumDriverManager()
            return webdriver.Edge(service=Service(install(bm)))
        elif (browser == "Chrome"):
            bm = ChromeDriverManager()
            return webdriver.Chrome(service=Service(install(bm)))
        elif (browser == "Firefox"):
            bm = GeckoDriverManager()
            return webdriver.Firefox(service=Service(install(bm)))
        elif (browser == "Opera"):
            bm = OperaDriverManager()
            return webdriver.Opera(service=Service(install(bm)))
        # elif (browser == "Brave"):
        #     bm = ChromeDriverManager(chrome_type=ChromeType.BRAVE)
        #     return webdriver.Chrome(service=Service(install(bm)))
    except:
        raise Exception("Browser not found")

## SCRIPT ##
"""
Uses Selenium to send a text
"""
phone_no = modify_number(phone_no)
if (validate_number(phone_no)):

    # Loads browser
    driver = set_browser(browser)
    
    # Goes to site
    site = f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}"
    driver.get(site)
    
    # Uses XPATH to find a send button
    element = lambda d : d.find_elements(by=By.XPATH, value="//div//button/span[@data-icon='send']")
    
    # Waits until send is found (in case of login)
    loaded = WebDriverWait(driver, 1000).until(method=element, message="User never signed in")
    
    # Loads a send button
    driver.implicitly_wait(10)

    send = element(driver)[0]

    site = f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}"
    driver.get(site)
    send = element(driver)[0]
    
    # Clicks the send button
    send.click()
    
    # Sleeps for 5 secs to allow time for text to send before closing window
    time.sleep(5) 
    
    # Closes window
    driver.close()
