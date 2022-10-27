import pygame
import sys
import obd_interface

class GUI():
    
    class GUI_Digit():
        def __init__(self, pose, size, color, int_places, dec_places = 0):
            font_path = "./digifaw.ttf"
            self.pose = pose
            self.color = color
            self.int_places = int_places
            self.dec_places = dec_places
            self.font = pygame.font.Font(font_path, size)
            
        def render(self, screen, val):
            if self.dec_places == 0:
                str_val = str(int(val))[-self.int_places:]
            else:
                [str_int, str_dec] = str(float(val)).split('.')
                str_int = str_int[-self.int_places:]
                str_dec = str_dec[:self.dec_places]
                str_val = str_int + '.' + str_dec
            
            text = self.font.render(str_val, True, self.color, background = None)
            textRect = text.get_rect()
            textRect.center = self.pose
            
            screen.blit(text, textRect)
    
    class GUI_Bar():
        def __init__(self, pose, size, color, min_val, max_val, increase_dir = "^"):
            self.pose = pose
            self.size = size
            self.color = color
            self.min_val = min_val
            self.max_val = max_val
            self.dir = increase_dir
            
        def render(self, screen, val):
            val_size = self.size
            val_pose = self.pose
            val_portion = (val - self.min_val) / (self.max_val - self.min_val)
            
            if dir == 'v':
                val_size[1] *= val_portion
                
            elif dir == '>':
                val_size[0] *= val_portion
                
            elif dir == '<':
                val_pose[0] *= 1 - val_portion
                val_size[0] *= val_portion
                
            else:
                val_pose[1] *= 1 - val_portion
                val_size[1] *= val_portion
            
            bar = pygame.Surface(val_size, flags = pygame.HWSURFACE)
            bar.fill(self.color)
            
            screen.blit(bar, val_pose)
    
    class GUI_Meter():
        def __init__(self):
            pass

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 600), flags = pygame.FULLSCREEN)
        pygame.display.set_caption("RPi ODB Monitor v1.0")
        self.font = pygame.font.Font("digifaw", 50)
        self.clock = pygame.time.Clock()
        
        self.obd = obd_interface.OBD()
        cmd_list = list(range(len(self.obd.info_list)))
        self.obd.register_cmd_watch(cmd_list)
    
    def read_obd(self):
        result = self.obd.query_cmd()
        
        return result
    
    def render(self):
        self.screen
        
    def run(self):
        while True:
            self.clock.tick(30)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
            
            self.render()
            pygame.display.update()
            
