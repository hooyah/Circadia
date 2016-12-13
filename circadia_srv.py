"""
Simple tcp socket server running on the lamp
for remote control from the editor
"""


import socket
import json
from MSR_HAL import circadiahw

sys_hw = circadiahw.CircadiaHw
system = dict()
sys_hw.init(system)
sys_hw.audio_off()
sys_hw.switchClock(False, False) # switch to display
sys_hw.textOut('listening on port 9942', center=True)
sys_hw._display.start_scroll()

print "switching lut to 'default'"
sys_hw.switchLut('default')


print 'running on', sys_hw.platform()
print 'listening on port 9942'
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('', 9942))
serversocket.listen(5) # become a server socket, maximum 5 connections


try:
    while True:
        print 'listening...'
        connection, address = serversocket.accept()
        print 'connection established from ', address

        buffer = ""
        while(1):
            buf = connection.recv(1024)
            if len(buf) > 0:
                buffer += buf
                continue
            else:
                print 'received: ', len(buffer)

                if buffer.startswith('hello'):
                    connection.send('ok')
                    connection.close()
                    break

                elif buffer.startswith('reset'):

                    connection.send('ok')
                    connection.close()

                    canvas = system['canvas']
                    for i,c in enumerate(grd):
                        canvas.drawLineH(i, 0.0, 0.0, 0.0)
                    sys_hw.update_screen(canvas)
                    break

                elif buffer.startswith('grad:'):
                    connection.send('ok')
                    connection.close()
                    try:
                        grd = json.loads(buffer[5:])
                        if len(grd) == 18:

                            canvas = system['canvas']
                            for i,c in enumerate(grd):
                                canvas.drawLineH(i, c[0], c[1], c[2])
                            sys_hw.update_screen(canvas)
                        else:
                            print 'corrupt packet'
                    except:
                        pass

                    break
                elif buffer.startswith('cnv:'):
                    connection.send('ok')
                    connection.close()
                    try:
                        grd = json.loads(buffer[4:])
                        if len(grd) == 18*16*3:

                            canvas = system['canvas']
                            canvas.data = grd
                            sys_hw.update_screen(canvas)
                        else:
                            print 'corrupt packet size', len(grd)
                            print grd
                    except:
                        pass

                    break

except:
    print "closing shop"

serversocket.close()
sys_hw.switchClock(True, False) # switch to clock
sys_hw.shutdown()

print 'done.'


