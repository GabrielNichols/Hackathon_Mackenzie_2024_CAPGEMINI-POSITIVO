import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Carregar o classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Criar a janela da interface
window = tk.Tk()
window.title("Reconhecimento Facial")
window.geometry("600x500")

# Criar um rótulo para exibir a imagem
label = tk.Label(window)
label.pack()

def update_frame():
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Converter o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar as faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Desenhar retângulos ao redor das faces detectadas
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Converter o frame para o formato de imagem suportado pelo Tkinter
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img = img.resize((600, 500), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(image=img)

    # Atualizar o rótulo com a nova imagem
    label.configure(image=img_tk)
    label.image = img_tk

    # Chamar a função novamente após um intervalo de tempo
    window.after(10, update_frame)

# Chamar a função para atualizar o frame inicialmente
update_frame()

# Iniciar o loop principal da interface
window.mainloop()

# Liberar a webcam
cap.release()
cv2.destroyAllWindows()

