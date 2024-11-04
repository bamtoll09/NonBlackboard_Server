from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from pprint import pprint   # for pretty print
import re # for regex
import json
import datetime
import time

def connect(id, pw):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    browser = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)

    url = 'https://kulms.korea.ac.kr/auth-saml/saml/login?apId=_147_1&redirectUrl='
    browser.get(url)

    print('1')

    print('2')

    try:
        time.sleep(4)

        if browser.current_url.startswith('https://sso.korea.ac.kr/saml/Auth.do'):
            print('waiting')

            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(
                    (By.ID, 'password')
                )
            )
            print('3')

            one_id = browser.find_element(By.ID, 'one_id')
            password = browser.find_element(By.ID, 'password')
            submit = browser.find_elements(By.CLASS_NAME, 'ibtn')

            one_id.send_keys(id)
            time.sleep(0.2)
            password.send_keys(pw)

            time.sleep(0.3)

            submit[0].click()

            time.sleep(0.3)

            try:
                alert_result = browser.switch_to.alert
                alert_result.accept()
                print('Alert accepted')
                return (404, "There is no information about your account on database.")
            except Exception as e:
                # print(e)
                print('There is no alert.')

            print('4')

            print('5')

            time.sleep(13)

            # crawlling.py
            nameList = []
            titleList = []
            contentList = []
            clockList = []
            result = {}

            soup = BeautifulSoup(browser.page_source, 'html.parser')

            course_name = soup.select('li.notification-default')

            for li in course_name:
                for a in li.select_one('a'):
                    text = a.text.strip()
                    text = text[text.find(']')+1:text.find('(')]
                    nameList.append(text)

            title = soup.select('div.name')
            
            for div in title:
                text = div.text.strip()
                titleList.append(text)

            content = soup.select('div.content')
            # print(content[7].text.strip().replace("\n", " "))

            for div in content:
                text = ' '.join(div.text.replace("\n", " ").replace("\xa0", "/").split())
                contentList.append(text)
            
            pprint(contentList)

            clocks = soup.select('.js-split-datetime')
            
            for clock in clocks:
                date = clock.select_one('.date').text.strip()

                if re.search('[A-z가-힣]', date):
                    date = datetime.date.today().strftime('%Y. %m. %d.')

                stime = clock.select_one('.time').text.strip()
                whole = date + ' ' + stime
                
                whole = datetime.datetime.strptime(whole, "%Y. %m. %d. %H:%M").strftime('%Y. %m. %d. %H:%M')

                print(whole)

                clockList.append(whole)

            for i in range(len(clockList)):
                result[clockList[i]] = [nameList[i], titleList[i], contentList[i]]

            msg = json.dumps(result, ensure_ascii=False)

            print('6')

            print(msg)

            print('7')

            return (200, msg)
        
        else:
            return (404, 'Error')

    except Exception as e:
        print('Error', e)

    finally:
        browser.quit()

# connect(ID, PASSWORD + '0')