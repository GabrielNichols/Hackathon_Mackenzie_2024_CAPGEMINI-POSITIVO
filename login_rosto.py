from deepface import DeepFace
import cv2
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Caminho para a pasta com as imagens cadastradas
folder = 'faces'

# Carregar o classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def register_face():
    global foto_tirada  # Define a variável como global para que ela seja a mesma fora da função

    if any(file.endswith('.jpg') for file in os.listdir('faces')):
        foto_tirada = True
    else:
        foto_tirada = False

    if not foto_tirada:
        messagebox.showwarning("Aviso", "Por favor, registre a face antes de verificar.")
        return
    
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Salvar temporariamente o frame como imagem
    cv2.imwrite('temp.jpg', frame)

    # Comparar o rosto detectado na webcam com as imagens da pasta
    for file in os.listdir(folder):
        if file.endswith('.jpg'):
            path = os.path.join(folder, file)
            result = DeepFace.verify('temp.jpg', path)

            # Se o rosto na webcam for reconhecido, exibir uma mensagem
            if result['verified']:
                messagebox.showinfo("Sucesso", f"Rosto reconhecido como {file}")
                break
    else:
        messagebox.showwarning("Aviso", "Rosto não reconhecido.")

    # Excluir a imagem temporária
    os.remove('temp.jpg')

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

window = tk.Tk()
window.title("Login de Usuários")
window.geometry("600x600")

# Inicializar a webcam após a criação da janela principal do Tkinter
cap = cv2.VideoCapture(0)
label_cam = tk.Label(window)
label_cam.pack()
update_frame()

# Botão para verificar a face
button_verificar = tk.Button(window, text="Verificar Face", command=register_face)
button_verificar.pack()

# Botão para fechar o programa
button_fechar = tk.Button(window, text="Fechar", command=fechar)
button_fechar.pack()

window.mainloop()