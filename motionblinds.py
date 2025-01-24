import asyncio
from motionblinds import MotionGateway, MotionBlind
import re
from .. import fhem, generic


class motionblinds(generic.FhemModule):

    devtypes = {"02000001":"Gateway", "02000002":"Gateway","10000000":"Standard Blind", "10000001":"Top/Down Bottom/Up", "10000002":"Double Roller"}
    readings = {"blind.device_type": "type", "blind.status": "status", "blind.position": "position", "blind.angle": "angle", "blind.limit_status":"limits", "blind.battery_voltage": "battery_voltage", "blind.battey_level":"battery_level", "blind.is_charging":"is_charging", "blind.RSSI":"RSSI"}

    blindtype = ["RollerBlind",
        "VenetianBlind",
        "RomanBlind",
        "HoneycombBlind",
        "ShangriLaBlind",
        "RollerShutter",
        "RollerGate",
        "Awning",
        "TopDownBottomUp",
        "DayNightBlind",
        "DimmingBlind" ,
        "Curtain" ,
        "CurtainLeft",
        "CurtainRight" ,
        "DoubleRoller" ,
        "VerticalBlindLeft",
        "WoodShutter" ,
        "SkylightBlind" ,
        "DualShade" ,
        "VerticalBlind" ,
        "VerticalBlindRight",
        "WovenWoodShades",
        "Switch" ,
        "InsectScreen" ,
        "TriangleBlind"
        ]

    def __init__(self, logger):
        super().__init__(logger)
        self.key = None
        self.IP = None
        self.gw = MotionGateway
        self.blind = MotionBlind
        self.mac = None
        self.devType = None
        self.max_angle = 0
        self.mode = None
        self.position = 0
        return


#
# set the FHEM readings for the blind
#
    async def __set_readings(self):
        # loop through the __dict__ keys and set the value according to the key name for exampe "blind.device_type": "type" will provide a key blind.device_type and a reading's name type
        # reading(type) is set to eval(blind.device_type)
        # prepare for the update of the readings
        await fhem.readingsBeginUpdate(self.hash)
        valeur = None
        readingsname = None
        blind=self.blind
        for key in self.readings.keys():
            lacle = key
        # extract object attributes value if not defined their __dict__ value
            readingsname = self.readings[key]
            try: 
                    # the attribute exists
                    # evaluate its value from the blind dict
                    valeur = eval(key)
                    self.logger.debug(f"set self.readings[{key}] into reading {readingsname} = {valeur}")
                    # set the reading in fhem's device
                    await fhem.readingsBulkUpdate(self.hash, readingsname, valeur, 1)
            except AttributeError:
                pass
        await fhem.readingsEndUpdate(self.hash, 0)


    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
    
        await super().Define(hash, args, argsh)

        if len(args) < 6:
            return "Usage: define NAME fhempy motionblinds IP KEY"


    # define the attributes

#        await self.set_attr_config(self._attr_list)
        await self.set_icon("fts_garage_door_30")
        await fhem.CommandAttr(hash, hash["NAME"] + " devStateIcon up:fts_garage_door_down:down down:fts_garage_door_up:up")
        await fhem.CommandAttr(hash, hash["NAME"] + " verbose 5")
    # check the defined attributes in the define command
    # DEFINE name fhempy motionblinds IP KEY MAC DEVICE_TYPE

        self.IP = args[3]
        hash['IP']=self.IP
        self.key = args[4]
        hash['key']=self.key
        self.mac = args[5]
        hash['mac'] = self.mac
        self.devtype = args[6]
        hash['Device_Type'] =  self.devtype

#initial mode is sim

        self.mode = "sim"
        if len(args) < 5:
            return "Usage: define brel fhempy test"
        
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "mode", "sim")
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "up")
        await fhem.readingsEndUpdate(self.hash, 1)


# define the gateway and get the blind from the gateway
        self.gw = MotionGateway(ip = self.IP, key = self.key)
        if (self.mode == "sim"):
            self.blind = MotionBlind(gateway=self.gw, mac=self.mac, device_type=self.devtype)
        else:
            self.gw.Update()
            self.blind = self.gw.device_list[self.mac]
# get  the device list
#        self.gw.GetDeviceList()
#        self.gw.update()
#        for blind in self.gw.device_list.values():
#            self.logger.info(f"Device found"+blind)

        set_config = {
            "up": {},
            "down": {},
            "mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "params": {"mode": {"default": "live", "optional": False}},
                "options": "live,sim",
            },
            "status":{},
            "position": {
                "args": ["position"], "params": {"position": {"default": 0, "options": "slider,0,1,100", "optional": False}},
            }
        }
        await self.set_set_config(set_config)

        # Attribute function format: set_attr_NAMEOFATTRIBUTE(self, hash)
        # self._attr_NAMEOFATTRIBUTE contains the new state
        async def set_attr_IP(self, hash):
            # attribute was set to self._attr_IP
            # you can use self._attr_interval already with the new variable
            pass

        # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)

    async def set_up(self, hash, params):
        # no params argument here, as set_up doesn't have arguments defined in set_list_conf
        if (self.mode == "sim"):
            # sim mode do nothing
            pass
        else:
            # isseu the open command to the blind followed by an update to get blind readings
#            self.gw.Update()
#            blind = self.gw.device_list[self.mac]
            self.blind.Open()
            self.blind.Update()
        await fhem.readingsSingleUpdate(self.hash,"state", "up", 1)
        await self.__set_readings()
            
    async def set_down(self, hash, params):
        # no params argument here, as set_down doesn't have arguments defined in set_list_conf
        if (self.mode == "sim"):
            pass
        else:
            # isseu the close command to the blind followed by an update to get blind readings
            self.blind.Close()
            self.blind.Update()
        # update FHM device readings
        await fhem.readingsSingleUpdate(self.hash,"state", "down", 1)
        await self.__set_readings()

    async def set_mode(self, hash, params):
        # user can specify mode as mode=eco or just eco as argument
        # params['mode'] contains the mode provided by user
        self.mode = params["mode"]
        await fhem.readingsSingleUpdate(hash, "mode", self.mode, 1)
 
    async def set_status(self, hash, params):
        # get the state of the blind
        if (self.mode == "sim"):
            pass
        else:
#            self.gw.Update()
#            blind = self.gw.device_list[self.mac]
            self.blind.Update()
        await self.__set_readings()
        await fhem.readingsSingleUpdate(self.hash,"state", "down", 1)

    async def set_position(self, hash, params):
        hash['position']=params['position']
        self.position = params['position']
    