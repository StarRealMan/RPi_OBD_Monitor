import pygame
import sys
# import obd_interface
            
class GUI():
    
    class GUI_Digit():
        def __init__(self, pose, font_size, color, font_path, int_places, dec_places = 0):
            self.pose = pose
            self.color = color
            self.int_places = int_places
            self.dec_places = dec_places
            self.size = (((int_places + dec_places) * 0.75 + 0.35) * font_size, 0.75 * font_size)
            
            self.font = pygame.font.Font(font_path, font_size)
            
        def render(self, screen, val):
            
            ph = ' '
            if val < 0:
                val = -val
                ph = '-'
            
            if self.dec_places == 0:
                if val >= pow(10, self.int_places):
                    str_val = '9' * self.int_places
                else:
                    str_val = str(round(val)).zfill(self.int_places)
            else:
                if val >= pow(10, self.int_places):
                    str_int = '9' * self.int_places
                    str_dec = '9' * self.dec_places
                else:
                    val = ("%." + str(self.dec_places) + "f") % float(val)
                    [str_int, str_dec] = val.split('.')
                    str_int = str_int.zfill(self.int_places)
                    
                str_val = str_int + '.' + str_dec
            
            text = self.font.render(ph + str_val, True, self.color)
            text_rect = text.get_rect()
            
            text_rect.center = (self.pose[0] + self.size[0] / 2, self.pose[1] + self.size[1] / 2)
            
            screen.blit(text, text_rect)
    
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
            
            if self.dir == 'v':
                val_size = (val_size[0], val_size[1] * val_portion)
                
            elif self.dir == '>':
                val_size = (val_size[0] * val_portion, val_size[1])
                
            elif self.dir == '<':
                val_pose = (val_pose[0] + val_size[0] * (1 - val_portion), val_pose[1])
                val_size = (val_size[0] * val_portion, val_size[1])
                
            else:
                val_pose = (val_pose[0], val_pose[1] + val_size[1] * (1 - val_portion))
                val_size = (val_size[0], val_size[1] * val_portion)
            
            val_size = (int(val_size[0]), int(val_size[1]))
            bar = pygame.Surface(val_size, flags = pygame.HWSURFACE)
            bar.fill(self.color)
            
            screen.blit(bar, val_pose)
    
    class GUI_Meter():
        def __init__(self, pose, size, min_val, max_val, pointer_path):
            self.pose = (pose[0] + size[0] / 2, pose[1] + size[1] / 2)
            self.min_val = min_val
            self.max_val = max_val
            
            self.pointer = pygame.image.load(pointer_path).convert_alpha()
            self.pointer = pygame.transform.scale(self.pointer, size)
            
        def render(self, screen, val):
            val_portion = (val - self.min_val) / (self.max_val - self.min_val)
            val_angle = val_portion * 270 - 135
            
            rot_pointer = pygame.transform.rotate(self.pointer, -val_angle)
            rot_rect = rot_pointer.get_rect()
            rot_rect.centerx = self.pose[0]
            rot_rect.centery = self.pose[1]
            
            screen.blit(rot_pointer, rot_rect)
            
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("RPi ODB Monitor v1.0")
        
        # for pc debug
        self.screen = pygame.display.set_mode((1024, 600))
        
        # for pi
        # self.screen = pygame.display.set_mode((1024, 600), flags = pygame.FULLSCREEN)
        
        self.clock = pygame.time.Clock()
        
        pointer_path = "assets/pointer.png"
        font_path = "assets/digifaw.ttf"
        foreground_path = "assets/foreground.png"
        background_path = "assets/background.png"
        
        self.componet = [
            None, 
            None, 
            self.GUI_Bar((50, 50), (50, 500), (255, 0, 0), 0.0, 100.0, "^"), 
            self.GUI_Bar((924, 50), (50, 500), (0, 0, 255), 0.0, 100.0, "^"), 
            self.GUI_Meter((137, 51), (300, 300), 20.0, 120.0, pointer_path), 
            self.GUI_Meter((587, 51), (300, 300), 50.0, 150.0, pointer_path), 
            self.GUI_Digit((162, 400), 40, (0, 0, 0), font_path, 3, 0), 
            self.GUI_Digit((334, 400), 40, (0, 0, 0), font_path, 3, 0), 
            self.GUI_Digit((560, 400), 40, (0, 0, 0), font_path, 2, 1), 
            self.GUI_Digit((742, 400), 40, (0, 0, 0), font_path, 2, 1), 
            self.GUI_Meter((437, 15), (150, 150), 94.0, 104.0, pointer_path), 
            self.GUI_Meter((437, 248), (150, 150), -40.0, 60.0, pointer_path), 
            None, 
            self.GUI_Bar((162, 510), (700, 50), (0, 255, 0), 11.0, 15.0, ">")
        ]
        
        self.foreground = pygame.image.load(foreground_path).convert_alpha()
        self.background = pygame.image.load(background_path).convert()
        
        # self.obd = obd_interface.OBD()
        # cmd_list = list(range(len(self.obd.info_list)))
        # self.obd.register_cmd_watch(cmd_list)
    
    def read_obd(self):
        # result = self.obd.query_cmd()
        
        result = [
            0.0, 
            0.0, 
            50.0, 
            50.0, 
            35.0, 
            89.4, 
            120, 
            140, 
            12.5, 
            43.6, 
            101, 
            20.5, 
            0.0, 
            13.5
        ]
        
        return result
    
    def render_foreground(self):
        self.screen.blit(self.foreground, (0, 0))
        
    def render_background(self):
        self.screen.blit(self.background, (0, 0))
        
    def render_dynamic(self):
        result = self.read_obd()
        for id, item in enumerate(self.componet):
            if item != None:
                val = result[id]
                item.render(self.screen, val)
       
    def run(self):
        while True:
            self.clock.tick(30)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pose = event.pos
                    if mouse_pose[0] > 984 and mouse_pose[1] < 40:
                        pygame.quit()
                        sys.exit()
            
            self.screen.fill((0, 0, 0))
            self.render_background()
            self.render_dynamic()
            self.render_foreground()
            
            pygame.display.update()