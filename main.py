from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import paho.mqtt.client as mqtt
from constants import *
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set('user', 'pass123')
client.connect(host='localhost', port=1883)
client.loop_start()

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
time.sleep(5)

old_message = {
  "sender": "",
  "date_and_time": "",
  "value": ""
}
while True:

  locator = (
    By.XPATH,
    "//span[contains(@class, 'html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs')]"
  )
  try:
    div_elements = WebDriverWait(driver, 3).until(
      expected_conditions.presence_of_all_elements_located(locator)
    )
  except TimeoutException: 
    print("Sender text missing")
    continue
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
  except TimeoutException: 
    print("Recent message missing")
    continue

  hover = ActionChains(driver).move_to_element(div_elements[-1])
  hover.perform()

  locator = (
    By.XPATH,
    "//div[contains(@class, 'x1cy8zhl x78zum5 xdt5ytf x193iq5w x1n2onr6 x1kxipp6')]/span[@aria-describedby]"
  )
  
  date_and_time = ""
  try:
    message_container = WebDriverWait(driver, 3).until(
      expected_conditions.presence_of_all_elements_located(locator)
    )
    tooltip_id = message_container[-1].get_attribute('aria-describedby')
    date_and_time_tooltip = driver.find_element(By.XPATH, f"//div[@id='{tooltip_id}']/div/div/span")
    date_and_time = date_and_time_tooltip.text
  except TimeoutException:
    print("Message container missing")

  message = {
    "sender": recent_sender,
    "date_and_time": date_and_time,
    "value": div_elements[-1].text
  }

  if old_message != message:
    old_message = message
    if 'pasundo' in message['value'].strip().lower():
	    client.publish('inTopic', f"{recent_sender} [{date_and_time}],{message['value']}")
    print(f"{recent_sender} [{date_and_time}]: {message["value"]}")
   
  if message["value"].lower().strip() == "exit":
    break

input("Press enter to quit...")
driver.quit()

client.loop_stop()
client.disconnect()

