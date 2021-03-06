#   Copyright 2008 Aaron Barnes
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


import wx, wx.grid as grid

import comms, gui, datetime, settings, action, comms.interface, comms.protocols as protocols, libs.config


class commsDiagnostics(grid.Grid):
    
    conn = None
    row = 0

    def __init__(self, parent):
        grid.Grid.__init__(self, parent)

        key = 'ui.commsdiagnostics.row.size.'
        width = []
        width.append( settings.get(key+'0', 110)    )
        width.append( settings.get(key+'1', 45)     )
        width.append( settings.get(key+'2', 75)     )
        width.append( settings.get(key+'3', 530)    )

        self.CreateGrid(        1, 4                )
        self.SetRowLabelSize(   50                  )
        self.SetColLabelValue(  0, 'Time'           )
        self.SetColSize(        0, int(width[0])    )
        self.SetColLabelValue(  1, 'Flags'          )             
        self.SetColSize(        1, int(width[1])    )
        self.SetColLabelValue(  2, 'Id'             )
        self.SetColSize(        2, int(width[2])    )
        self.SetColLabelValue(  3, 'Payload'        )
        self.SetColSize(        3, int(width[3])    )

        self.SetDefaultCellFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # Get all column resizing
        self.Bind(grid.EVT_GRID_COL_SIZE, self.onResize)

        # Bind to connection
        self.conn = comms.getConnection()
        self.conn.bindSendWatcher(self)
        self.conn.bindReceiveWatcher(self)

        # Bind to events
        self.Bind(comms.interface.EVT_SEND, self.printSentPacket)
        self.Bind(comms.interface.EVT_RECEIVE, self.printReceivedPacket)


    def onResize(self, event):
        '''Record new size'''
        key = 'ui.commsdiagnostics.row.size.'
        r = 0
        while r < self.GetNumberCols():
            settings.set(key+str(r), self.GetColSize(r))
            r += 1


    def printSentPacket(self, event):
        '''
        Print sent packet to grid
        '''
        self.insertRow(event.packet)


    def printReceivedPacket(self, event):
        '''
        Print received packet to grid
        '''
        protocol = self.conn.getProtocol()

        # If config set or generic response (unknown packet type), print to grid
        if libs.config.getBool('Logging', 'enable_gui_diagnostics') or \
                 isinstance(event.packet, protocol.responses.responseGeneric):
            self.insertRow(event.packet)


    def insertRow(self, packet):
        '''
        Insert row into grid
        '''
        time = datetime.datetime.time(datetime.datetime.now())
        header = self.getHeaderFlags(packet)
        payload = packet.getPayload()
        
        #Format stuff before printing
        payload_id = packet.getPayloadIdInt()
        payload_id_hum = comms.getConnection().getProtocol().getPacketName(payload_id)
        payload_hex_hum = self.formatPayloadHex(payload)

        self.AppendRows()
        self.SetCellValue(self.row, 0, str(time))
        self.SetCellValue(self.row, 1, str(header))
        self.SetCellValue(self.row, 2, str(payload_id) + ":" + payload_id_hum)
        self.SetCellValue(self.row, 3, payload_hex_hum)

        # Make sure entire row is visible
        if self.GetCellOverflow(self.row, 3):
            lines = payload_hex_hum.count('\n') + 1
            self.SetRowSize(self.row, (lines * 15) + 3)

        self.MakeCellVisible(self.row + 1, 1)
        self.ForceRefresh()

        self.row += 1


    def formatPayloadHex(self, data):
        output = ''
        bytes = []
        i = 0

        for raw_hex in data:

            raw_hex = ord(raw_hex)

            # If end of line
            if i % 16 == 0:
                
                # If not first line, add string to end
                if i > 0:
                    output += self.getASCII(bytes)+'\n'
                    bytes = []

                # Get offset and pad with 0's
                offset = hex(i)[2:5].rjust(4, '0')
                
                output += offset+': '
                
            i += 1
            output += hex(raw_hex)[2:5].rjust(2, '0')
            output += ' '
            bytes.append(raw_hex)

            if i % 8 == 0 and i % 16:
                output += "  "

        # Pad the end
        while i % 16:
            if not i % 8:
                output += ' '
            output += '-- '
            i += 1

        output += self.getASCII(bytes)
            
        return output


    def getASCII(self, output):
        ascii = "  "
        
        # Replace hex that can't translate to ASCII with a period
        for j, str in enumerate(output):

            if str in range(32, 127):
                ascii += chr(str)
            else:
                ascii += '.'
        
        return ascii


    def getHeaderFlags(self, packet):
        '''
        Retrieve noterised version of flag bits
        '''
        ascii = str()

        if packet.hasHeaderLengthFlag():
            ascii += 'L'

        if packet.hasHeaderAckFlag():
            ascii += 'A'

        return ascii


class actions():
    '''
    Modules' actions
    '''

    class printPacket(action.action):
        '''
        Save config to file
        '''

        def run(self):
            '''
            Print packet to diagnostics gui
            '''
            gui.frame.windows['main'].comms.printPacket(self._data)
