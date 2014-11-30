import legume

class JoinMsg(legume.messages.BaseMessage):
    """
    To Server: Client wants to join
    To Client: Another Client joined (PlayerUpdate must follow)
    """
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER + 1
    MessageValues = {
        'username' : 'varstring'
    }
    
    def __repr__(self):
        return '<JoinMsg{} ({})>'.format(self.MessageTypeID, self.username.value)

class PlayerUpdateMsg(legume.messages.BaseMessage):
    """
    To Server: Player tells its state
    To Client: Update state of a player
    """
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
        #'roll'      : 'float',
        'crouching' : 'bool'
    }
    
    def __repr__(self):
        return '<PlayerUpdateMsg{} ({})>'.format(self.MessageTypeID, self.username.value)

for c in (JoinMsg, PlayerUpdateMsg):
    legume.messages.message_factory.add(c)
