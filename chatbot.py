import tkinter as tk
from tkinter import scrolledtext, messagebox
from google import genai
from google.genai import types
from login import username
from dotenv import load_dotenv
import os, json, sqlite3, logging

logging.basicConfig(level=logging.DEBUG, format="- %(filename)s -  %(levelname)s - %(message)s") # Config do logging
   
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

client = genai.Client()

class ChatbotGUI:
    def __init__(self):
        self.lista_msgs = []
        
        self.iniciar_db()

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
            logging.info("Saindo...")
            self.root.quit()
            return
        
        self.adicionar_mensagem("Você", mensagem)
        self.entrada_msg.delete(0, tk.END)
        
        try:
            logging.info(f"Enviando mensagem para a API: '{mensagem}'")
            resposta = self.enviar_msg_api(mensagem)
            resposta_bot = resposta.text
            
            # Tentar encontrar e isolar o JSON na resposta do bot
            try:
                # Procura o início e o fim do bloco JSON
                inicio_json = resposta.text.find('{')
                fim_json = resposta.text.rfind('}') + 1
                
                if inicio_json != -1 and fim_json != -1:
                    json_string = resposta.text[inicio_json:fim_json]
                    
                    # Tenta decodificar o JSON extraído
                    dados_json = json.loads(json_string)
                    acao = dados_json.get('acao')
                    dados = dados_json.get('dados')

                    logging.debug(f"JSON decodificado: {dados_json}")
                    logging.debug(f"Ação identificada: {acao}")
                    
                    if acao == 'salvar_carro':
                        if dados and isinstance(dados, dict):
                            model = dados.get('model')
                            cv = dados.get('cv')
                            mark = dados.get('mark')
                            price = dados.get('price')

                            if model:
                                logging.info(f"Ação: salvar_carro para o modelo '{model}'")
                                resposta_bot = self.salvar_carro_db(model, cv, mark, price)
                            else:
                                resposta_bot = "Desculpe, não consegui identificar o nome do carro para salvar."
                        else:
                            resposta_bot = "Formato de dados inválido para a ação de salvar carro."

                    elif acao == 'listar_carros':
                        logging.info("Ação: listar_carros")
                        resposta_bot = self.listar_carros_db()
                    
                    elif acao == 'deletar_carro':
                        if dados and isinstance(dados, dict):
                            model = dados.get('model')
                            if model:
                                logging.info(f"Ação: deletar_carro para o modelo '{model}'")
                                resposta_bot = self.deletar_carro_db(model)
                            else:
                                resposta_bot = "Desculpe, não consegui identificar o nome do carro para deletar."
                        else:
                            resposta_bot = "Formato de dados inválido para a ação de deletar carro."
                    
                    else:
                        logging.warning(f"Ação não reconhecida: '{acao}'")
                        resposta_bot = "Não entendi a ação que você me pediu para fazer."
                
                else:
                    logging.info("Não foi possível encontrar um JSON na resposta da API.")
                    # Continua com a resposta_bot como resposta.text
            
            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"Erro ao decodificar JSON ou dados ausentes: {e}")
                logging.info("Tratando como texto livre.")
                # A resposta_bot já tem o texto padrão, então não faz nada
                pass
            
            self.adicionar_mensagem("Bot", resposta_bot)

        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado: {e}")
            self.adicionar_mensagem("Bot", f"Erro: {str(e)}")
    
    def enviar_msg_api(self, msg):
        self.lista_msgs.append({"role": "user", "content": msg})

        # Instrucao para o chatbot
        instruction = (
            "Você é um assistente, especialista e entusiasta de carros. Seu papel é ajudar o usuário a encontrar o carro ideal."
    "Você deve interpretar a intenção do usuário e responder de uma das seguintes formas:"
    "1. Se o usuário estiver fazendo uma pergunta geral sobre carros, responda com texto livre, dando no máximo 5 sugestões de carros, descrevendo-os brevemente. Destaque os pontos fortes dos carros, torque, cv, entre outros."
    "2. Se o usuário pedir para 'salvar', 'adicionar' ou 'guardar' um carro, responda APENAS com um JSON contendo a 'acao' e os 'dados' para a operação. Não inclua texto livre. O JSON deve ter o seguinte formato: {'acao': 'salvar_carro', 'dados': {'model': 'Nome do Carro', 'cv': 'Potencia do Carro', 'mark': 'Marca do Carro', 'price': 'Preco do Carro'}}."
    "3. Se o usuário pedir para 'ver' ou 'listar' os carros salvos, responda APENAS com um JSON no formato: {'acao': 'listar_carros'}."
    "4. Se o usuário pedir para 'deletar' um carro, responda APENAS com um JSON no formato: {'acao': 'deletar_carro', 'dados': {'model': 'Nome do Carro'}}."
    "Sempre extraia o nome do modelo do carro da mensagem do usuário e preencha o campo 'model' no JSON."

        )
        
        resposta = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=msg,
            config=types.GenerateContentConfig(
                system_instruction= instruction
            )
        )
        
        self.lista_msgs.append(resposta)
        return resposta
    
    def iniciar_db(self):
        # Inicia a conexao com o banco de dados
        self.conexao = sqlite3.connect("carros.db")
        self.cursor = self.conexao.cursor()


    def salvar_carro_db(self, model, cv, mark, price):
        # Salva o carro no banco de dados
        # Falta salvar o restante das coisas cd, mark, price
        try:
            self.cursor.execute("INSERT INTO cars (model, cv, mark, price) VALUES (?, ?, ?, ?)", (model, cv, mark, price,))
            self.conexao.commit()
            return f"O carro '{model}' foi salvo com sucesso!"
        except sqlite3.IntegrityError:
            return f"O carro '{model}' já está na sua lista."
        except Exception as e:
            return f"Ocorreu um erro inesperado ao tentar salvar o carro: {e}"
        

    def listar_carros_db(self):
        # Lista todos os carros salvos no banco
        self.cursor.execute("SELECT model FROM cars") 
        carros = self.cursor.fetchall()
        if not carros:
            return f"Você ainda não tem nenhum carro salvo."
        
        lista = "\n".join([carro[0] for carro in carros])
        return f"Seus carros salvos são: \n{lista}"
    

    def deletar_carro_db(self, model):
        # Deletar um carro do banco
        self.cursor.execute("DELETE FROM cars WHERE model = ?", (model,))
        self.conexao.commit()
        if self.cursor.rowcount > 0:
            return f"O carro '{model}' foi deletado da sua lista."
        else:
            return f"Não encontrei o carro '{model}' na sua lista."
    
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