from transmitter.messages import Message

class JoinMsg(Message):
    """
    To Server: Client wants to join
    To Client: Another Client joined (PlayerUpdate must follow)
    """
    msgID = 1
    msgData = {
        'username' : ('str', '')
    }

class PlayerUpdateMsg(Message):
    """
    To Server: Player tells its state
    To Client: Update state of a player
    """
    msgID = 2
    msgData = {
        'username'  : ('str', ''),
        'posx'      : ('float', 0),
        'posy'      : ('float', 0),
        'posz'      : ('float', 0),
        'velx'      : ('float', 0),
        'vely'      : ('float', 0),
        'velz'      : ('float', 0),
        'yaw'       : ('float', 0),
        'pitch'     : ('float', 0),
        'crouching' : ('bool', False)
    }

def registerMessages(factory):
    factory.add(JoinMsg, PlayerUpdateMsg)
