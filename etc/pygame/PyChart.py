# -*- coding: utf-8 -*-

import pygame
from utils import line, text, rect, rgbColor
    
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
        line(screen, [(0,0), (100, 100)], 'red', alpha= 0.5)
        rect(screen, (50, 100), (10, 60), 'blue', alpha=0.6)
        text(screen, (200, 100), 'Great', 'green', alpha=0.1)
        
        
    
if __name__ == "__main__":
    chart = PyCandleChart('DJI [M5]', (480, 320))
    chart.main()
    