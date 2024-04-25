import cv2
import sqlite3
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import messagebox
import os
from customtkinter import *
import tkinter.ttk as ttk
import pandas as pd
from tkcalendar import DateEntry
import re

# Conectar ao banco de dados
conn = sqlite3.connect('Registros.db')
c = conn.cursor()

# Criar a tabela se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS Registros
             (id INTEGER PRIMARY KEY, nome TEXT, sobrenome TEXT, data_nascimento DATE, foto_path TEXT)''')

# Manter uma referência global para a imagem do rótulo
current_image = None

# Função para atualizar a TreeView com os registros do banco de dados
def update_treeview():
    # Ler os dados da tabela
    df = pd.read_sql_query("SELECT * FROM Registros", conn)

    # Limpar a TreeView
    tree.delete(*tree.get_children())

    # Inserir os dados na TreeView
    for index, row in df.iterrows():
        tree.insert("", "end", values=row.tolist())

# Função para excluir o registro selecionado
def delete_selected_record():
    selected_item = tree.selection()[0]  # Obter o item selecionado
    selected_values = tree.item(selected_item)['values']  # Obter os valores do item selecionado

    selected_id = selected_values[0]  # Obter o ID do item selecionado
    image_path = selected_values[-1]  # Obter o caminho da imagem do item selecionado

    # Excluir o registro do banco de dados
    c.execute("DELETE FROM Registros WHERE id=?", (selected_id,))
    conn.commit()

    # Excluir a imagem
    if os.path.isfile(image_path):
        os.remove(image_path)

    # Excluir o item da TreeView
    tree.delete(selected_item)

def registrar_usuario():
    # Inicializar a webcam
    cap = cv2.VideoCapture(0)

    # Carregar o classificador pré-treinado para detecção de faces
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    conn = sqlite3.connect('Registros.db')

    foto_tirada = False

    def extrair_codificacao_face(frame):
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

            encoding = face.flatten().tolist()
            return encoding

        return None

    def gerar_id():
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

    def fechar():
        conn.close()
        cap.release()
        cv2.destroyAllWindows()
        janelacadastro.destroy()

    def atualizar_frame():
        nonlocal foto_tirada
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

        # Manter uma referência global para a imagem atual
        global current_image
        current_image = img

        # Atualizar o rótulo com o novo frame
        label_cam.img = img
        label_cam.configure(image=img)

        # Chamar a função novamente após um intervalo de tempo
        window.after(10, atualizar_frame)

    def registrar_face():
        nonlocal foto_tirada
        # Ler o frame da webcam
        ret, frame = cap.read()

        # Extrair a codificação da face
        encoding = extrair_codificacao_face(frame)

        if encoding:
            # Inserir a codificação no banco de dados
            nome = entry_nome.get()
            sobrenome = entry_sobrenome.get()
            data_nascimento = entry_data.get()

            # Adicionar validações
            if not nome.isalpha():
                messagebox.showerror("Erro", "O campo 'Nome' deve conter apenas letras.")
                return

            if not sobrenome.isalpha():
                messagebox.showerror("Erro", "O campo 'Sobrenome' deve conter apenas letras.")
                return

            # Função para validar a data de nascimento
            def validar_data(data_nascimento):
                # Expressão regular para o formato DD/MM/AAAA
                regex_data = r'^\d{2}/\d{2}/\d{4}$'

                # Verificar se a data corresponde ao formato esperado
                if not re.match(regex_data, data_nascimento):
                    messagebox.showerror("Erro", "O campo 'Data de Nascimento' deve estar no formato DD/MM/AAAA.")
                    return False

                return True

            # Consultar o banco de dados para verificar se já existe um registro com os mesmos dados
            # Conectar ao banco de dados
            conn = sqlite3.connect('Registros.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Registros WHERE nome=? AND sobrenome=? AND data_nascimento=?", (nome, sobrenome, data_nascimento))
            existing_record = c.fetchone()
            if existing_record:
                messagebox.showerror("Erro", "Já existe um registro com esses dados.")
                return

            # Uso da função na validação da data de nascimento
            if not validar_data(data_nascimento):
                return

            # Salvar a imagem em uma pasta
            id_usuario = gerar_id()
            folder = "faces"
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = f"{folder}/{id_usuario}.jpg"
            cv2.imwrite(path, frame)

            # Converter a imagem para o formato de imagem suportado pelo Tkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(image=img)

            # Manter uma referência global para a imagem atual
            global current_image
            current_image = img

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

    # Criar a janela da interface
    janelacadastro = CTkToplevel(window)
    janelacadastro.title("Cadastro de Usuários")

    # Criar um rótulo para mostrar o feed da webcam
    label_cam = CTkLabel(janelacadastro, text='')
    label_cam.pack()

    # Atualizar o feed da webcam
    atualizar_frame()

    # Criar os campos de entrada para nome, sobrenome e data de nascimento
    label_nome = CTkLabel(janelacadastro, text="Nome:")
    label_nome.pack()
    entry_nome = CTkEntry(janelacadastro)
    entry_nome.pack()
    entry_nome.insert(tk.END, "Exemplo: João")
    entry_nome.bind("<FocusIn>", lambda event: entry_nome.delete(0, tk.END) if entry_nome.get() == "Exemplo: João" else None)
    entry_nome.bind("<FocusOut>", lambda event: entry_nome.insert(tk.END, "Exemplo: João") if entry_nome.get() == "" else None)

    label_sobrenome = CTkLabel(janelacadastro, text="Sobrenome:")
    label_sobrenome.pack()
    entry_sobrenome = CTkEntry(janelacadastro)
    entry_sobrenome.pack()
    entry_sobrenome.insert(tk.END, "Exemplo: Silva")
    entry_sobrenome.bind("<FocusIn>", lambda event: entry_sobrenome.delete(0, tk.END) if entry_sobrenome.get() == "Exemplo: Silva" else None)
    entry_sobrenome.bind("<FocusOut>", lambda event: entry_sobrenome.insert(tk.END, "Exemplo: Silva") if entry_sobrenome.get() == "" else None)

    label_data = CTkLabel(janelacadastro, text="Data de Nascimento:")
    label_data.pack()
    entry_data = DateEntry(janelacadastro, date_pattern='dd/mm/yyyy')
    entry_data.pack()

    # Botão para registrar a face
    button_register = CTkButton(janelacadastro, text="Registrar Face", command=registrar_face)
    button_register.pack()

    # Botão para fechar a janela de cadastro
    button_fechar = CTkButton(janelacadastro, text="Fechar", command=fechar)
    button_fechar.pack()

    # Atualizar a TreeView inicialmente
    update_treeview()

    # Iniciar o loop principal da interface
    janelacadastro.mainloop()

def fechar_db():
        conn.close()
        cv2.destroyAllWindows()
        window.destroy()
        quit()

# Criar uma TreeView para mostrar os registros
window = CTk()
window.title("Registros do Banco de Dados")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
set_appearance_mode("dark")
window.geometry(f"{screen_width}x{screen_height}")
window.columnconfigure((0,1,2,3,4), weight=1)
window.rowconfigure((0,1,2,3,4), weight=1)
window.state('zoomed')

x = (window.winfo_screenwidth() // 2) - (screen_width // 2)
y = (window.winfo_screenheight() // 2) - (screen_height // 2)

tree = ttk.Treeview(window)

style = ttk.Style()
style.configure("Treeview", background="#D9D9D9", foreground="black", fieldbackground="#D9D9D9")

tree['show'] = 'headings'
tree["columns"] = ("id", "nome", "sobrenome", "data_nascimento", "foto_path")
tree.heading(column="id", text="ID")
tree.heading(column="nome", text="Nome")
tree.heading(column="sobrenome", text="Sobrenome")
tree.heading(column="data_nascimento", text="Data de Nascimento")
tree.heading(column="foto_path", text="Caminho da Foto") 
tree.grid(row=2, column=2, padx=x, pady=y, sticky="n")

# Botão para atualizar os registros
button_update = CTkButton(window, text="Atualizar Registros", command=update_treeview)
button_update.place(x=screen_width/2, y=screen_height/2 + 50, anchor="center")

# Botão para registrar a face
button_register = CTkButton(window, text="Registrar Face", command=registrar_usuario)
button_register.place(x=screen_width/2, y=screen_height/2 + 100, anchor="center")

# Botão para excluir o registro selecionado
delete_button = CTkButton(window, text="Excluir", command=delete_selected_record)
delete_button.place(x=screen_width/2, y=screen_height/2 + 150, anchor="center")

# Botão para fechar o programa
button_fechar = CTkButton(window, text="Fechar", command=fechar_db)
button_fechar.place(x=screen_width/2, y=screen_height/2 + 200, anchor="center")

# Atualizar a TreeView inicialmente
update_treeview()

# Iniciar o loop principal da interface
window.mainloop()