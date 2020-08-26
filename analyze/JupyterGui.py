# -*- coding: utf-8 -*-
from ipywidgets import Layout, Box, VBox, HBox, ButtonStyle, GridBox, Checkbox
from ipywidgets import Label, Text, Button, RadioButtons
from ipywidgets import FloatText, FloatSlider, FloatProgress, ToggleButton
from ipywidgets import Select, SelectionRangeSlider
from tkinter import Tk, filedialog, messagebox
from matplotlib.font_manager import FontProperties, win32FontDirectory
from datetime import datetime
import pandas as pd

def font(size):
    font_dir = win32FontDirectory()
    font = FontProperties(fname = font_dir +'/YuGothM.ttc', size=size)
    return font

class JupyterGui:
    
    def __init__(self):
        #self.createGui()
        pass
    
    def selectHolder(self, initial_dir):
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        root.lift()
        root.focus_force()
        return filedialog.askdirectory(initialdir= initial_dir)
    
    def selectFile(self, extension, initial_dir):
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        root.lift()
        root.focus_force()
        return filedialog.askopenfilename(filetypes=[('', extension)], initialdir= initial_dir)
        
    def createGui(self):
        sections = [self.createFileSelectSection(self.fileSelectAction, '', './', 100, 20),
                    self.createSectionSample1(),
                    self.createSectionSample2()]
        return VBox(sections)
    
    def createFileSelectSection(self, action, desctiption, initial_filepath, width, height):
        button = Button(description='Select File', layout=Layout(width=str(width) + 'px', height=str(height) + 'px'))
        button.on_click(action)
        label = Label(initial_filepath)
        return VBox([Label('Select File'), HBox([button, label])])
    
    def fileSelectAction(self, b):
        path = self.selectFile('csv', './')
        return path
    
    def createSectionSample1(self):
        label = Label('section11')
        checkbox1 = Checkbox(value=True, description='sample1', layout=Layout(width='auto', height='50px'))
        inputbox1 = Text(value='value1', placeholder='value', description='Value1')
        checkbox2 = Checkbox(value=True, description='sample1', layout=Layout(width='auto', height='50px'))
        inputbox2 = Text(value='value2', placeholder='value', description='Value2')
        boxes = [label, HBox([checkbox1, inputbox1]), HBox([checkbox2, inputbox2])]
        return VBox(boxes)
    
    def createSectionSample2(self):
        start_date = datetime(2018, 4, 24)
        end_date = datetime.now()
        dates = pd.date_range(start_date, end_date, freq='D')
        options = [(date.strftime(' %d %b %Y '), date) for date in dates]
        index = (0, len(options)-1)
        slider = SelectionRangeSlider(options=options,
                                                              index=index,
                                                              description='Dates',
                                                              orientation='horizontal',
                                                              layout={'width': '500px'} )
        return VBox([slider])
        
        
        