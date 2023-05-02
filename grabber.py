import json
import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Vehicle:
    def __init__(self, image, year, make, model, color, engine, stockNumber, row, dateAdded):
        self.image = image
        self.year = year
        self.make = make
        self.model = model
        self.color = color
        self.engine = engine
        self.stockNumber = stockNumber
        self.row = row
        self.dateAdded = dateAdded

    def __repr__(self):
        return f"{self.image}\n{self.year}\n{self.make}\n{self.model}\n{self.color}\n{self.engine}\n{self.stockNumber}\n{self.row}\n{self.dateAdded}"


class VehicleScrapper:
    def __init__(self, makeQuery: str, modelQuery: str):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=chrome_options)
        self.url = "https://inventory.sturtevantauto.com/"
        self.makeQuery = makeQuery.upper()
        self.modelQuery = modelQuery.upper()
        self.browser.get(self.url)
        self.vehicleList = []

    def _traverseWebsite(self) -> None:
        # load make
        make = Select(self.browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div/form/select[1]"))
        make.select_by_visible_text(self.makeQuery)

        # wait for page to load the Models
        WebDriverWait(self.browser, 1).until(
            EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[2]/div/div/div/form/select[2]"), "TRAILBLAZER"))

        # load make
        model = Select(self.browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div/form/select[2]"))
        model.select_by_visible_text(self.modelQuery)

    def _scrapeTableAttributesList(self) -> list:
        self._traverseWebsite()
        attributeList = self.browser.find_elements(By.XPATH, "/html/body/div[2]/div/div/div/div[1]/table/tbody")

        rawVehicleDetails = []
        for i in range(len(attributeList)):
            rawVehicleDetails.append(attributeList[i].find_elements(By.TAG_NAME, "td"))
        return rawVehicleDetails[0]

    def _populateVehicles(self) -> None:
        vehicleAttributeList = self._scrapeTableAttributesList()
        for i in range(0, len(vehicleAttributeList), 9):
            self.vehicleList.append(Vehicle(
                vehicleAttributeList[i + 0].text,
                vehicleAttributeList[i + 1].text,
                vehicleAttributeList[i + 2].text,
                vehicleAttributeList[i + 3].text,
                vehicleAttributeList[i + 4].text,
                vehicleAttributeList[i + 5].text,
                vehicleAttributeList[i + 6].text,
                vehicleAttributeList[i + 7].text,
                vehicleAttributeList[i + 8].text,
            ))

    def getVehicles(self) -> list:
        start = time.time()
        print("Grabbing Info..")
        _ = self._scrapeTableAttributesList()
        self._populateVehicles()
        end = time.time()
        print(f"Took {int(end - start)} seconds to grab...")
        return self.vehicleList

    def dump(self):
        jsonStr = json.dumps([obj.__dict__ for obj in self.vehicleList], indent=4)
        now = time.strftime("%m%d%H%M")
        f = open(f"{now}-{self.makeQuery}-{self.modelQuery}.json", "w")
        f.write(jsonStr)
        f.close()
