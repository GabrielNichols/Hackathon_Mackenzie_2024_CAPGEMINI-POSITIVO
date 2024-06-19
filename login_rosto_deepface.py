import cv2
import deepface.DeepFace
import mediapipe as mp
import numpy as np
import os
import tkinter as tk
from customtkinter import *
from PIL import Image, ImageTk
import threading

# Caminho para a pasta com as imagens cadastradas
folder = 'faces'

# Configuração do MediaPipe
mp_face_mesh = mp.solutions.face_mesh

# Inicializar a captura de vídeo
cap = cv2.VideoCapture(0)

# Parâmetros para a detecção de piscadas
EAR_THRESHOLD = 0.2
EAR_CONSEC_FRAMES = 3

def calculate_eye_aspect_ratio(landmarks, eye_indices):
    eye_points = np.array([landmarks[i] for i in eye_indices])
    vertical = np.linalg.norm(eye_points[1] - eye_points[5]) + np.linalg.norm(eye_points[2] - eye_points[4])
    horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
    ear = vertical / (2.0 * horizontal)
    return ear

right_eye_indices = [33, 160, 158, 133, 153, 144]
left_eye_indices = [362, 385, 387, 263, 373, 380]

def verificar_piscada(callback):
    update_message("Por favor, pisque agora.")
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        frame_count = 0
        blink_count = 0

        while frame_count < 100:
            success, frame = cap.read()
            if not success:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                for landmarks in results.multi_face_landmarks:
                    landmark_list = [(lm.x * frame.shape[1], lm.y * frame.shape[0]) for lm in landmarks.landmark]
                    right_ear = calculate_eye_aspect_ratio(landmark_list, right_eye_indices)
                    left_ear = calculate_eye_aspect_ratio(landmark_list, left_eye_indices)

                    if (right_ear + left_ear) / 2 < EAR_THRESHOLD:
                        blink_count += 1
                    else:
                        blink_count = 0

                    if blink_count >= EAR_CONSEC_FRAMES:
                        callback(True)
                        return
            frame_count += 1

        callback(False)

def register_face():
    global foto_tirada

    if any(file.endswith('.jpg') for file in os.listdir(folder)):
        foto_tirada = True
    else:
        foto_tirada = False

    if not foto_tirada:
        update_message("Por favor, registre a face antes de verificar.")
        return

    def on_blink_detected(piscou):
        if piscou:
            face_recognized = False
            while not face_recognized:
                ret, frame = cap.read()
                cv2.imwrite('faces/temp.jpg', frame)
                img1 = 'faces/temp.jpg'
                for file in os.listdir(folder):
                    if file.endswith('.jpg') and not file == 'temp.jpg':
                        img2 = os.path.join(folder, file)
                        try:
                            result = deepface.DeepFace.verify(img1_path=img1, img2_path=img2)
                            if result['verified']:
                                update_message(f"Rosto reconhecido como {file}")
                                show_border_green()
                                face_recognized = True
                                break
                        except Exception as e:
                            print("Erro ao verificar faces:", e)
                if not face_recognized:
                    update_message("Rosto não reconhecido.")
                    show_border_red()
                    break
            os.remove('faces/temp.jpg')
            foto_tirada = False
        else:
            update_message("Não foi possível detectar a piscada.")

    threading.Thread(target=verificar_piscada, args=(on_blink_detected,)).start()

def show_border_green():
    border_label_green.place(relx=0.5, rely=0, anchor='n')
    window.after(4000, border_label_green.place_forget)  # Hide the border after 4 seconds

def show_border_red():
    border_label_red.place(relx=0.5, rely=0, anchor='n')
    window.after(4000, border_label_red.place_forget)  # Hide the border after 4 seconds

def update_frame():
    ret, frame = cap.read()
    if ret:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img)
        label_cam.imgtk = img_tk
        label_cam.configure(image=img_tk)
    window.after(10, update_frame)

def update_message(message):
    label_info.configure(text=message)
    window.after(4000, lambda: label_info.configure(text=""))

def fechar():
    cap.release()
    cv2.destroyAllWindows()
    window.destroy()

window = CTk()
window.title("Login de Usuários")
window.geometry("600x600")

label_cam = CTkLabel(window, text="", bg_color="transparent")
label_cam.pack()

label_info = CTkLabel(window, text="", font=("Helvetica", 16), bg_color="transparent")
label_info.place(relx=0.5, rely=0.1, anchor="center")

border_label_green = CTkLabel(window, text='', height=10, bg_color="#00FF00", width=window.winfo_screenwidth())
border_label_red = CTkLabel(window, text='', height=10, bg_color="#FF0000", width=window.winfo_screenwidth())

update_frame()

button_verificar = CTkButton(window, text="Verificar Face", command=register_face)
button_verificar.pack()

button_fechar = CTkButton(window, text="Fechar", command=fechar)
button_fechar.pack()

window.mainloop()
