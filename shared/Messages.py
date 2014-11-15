import legume

class JoinMsg(legume.messages.BaseMessage):
    """ Sent when Client wants to connect """
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER + 1
    MessageValues = {
        'username' : 'varstring'
    }

class PlayerUpdateMsg(legume.messages.BaseMessage):
    """ Sent when a player is updated """
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER + 2
    MessageValues = {
        'username'  : 'varstring',
        'posx'      : 'float',
        'posy'      : 'float',
        'posz'      : 'float',
        'velx'      : 'float',
        'vely'      : 'float',
        'velz'      : 'float',
        'yaw'       : 'float',
        'pitch'     : 'float',
        'roll'      : 'float',
        'crouching' : 'bool'
    }

for c in (JoinMsg, PlayerUpdateMsg):
    legume.messages.message_factory.add(c)
