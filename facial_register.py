from datetime import date
import cv2
import sqlite3
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import messagebox
import uuid
import deepface
import os
import random

# Inicializar a webcam
cap = cv2.VideoCapture(0)

# Carregar o classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Conectar ao banco de dados
conn = sqlite3.connect('Registros.db')
c = conn.cursor()

# Criar a tabela se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS Registros
             (id INTEGER PRIMARY KEY, nome TEXT, sobrenome TEXT, data_nascimento DATE, foto_path TEXT)''')

foto_tirada = False
def register_face():
    global foto_tirada

def extract_face_encoding(frame):
    # Converter o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar as faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Verificar se foi detectada exatamente uma face
    if len(faces) == 1:
        (x, y, w, h) = faces[0]
        face = gray[y:y+h, x:x+w]
        # Redimensionar a face para um tamanho fixo
        face = cv2.resize(face, (100, 100))

        # Codificar a face usando numpy
        encoding = face.flatten().tolist()
        return encoding

    return None

def generate_id():
    # Conectar ao banco de dados
    conn = sqlite3.connect('Registros.db')
    c = conn.cursor()

    # Obter o maior ID atualmente no banco de dados
    c.execute('SELECT MAX(id) FROM Registros')
    max_id = c.fetchone()[0]

    # Se a tabela estiver vazia, começar do 1
    if max_id is None:
        return '00001'

    # Gerar o próximo ID adicionando 1 ao maior ID atual
    next_id = int(max_id) + 1

    # Retornar o próximo ID como uma string de 5 dígitos
    return str(next_id).zfill(5)

def register_face():
    # Ler o frame da webcam
    ret, frame = cap.read()

    # Extrair a codificação da face
    encoding = extract_face_encoding(frame)

    if encoding:
        # Inserir a codificação no banco de dados
        nome = entry_nome.get()
        sobrenome = entry_sobrenome.get()
        data_nascimento = entry_data.get()

        # Salvar a imagem em uma pasta
        id_usuario = generate_id()
        folder = "faces"
        if not os.path.exists(folder):
            os.makedirs(folder)
        path = f"{folder}/{id_usuario}.jpg"
        cv2.imwrite(path, frame)

        # Converter a imagem para o formato de imagem suportado pelo Tkinter
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)

        # Atualizar o rótulo com a nova imagem
        label_cam.img = img
        label_cam.configure(image=img)

        foto_tirada = True

        # Conectar ao banco de dados
        conn = sqlite3.connect('Registros.db')
        c = conn.cursor()

        # Inserir os dados na tabela
        c.execute('INSERT INTO Registros (id, nome, sobrenome, data_nascimento, foto_path) VALUES (?, ?, ?, ?, ?)',
                  (id_usuario, nome, sobrenome, data_nascimento, path))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Face registrada com sucesso!")

        window.after(3500, fechar)
    else:
        messagebox.showwarning("Erro", "Nenhuma face detectada ou mais de uma face detectada.")

# Função para fechar a conexão com o banco de dados e finalizar o programa
def fechar():
    conn.close()
    cap.release()
    cv2.destroyAllWindows()
    window.destroy()

    # Fechar o programa
    quit()

# Criar a janela da interface
window = tk.Tk()
window.title("Cadastro de Usuários")

# Criar um rótulo para mostrar o feed da webcam
label_cam = tk.Label(window)
label_cam.pack()

# Criar os campos de entrada para nome, sobrenome e data de nascimento
label_nome = tk.Label(window, text="Nome:")
label_nome.pack()
entry_nome = tk.Entry(window)
entry_nome.pack()

label_sobrenome = tk.Label(window, text="Sobrenome:")
label_sobrenome.pack()
entry_sobrenome = tk.Entry(window)
entry_sobrenome.pack()

label_data = tk.Label(window, text="Data de Nascimento:")
label_data.pack()
entry_data = tk.Entry(window)
entry_data.pack()

# Botão para registrar a face
button_register = tk.Button(window, text="Registrar Face", command=register_face)
button_register.pack()

# Botão para fechar o programa
button_fechar = tk.Button(window, text="Fechar", command=fechar)
button_fechar.pack()

def update_frame():
    global foto_tirada
    # Ler o frame da webcam
    ret, frame = cap.read()

    if foto_tirada:
        return

    # Converter o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar as faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Desenhar retângulos ao redor das faces detectadas
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Converter o frame para o formato de imagem suportado pelo Tkinter
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)

    # Atualizar o rótulo com o novo frame
    label_cam.img = img
    label_cam.configure(image=img)

    # Chamar a função novamente após um intervalo de tempo
    window.after(10, update_frame)

# Chamar a função para atualizar o frame inicialmente
update_frame()

# Iniciar o loop principal da interface
window.mainloop()