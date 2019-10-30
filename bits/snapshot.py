from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import base64

chrome_options = Options()
chrome_options.add_argument("--ignore-gpu-blacklist")
chrome_options.add_argument("--use-gl")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument('window-size=2560,1440')
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver.exe")


def modelSnapshot(template_path, save_path,data_path):
    driver.get(os.path.abspath(template_path))
    model_info = {}
    model_info['maps'] ={}
    driver.execute_script("loadgltf(arguments[0]);", data_path)
    attempt = 0
    while attempt < 100:
        try:
            driver.get_screenshot_as_file("./test.png")
            dataDivs = driver.find_elements_by_xpath("//div[@id='model-info']/div")
            mapDivs = driver.find_elements_by_xpath("//div[@id='model-info']/div[@id='maps']/div")
            if dataDivs.__len__() < 2:
                continue
            for dataDiv in dataDivs:
                if dataDiv.get_attribute('id') != 'maps':
                    model_info[dataDiv.get_attribute('id')] = dataDiv.text
            for mapDiv in mapDivs:
                model_info['maps'][mapDiv.get_attribute('id')] = mapDiv.text
            if model_info.__len__() < 2:
                print(data_path)
            snapshotDiv = driver.find_element_by_id('snapshot')
            driver.get_screenshot_as_file("./test.png")
            with open(os.path.join(save_path,"preview.png"),"wb") as f:
                f.write(base64.b64decode(snapshotDiv.text.split(',')[1]))
            break
        except:
            time.sleep(1)
            attempt += 1
    # driver.execute_script("init();")
    return model_info




# modelSnapshot("./template.html",  os.path.abspath("../assets/models/2e1816c0").replace("\\","/"),  os.path.abspath("../assets/models/2e1816c0/scene.gltf").replace("\\","/")  )

