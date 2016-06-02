import os

class Audio:
    
    def PlayWavFile(self, file):
        filename = '../audio/' + file + '.wav'
        
        os.system('aplay %s' % filename)
        
if __name__ == '__main__':
    a = Audio()
    a.PlayWavFile('wind')
    a.PlayWavFile('1')
    a.PlayWavFile('0')
    a.PlayWavFile('0')
    a.PlayWavFile('at')
    a.PlayWavFile('2')
    a.PlayWavFile('0')
    a.PlayWavFile('gusting')
    a.PlayWavFile('3')
    a.PlayWavFile('5')