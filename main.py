import requests
import random
import time
import json
import threading
import base64
from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator

proxies = open('proxies.txt', 'r').read().splitlines()

def ReverseImage(path, proxy1, word, lenamount):
    global proxies
    try:
        proxies.remove(proxy1)
    except: pass
    proxydict = {'https': f'https://{proxy1}'}

    imageupload = requests.post('https://PRIVATE-IMAGE-UPLOADER', data={"image": open(path, 'rb').read()})

    yandexresults = requests.get(f'https://yandex.com/images/search?url=https://PRIVATE-IMAGE-UPLOADER/i/{imageupload.text}&rpt=imageview', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}, proxies=proxydict, timeout=10)
    a = 'class="Button2 Button2_width_auto Button2_view_default Button2_size_l Button2_type_link Button2_tone_gray Tags-Item"><span class="Button2-Text">'
    
    if 'showcaptcha' in yandexresults.url:
        ReverseImage(path, random.choice(proxies), word, lenamount)

    for i in range(yandexresults.text.count(a)):
        translator = Translator()
        if word in translator.translate(yandexresults.text.split(a)[i + 1].split('</')[0], dest='en').text:
            return True
    return False

def Start(driver, img, proxy1, lenamount, word):
    path = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(7)) + '.jpeg'
    r = requests.get(img, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'})
    f = open(path, 'wb')
    for chunk in r:
        f.write(chunk)

    while True:
        try:
            if ReverseImage(path, proxy1, word, lenamount):
                print(f' [!] Image {str((lenamount-9)*-1)} is correct.')
                driver.find_elements_by_css_selector("div[class='task-image']")[int((lenamount-9)*-1)].click()
                break
            else:
                print(f' [!] Image {str((lenamount-9)*-1)} is incorrect.')
                break
            break
        except Exception as e: 
            pass

server = Server('browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat')
server.start()
proxy = server.create_proxy()

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
proxy.new_har(options={'captureContent':True})

driver.get('https://caspers.app/')
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[src^='https://assets.hcaptcha.com/captcha/v1/']")))
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,"checkbox"))).click()

time.sleep(5)

imglist = []

question = ''

for entry in proxy.har["log"]["entries"]:
    if entry["request"]["url"].startswith('https://imgs.hcaptcha.com/'):
        imglist.append(entry["request"]["url"])
    if entry['request']['url'] == 'https://hcaptcha.com/getcaptcha':
        question = json.loads(entry['response']['content']['text'])['requester_question']['en']

item = question.split(' ')[-1]

print(f' [!] Item: {item}')
print(f' [!] Pages: {str((len(imglist)-3)/9)}')

driver.switch_to.default_content()
WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='Main content of the hCaptcha challenge']")))

imglist = imglist[:len(imglist)-3]

for _ in range(int(len(imglist)/9)):
    currentpage = imglist[:9]
    for img in imglist[:9]:
        threading.Thread(target=Start, args=(driver, img, random.choice(proxies).strip(), len(currentpage), item)).start()
        currentpage.remove(img)
        imglist.remove(img)
    while threading.active_count() != 1:
        pass
    driver.find_element_by_css_selector("div[class='submit-background']").click()
    print('\n [!] Next Page\n')
    