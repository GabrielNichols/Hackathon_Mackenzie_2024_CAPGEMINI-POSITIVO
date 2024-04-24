import sounddevice as sd
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.spatial import distance

# Função para gravar áudio
def record_audio(duration, filename):
    fs = 44100  # Taxa de amostragem
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    sd.write(filename, audio, fs)

# Gravar áudio
record_audio(2, 'audio_registro.wav')

# Carregar áudio
audio_registro, fs = librosa.load('audio_registro.wav', sr=None)

# Calcular espectrograma
spectrogram_registro = librosa.feature.melspectrogram(y=audio_registro, sr=fs)
spectrogram_registro_db = librosa.power_to_db(spectrogram_registro, ref=np.max)

# Plotar espectrograma
librosa.display.specshow(spectrogram_registro_db, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Espectrograma do Áudio de Registro')
plt.show()

# Exemplo de áudio para comparar (pode ser outro áudio gravado anteriormente)
audio_a_comparar, fs = librosa.load('audio_a_comparar.wav', sr=None)

# Calcular espectrograma
spectrogram_a_comparar = librosa.feature.melspectrogram(y=audio_a_comparar, sr=fs)
spectrogram_a_comparar_db = librosa.power_to_db(spectrogram_a_comparar, ref=np.max)

# Comparar espectrogramas
dist = distance.euclidean(spectrogram_registro_db.ravel(), spectrogram_a_comparar_db.ravel())
print(f"Distância Euclidiana entre os Espectrogramas: {dist}")
