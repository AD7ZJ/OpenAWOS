import os

class Audio:
    
    def Synthesize(self, msg):
        """Use a text to speech engine to synthesize the message"""
        os.system('pico2wave -w /tmp/awosReport.wav \"%s\"' % msg);
        # omxplayer seems to lockup without the --no-osd option
        os.system('omxplayer --no-osd /tmp/awosReport.wav > /dev/null 2>&1')
        
if __name__ == '__main__':
    a = Audio()
    a.Synthesize("Wind 2 0 0 at 1 5 gusting 2 1")
    
