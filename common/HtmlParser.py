# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import toolKit

class HtmlParser:
    
    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        return
    
    def td2text(self, td):
        out = []
        for string in td.strings:
            out.append(string)
        return out

    def td2Strings(self, td):
        s = td.text
        s = s.replace('\n', ' ')
        s = s.replace('[', ' ')
        s = s.replace(']', ' ')
        s = s.replace('(', ' ')
        s = s.replace(')', ' ')
        s = s.replace(',', '')
        s = s.strip()
        values = s.split()
        return values
    
    def td2floatValues(self, td):
        values = self.td2Strings(td)
        out = []
        for v in values:
            v = v.strip()
            if toolKit.isFloatString(v) :
                out.append(self.str2float(v))
        return out

    
