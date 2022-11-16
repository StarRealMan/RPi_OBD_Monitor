import smbus
import math
import numpy as np

class IMU():
    def __init__(self, dt):
        self.bus = smbus.SMBus(1)
        self.device_address = 0x68
                
        self.kp = 0.5
        self.ki = 0.001
        self.dt = dt
        
        self.acc = np.array([0.0, 0.0, 0.0])
        self.gyro = np.array([0.0, 0.0, 0.0])
        self.gyro_bias = np.array([0.0, 0.0, 0.0])
        
        self.eular_angle = np.array([0, 0, 0])      # Order: RPY
        self.quaternion = np.array([1, 0, 0, 0])
        
        self.world_z = np.array([0, 0, 1])
        self.error_z_int = np.array([0, 0, 0])
        
        self.xy_plane_acc = np.array([0, 0])
        self.z_axis_acc = 0
        
        self.register = {
            "PWR_MGMT_1"  : 0x6B,
            "SMPLRT_DIV"  : 0x19,
            "CONFIG"      : 0x1A,
            "GYRO_CONFIG" : 0x1B,
            "INT_ENABLE"  : 0x38,
            "ACCEL_XOUT_H": 0x3B,
            "ACCEL_YOUT_H": 0x3D,
            "ACCEL_ZOUT_H": 0x3F,
            "GYRO_XOUT_H" : 0x43,
            "GYRO_YOUT_H" : 0x45,
            "GYRO_ZOUT_H" : 0x47
        }
        
        self.bus.write_byte_data(self.device_address, self.register["SMPLRT_DIV"], 7)
        self.bus.write_byte_data(self.device_address, self.register["PWR_MGMT_1"], 1)
        self.bus.write_byte_data(self.device_address, self.register["CONFIG"], 0)
        self.bus.write_byte_data(self.device_address, self.register["GYRO_CONFIG"], 24)
        self.bus.write_byte_data(self.device_address, self.register["INT_ENABLE"], 1)
	
    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.device_address, addr)
        low = self.bus.read_byte_data(self.device_address, addr+1)
        
        value = ((high << 8) | low)
        if value > 32768:
            value = value - 65536
        
        return value

    def read_gyro_data(self):
        # Unit: degree/s
        gyro_x = self.read_raw_data(self.register["GYRO_XOUT_H"])
        gyro_y = self.read_raw_data(self.register["GYRO_YOUT_H"])
        gyro_z = self.read_raw_data(self.register["GYRO_ZOUT_H"])
        self.gyro = np.array([gyro_x/131.0, gyro_y/131.0, gyro_z/131.0])

    def read_acc_data(self):
        # Unit: g
        acc_x = self.read_raw_data(self.register["ACCEL_XOUT_H"])
        acc_y = self.read_raw_data(self.register["ACCEL_YOUT_H"])
        acc_z = self.read_raw_data(self.register["ACCEL_ZOUT_H"])
        self.acc = np.array([acc_x/16384.0, acc_y/16384.0, acc_z/16384.0])
        
    def read_data(self):
        self.read_gyro_data()
        self.read_acc_data()
    
    def get_gyro(self):
        return self.gyro
    
    def get_acc(self):
        return self.acc
    
    def mahony(self):
        raw_gyro = self.get_gyro() - self.gyro_bias
        
        raw_acc = self.get_acc()
        norm_acc = raw_acc / np.linalg.norm(raw_acc)
        
        error_z = np.cross(norm_acc, self.world_z)
        self.error_z_int += self.ki * error_z * self.dt
        pseudo_gyro = raw_gyro + self.kp * error_z + self.error_z_int
        
        delta_angel = pseudo_gyro * self.dt
        delta_angel_mat = np.array([
            [0, -delta_angel[0], -delta_angel[1], -delta_angel[2]],
            [delta_angel[0], 0, delta_angel[2], -delta_angel[1]],
            [delta_angel[1], -delta_angel[2], 0, delta_angel[0]],
            [delta_angel[2], delta_angel[1], -delta_angel[0], 0]
        ])
        
        last_quaternion = self.quaternion.copy()
        self.quaternion = last_quaternion + 0.5 * delta_angel_mat @ last_quaternion
        
        self.quaternion = self.quaternion / np.linalg.norm(self.quaternion)
        self.quaternion_square = self.quaternion * self.quaternion
        
        R11 = self.quaternion_square[0] + self.quaternion_square[1] - self.quaternion_square[2] - self.quaternion_square[3]
        R21 = 2 * (self.quaternion[1] * self.quaternion[2] + self.quaternion[0] * self.quaternion[3])
        self.world_z[0] = 2 * (self.quaternion[1] * self.quaternion[3] - self.quaternion[0] * self.quaternion[2])
        self.world_z[1] = 2 * (self.quaternion[2] * self.quaternion[3] + self.quaternion[0] * self.quaternion[1])
        self.world_z[2] = self.quaternion_square[0] - self.quaternion_square[1] - self.quaternion_square[2] + self.quaternion_square[3]
        self.world_z = self.world_z / np.linalg.norm(self.world_z)
        
        if self.world_z[0] > 1:
            self.world_z[0] = 1
        if self.world_z[0] < -1:
            self.world_z[0] = -1
        
        self.eular_angle[0] = math.atan2(self.world_z[1], self.world_z[2]) * 180 / math.pi
        self.eular_angle[1] = math.asin(self.world_z[0]) * 180 / math.pi
        self.eular_angle[2] = math.atan2(R21, R11) * 180 / math.pi

        return self.eular_angle
    
    def get_world_z(self):
        return self.world_z
    
    def get_eular(self):
        return self.eular_angle
    
    def g_ball(self):
        raw_acc = self.get_acc()
        gravity = self.get_world_z()
        real_acc = raw_acc - gravity
        
        self.xy_plane_acc = np.array([real_acc[0], real_acc[1]])
        self.z_axis_acc = real_acc[2]
        
        return self.xy_plane_acc, self.z_axis_acc