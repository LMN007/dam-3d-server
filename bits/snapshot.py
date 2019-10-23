from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import os
import re
import json
import time
import base64

chrome_options = Options()
chrome_options.add_argument("--ignore-gpu-blacklist")
chrome_options.add_argument("--use-gl")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('window-size=2560,1440')

# template_path = "./template.html"

# data_path = "./data"
# if os.path.exists(data_path) is not True:
#     os.mkdir(data_path)

# driver.get(os.path.abspath(template_path))

# model_path = "./models"
# models = os.listdir(model_path)
# gltf_path_list = []
# for model in models:
#     chosen_model = os.path.join(model_path,model)
#     files = os.listdir(chosen_model)
#     for file in files:
#         if re.search("\.gltf",file) is not None:
#             gltf_path_list.append(os.path.join(chosen_model,file).replace("\\","/"))

# print(gltf_path_list)
# print(gltf_path_list.__len__())

# models_info = []
# count = 0
# for gltf in gltf_path_list:

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="chromedriver.exe")
def modelSnapshot(template_path, save_path,data_path):
    # print(os.path.abspath(template_path))
    driver.get(os.path.abspath(template_path))
    print(os.path.abspath(template_path))
    # driver.get(template_path)
    model_info = {}
    model_info['maps'] ={}
    print(data_path)
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
            #models_info.append(model_info)
            snapshotDiv = driver.find_element_by_id('snapshot')
            print(data_path, " ", model_info)
            with open(os.path.join(save_path,"snapshot.png"),"wb") as f:
                f.write(base64.b64decode(snapshotDiv.text.split(',')[1]))
            # with open(os.path.join(output_path,"data.json"),"w",encoding="utf-8") as f:
            #     f.write(json.dumps(model_info))
            break
        except:
            time.sleep(1)
            attempt += 1
        return model_info
# driver.execute_script("init();")