import obd

class OBD():
    def __init__(self):
        
        obd.logger.setLevel(obd.logging.DEBUG)
        self.connection = obd.Async("/dev/rfcomm0", protocol="6", baudrate="38400", 
                                    fast=False, timeout = 30)
        while len(self.connection.supported_commands) < 100:
            self.connection = obd.Async("/dev/rfcomm0", protocol="6", baudrate="38400", 
                                        fast=False, timeout = 30)

        self.info_list = [
            # Drive
            "RPM", 
            "SPEED", 
            "THROTTLE_POS", 
            "ENGINE_LOAD",                          # Power Output
            
            # Engine
            "OIL_TEMP", 
            "COOLANT_TEMP", 
            "FUEL_PRESSURE", 
            
            # Air
            "INTAKE_PRESSURE", 
            "INTAKE_TEMP", 
            "MAF",                                  # Air Flow Rate
            "AMBIANT_AIR_TEMP",
            "BAROMETRIC_PRESSURE", 
            
            # Casual
            "GET_DTC",
            "CONTROL_MODULE_VOLTAGE",               # Battery Voltage
        ]

    def cmd_id_2_name(self, id):
        return self.info_list[id]
    
    def register_cmd_watch(self, cmd_list):
        self.obd_cmd_list = []
        for cmd in cmd_list:
            if isinstance(cmd, int):
                cmd = self.cmd_id_2_name(cmd)
            obd_cmd = getattr(obd.commands, cmd)
            self.obd_cmd_list.append(obd_cmd)
            self.connection.watch(obd_cmd)
            
        self.connection.start()
    
    def query_cmd(self):
        response_list = []
        for obd_cmd in self.obd_cmd_list:
            response = self.connection.query(obd_cmd)
            response_list.append(response)
        
        return response_list
    
    def end_cmd_watch(self):
        print("OBD command watch end")
        self.connection.stop()
        
    def delete_cmd_watch(self):
        print("OBD command unwatched")
        self.connection.unwatch_all()