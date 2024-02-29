from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from constants import *
import time

options = Options()
options.add_argument("-headless")

driver = webdriver.Firefox(options=options)
driver.get(BASE_URL)

email_addr_input = driver.find_element(By.XPATH, "//input[@name='email']")
password_input = driver.find_element(By.XPATH, "//input[@name='pass']")
login_button = driver.find_element(By.XPATH, "//button[@name='login']")

email_addr_input.send_keys(EMAIL_ADDRESS)
password_input.send_keys(PASSWORD)
login_button.click()

time.sleep(2)
driver.get(GROUP_CHAT_LINK)
time.sleep(10)

old_message = ""
while True:
  locator = (
    By.XPATH,
    "//span[contains(@class, 'html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs')]"
  )
  try:
    div_elements = WebDriverWait(driver, 3).until(
      expected_conditions.presence_of_all_elements_located(locator)
    )
  except TimeoutException: continue
  recent_sender = div_elements[-1].text

  locator = (
    By.XPATH,
    "//div[contains(@class, 'x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a x18lvrbx')]"
  )
  time.sleep(1)
  try:
    div_elements = WebDriverWait(driver, 3).until(
      expected_conditions.presence_of_all_elements_located(locator)
    )
  except TimeoutException: continue
  recent_message = div_elements[-1].text
  if old_message != recent_message:
    old_message = recent_message
    print(f"{recent_sender}: {recent_message}")
   
  if recent_message.lower().strip() == "exit":
    break

input("Press enter to quit...")
driver.quit()