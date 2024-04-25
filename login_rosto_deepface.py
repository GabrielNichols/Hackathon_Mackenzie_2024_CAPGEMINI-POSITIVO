from deepface import DeepFace
import cv2
import os
import tkinter as tk
from customtkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import dlib
from scipy.spatial import distance as dist

# Caminho para a pasta com as imagens cadastradas
folder = 'faces'

# Carregar o classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Carregar o detector de pontos faciais pré-treinado
predictor_path = 'shape_predictor_68_face_landmarks.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

# Função para calcular a razão de abertura dos olhos
def eye_aspect_ratio(eye):
    # Calcular as distâncias euclidianas entre os pontos verticais dos olhos
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Calcular as distâncias euclidianas entre os pontos horizontais dos olhos
    C = dist.euclidean(eye[0], eye[3])

    # Calcular a razão de abertura dos olhos
    ear = (A + B) / (2.0 * C)

    return ear

# Definir os limites da razão de abertura dos olhos
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3

# Inicializar o contador de frames consecutivos com os olhos fechados
COUNTER = 0

# Inicializar o detector de faces
detector = dlib.get_frontal_face_detector()

# Inicializar o preditor facial
predictor = dlib.shape_predictor(predictor_path)

# Inicializar a captura de vídeo
cap = cv2.VideoCapture(0)

def verificar_piscada():
    global COUNTER

    # Definir a quantidade de frames para verificar a piscada
    frames_piscada = 3

    while True:
        # Ler o frame da webcam
        ret, frame = cap.read()

        # Redimensionar o frame para melhorar o desempenho
        frame = cv2.resize(frame, (480, 360))

        # Converter o frame para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar as faces no frame
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            # Calcular a razão de abertura dos olhos
            left_eye = shape[42:48]
            right_eye = shape[36:42]
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            # Calcular a média das razões de abertura dos olhos
            ear = (left_ear + right_ear) / 2.0

            # Se a razão de abertura dos olhos for menor que o limite, incrementar o contador
            if ear < EYE_AR_THRESH:
                COUNTER += 1

                # Se o contador atingir o número de frames consecutivos necessários, retornar True
                if COUNTER >= frames_piscada:
                    # Reiniciar o contador para a próxima verificação
                    COUNTER = 0
                    return True

            # Caso contrário, reiniciar o contador
            else:
                COUNTER = 0

        # Checar se a tecla 'q' foi pressionada para sair do loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return False


def register_face():
    global foto_tirada  # Define a variável como global para que ela seja a mesma fora da função

    if any(file.endswith('.jpg') for file in os.listdir('faces')):
        foto_tirada = True
    else:
        foto_tirada = False

    if not foto_tirada:
        messagebox.showwarning("Aviso", "Por favor, registre a face antes de verificar.")
        return

    # Exibir a mensagem para o usuário piscar
    messagebox.showinfo("Aviso", "Por favor, pisque para verificar.")

    # Aguardar até que a piscada seja detectada
    while True:
        if verificar_piscada():
            break

    # Ler o frame da webcam
    ret, frame = cap.read()

    # Salva a imagem temporária na pasta faces
    cv2.imwrite('faces/temp.jpg', frame)

    # Comparar o rosto detectado na webcam com as imagens da pasta
    for file in os.listdir(folder):
        if file.endswith('.jpg') and not file == 'temp.jpg':
            path = os.path.join(folder, file)

            img1 = path
            img2 = 'faces/temp.jpg'

            result = DeepFace.verify(img1, img2, model_name="VGG-Face")

            # Se o rosto na webcam for reconhecido, exibir uma mensagem
            if result['verified']:
                messagebox.showinfo("Sucesso", f"Rosto reconhecido como {file}")
                break
    else:
        messagebox.showwarning("Aviso", "Rosto não reconhecido.")

    # Excluir a imagem temporária
    os.remove('faces/temp.jpg')

    foto_tirada = False

def update_frame():
    # Ler o frame da webcam
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detectar as faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Desenhar retângulos ao redor das faces detectadas
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # Exibir o frame na label_cam
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)
    label_cam.img = img
    label_cam.configure(image=img)
    window.after(10, update_frame)

def fechar():
    cap.release()
    cv2.destroyAllWindows()
    window.destroy()
    quit()

window = CTk()
window.title("Login de Usuários")
window.geometry("600x600")

# Inicializar a webcam após a criação da janela principal do Tkinter
cap = cv2.VideoCapture(0)
label_cam = tk.Label(window)
label_cam.pack()
update_frame()

# Botão para verificar a face
button_verificar = CTkButton(window, text="Verificar Face", command=register_face)
button_verificar.pack()

# Botão para fechar o programa
button_fechar = CTkButton(window, text="Fechar", command=fechar)
button_fechar.pack()

window.mainloop()