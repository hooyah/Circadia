"""
    Circadia Sunrise Lamp - Graphic modules

    Author: fhu
"""

import os
import pygame
from MSR_OS import modbase
import MSR_OS.floatCanvas as fc


class gradient_module(modbase.GModule):
    """ generates a color gradient that changes over time """

    def __init__(self, basepath, moduleDef, width, height):

        modbase.GModule.__init__(self, moduleDef)
        # todo: add error checking

        params = moduleDef['params']

        self.surf = fc.Canvas(width, height)
        self.gradient = fc.Gradient4(params['keys'])
        self.dbg = 0
        #print self.gradients


    def tick(self, timeInt):

        if timeInt.elapsedSeconds() - self.lastEval > .016:

            self.lastEval =  timeInt.elapsedSeconds()

            # draw the gradient
            w = self.surf.width
            h = self.surf.height

            timeNormalized = timeInt.elapsedNormalized()

            for y in xrange(h):
                colR, colG, colB = self.gradient.eval( timeNormalized, float(y)/(h-1) )
                self.surf.drawLineH(y, colR, colG, colB)

            return True
        else:
            return False


    def updateCanvas(self, background):

        background.blit( self.surf )
        return





class ImgShift_module(modbase.GModule):
    """ animates an image file over the canvas"""

    def __init__(self, basepath, moduleDef, width, height):

        modbase.GModule.__init__(self, moduleDef)
        # todo: add error checking

        params = moduleDef['params']

        self.surf = fc.Canvas(width, height)

        ifile = basepath + os.sep + params['file']
        if not os.path.isfile(ifile):
            print "ImgShift: can't open file: "+ifile
        self.oversampling = params['oversampling']
        self.img = pygame.image.load(ifile)
        self.imgWidth = self.img.get_width()
        self.imgHeight = self.img.get_height()
        if self.oversampling != 1.0:
            self.img = pygame.transform.smoothscale(self.img, (int(self.imgWidth*self.oversampling), int(self.imgHeight*self.oversampling)))
        self.offsetX = params['offset'][0]
        self.offsetY = params['offset'][1]
        self.speedX = params['speed'][0]
        self.speedY = params['speed'][1]




    def tick(self, timeInt):

        elapsed = timeInt.elapsedSeconds()
        gain = self.envelope.eval(timeInt.elapsedNormalized())
        if elapsed - self.lastEval > .016:

            self.lastEval =  elapsed

            w = self.surf.width
            h = self.surf.height

            offx = self.offsetX + self.speedX * elapsed
            offy = self.offsetY + self.speedY * elapsed

            self.surf.fill(0.0,0.0,0.0)

            imgw = self.imgWidth - 1
            imgh = self.imgHeight - 1

            for to_x in xrange(w):
                from_x = ( (imgw + to_x - offx)%imgw ) * self.oversampling
                for to_y in xrange(h):
                    from_y = ( (imgh + to_y*2 - offy)%imgh ) * self.oversampling
                    col = self.img.get_at( (int(from_x), int(from_y)) )
                    self.surf.drawPixel(to_x, to_y, gain*col[0]/255.0, gain*col[1]/255.0, gain*col[2]/255.0)

            return True
        else:
            return False


    def updateCanvas(self, background):

        background.blit( self.surf )
        return



__author__ = 'florian'
