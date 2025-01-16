import asyncio
from motionblinds import MotionGateway

from .. import fhem, generic


class motionblinds(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.key = None
        self.IP = None


    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

    # define the attributes

        self._attr_list = {
            "key": {"default": "127.0.0.1"},
            "IP": {"default": None},
        }

        await self.set_attr_config(self._attr_list)
        await self.set_icon("fts_garage_door_30")
        await fhem.CommandAttr(self.hash, self.hash["NAME"] + " devStateIcon up:fts_garage_door_down:down down:fts_garage_door_up:up")

    # check the defined attributes in the define command
        if len(args) < 5:
            return "Usage: define NAME fhempy test IP"

        self.address = args[3]
        hash["IP"]= args[3]

        self.logger.info(f"Define test address {self.address}")

        self.key = args[4]
        hash["key"] = args[4]
        
    
        self.logger.info(f"Define test key {self.address}")

        set_config = {
            "up": {},
            "down": {},
        }
        await self.set_set_config(set_config)


        if len(args) > 3:
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
        await fhem.readingsSingleUpdate(self.hash,"state", "up", 1)
        return ""

    async def set_down(self, hash, params):
        # no params argument here, as set_down doesn't have arguments defined in set_list_conf
        await fhem.readingsSingleUpdate(self.hash,"state", "down", 1)
        return ""
