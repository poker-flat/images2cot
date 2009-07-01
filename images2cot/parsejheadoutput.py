# parsejheadoutput.py
#
# This script will parse the output of `jhead -v *.JPG` in a directory. The
# input is the file to parse. The result will be an XML file that the
# SwathViewer can interpret as the Curser On Target for the UAS.
#
# Author: Jonathan Sawyer
# Date: 4-22-2009
# Version: 0.1.2
# Last modified: 6-30-2009

import sys, os, re

class JheadParser:
    """
    Data class for storing Jhead output. This will be put into SwathViewer
    XML Curser on Target data
    """
    re_Filename = r'^\s*File name\s*:\s*(.*)\n'
    re_GPSLatitude = r'^\s*GPS Latitude\s*:\s*(.*)\n'
    re_GPSLongitude = r'^\s*GPS Longitude\s*:\s*(.*)\n'
    re_GPSAltitude = r'^\s*GPS Altitude\s*:\s*(.*)\n'
    re_CameraMake = r'^\s*Camera make\s*:\s*(.*)\n'
    re_CameraModel = r'^\s*Camera model\s*:\s*(.*)\n'
    re_ExposureTime = r'^\s*Exposure time\s*:\s*(.*)\n'
    re_GPSTimeStamp = r'^\s*GPSTimeStamp\s*=\s*(.*)\n'
    re_GPSDateStamp = r'^\s*GPSDateStamp\s*="(.*)"\n'

    Filename = None
    DateTime = None
    CameraMake = None
    CameraModel = None
    ExposureTime = None
    GPSLatitude = None
    GPSLongitude = None
    GPSAltitude = None 
    GPSTimeStamp = None
    GPSDateStamp = None
    GPSVersion = '2.2.0.0'
    
    VertexOffset = 0.001717906999999
    
    #
    # Public methods
    #
    
    def parse_block(self, block):
        ar = block.split('\n')
        for line in ar:
            print "parsing", line,
            if self.parse(line+'\n'):
                print "parsed"
            else:
                print "not parsed"

    def parse(self, line):
        if self.__parse_Filename(line): return True
        if self.__parse_CameraMake(line): return True
        if self.__parse_CameraModel(line): return True
        if self.__parse_ExposureTime(line): return True
        if self.__parse_GPSLatitude(line): return True
        if self.__parse_GPSLongitude(line): return True
        if self.__parse_GPSAltitude(line): return True
        if self.__parse_GPSTimeStamp(line): return True
        if self.__parse_GPSDateStamp(line): return True
        return False
    
    def write_xml(self):
        self.__combine_DateTimeStamp()
        if not self.GPSLatitude or not self.GPSLongitude:
            return False
        
        print 'Writing XML...'
        try:
            xmlfile = open('xml_file.xml', 'a+')
        except:
            print 'Could not open XML file for writing. Exiting.'
            raise SystemExit
        
        txt = "<?xml version=\"1.0\" standalone=\"yes\"?>\n\
<event xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" uid=\"" + self.CameraMake + ' ' + self.CameraModel + "\" version=\"2.0\" how=\"m-g\" time=\"" + self.DateTime + "\" qos=\"0-r-c\" stale=\"" + self.DateTime + "\" type=\"b-m-p-s-p-i\" start=\"" + self.DateTime + "\">\n\
  <detail>\n\
    <link relation=\"p-p\" uid=\"" + self.CameraMake + ' ' + self.CameraModel + "\" type=\"a-f-A-M-F-Q-r\" version=\"0.2\" />\n\
    <_flow-tags_ BoeingInsitu=\"" + self.DateTime + "\" />\n\
    <remarks />\n\
    <sensor fov=\"0\" azimuth=\"0\" elevation=\"100.0\" range=\"100.0\" version=\"0.3\" model=\"" + self.CameraModel + "\" type=\"" + self.CameraModel + "\" />\n\
    <shape>\n\
      <polyline>\n\
        <vertex lat=\"" + str(self.GPSLatitude + self.VertexOffset) + "\" lon=\"" + str(self.GPSLongitude - self.VertexOffset) + "\" hae=\"" + str(self.GPSAltitude) + "\" />\n\
        <vertex lat=\"" + str(self.GPSLatitude + self.VertexOffset) + "\" lon=\"" + str(self.GPSLongitude + self.VertexOffset) + "\" hae=\"" + str(self.GPSAltitude) + "\" />\n\
        <vertex lat=\"" + str(self.GPSLatitude - self.VertexOffset) + "\" lon=\"" + str(self.GPSLongitude + self.VertexOffset) + "\" hae=\"" + str(self.GPSAltitude) + "\" />\n\
        <vertex lat=\"" + str(self.GPSLatitude - self.VertexOffset) + "\" lon=\"" + str(self.GPSLongitude - self.VertexOffset) + "\" hae=\"" + str(self.GPSAltitude) + "\" />\n\
      </polyline>\n\
    </shape>\n\
  </detail>\n\
  <point lat=\"" + str(self.GPSLatitude) + "\" lon=\"" + str(self.GPSLongitude) + "\" hae=\"" + str(self.GPSAltitude) + "\" le=\"9999.99\" ce=\"9999.99\" />\n\
</event>\n\
<?xml version=\"1.0\" standalone=\"yes\"?>\n\
<event xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" uid=\"" + self.CameraMake + ' ' + self.CameraModel + "\" version=\"2.0\" how=\"m-g\" time=\"" + self.DateTime + "\" qos=\"0-r-c\" stale=\"" + self.DateTime + "\" type=\"a-f-A-M-F-Q-r\" start=\"" + self.DateTime + "\">\n\
  <detail>\n\
    <_flow-tags_ BoeingInsitu=\"" + self.DateTime + "\" />\n\
    <track course=\"191.3\" speed=\"0\" />\n\
    <spatial>\n\
      <attitude roll=\"0\" pitch=\"0\" yaw=\"0\" />\n\
      <spin roll=\"0\" pitch=\"0\" yaw=\"0\" />\n\
    </spatial>\n\
    <remarks />\n\
    <status>\n\
      <fuel burnable=\"7.7000\" burnrate=\"0.0000000\" offload=\"0\" />\n\
    </status>\n\
  </detail>\n\
  <point lat=\"" + str(self.GPSLatitude) + "\" lon=\"" + str(self.GPSLongitude) + "\" hae=\"" + str(self.GPSAltitude) + "\" le=\"9999.99\" ce=\"4\" />\n\
</event>\n"


        xmlfile.write(txt)
        xmlfile.close()
        return True
    
    #
    # Private methods
    #
    def __combine_DateTimeStamp(self):
        self.DateTime = str(self.GPSDateStamp) + 'T' + str(self.GPSTimeStamp) + '.76Z'
        return True    

    def __parse_Filename(self, line):
        match = re.match(self.re_Filename, line)
        if match:
            print 'File name:',match.group(1)
            self.Filename = match.group(1)
            return True
        return False
    
    def __parse_DateTime(self, line):
        match = re.match(self.re_DateTime, line)
        if match:
            # match.group(1) looks like "2009:04:21 09:09:59"
            # we need it to look like "2009-04-21T09:09:59.76Z"
            txt = match.group(1)
            arr = txt.split()
            arr[0] = '-'.join(arr[0].split(':'))
            txt = 'T'.join(arr)+'.76Z'
            print 'Date/Time:',txt
            self.DateTime = txt
            return True
        return False

    def __parse_GPSTimeStamp(self, line):
        match = re.match(self.re_GPSTimeStamp, line)
        if match and not re.match(r'\?', match.group(1)):
            arr = match.group(1).split(', ')[0:3]
            hour = int((arr[0])[0:-2]) #optimization, assumes arr[0] is in form "hh/1"
            minute = int((arr[1])[0:-2]) #optimization, assumes arr[1] is in form "mm/1"
            second = arr[2].split('/')
            second = int(second[0]) / int(second[1])
            self.GPSTimeStamp = str(hour) + ':' + str(minute) + ':' + str(second)
            print "GPSTimeStamp:", self.GPSTimeStamp
            return True
        return False

    def __parse_GPSDateStamp(self, line):
        match = re.match(self.re_GPSDateStamp, line)
        if match and not re.match(r'\?', match.group(1)):
           self.GPSDateStamp = match.group(1)
           print "GPSDateStamp:", self.GPSDateStamp
           return True
        return False

    def __parse_GPSLatitude(self, line):
        match = re.match(self.re_GPSLatitude, line)
        if match and not re.match(r'\?', match.group(1)):
            dec = self.__parse_DMS_to_decimal(match.group(1))
            print 'GPSLatitude: %(#).15f' % {'#': dec}
            self.GPSLatitude = dec
            return True
        return False
    
    def __parse_GPSLongitude(self, line):
        match = re.match(self.re_GPSLongitude, line)
        if match and not re.match(r'\?', match.group(1)):
            dec = self.__parse_DMS_to_decimal(match.group(1))
            print 'GPSLongitude: %(#).15f' % {'#': dec}
            self.GPSLongitude = dec
            return True
        return False
    
    def __parse_GPSAltitude(self, line):
        """line is in the form of `208.0m`. We need this into float format."""
        match = re.match(self.re_GPSAltitude, line)
        if match and not re.match(r'\?', match.group(1)):
            txt = match.group(1)
            height = float(txt[0:-1])
            print 'GPSAltitude:',height,'m'
            self.GPSAltitude = height
            return True
        return False
    
    def __parse_CameraMake(self, line):
        match = re.match(self.re_CameraMake, line)
        if match and not re.match(r'\?', match.group(1)):
            print 'Camera make:',match.group(1)
            self.CameraMake = match.group(1)
            return True
        return False
    
    def __parse_CameraModel(self, line):
        match = re.match(self.re_CameraModel, line)
        if match and not re.match(r'\?', match.group(1)):
            print 'Camera model:',match.group(1)
            self.CameraModel = match.group(1)
            return True
        return False
    
    def __parse_ExposureTime(self, line):
        """line is in the form of `0.0001 s  (1/8000)`, we need just the
        exposure time in seconds"""
        match = re.match(self.re_ExposureTime, line)
        if match and not re.match(r'\?', match.group(1)):
            txt = match.group(1)
            arr = txt.split()
            sec = float(arr[0])
            print 'Exposure time:',sec,'s'
            self.ExposureTime = sec
            return True
        return False
    
    def __parse_DMS_to_decimal(self, line):
        """line is in the form of `N 64d 51.5500m  0s`, we need this in decimal
        notation, i.e., `64.8473`"""
        txt = line.split()
        sign = 0
        
        pos = txt[0]
        if pos == 'N' or pos == 'E':
            sign = 1
        if pos == 'S' or pos == 'W':
            sign = -1
        if sign == 0:
            return None
        
        # convert '147d' to the integer 147
        deg = int((txt[1])[0:-1])
        # convert '51.5500m' to the float 51.5500
        min = float((txt[2])[0:-1])
        # etc
        sec = float((txt[3])[0:-1])
        # add minutes and seconds
        minsec = min+sec
        # divide by 60*60 to get the ratio
        minsec_dec = minsec / 60.0
        # add the result to the degrees
        dec_dms = deg + minsec_dec
        # return the decimal number with the proper sign as noted above
        # if sign is 0, the result is 0, and thus the string is ill formed.
        return dec_dms*sign
    
    ##################
    ###End of class###
    ##################


#### loop it for reading
###reading = True
###count = 0
###while reading:
###    parser = JheadParser()
###        
###    # each block (per jpeg) is separated by a new line, so we loop over each
###    # block and store it in JheadParser object after each block read, we write
###    # out to the XML file the "event" of the frame capture.
###    while True:
###        if line == "\n" or not line:
###            parser.write_xml()
###            print '--------------'
###            break
###        
###        parser.parse(line)
###        line = f.readline()
###    
####    count+=1
####    if count > 3:
####        break
###    
###    line = f.readline()
###    if not line: reading = False
###    
####print line
###f.close()
