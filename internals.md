# What are we dealing with ?

The motion-blinds library defines objects

    class ParseException(Exception):
    class GatewayStatus(IntEnum):
    class BlindType(IntEnum):
    class BlindStatus(IntEnum):
    class LimitStatus(IntEnum):
    class VoltageMode(IntEnum):
    class WirelessMode(IntEnum):
    class MotionCommunication: Communication class for Motion Gateways.
    class MotionDiscovery(MotionCommunication):
    class MotionMulticast(MotionCommunication): Multicast UDP communication class for a MotionGateway.
    class MotionGateway(MotionCommunication): 
        Main class representing the Motion Gateway. 
        "Key not specified, specify a key when creating the gateway class like MotionGateway(ip = '192.168.1.100', key = 'abcd1234-56ef-78') when using _get_access_token."
        "Key not specified, specify a key when creating the gateway class like MotionGateway(ip = '192.168.1.100', key = 'abcd1234-56ef-78') when using the access_token."
    class MotionBlind: Sub class representing a blind connected to the Motion Gateway.
    class MotionTopDownBottomUp(MotionBlind): Sub class representing a Top Down Bottom Up blind connected to the Motion Gateway.

    
