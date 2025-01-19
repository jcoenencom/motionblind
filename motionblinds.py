import asyncio
from motionblinds import MotionGateway, MotionBlind

from .. import fhem, generic


class motionblinds(generic.FhemModule):

    devtypes = {"02000001":"Gateway", "02000002":"Gateway","10000000":"Standard Blind", "10000001":"Top/Down Bottom/Up", "10000002":"Double Roller"}

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
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
    
        await super().Define(hash, args, argsh)

        if len(args) < 6:
            return "Usage: define NAME fhempy motionblinds IP KEY"


    # define the attributes

#        await self.set_attr_config(self._attr_list)
        await self.set_icon("fts_garage_door_30")
        await fhem.CommandAttr(self.hash, self.hash["NAME"] + " devStateIcon up:fts_garage_door_down:down down:fts_garage_door_up:up")

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

# define the gateway
        self.gw = MotionGateway(ip = self.IP, key = self.key)
        self.blind = MotionBlind(gateway=self.gw, mac=self.mac, device_type=self.devtype)
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
        }
        await self.set_set_config(set_config)

#initial mode is sim
        await fhem.readingsSingleUpdate(hash, "mode", "sim", 1)
        self.mode = "sim"
        if len(args) < 5:
            return "Usage: define brel fhempy test"
        
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "up")
        await fhem.readingsEndUpdate(hash, 1)

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
            await fhem.readingsSingleUpdate(self.hash,"state", "up", 1)
            return "set sim up done"
        else:
            self.gw.GetDeviceList()
            self.gw.Update()
            blind = gw.device_list[self.mac]
            self.blind.Open()
            await fhem.readingsSingleUpdate(self.hash,"state", "up", 1)

            
    async def set_down(self, hash, params):
        # no params argument here, as set_down doesn't have arguments defined in set_list_conf
        if (self.mode == "sim"):
            await fhem.readingsSingleUpdate(self.hash,"state", "down", 1)
            return "Set sim down done"
        else:
            self.gw.GetDeviceList()
            self.gw.Update()
            blind = gw.device_list[self.mac]
            self.blind.Close()
            await fhem.readingsSingleUpdate(self.hash,"state", "down", 1)

    async def set_mode(self, hash, params):
        # user can specify mode as mode=eco or just eco as argument
        # params['mode'] contains the mode provided by user
        self.mode = params["mode"]
        await fhem.readingsSingleUpdate(hash, "mode", self.mode, 1)
 
