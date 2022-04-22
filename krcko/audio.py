import logging
import wave

#global PlayObject
play_obj = None

def play_audio(path :str) -> None:
	'''starts new audio track if none is playing currently '''
	
	global play_obj

	#nothing is playing
	if play_obj is None or\
		not play_obj.is_playing():
		#
		try:
			wave_read = wave.open(path, 'rb')
		except:
			logging.error("failed to load wave file: " + path)
			return
		#load wave
		wave_obj = sa.WaveObject.from_wave_read(wave_read)
		#play
		play_obj = wave_obj.play()
	

def stop_audio() -> None:
	'''stop currently playing audio, if there is any'''
	
	global play_obj
	
	if play_obj is None or\
		not play_obj.is_playing():
		#
		return

	#stop
	play_obj.stop()



def is_playing_audio() -> bool:
	'''check if there is any audio playing'''

	global play_obj
		
	return play_obj is not None or play_obj.is_playing()



