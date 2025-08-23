import tkinter as tk
from tkinter import messagebox
import sqlite3, logging
from login import LoginScreen



logging.basicConfig(level=logging.DEBUG, format="- %(filename)s - %(levelname)s - %(message)s")

class CadastroScreen:
    
    def __init__(self):
        # Criar janela principal
        self.root = tk.Tk()
        self.root.title("CADASTRO")
        self.root.geometry("500x400")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.root.eval('tk::PlaceWindow . center')
        
        self.create_widgets()
    
    def create_widgets(self):
        # Título
        title = tk.Label(self.root, text="CRIAR CONTA", font=("Arial", 16, "bold"), 
                        bg='white', fg='#333')
        title.pack(pady=20)
        
        # Campo Nome
        tk.Label(self.root, text="Nome:", font=("Arial", 10), bg='white').pack(anchor='w', padx=50)
        self.nome_entry = tk.Entry(self.root, font=("Arial", 12), width=25)
        self.nome_entry.pack(pady=5)
        
        # Campo Senha
        tk.Label(self.root, text="Senha:", font=("Arial", 10), bg='white').pack(anchor='w', padx=50)
        self.senha_entry = tk.Entry(self.root, font=("Arial", 12), width=25, show="*")
        self.senha_entry.pack(pady=5)
        
        # Campo Confirmar Senha
        tk.Label(self.root, text="Confirmar Senha:", font=("Arial", 10), bg='white').pack(anchor='w', padx=50)
        self.confirmar_senha_entry = tk.Entry(self.root, font=("Arial", 12), width=25, show="*")
        self.confirmar_senha_entry.pack(pady=5)
        
        # Botão Cadastrar
        cadastrar_btn = tk.Button(self.root, text="CADASTRAR", font=("Arial", 12, "bold"),
                                bg='#4CAF50', fg='white', width=20, height=1,
                                command=self.on_cadastrar_click)
        cadastrar_btn.pack(pady=20)

        # Botao Voltar
        voltar_btn = tk.Button(self.root, text="VOLTAR", font=("Arial", 12, "bold"),
                                bg='#4CAF50', fg='white', width=20, height=1,
                                command=self.on_voltar_click)
        voltar_btn.pack(pady=5)

    def on_voltar_click(self):
        self.root.destroy()
        LoginScreen()
    
    def on_cadastrar_click(self):
        # Aqui você adicionará a lógica de cadastro
        nome = self.nome_entry.get()
        senha = self.senha_entry.get()
        confirmar_senha = self.confirmar_senha_entry.get()

        # Conexao com o banco
        try:
            conexao = sqlite3.connect("carros.db")
            cursor = conexao.cursor()

            # Validacao se o usuario existe
            cursor.execute("SELECT id FROM users WHERE login = ?", (nome,))
            usuario_existe = cursor.fetchone()

            if usuario_existe:
                # Se o fetchone() retornar algo, o usuario existe
                messagebox.showinfo("Erro", "Este usuario ja esta cadastrado.")
            else:
                if nome and senha and confirmar_senha:
                    if senha == confirmar_senha:
                        cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)", (nome, senha))
                        conexao.commit()
                        logging.debug(f"Usuario adicionado: {nome}")
                        logging.debug(f"Senha adicionada: {senha}")
                        messagebox.showinfo("Sucesso", f"Cadastro realizado para: {nome}")
                        self.root.destroy()
                        LoginScreen()
                    else:
                        messagebox.showerror("Erro", "Senhas não coincidem!")
                    
                else:
                    messagebox.showerror("Erro", "Preencha todos os campos!")

        except Exception as e:
            messagebox.showerror("Erro", f"Problema no banco de dados: {e}")    

        finally:
            conexao.close()
        
    
    def run(self):
        self.root.mainloop()

# Para executar a tela
if __name__ == "__main__":
    app = CadastroScreen()
    app.run()
