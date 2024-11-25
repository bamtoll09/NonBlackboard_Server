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

KST = datetime.timezone(datetime.timedelta(hours=9))

def connect(id, pw):
    options = Options()
    #options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    #options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)
    tz_params = {'timezoneId': 'Asia/Seoul'}
    browser.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

    url = 'https://kulms.korea.ac.kr/auth-saml/saml/login?apId=_147_1&redirectUrl='
    browser.get(url)

    print('Connecting Website...');

    try:
        time.sleep(4)

        if browser.current_url.startswith('https://sso.korea.ac.kr/saml/Auth.do'):
            print('Waiting Website...')

            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(
                    (By.ID, 'password')
                )
            )

            print('Logging in...');

            one_id = browser.find_element(By.ID, 'one_id')
            password = browser.find_element(By.ID, 'password')
            submit = browser.find_elements(By.CLASS_NAME, 'ibtn')

            one_id.send_keys(id)
            time.sleep(0.2)
            password.send_keys(pw)

            time.sleep(0.3)

            submit[0].click()
            time.sleep(0.3)

            print("Login Success!");

            try:
                alert_result = browser.switch_to.alert
                alert_result.accept()
                print('Alert accepted')
                return (202, "There is no information about your account on database.")
            except Exception as e:
                # print(e)
                print('There is no alert.')

            print("Waiting Streams...");

            time.sleep(13)

            print("Getting Streams...");

            # crawlling.py
            idList = []
            nameList = []
            titleList = []
            contentList = []
            clockList = []
            linkList = []
            result = {}

            soup = BeautifulSoup(browser.page_source, 'html.parser')

            element_ids = soup.select('div.element-details')

            for elem_id in element_ids:
                id = json.loads(elem_id['analytics-context'])['id']
                idList.append(id)

            # pprint(idList)

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

            pprint(titleList)

            content = soup.select('div.content')
            # print(content[7].text.strip().replace("\n", " "))

            for div in content:
                text = ' '.join(div.text.replace("\n", " ").replace("\xa0", "/").split())
                contentList.append(text)
            
            # pprint(contentList)

            clocks = soup.select('.js-split-datetime')
            
            for clock in clocks:
                date = clock.select_one('.date').text.strip()

                # Is there a gap of event
                if re.search('[A-z가-힣]', date):
                    pattern  = re.compile(r'[A-z가-힣]+\s?')
                    match = re.search(pattern, date).group()

                    time_before = 1

                    # "한 시간"
                    if match == "한 ":
                        match = date[2:]
                    else:
                        time_before = int(date[:date.find(match)])

                    delta = datetime.timedelta()

                    if match == "초":
                        delta = datetime.timedelta(seconds=time_before)
                        pass
                    elif match == "분":
                        delta = datetime.timedelta(minutes=time_before)
                        pass
                    elif match == "시간":
                        delta = datetime.timedelta(hours=time_before)
                        pass
                    else:
                        print("Unknown word: " + match)

                    date = (datetime.datetime.now(KST) - delta).strftime('%Y. %m. %d.')

                stime = clock.select_one('.time').text.strip()
                whole = date + ' ' + stime
                
                whole = datetime.datetime.strptime(whole, "%Y. %m. %d. %H:%M").strftime('%Y. %m. %d. %H:%M')

                # print(whole)

                clockList.append(whole)

            links = soup.select('.js-title-link')

            for link in links:
                link['href'] = link['href'].replace('ultra/', 'ultra/courses').replace('/outline', '/cl/outline')
                linkList.append(link['href'])

            for i in range(len(idList)):
                result[idList[i]] = [clockList[i], nameList[i], titleList[i], contentList[i], linkList[i]]

            msg = json.dumps(result, ensure_ascii=False)

            # print('6')

            # print(msg)

            # print('7')

            return (200, msg)
        
        else:
            return (202, 'Error')

    except Exception as e:
        print('Error', e)

    finally:
        browser.quit()
        
if __name__ == '__main__':
    import account
    connect(account.ID, account.PW)