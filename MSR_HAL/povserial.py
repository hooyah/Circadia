"""
    Circadia Sunrise Lamp - POV clock communication

    handles the serial communication protocol with the POV clock

    Author: fhu
"""


import serial

class pov:
	""" POV serial communication

		supported messages (direct to display):
		"C"  - switch to clock display
		"Sx" - show seconds, x=0/1
		"D"  - switch to character display
		"K"  - clear display buffer
		"Mxxxxxxx" - copy message into display buffer (replace)
		"mYxxxx"   - copy message into display buffer at offset Y
		"Thms" - set time
		"J"    - switch to next magnet lock
		"Rx"      - set display rotation speed x=10-rot (-4<=rot<=4)
		"Xzy0..y5 - program special character z=[1-8] y=6bytes
		messages to controller:
		"Q" - ask for Status
			returns "qSMB" - status, S=speed, M=displayMode, B=button status
		"Yx" - set motor speed 0-90 (clamped at 90 for safety)
		

	"""
	def __init__(self):
		self.com = serial.Serial('/dev/ttyAMA0', 2400)
		self.rxbuff = bytearray()
		self.msgbuff = list()
		self.com.flushInput()
		self.com.flushOutput()
		self.scroll_speed = 2
		self.disp_len = 36

	def crc8(self, txt):
	
		txt = bytearray(txt)
		crc = 0
		for c in txt:
			crc = crc ^ c
			for b in xrange(8):
				if (crc & 0x01):
					crc = (crc>>1)^0x8c
				else:
					crc = crc >> 1
		return crc
	
	def sendMessage(self, msg):
									  
		tosend = bytearray('%c%s**%c'%(254,msg,250))
		crc = self.crc8(msg)
		tosend[-3] = crc>>4
		tosend[-2] = crc&0x0f
		if self.com:
			self.com.write(tosend)
			

	def handleRx(self):

		inlen = self.com.inWaiting()
		if inlen > 0:
				self.rxbuff += self.com.read(inlen)

		while len(self.rxbuff) > 0:
				# look for message begin
				msgb = self.rxbuff.find('%c'%(253))
				if msgb == -1:
						return
				#print "found begin"
				msge = self.rxbuff[msgb:].find('%c'%(250))
				if msge == -1:
						return
				#print "found end"

				# verify message
				msg = self.rxbuff[msgb+1:msge-2]
				crc = self.crc8(msg)

				#print list(msg), list(self.rxbuff), self.rxbuff[msge-1]
				#print "crc", crc, self.rxbuff[msge-2],self.rxbuff[msge-1]
				#print (self.rxbuff[msge-2]<<4)+self.rxbuff[msge-1]


				# handle message
				if msge > 2 and crc == ((self.rxbuff[msge-2]<<4)+self.rxbuff[msge-1]):
					# msg valid
					if len(self.msgbuff) < 100: # only save 100 messages
						self.msgbuff.append(msg)
				
				# remove message from buffer
				self.rxbuff = self.rxbuff[msge+1:]

	def getNextMessage(self):

		if len(self.msgbuff):
			return self.msgbuff.pop(0)
		else:
			return None

	def flushMessages(self):
		self.msgbuff = list()

	# common messages
	
	def switchToDisplay(self):
		self.sendMessage('D')
		
	def switchToClock(self):
		self.sendMessage('C')

	def start_scroll(self):
		self.sendMessage('R%c'%(10+self.scroll_speed))

	def stop_scroll(self):
		self.sendMessage('R%c'%(10))

	def set_scroll_speed(self, speed):
		speed = max(-4, min(4, speed))
		self.scroll_speed = speed
		self.sendMessage('R%c'%(10+self.scroll_speed))

	def set_rpm(self, rpm):
		rpm = max(10, min(90, rpm))
		self.sendMessage('Y%c'%rpm)

	def setTime(self, hour, minute, second):
		self.sendMessage('T%c%c%c'%(hour, minute, second))

	def text(self, txt):
		self.sendMessage('M%s'%txt[:36])

	def textPos(self, offset, txt):
		self.sendMessage('m%c%s'%(offset, txt[:36]))

	def incMagLock(self):
		self.sendMessage('J')

	def secondsDisplay(self, onOff):
		self.sendMessage('S%d'%(1 if onOff else 0))

	def clear(self):
		self.sendMessage('K')


