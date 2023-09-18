import pyaudio
import wave
import speech_recognition as sr
from flask import Flask, make_response
from flask_cors import CORS
import time
import os
import threading

text = 'Não entendi o que você disse!'

def delete_file_after_delay(filename, delay=1):
    """Delete a file after a certain delay (in seconds)."""
    time.sleep(delay)
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Arquivo {filename} foi excluído!")
    else:
        print(f"Arquivo {filename} não encontrado!")


def capturar_audio(nome_arquivo="audio_capturado.wav", duracao=5):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
    )
    frames = []

    for _ in range(0, int(RATE / CHUNK * duracao)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(nome_arquivo, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Transcrevendo o áudio capturado
    recognizer = sr.Recognizer()
    with sr.AudioFile(nome_arquivo) as source:
        recognizer.adjust_for_ambient_noise(source)
        captured_audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(captured_audio, language="pt-BR")
            
        except sr.UnknownValueError:
            text = "Não foi possível entender o áudio!"
        except sr.RequestError:
            text = "Houve um erro ao tentar se conectar com a API de reconhecimento de fala."
        
        print(text)
        return text

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def capturar():
    nome_arquivo = "audio_capturado.wav"
    print("Capturando audio...")
    texto = capturar_audio(nome_arquivo=nome_arquivo)
    print("Áudio capturado!")

    threading.Thread(target=delete_file_after_delay, args=(nome_arquivo,)).start()

    resposta = make_response(texto)
    
    resposta.headers['Content-Type'] = 'text/plain'
    
    return resposta

if __name__ == "__main__":
     app.run(host='26.150.219.242', port=5000, debug=True)
     

