# -*- coding: utf-8 -*-

import os
import glob



def filePathList(dir_path, extension):
    c = dir_path[0]
    if c != '/' and c != '.' and c != '\\':
        path = './' + dir_path
    else:
        path = dir_path
    c = dir_path[-1]
    if c!= '/' and c!= '\\':
        path = path + '/'
    path += '*.' + extension
    file_list = glob.glob(path)
    return file_list

def fileNameList(dir_path, extension):
    file_list = filePathList(dir_path, extension)
    names = []
    for file in file_list:
        names.append(os.path.basename(file))
    return names

def test():
    file_list = filePathList('./data/click-sec/DJI2019', '*')
    print(file_list)
    
    file_names = fileNameList('./data/click-sec/DJI2019', '*')
    print(file_names)
    
    
if __name__ == '__main__':  
    test()