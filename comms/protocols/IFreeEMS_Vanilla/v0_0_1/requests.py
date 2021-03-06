#   Copyright 2009 Aaron Barnes
#
#   This file is part of the FreeEMS project.
#
#   FreeEMS software is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   FreeEMS software is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with any FreeEMS software.  If not, see <http://www.gnu.org/licenses/>.
#
#   We ask that if you make any changes to this file you send them upstream to us at admin@diyefi.org

import packet
import __init__ as protocol
import comms.protocols.__init__ as protocols

# Base request object
class request(packet.packet):

    def __init__(self):
        pass


# Interface version request
class requestInterfaceVersion(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_INTERFACE_VERSION)


# Firmware version request
class requestFirmwareVersion(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_FIRMWARE_VERSION)

    
# Firmware max packet size request
class requestMaxPacketSize(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_MAX_PACKET_SIZE)


# Firmware echo packet return request
class requestEchoPacketReturn(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_ECHO_PACKET_RETURN)
        
        string = ''
        for byte in range(0,255):
            string += chr(byte)

        self.setPayload(string)


class requestBasicDatalog(request):
    '''
    Basic datalog toggle packet

    Toggles datalogging depending on payload
    '''

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_BASIC_DATALOG)


    def stop(self):
        self.setPayload(protocols.SZEROS)


    def startBasic(self):
        self.setPayload(protocols.SBIT0)


# Memory request parent class
class _requestMemory(request):

    def __init__(self):
        request.__init__(self)


    def setBlockId(self, id):
        block_id = protocols.to8bit(id, 2)
        self.setPayload(block_id)


# Firmware memory block request
class requestRetrieveBlockFromRAM(_requestMemory):

    def __init__(self):
        _requestMemory.__init__(self)
        self.setPayloadId(protocol.REQUEST_RETRIEVE_BLOCK_FROM_RAM)


# Firmware memory block request
class requestRetrieveBlockFromFlash(_requestMemory):

    def __init__(self):
        _requestMemory.__init__(self)
        self.setPayloadId(protocol.REQUEST_RETRIEVE_BLOCK_FROM_FLASH)


# Firmware memory block request
class requestBurnBlockFromRamToFlash(_requestMemory):
        
    def __init__(self):
        _requestMemory.__init__(self)
        self.setPayloadId(protocol.REQUEST_BURN_BLOCK_FROM_RAM_TO_FLASH)
            

# Firmware system reset request (hard)
class requestHardSystemReset(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_HARD_SYSTEM_RESET)


# Firmware system reset request (soft)
class requestSoftSystemReset(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_SOFT_SYSTEM_RESET)


# Update main table cell value
class requestUpdateMainTableCell(request):

    def __init__(self):
        request.__init__(self)
        self.setPayloadId(protocol.REQUEST_ADJUST_MAIN_TABLE_CELL)


    def setTableId(self, id):
        id = protocols.shortTo8bit(id)
        self.setPayload(self.getPayload() + id)


    def setRpmAxis(self, rpm):
        rpm = protocols.shortTo8bit(rpm)
        self.setPayload(self.getPayload() + rpm)


    def setLoadAxis(self, load):
        load = protocols.shortTo8bit(load)
        self.setPayload(self.getPayload() + load)


    def setValue(self, value):
        value = protocols.shortTo8bit(value)
        self.setPayload(self.getPayload() + value)
