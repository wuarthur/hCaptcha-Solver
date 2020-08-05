import requests
import random
import time
import json
import threading
import os
import multiprocessing
from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator

### CONFIG ###
proxies = open('proxies.txt', 'r').read().splitlines()

yandex_timeout = 5

server = Server('browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat')
server.start()

chrome_options = webdriver.ChromeOptions()

proxy = server.create_proxy()
chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
### CONFIG ###


class hCaptcha:
    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)


    def Upload(self, path):
        imageupload = requests.post('https://PRIVATE-IMAGE-UPLOADER', data={"image": open(path, 'rb').read()})
        return f'https://PRIVATE-IMAGE-UPLOADER/i/{imageupload.text}'


    def ReverseImage(self, link, word, lenamount):
        yandexproxy  =  random.choice(proxies)
        try: proxies.remove(yandexproxy)
        except: pass

        proxydict = {
            'https': f'https://{yandexproxy}'
        }

        yandexresults = requests.get(f'https://yandex.com/images/search?url={link}&rpt=imageview', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.'
            '4147.105 Safari/537.36'
        }, proxies=proxydict, timeout=yandex_timeout)

        htmlhandle = 'class="Button2 Button2_width_auto Button2_view_default Button2_size_l Button2_type_link Button2_to'
        'ne_gray Tags-Item"><span class="Button2-Text">'

        if 'showcaptcha' in yandexresults.url:
            self.ReverseImage(link, word, lenamount)

        for i in range(yandexresults.text.count(htmlhandle)):
            translator = Translator()
            translated = translator.translate(yandexresults.text.split(htmlhandle)[i + 1].split('</')[0], dest='en').text
            if word in translated or translated in word:
                return True
        return False


    def HandleReverseImg(self, img, lenamount, word):
        filename = ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(7))
        r = requests.get(img, stream=True)
        ftype = r.headers['content-type'].split('/')[1]
        if ';' in ftype:
            ftype = ftype.split(';')[0]

        f = open(f"images\\{filename}.{ftype}", 'wb')
        for chunk in r.raw:
            f.write(chunk)

        while True:
            try:
                link = self.Upload(f"images\\{filename}.{ftype}")
                break
            except:
                pass

        while True:
            try:
                if self.ReverseImage(link, word, lenamount):
                    print(f' [!] Image {str((lenamount-9)*-1)} is correct.')
                    self.driver.find_elements_by_css_selector("div[class='task-image']")[int((lenamount-9)*-1)].click()
                    break
                else:
                    print(f' [!] Image {str((lenamount-9)*-1)} is incorrect.')
                    break
            except Exception as e:
                pass

    def start(self):
        proxy.new_har(options={'captureContent': True})
        self.driver.get('https://caspers.app/')

        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src^='https://assets.hcaptcha.com/captcha/v1/']")))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "checkbox"))).click()

        time.sleep(5)

        imglist = []

        for entry in proxy.har["log"]["entries"]:
            if entry["request"]["url"].startswith('https://imgs.hcaptcha.com/'):
                imglist.append(entry["request"]["url"])
            if entry['request']['url'] == 'https://hcaptcha.com/getcaptcha':
                question = json.loads(entry['response']['content']['text'])['requester_question']['en']

        item = question.split(' ')[-1]
        print(f' [!] Item: {item}')
        print(f' [!] Pages: {str((len(imglist) - 3) / 9)}\n')

        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='Main content of the hCaptcha challenge']")))

        imglist = imglist[:len(imglist)-3]
        for pagenum in range(int(len(imglist)/9)):
            currentpage = imglist[:9]
            for img in imglist[:9]:
                threading.Thread(target=self.HandleReverseImg,
                                 args=(img, len(currentpage), item)).start()
                currentpage.remove(img)
                imglist.remove(img)
            while threading.active_count() != 1:
                pass
            if len(imglist) / 9 != pagenum + 1:
                self.driver.find_element_by_css_selector("div[class='submit-background']").click()
                print('\n [!] Next Page\n')
            else:
                self.driver.find_element_by_css_selector("div[class='submit-background']").click()
                print('\n [!] Done.\n')

if __name__ == '__main__':
    main = hCaptcha()
    main.start()
