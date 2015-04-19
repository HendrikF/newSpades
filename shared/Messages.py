from transmitter.Message import Message

_lastID = 0
def _getID():
    global _lastID
    _lastID += 1
    return _lastID

messages = []
def _add(clas):
    global messages
    messages.append(clas)
    return clas

@_add
class JoinMsg(Message):
    """
    To Server: Client wants to join
    To Client: Another Client joined (PlayerUpdate must follow)
    """
    msgID = _getID()
    msgReliable = True
    msgData = {
        'username' : ('str', '')
    }

@_add
class LeaveMsg(Message):
    """
    To Server: --
    To Client: A Client left the game
    """
    msgID = _getID()
    msgReliable = True
    msgData = {
        'username' : ('str', '')
    }

@_add
class PlayerUpdate(Message):
    """
    To Server: (Server MUST IGNORE the username (security issue))
    To Client:
    """
    msgID = _getID()
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

@_add
class BlockBuildMsg(Message):
    """
    To Server: .. obvious I think
    To Client: ..
    """
    msgID = _getID()
    msgReliable = True
    msgData = {
        'x' : ('int', 0),
        'y' : ('int', 0),
        'z' : ('int', 0),
        'r' : ('float', 0),
        'g' : ('float', 0),
        'b' : ('float', 0)
    }

@_add
class BlockBreakMsg(Message):
    """
    To Server: .. obvious I think
    To Client: ..
    """
    msgID = _getID()
    msgReliable = True
    msgData = {
        'x' : ('int', 0),
        'y' : ('int', 0),
        'z' : ('int', 0)
    }
