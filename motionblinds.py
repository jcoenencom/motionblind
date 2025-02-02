import asyncio
import threading
from motionblinds import MotionGateway, MotionBlind, MotionMulticast
import re
from .. import fhem, generic


class motionblinds(generic.FhemModule):

    devtypes = {"02000001":"Gateway", "02000002":"Gateway","10000000":"Standard Blind", "10000001":"Top/Down Bottom/Up", "10000002":"Double Roller"}
    readings = {"blind.blind_type": "type", "blind.status": "status", "blind.position": "position", "blind.angle": "angle", "blind.limit_status":"limits", "blind.battery_voltage": "battery_voltage", "blind.battey_level":"battery_level", "blind.is_charging":"is_charging", "blind.RSSI":"RSSI"}

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
        self.changed = 0
        self._attr_looptimer = 30
        self._attr_UDPRxCheck = 1
        self.changed = 0
        self.direction=""
        self.Backgroundtask = set()
        return


#
# set the FHEM readings for the blind
#

    def callback_func_blind(self):
        # UDP callback, when the gateway detect a change in the blind status, it sends a message to the FHEM device
        # at the moment the callback is sequential and cannot call the fhem async method to update the readings
        # so a flag is set that is read by the status_loop routine started at the device creation

        self.logger.info(f"Rcvd Multicast message from blind {self.blind}")
        # set the flag indicating an UDP message has been received
        self.logger.info(f"Set change flag")
        self.changed = 1

    async def __set_readings(self):
        # loop through the __dict__ keys and set the value according to the key name for exampe "blind.device_type": "type" will provide a key blind.device_type and a reading's name type
        # reading(type) is set to eval(blind.device_type)
        # prepare for the update of the readings
        await fhem.readingsBeginUpdate(self.hash)
        valeur = None
        readingsname = None
        self.gw.Update()
        blind = self.blind
#        blind.Update()
        self.logger.debug(f"__set_readings {blind}")
#        self.logger.debug(f"__set_readings calling blind.Update()")
#        blind.Update()
        for key in self.readings.keys():
            lacle = key
        # extract object attributes value if not defined their __dict__ value
            readingsname = self.readings[key]
            try: 
                    # the attribute exists
                    # evaluate its value from the blind dict
                    valeur = eval(key)
#                    self.logger.debug(f"set self.readings[{key}] into reading {readingsname} = {valeur}")
                    # set the reading in fhem's device
                    await fhem.readingsBulkUpdate(self.hash, readingsname, valeur, 1)
            except AttributeError:
                pass
#        self.logger.debug(f"storing battery_level = {blind.battery_level}")
        await fhem.readingsBulkUpdate(self.hash, "battery_level", blind.battery_level, 1)
        await fhem.readingsEndUpdate(self.hash, 1)


    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
    

        await super().Define(hash, args, argsh)

        if len(args) < 6:
            return "Usage: define NAME fhempy motionblinds IP KEY"


    # define the attributes

#        await self.set_attr_config(self._attr_list)
        await self.set_icon("fts_garage_door_30")
        await fhem.CommandAttr(hash, hash["NAME"] + " devStateIcon up:fts_garage_door_down:down down:fts_garage_door_up:up Stopped_Opening:fts_shutter_down:down Stopped_Closing:fts_shutter_up:up Opening:rc_GREEN:Stop Closing:rc_GREEN:Stop")
        await fhem.CommandAttr(hash, hash["NAME"] + " webCmd position:jog_up:jog_down")
#        await fhem.CommandAttr(hash, hash['NAME'] + " cmdIcon Stop:rc_GREEN jog_up:edit_collapse jog_down:edit_expand")
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
        self.hash = hash

#initial mode is live

        self.mode = "live"
        if len(args) < 5:
            return "Usage: define brel fhempy test"
        
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "mode", "live")
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "up")
        await fhem.readingsEndUpdate(self.hash, 1)

        # start update loop
        self._updateloop = self.create_async_task(self.update_loop())

# define the gateway and get the blind from the gateway and setiup the call back function for the milticast liste

        motion_multicast = MotionMulticast(interface = "any")
        motion_multicast.Start_listen()
        self.gw = MotionGateway(ip = self.IP, key = self.key, multicast = motion_multicast)

        self.gw.Update()

        self.blind = self.gw.device_list[self.mac]
        self.blind.Register_callback("1", self.callback_func_blind)

        attr_config = {
            "looptimer": {
                "default": 30,
                "format": "int",
                "help": "Change gateway poll interval defaut is 30 x UDPRxCheck seconds",
            }, 
            "UDPRxCheck": {
                "default": 1,
                "format": "int",
                "help": "Change UDP message receive caheck interval defaut is 1 second.",
                },
            }

        await self.set_attr_config(attr_config)
        await fhem.CommandAttr(hash, hash["NAME"] + f" UDPRxCheck {self._attr_UDPRxCheck}")
        await fhem.CommandAttr(hash, hash["NAME"] + f" looptimer {self._attr_looptimer}")

        set_config = {
            "up": {},
            "down": {},
            "jog_up":{},
            "jog_down": {},
            "status":{},
            "Stop": {},
            "position": {
                "args": ["position"],
                "params": {"position": {"format": "int"}},
                "options": "slider,0,1,100,0",
            },
            
        }
        await self.set_set_config(set_config)
        self.logger.info(f"Call __set_readings for device Device {self.mac} being created")
#        await self.__set_readings()
        # Attribute function format: set_attr_NAMEOFATTRIBUTE(self, hash)
        # self._attr_NAMEOFATTRIBUTE contains the new state
        #async def set_attr_IP(self, hash):
            # attribute was set to self._attr_IP
            # you can use self._attr_interval already with the new variable
        #    pass


    async def set_up(self, hash, params):
        # no params argument here, as set_up doesn't have arguments defined in set_list_conf
            # isseu the open command to the blind followed by an update to get blind readings
        self.blind.Open()
        self.blind.Update()
        await fhem.readingsSingleUpdate(self.hash,"state", "Opening", 1)
        self.logger.debug("set_up:")

            
    async def set_down(self, hash, params):
        # no params argument here, as set_down doesn't have arguments defined in set_list_conf

        # issue the close command to the blind followed by an update to get blind readings
        self.logger.debug("set_down:")
        self.blind.Close()
        self.blind.Update()

        # update FHM device readings
#        self.blind.Update()
        await fhem.readingsSingleUpdate(self.hash,"state", "Closing", 1)
#        await self.__set_readings()

    async def set_mode(self, hash, params):
        # user can specify mode as mode=eco or just eco as argument
        # params['mode'] contains the mode provided by user
        self.mode = params["mode"]
        await fhem.readingsSingleUpdate(hash, "mode", self.mode, 1)
 
    async def set_status(self, hash, params):
        # get the state of the blind
        self.blind.Update()
        await self.__set_readings()

    async def set_Stop(self,hash,params):
        if (self.blind.status == 'Closing') or (self.blind.status == 'Opening'):
            direction = "Stop_" + self.blind.status
            self.logger.info(f"set_Stop: with blind.status = {direction}")
        self.blind.Update()
        self.blind.Stop()

# get the status os the blind
        await self.set_status(hash,params)

    async def set_position(self, hash, params):
        position = params["position"]
        self.logger.debug(f"set_position: SET POSITION AT {position}")
        self.blind.Update()
        
        for key in params.keys():
            self.logger.debug(f"params[{key}]")
        
#        await fhem.readingsSingleUpdate(self.hash, "location", params['valeur'], 1)

#        blind = self.gw.device_list[self.mac]

        self.blind.Set_position(position)
        self.blind.Update()
        self.logger.debug(f"set_position: POSITION being set")



    async def set_jog_up(self, hash, params):
        # no params argument here, as set_jog_up doesn't have arguments defined in set_list_conf
        # isseu the close command to the blind followed by an update to get blind readings
        self.blind.Jog_up()

    async def set_jog_down(self, hash, params):
        # no params argument here, as set_jog_up doesn't have arguments defined in set_list_conf
        # isseu the close command to the blind followed by an update to get blind readings
        self.blind.Jog_down()



# regular update of the status

    async def update_loop(self):
#start with looptimer reached so that we start with an update ofblind status
        looptimer = int(self._attr_looptimer)
        while True:
            if (self.changed !=0): 
                self.logger.info(f"update_loop: UDP message processing: {self.blind}")
                # reset the detection flag and timer
                self.changed = 0
                looptimer = 0
                await self.set_state()
            elif (looptimer >= int(self._attr_looptimer)):        
#                self.logger.debug(f"update_loop: looptimer {looptimer} reached {self._attr_looptimer} count")
                looptimer = 0
                self.blind.Update()        
#                    await self.__set_readings()
                await self.set_state()
            # either from UDP  message or Update, need to insert the readings
     
            looptimer += 1
#            self.logger.debug(f"update_loop: looptimer reached {looptimer} count")
            await asyncio.sleep(self._attr_UDPRxCheck)


    async def set_state(self):
        # set state of device:
        # Opening - Closing - Stopped_Opening - Stopped_Closing - up - donw
        state=""
        if (self.blind.status == 'Closing') or (self.blind.status == 'Opening'):
            self.direction = self.blind.status
            self.position = self.blind.position
            state = self.direction
            self.logger.info(f"set_state: with blind.direction = {self.direction}")
        elif self.blind.status == 'Stopped':
            if (self.blind.position == 0):
                state="up"
            elif (self.blind.position ==100):
                state="down"            
            else:
                #we have stopped while moving, set direction to Stopped_previous motion
                state = "Stopped"
                self.logger.debug(f"update_loop: previous direction {self.direction} ***")
                if (self.direction == "Stopped_Opening") or (self.direction == "Stopped_Closing"):
                    state = self.direction
                elif self.direction != "":
                   self.direction = "Stopped_" + self.direction
                   self.logger.debug(f"update_loop: new direction {self.direction} ***")
                else:
                    if self.position < 50:
                        state = "down"
                    else:
                        state="up"
        
        self.position = self.blind.position
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "direction", self.direction, 1)
        await fhem.readingsBulkUpdate(self.hash, "state", state, 1)
        await fhem.readingsBulkUpdate(self.hash, "status", self.blind.status, 1)
        await fhem.readingsBulkUpdate(self.hash, "position", self.position)
        await fhem.readingsEndUpdate(self.hash, 1)