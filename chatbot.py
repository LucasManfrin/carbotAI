import tkinter as tk
from tkinter import scrolledtext, messagebox
from google import genai
from google.genai import types
from login import username
from dotenv import load_dotenv
import os
   
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

client = genai.Client()

class ChatbotGUI:
    def __init__(self):
        self.lista_msgs = []
        
        # Criar janela principal
        self.root = tk.Tk()
        self.root.title("Chatbot de Carros")
        self.root.state("zoomed")
        self.root.configure(bg='white')
        
        self.criar_interface()
    
    def criar_interface(self):
        # Título
        titulo = tk.Label(self.root, text="🚗 CHATBOT DE CARROS", 
                         font=('Arial', 16, 'bold'), bg='white')
        titulo.pack(pady=10)
        
        # Área de conversa (histórico)
        self.area_conversa = scrolledtext.ScrolledText(
            self.root, 
            width=140, 
            height=50,
            font=('Arial', 10),
            bg='#f5f5f5',
            state='disabled'
        )
        self.area_conversa.pack(padx=20, pady=10)
        
        # Frame para entrada e botão
        frame_entrada = tk.Frame(self.root, bg='white')
        frame_entrada.pack(fill='x', padx=20, pady=10)
        
        # Campo de entrada
        self.entrada_msg = tk.Entry(
            frame_entrada, 
            font=('Arial', 12),
            border=2,
            width=50
        )
        self.entrada_msg.pack(side='left', fill='x', expand=True)
        
        # Botão enviar
        botao_enviar = tk.Button(
            frame_entrada,
            text="ENVIAR",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            width=10,
            command=self.enviar_mensagem
        )
        botao_enviar.pack(side='right', padx=(10, 0))
        
        # Permitir enviar com Enter
        self.entrada_msg.bind('<Return>', lambda event: self.enviar_mensagem())
        
        # Mensagem inicial
        self.adicionar_mensagem(f"Bot", f"Olá {username}! Sou seu assistente especialista em carros! Como posso te ajudar hoje?")
    
    def enviar_mensagem(self):
        mensagem = self.entrada_msg.get().strip()
        
        if not mensagem:
            return
        
        if mensagem.lower() == "sair":
            self.root.quit()
            return
        
        # Mostrar mensagem do usuário
        self.adicionar_mensagem("Você", mensagem)
        self.entrada_msg.delete(0, tk.END)
        
        try:
            # Enviar para a API
            resposta = self.enviar_msg_api(mensagem)
            self.adicionar_mensagem("Bot", resposta.text)
        except Exception as e:
            self.adicionar_mensagem("Bot", f"Erro: {str(e)}")
    
    def enviar_msg_api(self, msg):
        self.lista_msgs.append({"role": "user", "content": msg})
        
        resposta = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=msg,
            config=types.GenerateContentConfig(
                system_instruction="Você é um assistente, especialista e entusiasta de carros, com uma paixão especial por carros esportivos. Seu papel é ajudar o usuário a encontrar o carro ideal, focado nos objetivos dele. Seu tom é objetivo, mas não sério, usando uma linguagem um pouco mais informal e entusiasmada. Siga estas instruções rigorosamente para manter as respostas curtas e úteis: Forneça no máximo 5 sugestões de carros por pergunta, Para cada carro sugerido, use uma lista de pontos para descrever brevemente: 'Por que é incrível' e 'O que observar', Mantenha cada ponto com no máximo duas frases curtas e Inclua uma conclusão de no máximo duas frases.!"
            )
        )
        
        self.lista_msgs.append(resposta)
        return resposta
    
    def adicionar_mensagem(self, remetente, mensagem):
        self.area_conversa.config(state='normal')
        self.area_conversa.insert(tk.END, f"{remetente}: {mensagem}\n\n")
        self.area_conversa.config(state='disabled')
        self.area_conversa.see(tk.END)  # Scroll para o final
    
    def executar(self):
        self.root.mainloop()

# Executar o chatbot
if __name__ == "__main__":
    chatbot = ChatbotGUI()
    chatbot.executar()