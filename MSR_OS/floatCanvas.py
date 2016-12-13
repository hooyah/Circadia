"""
    Circadia Sunrise Lamp - Utilities

    A simple float canvas and gradient classes

    Author: fhu
"""


import pygame


class Canvas():
    """ A simple float Canvas. color components range from [0.0 - 1.0]"""

    def __init__(self, w, h):
        """
        Create a Canvas with dimension w*h
        :param w (int): width
        :param h (int): height
        """

        self.width = int(w)
        self.height = int(h)

        self.fill( 0.0, 0.0, 0.0 )

        self.bayer = [ [1,9,3,11], [13,5,15,7], [4,12,2,10], [16,8,14,6]]
        self.bayer = [[self.bayer[x][y]/17.0 for x in range(4)] for y in range(4)]

    def fill(self, r,g,b):
        """
        fill the canvas with a color
        :param r (float): red
        :param g (float): green
        :param b (float): blue
        """

        self.data = [float(r),float(g),float(b)] * (self.width*self.height)

    def drawPixel(self, x, y, r, g, b):
        """
        set pixel[x,y] to color(r,g,b)
        :param x (int): column
        :param y (int): row
        :param r (float): red
        :param g (float): green
        :param b (float): blue
        """

        x = int(x)
        y = int(y)

        i = (y * self.width + x)*3
        self.data[i]   = r
        self.data[i+1] = g
        self.data[i+2] = b

    def getPixel(self, x, y):
        """
        get the color of pixel[x,y]
        :param x (int): column
        :param y (int): row
        :return (tupple): ( red, green, blue)
        """

        x = int(x)
        y = int(y)

        i = (y * self.width + x)*3
        return ( self.data[i], self.data[i+1], self.data[i+2] )

    def getRow(self, y):
        """
        return an entire row of colors
        :param y (int): row
        :return (list): [red0, green0, blue0,...,redw-1, greenw-1, bluew-1]
        """

        iy0 = int(y)*self.width*3
        iy1 = int(y+1)*self.width*3

        return self.data[iy0:iy1]


    def drawLineH(self, y, r,g,b):
        """
        draw a horizontal line
        :param y (int): row
        :param r (float): red
        :param g (float): green
        :param b (float): blue
        """

        y = int(y)
        start = y*self.width*3
        end = start+self.width*3
        for p in xrange(start, end, 3):
            self.data[p] = r
            self.data[p+1] = g
            self.data[p+2] = b

    def multFill(self, y0, y1, multr, multg, multb ):
        """
        multiply rows y0 to y1 with a value
        :param y0 (int): start row
        :param y1 (int): end row
        :param multr (float): red multiplier
        :param multg (float): green multiplier
        :param multb (float): blue multiplier
        """

        y0 = max(0, min(self.height-1, int(y0)))
        y1 = max(0, min(self.height-1, int(y1)))
        start = y0*self.width*3
        end   = (y1+1)*self.width*3
        for p in xrange(start, end, 3):
            self.data[p] *= multr
            self.data[p+1] *= multg
            self.data[p+2] *= multb

    def blit(self, other):
        """
        copy this entire canvas into 'other'
        :param other: target canvas
        """

        if other.width*other.height != self.width*self.height:
            print 'canvas incompatible for blit'
        else:
            for p in xrange(self.width*self.height*3):
                self.data[p] = other.data[p]

    def toPygameSurface(self, lut=None):
        """
        generate a pygame surface from this canvas, using dithering and lut
        :param lut (Gradient3): optional color look up table
        :return (pygame.Surface): pygame surface object
        """

        pysurf = pygame.Surface((self.width, self.height), depth=32)
        pysurf.lock()

        for x in xrange(self.width):
            for y in xrange(self.height):
                p = (x+y*self.width)*3
                col = (self.data[p], self.data[p+1], self.data[p+2])
                if lut:
                    col = ( lut[0].eval(col[0]), lut[1].eval(col[1]), lut[2].eval(col[2]) )

                b = self.bayer[x%4][(y*2)%4]
                col = ( col[0]*255.0+b, col[1]*255.0+b, col[2]*255.0+b )
                pysurf.set_at((x,y),(min(255,col[0]), min(255,col[1]), min(255,col[2])))

        pysurf.unlock()
        return pysurf













class Gradient1:
    """ simple float gradient class"""

    def __init__(self, keys=[(0.0,0.0),(1.0,1.0)]):
        """
        create a Gradient1
        :param keys (list):  [ [param0, value0], [param1, value1], ... ]
        """
        self.keys = keys
        if len(keys):
            self.keys.sort()
        #print 'foo', self.keys


    def eval(self, atVal):
        """
        evaluate the gradient
        :param atVal (float): parameter
        :return (float): value at the parameter
        """

        val = 0
        if len(self.keys) == 0:
            return val

        if atVal <= self.keys[0][0]:
            return self.keys[0][1]

        for i,k in enumerate(self.keys):
            if atVal >= k[0]:
                if i < len(self.keys) - 1:
                    f = (atVal-k[0]) / (self.keys[i+1][0] - k[0])
                    val = k[1] * (1.0-f) + self.keys[i+1][1] * f
                else:
                    val = self.keys[-1][1]

        return val


class Gradient3:
    """ simple color gradient class"""

    # keys are in the format
    def __init__(self, keys=[[0.0,(0.0,0.0,0.0)],[1.0,(1.0,1.0,1.0)]]):
        """
        create a Gradient3
        :param keys (list):  [ [param0, (r0,g0,b0)], [param1, (r1, g1, b1)], ... ]
        """
        self.keys = keys
        if len(keys):
            self.keys.sort()


    def eval(self, atVal):
        """
        evaluate the gradient
        :param atVal (float): parameter
        :return (tuple): color at the parameter (r,g,b)
        """

        val = (0,0,0)
        if len(self.keys) == 0:
            return val

        if atVal <= self.keys[0][0]:
            return (self.keys[0][1][0], self.keys[0][1][1], self.keys[0][1][2])

        for i,k in enumerate(self.keys):
            if k[0] >= atVal:
                d = k[0] - self.keys[i-1][0]
                f = 1.0
                if d > 1e-8:
                    f = (atVal-self.keys[i-1][0]) / d

                val = ( k[1][0] * f + self.keys[i-1][1][0] * (1.0-f),
                        k[1][1] * f + self.keys[i-1][1][1] * (1.0-f),
                        k[1][2] * f + self.keys[i-1][1][2] * (1.0-f) )
                return val

        return (self.keys[-1][1][0], self.keys[-1][1][1], self.keys[-1][1][2])

    def toGradient1(self):
        """
        turn this Gradient3 into 3 Gradient1s
        :return (list):  [ GradientR, GradientG, GradientB ]
        """
        k0 = [ [k[0], k[1][0]] for k in self.keys ]
        k1 = [ [k[0], k[1][1]] for k in self.keys ]
        k2 = [ [k[0], k[1][2]] for k in self.keys ]
        return [Gradient1(k0), Gradient1(k1), Gradient1(k2)]



class Gradient4:
    """ simple animated color gradient """

    # keys are in the format

    def __init__(self, keys=[ {'time':0.0,'grad':[ [1.0,  [1.0, 0.976 ,0.024] ],]}, ]):
        """
        create a Gradient4
        :param keys (list): [ {'time':param0, 'grad':Gradient3()}, ['time':param1, 'grad':gradient3()], ... ]
        """

        self.keys = list()
        for k in keys:
            self.keys.append( [ k['time'], Gradient3(k['grad']) ] )
        self.keys.sort()



    def eval(self, atTime, atVal):
        """
        evaluate the color at a specific time
        :param atTime (float): time to evaluate
        :param atVal (float): parameter to evaluate
        :return:
        """

        val = (0,0,0)
        if len(self.keys) == 0:
            return val

        if atTime <= self.keys[0][0]:
            return self.keys[0][1].eval(atVal)

        for i,k in enumerate(self.keys):
            if k[0] >= atTime:
                d = k[0] - self.keys[i-1][0]
                f = 1.0
                if d > 1e-8:
                    f = (atTime-self.keys[i-1][0]) / d

                val0 = k[1].eval(atVal)
                val1 = self.keys[i-1][1].eval(atVal)
                val = ( val0[0] * f + val1[0] * (1.0-f),
                        val0[1] * f + val1[1] * (1.0-f),
                        val0[2] * f + val1[2] * (1.0-f) )
                return val

        return self.keys[-1][1].eval(atVal)


__author__ = "fhu"
