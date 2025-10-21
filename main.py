import telebot
import mysql.connector
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import ReplyKeyboardRemove

bot = telebot.TeleBot("8093485363:AAGyGfTTgksSvKp-vywNKze4Lb2z2SKy2MM")

# Estado para recordar la conversación con cada usuario
usuarios_esperando_respuesta = {}

def conectar_BD():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "bottelegram"
    )
    return db

def obtenerDatos():
      conexion = conectar_BD()
      cursor = conexion.cursor(dictionary=True)
      cursor.execute("SELECT * FROM canciones LIMIT 5")
      datos=cursor.fetchall()
      cursor.close()
      conexion.close()
      return datos

def hacerConsulta(consulta):
    conexion = conectar_BD()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(consulta)
    datos=cursor.fetchall()
    cursor.close()
    conexion.close()
    return datos

def mostrarGeneros():
    datos=hacerConsulta("SELECT DISTINCT Genero FROM canciones")
    respuesta=""
    if datos:
        for dato in datos:
            respuesta += f"{dato['Genero']}\n"
    else:
        respuesta = "No hay ningun genero disponible"
    
    return respuesta

def buscarCanciones(genero):
    genero=genero.capitalize()    
    canciones=hacerConsulta("SELECT * FROM canciones WHERE Genero='"+genero+"'")
    respuesta=""
    if canciones:
        respuesta="Nuestras recomendaciones de "+genero+" son: \n"
        for cancion in canciones:
            respuesta += f"{cancion['Nombre']} \t\t de \t\t {cancion['Artista']}\n"
    else:
        respuesta="No hay canciones de ese genero."
    
    return respuesta

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Como estas?")
	
@bot.message_handler(commands=['consulta'])
def handle_request(message):
	
    datos=obtenerDatos()
    if datos:
        respuesta = ""
        for dato in datos:
            respuesta += f"Nombre: {dato['Nombre']}\n"
    else:
        respuesta = "No hay registro"
    
    bot.reply_to(message, respuesta)

# Comando para iniciar la recomendación
@bot.message_handler(commands=['recomendacion'])
def recomendar_genero(message):
    respuesta=mostrarGeneros()
    chat_id = message.chat.id
    usuarios_esperando_respuesta[chat_id] = True  

    bot.send_message(chat_id, "Elige un género musical:\n"+respuesta)

# Capturar respuesta del usuario
@bot.message_handler(func=lambda message: message.chat.id in usuarios_esperando_respuesta)
def responder_recomendacion(message):
    chat_id = message.chat.id
    genero = message.text
    respuesta=buscarCanciones(genero)

    bot.send_message(chat_id, respuesta, parse_mode="Markdown")

    #if genero in canciones_por_genero:
    #    respuesta = canciones_por_genero[genero]
    #    bot.send_message(chat_id, respuesta, parse_mode="Markdown")
    #else:
    #    bot.send_message(chat_id, "❌ No reconocí ese género. Intenta de nuevo usando /recomendacion.")

    # Eliminar al usuario de la lista de espera
    usuarios_esperando_respuesta.pop(chat_id, None)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "Ingrese el comando /recomendacion.")

bot.infinity_polling()