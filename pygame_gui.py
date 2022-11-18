import pygame
import sys
import obd_interface
import imu

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
            
    class GUI_Acc_Ball():
        def __init__(self, pose, size, color, max_val):
            self.pose = pose
            self.size = size
            self.color = color
            self.width = int(size / 10)
            self.max_val = max_val
            
        def render(self, screen, val):
            x_val_portion = val[0] / self.max_val
            y_val_portion = val[1] / self.max_val
            
            end_pos_x = self.pose[0] + x_val_portion * self.size / 2
            end_pos_y = self.pose[1] - y_val_portion * self.size / 2
            end_pose = (end_pos_x, end_pos_y)
            
            pygame.draw.line(screen, self.color, self.pose, end_pose, self.width)
            pygame.draw.circle(screen, self.color, self.pose, self.width * 3)
            
            screen.blit(screen, (0, 0))
    class GUI_Car_Rot():
        def __init__(self, pose, size, car_path):
            self.pose = (pose[0] + size[0] / 2, pose[1] + size[1] / 2)
            
            self.image = pygame.image.load(car_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, size)
            
        def render(self, screen, val):
            rot_image = pygame.transform.rotate(self.image, val)
            rot_rect = rot_image.get_rect()
            rot_rect.centerx = self.pose[0]
            rot_rect.centery = self.pose[1]
            
            screen.blit(rot_image, rot_rect)
            
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("RPi ODB Monitor v1.0")
        
        # for pc debug
        self.screen = pygame.display.set_mode((1024, 600))
        
        # for rpi
        # self.screen = pygame.display.set_mode((1024, 600), flags = pygame.FULLSCREEN)
        
        self.clock = pygame.time.Clock()
        
        pointer_path = "assets/pointer.png"
        font_path = "assets/digifaw.ttf"
        foreground_path = "assets/foreground.png"
        background_path = "assets/background.png"
        
        car_roll_rot = "assets/car_roll.png"
        car_pitch_rot = "assets/car_pitch.png"
        
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
        
        # self.obd = obd_interface.OBD()
        # if not self.obd.get_connection_status():
        #     pygame.quit()
        #     sys.exit()

        # cmd_list = list(range(len(self.obd.info_list)))
        # self.obd.register_cmd_watch(cmd_list)
                
        self.imu_component = [
            self.GUI_Acc_Ball((512, 205), 80, (255, 190, 0), 0.5), 
            self.GUI_Car_Rot((880, 45), 80, car_roll_rot), 
            self.GUI_Car_Rot((630, 45), 80, car_pitch_rot)
        ]
        
        # self.imu = imu.IMU(1.0/60)
        
        self.foreground = pygame.image.load(foreground_path).convert_alpha()
        self.background = pygame.image.load(background_path).convert()
    
    def read_obd(self):
        result = self.obd.query_cmd()
        
        return result
    
    def read_imu(self):
        eular_angle = self.imu.mahony()
        xy_acc, z_acc = self.imu.g_ball()
        
        return (xy_acc[0], xy_acc[1]), eular_angle[0], eular_angle[1]
    
    def render_foreground(self):
        self.screen.blit(self.foreground, (0, 0))
        
    def render_background(self):
        self.screen.blit(self.background, (0, 0))
        
    def render_dynamic(self):
        # result = self.read_obd()
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        for id, item in enumerate(self.componet):
            if item != None:
                val = result[id]
                item.render(self.screen, val)
       
        imu_result = self.read_imu()
        
        for id, item in enumerate(self.imu_component):
            if item != None:
                val = imu_result[id]
                item.render(self.screen, val)
       
    def run(self):
        while True:
            self.clock.tick(60)
            
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