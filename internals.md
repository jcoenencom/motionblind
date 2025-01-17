# What are we dealing with ?

The motion-blinds library defines objects

+ class ParseException(Exception):
+ class GatewayStatus(IntEnum):
+ class BlindType(IntEnum):
+ class BlindStatus(IntEnum):
+ class LimitStatus(IntEnum):
+ class VoltageMode(IntEnum):
+ class WirelessMode(IntEnum):
+ class MotionCommunication: Communication class for Motion Gateways.
+ class MotionDiscovery(MotionCommunication):
+ class MotionMulticast(MotionCommunication): Multicast UDP communication class for a MotionGateway.
+ class MotionGateway(MotionCommunication): 
    Main class representing the Motion Gateway. 
    "Key not specified, specify a key when creating the gateway class like MotionGateway(ip = '192.168.1.100', key = 'abcd1234-56ef-78') when using _get_access_token."
    "Key not specified, specify a key when creating the gateway class like MotionGateway(ip = '192.168.1.100', key = 'abcd1234-56ef-78') when using the access_token."
+ class MotionBlind: Sub class representing a blind connected to the Motion Gateway.
+ class MotionTopDownBottomUp(MotionBlind): Sub class representing a Top Down Bottom Up blind connected to the Motion Gateway.


## Connecting the gateway

    from motionblinds import MotionGateway
    m = MotionGateway(ip = "192.168.1.100", key = "12ab345c-d67e-8f")

### The gateway holds a device list that is populated by a request to the gateway itself 
using GetDeviceList gateway method

    m.GetDeviceList()

### Now the instance of the GateWay knows the devices known by the physical gateway
To extract the list of devices:

    for blind in m.device_list.values():
        blind.Update()
        print(blind)

#### NOTE: The Update method is necessary as the library does not poll the gateway to get the latest state of the devices, so it is necessary to issue an update in order to have the correct state of the devices.

will provide this type of data, which is a string representation (__repr__) of the object

    <MotionBlind mac: abcdefghujkl0001, type: RollerBlind, status: Stopped, position: 0 %, angle: 0, limit: Limits, battery: 1195, RSSI: -82 dBm>
    <MotionBlind mac: abcdefghujkl0001, type: RollerBlind, status: stopped, position: 0 &, angle: 0.0, limit BothLimitsDetected, battery: DC, 103.0 %,12.4 V, charging: False, RSSI: -53 dBm, com: BiDirection>
    
Which is a representation of the Blind Object's variables, this is something that we can use to extract data for fhem the representation.

Although it looks like a dict, it is not directly usable in python and needs to be converted (and it's not written to be used by eval to recreate the object).

An object MotionBlind is defined by the following arguments:

        gateway: MotionGateway = None,
        mac: str = None,
        device_type: str = None,
        max_angle: int = 180,

So defining a object using (an unspecified argument will be defaulted to its predefined value, eg max_angle will 180, gateway will be None):

        MBObject = MotionBlind(gateway=mgw, mac=blind_mac, device_type='RollerBlind')

#### Note: the class MotionBlind is not available for import in python with the standard library, in order to use it one has to edit __init__.py file in the library package and insert the following
    from .motion_blinds import MotionBlind
        
