import pyaudio
import wave
import time


class Audio:
    waveFile = None

    # define callback (2)
    def AudioCallback(self, in_data, frame_count, time_info, status):
        data = self.waveFile.readframes(frame_count)
        return (data, pyaudio.paContinue)
    
    def PlayWavFile(self, file):
        filename = '../audio/' + file + '.wav'
        self.waveFile = wave.open(filename, 'rb')
        
        p = pyaudio.PyAudio()
        
        # open stream using callback
        stream = p.open(format=p.get_format_from_width(self.waveFile.getsampwidth()),
                        channels=self.waveFile.getnchannels(),
                        rate=self.waveFile.getframerate(),
                        output=True,
                        stream_callback=self.AudioCallback)
        
        stream.start_stream()
        
        # wait for stream to finish
        while stream.is_active():
            time.sleep(0.1)
        
        # stop stream (6)
        stream.stop_stream()
        stream.close()
        self.waveFile.close()
        
        # close PyAudio (7)
        p.terminate()
        
if __name__ == '__main__':
    a = Audio()
    a.PlayWavFile('../audio/wind.wav')