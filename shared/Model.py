from shared.BlockStructure import BlockStructure

import logging
logger = logging.getLogger(__name__)

class Model(BlockStructure):
    def __init__(self, scale=0.1, scale2=1, offset=(0,0,0), offset2=(0,0,0)):
        super().__init__()
        self.scale = scale
        self.scale2 = scale2
        self.offset = offset
        self.offset2 = offset2
