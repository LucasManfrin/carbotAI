import tkinter as tk
from tkinter import messagebox
import sqlite3
from cadastro import CadastroScreen


class LoginScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        self.center_window()
        
        self.create_widgets()
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Cria os widgets da interface"""
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        title_label = tk.Label(main_frame, text="LOGIN", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        tk.Label(main_frame, text="Usuário:", font=("Arial", 10)).pack(anchor='w')
        self.username_entry = tk.Entry(main_frame, font=("Arial", 10), width=25)
        self.username_entry.pack(pady=(0, 10), fill='x')
        
        tk.Label(main_frame, text="Senha:", font=("Arial", 10)).pack(anchor='w')
        self.password_entry = tk.Entry(main_frame, font=("Arial", 10), width=25, show="*")
        self.password_entry.pack(pady=(0, 20), fill='x')
        
        login_button = tk.Button(
            main_frame, 
            text="ENTRAR", 
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            cursor="hand2",
            command=self.on_login_click
        )
        login_button.pack(fill='x', pady=5)

        cadastro = tk.Button(
            main_frame, 
            text="NÃO POSSUI LOGIN? CLIQUE AQUI!", 
            font=("Arial", 12, "bold"),
            bg="#4CAF59",
            fg="white",
            cursor="hand2",
            command=self.ir_para_cadastro
        )
        cadastro.pack(fill='x', pady=5)

    def ir_para_cadastro(self):
        """Função chamada quando clica no botão entrar"""
        self.root.destroy() # Fecha a tela de login
        CadastroScreen() # Abre a tela de cadastro
        
    def on_login_click(self):
        """Função chamada quando clica no botão entrar"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
            
        # Conexao com o banco
        try:
            conexao = sqlite3.connect('carros.db')
            cursor = conexao.cursor()
            # Lendo a senha do usuario
            cursor.execute("SELECT password FROM users WHERE login = ?", (username,))
            senha = cursor.fetchone()
            # print("Senha no banco: ", senha[0])
            # print("Senha digitado: ", password)

        except Exception as e:
            messagebox.showerror("Erro", f"Problema no banco de dados: {e}")

        finally:
           conexao.close()
        
        # Validacao de Login
        if senha:
            if str(senha[0]).strip() == str(password).strip():
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "Usuário não encontrado!")

 
        
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

# Executar a aplicação
if __name__ == "__main__":
    app = LoginScreen()
    app.run()
