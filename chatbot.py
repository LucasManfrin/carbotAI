from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCvEIte4FtXnx5sHMDwXBmDCaum4WkSdW4")


def enviar_msg(msg, lista_msgs=[]):
    lista_msgs.append(
        {"role": "user", "content": msg}
    )
    resposta = client.models.generate_content(
    model = "gemini-2.5-flash", 
    contents=texto,
    config=types.GenerateContentConfig(
        system_instruction="You are an assistant and enthusiast for cars in general, but with a great passion for sports cars, your role is to help discover the best car that the user is looking for, aiming at the user's objectives.")
    )

    lista_msgs.append(resposta)
    return resposta

lista_msgs = []
while True:
    texto = input("Escreva aqui sua mensagem: ")

    if texto == "Sair":
        break

    else:
        resposta = enviar_msg(texto, lista_msgs)
        print("AI: ", resposta.text)

