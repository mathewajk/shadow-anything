import parselmouth
from parselmouth.praat import call
from flask import Flask, flash, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import tempfile
import numpy as np
UPLOAD_FOLDER = 'files'

app = Flask(__name__)
app.config.from_object('settings')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# enable CORS
CORS(app, resources={r'/*': {'origins': app.config['CLIENT_URL']}})

@app.route('/', methods=['GET'])
def root():
    return app.send_static_file('index.html')

@app.route('/pitch', methods=['POST'])
def pitch_track():
    pitch_track = []
    formants = []
    with tempfile.NamedTemporaryFile(suffix=".blob") as tmp:
        tmp.write(request.files['audio'].read())
        tmp.seek(0)
        audio = AudioSegment.from_file(tmp.name)
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
            audio.export(wav_file.name, format="wav")
            wav_file.seek(0)
            sound = parselmouth.Sound(wav_file.name).convert_to_mono()
            try:
                trimmed_sound = call(sound, "Trim silences", 0.08, True, 100, 0.0, -15.0, 0.1, 0.05, False, "trimmed")[0]
            except Exception as e:
                print(e)
                trimmed_sound = sound
            pitch_track = get_pitch(trimmed_sound)
            formants = get_formants(trimmed_sound)
    return jsonify({
        'pitch_track': list(pitch_track),
        'formant_track': formants,
    })

def get_pitch(sound):
    pitch = sound.to_pitch()
    pitch_values = list(zip(pitch.ts() - pitch.get_start_time(), pitch.selected_array['frequency']))
    return pitch_values

def get_formants(sound):
    TARGET_FORMANTS = [1, 2]
    formant_track = sound.to_formant_burg(max_number_of_formants=5)
    times = formant_track.ts()
    formants = {}
    for formant in TARGET_FORMANTS:
        formants[f'F{formant}'] = [[time - formant_track.get_start_time(), get_formant_at_time(formant_track, formant, time)] for time in times]
    return formants

def get_formant_at_time(formant_track, formant_number, time):
    formant_value = formant_track.get_value_at_time(formant_number = formant_number, time = time)
    if np.isnan(formant_value):
        return 'NaN'
    else:
        return formant_value

if __name__ == '__main__':
    app.run()