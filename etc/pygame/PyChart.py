# -*- coding: utf-8 -*-

import pygame

import matplotlib.colors
import matplotlib.cm

def rgbColor(name, alpha=1.0):
    rgb = matplotlib.colors.to_rgb(name.lower())
    return (rgb[0] * 255, rgb[1] * 255, rgb[2] * 255, alpha * 255)

def color(style, value):
    color_map = {'spring':matplotlib.cm.spring,
                 'summer':matplotlib.cm.summer,
                 'autumn':matplotlib.cm.autumn,
                 'winter':matplotlib.cm.winter,
                 'copper':matplotlib.cm.copper,
                 'plasma':matplotlib.cm.plasma,
                 'magma':matplotlib.cm.magma,
                 'cividis':matplotlib.cm.cividis,
                 'hsv':matplotlib.cm.hsv}
    cm = color_map[style.lower()]
    c = cm(value)
    return (c[0] * 255, c[1] * 255, c[2] * 255)
    
class PyCandleChart:
    
    def __init__(self, title, window_size, frame_rate=30):
        global screen
        pygame.display.set_caption(title)
        success, failure = pygame.init()
        print("Initializing pygame: {0} success and {1} failure.".format(success, failure))
        self.window_size = window_size
        screen = pygame.display.set_mode(window_size)
        clock = pygame.time.Clock()
        self.clock = clock
        self.frame_rate = frame_rate
        pass
    
    def line(self, points, color, alpha=1.0, linewidth=1):
        if type(color) is str:
            c = rgbColor(color.lower(), alpha=alpha)
        else:
            c = color
        pygame.draw.line(screen, c, points[0], points[1]) #, int(linewidth))
        return
    
    def rect(self, point, size, color, alpha=1.0, linewidth=1):
        if type(color) is str:
            c = rgbColor(color.lower(), alpha=alpha)
        else:
            c = color
        pygame.draw.rect(screen, c, point + size) #, int(linewidth))
        return
        
    def text(self, point, text, color, alpha=1.0, font_size=24):
        if type(color) is str:
            c = rgbColor(color.lower(), alpha=alpha)
        else:
            c = color
        font = pygame.font.Font(None, font_size)
        t = font.render(text, True, c)
        screen.blit(t, point)
        return
        
    def loadImage(self, path):
        image = pygame.image.load(path).convert_alpha()
        return image
    
    def image(self, point, image):
        rect = image.get_rect().move(point[0], point[1])
        screen.blit(image, rect)
        return
        
    def main(self):
        screen.fill(rgbColor('white'))
        pygame.event.pump()
        loop = True
        while(loop):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    break
            self.render()
            pygame.display.update()
            pygame.time.delay(self.frame_rate)
        pygame.quit()
        return
    
    def render(self):
        self.line([(0,0), (100, 100)], 'red', alpha= 0.5)
        self.rect((50, 100), (10, 60), 'blue', alpha=0.6)
        self.text((200, 100), 'Great', 'green', alpha=0.1)
        
        
    
if __name__ == "__main__":
    chart = PyCandleChart('DJI [M5]', (480, 320))
    chart.main()
    