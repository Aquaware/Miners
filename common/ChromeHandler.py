#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 21:58:49 2018

@author: iku
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import time

ChromePath = './chromedriver'
WaitTimeSec = 30


class ChromeHandler:
    
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=ChromePath)
        self.driver.implicitly_wait(WaitTimeSec)
        self.isOpen = False
        return
    
    def connect(self, urlString):
        self.driver.get(urlString)
        self.isOpen = True
        return
    
    def clickByLinkText(self, text):
        self.driver.find_element_by_partial_link_text(text).click()
        return        

    def switchTabByTitle(self, title):
        found = False
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            if self.driver.title == title:
                found= True
                break
        return found
    
    def html(self):
        return self.driver.page_source
    
    def inputElement(self, elementId, text):
        element = self.driver.find_element_by_id(elementId)
        element.send_keys(text)
        return
    
    def clickButtonByName(self, elementName):
        button = self.driver.find_element_by_name(elementName)
        button.click()
        return
    
    def clickButtonById(self, elementId):
        button = self.driver.find_element_by_id(elementId)
        button.click()
        return
    
    def linkByText(self, text):
        element = self.driver.find_element_by_link_text(text)
        element.click()
        return        
        
    def linkByClassName(self, className):
        element = self.driver.find_element_by_class_name(className)
        element.click()
        return
    
    def linksByClassName(self, className, index):
        elements = self.driver.find_elements_by_class_name(className)
        if len(elements) > index:
            elements[index].click()
        return len(elements)
    
    
    def selectListByName(self, elementName, value):
        element = self.driver.find_element_by_name(elementName)
        dropdown = Select(element)
        dropdown.select_by_value(value)
        return
    
    def close(self):
        if self.isOpen:
            self.driver.close()
            self.isOpen = False
        return
    
    def screenShot(self, filepath):
        self.driver.save_screenshot(filepath)
        return

    def executeJS(self, script, args):
        self.driver.execute_script(script, args)
        pass