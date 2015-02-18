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

class LeaveMsg(Message):
    """
    To Server: --
    To Client: A Client left the game
    """
    msgID = 2
    msgData = {
        'username' : ('str', '')
    }

class CompleteUpdate(Message):
    """
    To Server: (Server MUST IGNORE the username (security issue))
    To Client:
    """
    msgID = 3
    msgData = {
        'username'  : ('str', ''),
        'x'         : ('float', 0),
        'y'         : ('float', 0),
        'z'         : ('float', 0),
        'dx'        : ('float', 0),
        'dy'        : ('float', 0),
        'dz'        : ('float', 0),
        'yaw'       : ('float', 0),
        'pitch'     : ('float', 0),
        'crouching' : ('bool', False)
    }

class Update(Message):
    """
    To Server: (Server MUST IGNORE the username (security issue))
    To Client:
    """
    msgID = 4
    msgData = {
        'username'  : ('str', ''),
        'key'       : ('str', ''),
        'value'     : ('float', 0)
    }

class BlockBuildMsg(Message):
    """
    To Server: .. obvious I think
    To Client: ..
    """
    msgID = 5
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
    msgID = 6
    msgData = {
        'x' : ('int', 0),
        'y' : ('int', 0),
        'z' : ('int', 0)
    }

def registerMessages(factory):
    factory.add(
        JoinMsg,
        LeaveMsg,
        CompleteUpdate,
        Update,
        BlockBuildMsg,
        BlockBreakMsg)
