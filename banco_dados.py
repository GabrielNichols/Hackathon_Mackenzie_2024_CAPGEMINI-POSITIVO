import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
import os

# Conectar ao banco de dados
conn = sqlite3.connect('Registros.db')
c = conn.cursor()

# Criar a tabela se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS Registros
             (id INTEGER PRIMARY KEY, nome TEXT, sobrenome TEXT, data_nascimento DATE, foto_path TEXT)''')

# Função para atualizar a TreeView com os registros do banco de dados
def update_treeview():
    # Ler os dados da tabela
    df = pd.read_sql_query("SELECT * FROM Registros", conn)

    # Limpar a TreeView
    for i in tree.get_children():
        tree.delete(i)

    # Inserir os dados na TreeView
    for index, row in df.iterrows():
        tree.insert("", "end", values=row.tolist())

# Criar a janela da interface
window = tk.Tk()
window.title("Registros do Banco de Dados")

# Criar uma TreeView para mostrar os registros
tree = ttk.Treeview(window)
tree['show'] = 'headings'
tree["columns"] = ("id", "nome", "sobrenome", "data_nascimento", "foto_path")
tree.heading("id", text="ID")
tree.heading("nome", text="Nome")
tree.heading("sobrenome", text="Sobrenome")
tree.heading("data_nascimento", text="Data de Nascimento")
tree.heading("foto_path", text="Caminho da Foto")
tree.pack()

# Botão para atualizar os registros
button_update = tk.Button(window, text="Atualizar Registros", command=update_treeview)
button_update.pack()

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

# Criar um botão para excluir o registro selecionado
delete_button = ttk.Button(window, text="Excluir", command=delete_selected_record)
delete_button.pack()

# Função para fechar a conexão com o banco de dados e finalizar o programa
def fechar():
    conn.close()
    window.quit()

# Botão para fechar o programa
button_fechar = tk.Button(window, text="Fechar", command=fechar)
button_fechar.pack()

# Atualizar a TreeView inicialmente
update_treeview()

# Iniciar o loop principal da interface
window.mainloop()