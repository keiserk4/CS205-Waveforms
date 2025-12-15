from pathlib import Path
from file_transformer import mp3_transformer
from song_transform_functions import song_digitizer, song_downsampler

# Resolve songs base directory relative to this script and ensure mp3/piano exists
base_songs = (Path(__file__).resolve().parent / '..' / 'songs').resolve()
base_songs.mkdir(parents=True, exist_ok=True)
(base_songs / 'mp3' / 'piano').mkdir(parents=True, exist_ok=True)

# Use forward-slash style root path so the existing string concatenation in
# `mp3_transformer` using '/' produces valid paths on Windows too.
root_path = str(base_songs).replace('\\', '/')

# SAVE TO WAV
mpt = mp3_transformer(root_path)
mpt.set_input_path('mp3')
mpt.set_output_path('wav')
mpt.set_overwrite(True)

mpt.transform_song([song_downsampler, song_digitizer], mpt._input_folders, 'wav', 8000)
print("Completed transformation of songs to WAV")


# SAVE TO PICKLE
mpt = mp3_transformer(root_path)
mpt.set_input_path('mp3')
mpt.set_output_path('pickle')
mpt.set_overwrite(True)

mpt.transform_song([song_downsampler, song_digitizer], mpt._input_folders, 'pkl')
print("Completed transformation of songs to PICKLE")


