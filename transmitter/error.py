class TransmitterError(Exception): pass
class InvalidFieldFormat(   ValueError, TransmitterError): pass
class MessageNotFound(      KeyError,   TransmitterError): pass
class InvalidMessageField(  KeyError,   TransmitterError): pass
class InvalidMessageID(     ValueError, TransmitterError): pass
class DuplicateMessageID(   ValueError, TransmitterError): pass
class PeerNotFound(         KeyError,   TransmitterError): pass
