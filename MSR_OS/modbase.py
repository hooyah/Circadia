"""
    Circadia Sunrise Lamp - Effects base class

    Base classes for effects modules (graphics and sound)
    Some helper classes

    Author: fhu
"""


class SModule:
    """ Sound module base class """

    def __init__(self, moduleDef):
        """ Create the sound module, initialize it with parameters from the json theme file """

        self.max_volume = moduleDef['params']['maxLevel'] if ('maxLevel' in moduleDef['params']) else 1.0
        self.envelope = Envelope.fromJson(moduleDef['envelope']) if ('envelope' in moduleDef) else Envelope()
        self.reset()

    def reset(self):
        """ reset the module """
        self.lastEval = -1000
        pass

    def tick(self, timeInterval):
        """ polling function.  called in regular intervals with the time elapsed since theme start """
        pass





class GModule:
    """
    Graphics module base class
    """

    def __init__(self, moduleDef):
        """ Create the graphic module, initialize it with parameters from the json theme file """
        self.envelope = Envelope.fromJson(moduleDef['envelope']) if ('envelope' in moduleDef) else Envelope()
        self.reset()
        pass

    def reset(self):
        """ reset the module """
        self.lastEval = -1000
        pass

    def tick(self, time):
        """ polling function.  called in regular intervals with the time elapsed since theme start """
        pass





class Envelope:
    """ A one dimensional lookup. Used for clip volume control """

    def __init__(self, keys=[[0.0,1.0]], logarithmic=False):
        """
        create an Envelope
        :param keys (list): [ [time0, volume0], [time1, volume1], ... ]
        :param logarithmic (bool): values returned by eval will be on a logarithmic scale
        """
        self.log = logarithmic
        self.keys = keys
        if len(keys):
            self.keys.sort()

    @staticmethod
    def fromDict(keysDict, logarithmic=False):
        """
        Create an Envelope from a list of dictionaries with time, value pairs
        :param keysDict (list): [ {'time':time0, 'val':volume0}, {'time':time1, 'val':volume1}, ... ]
        :param logarithmic (bool): values returned by eval will be on a logarithmic scale
        :return (Envelope): a new Envelope object
        """
        return Envelope( keys=[(k['time'], k['val']) for k in keysDict ], logarithmic=logarithmic)

    @staticmethod
    def fromJson(jsonDict):
        """
        Create an Envelope by picking the parameters out of the json style dict (from a theme description)
        :param jsonDict (dict): { 'keys':[keys], 'logarithmic:':log }
        :return (Envelope): a new Envelope object
        """
        return Envelope.fromDict(jsonDict['keys'], True if jsonDict['type']=='log' else False)

    def eval(self, atTime):
        """
        :param atTime: Evaluate the volume at the specified time
        :return (float): volume
        """

        val = 0
        if len(self.keys) > 0:
            val = self.keys[0][1]
        for i,k in enumerate(self.keys):
            if atTime >= k[0]:
                if i < len(self.keys) - 1:
                    f = (atTime-k[0]) / (self.keys[i+1][0] - k[0])
                    val = k[1] * (1.0-f) + self.keys[i+1][1] * f;
                else:
                    val = self.keys[-1][1]
        if self.log:
            val = pow(val,2)  #ehm..
        return val


class timePassed:
    """ Helper class """

    def __init__(self, startTime, duration, currentTime):

        self.startTime = startTime
        self.duration = duration
        self.time = currentTime

    def elapsedNormalized(self):

        return max(0.0, min(1.0, (self.time - self.startTime) / self.duration))

    def elapsedSeconds(self):

        return self.time - self.startTime


class timeInterval:
    """ Simple time interval class """

    def __init__(self, startTime, duration):
        """ create a timeInterval between startTime and startTime+duration """

        self.startTime = startTime
        self.duration = duration

    def elapsedNormalized(self, currentTime):
        """
        returns the time elapsed between startTime and now. normalized to the total duration
        :return (float): [0-1]
        """
        return max(0.0, min(1.0, (currentTime - self.startTime) / self.duration))

    def elapsedSeconds(self, currentTime):
        """
        returns the time elapsed between startTime and now. in seconds
        :param currentTime:
        :return (float): elapsed time in seconds
        """
        return currentTime - self.startTime

    def elapsed(self, currentTime):
        """
        returns the time elapsed between startTime and now as a class timePassed
        :return (timePassed): elapsed time as timePassed object
        """
        return timePassed(self.startTime, self.duration, currentTime)


__author__ = 'florian'
