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
    To Server: Player tells its state (Server MUST IGNORE the username (security issue))
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

class LeaveMsg(Message):
    """
    To Server: --
    To Client: A Client left the game
    """
    msgID = 3
    msgData = {
        'username' : ('str', '')
    }

class BlockBuildMsg(Message):
    """
    To Server: .. obvious I think
    To Client: ..
    """
    msgID = 4
    msgData = {
        'x' : ('int', 0),
        'y' : ('int', 0),
        'z' : ('int', 0),
        'r' : ('float', 0),
        'g' : ('float', 0),
        'b' : ('float', 0)
    }

class BlockBreakMsg(Message):
    """
    To Server: .. obvious I think
    To Client: ..
    """
    msgID = 5
    msgData = {
        'x' : ('int', 0),
        'y' : ('int', 0),
        'z' : ('int', 0)
    }

def registerMessages(factory):
    factory.add(
        JoinMsg, 
        PlayerUpdateMsg, 
        LeaveMsg, 
        BlockBuildMsg, 
        BlockBreakMsg)
