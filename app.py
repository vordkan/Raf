import datetime
import os.path
import json
import webbrowser
import time
import threading
import mysql.connector

from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
from datetime import datetime
import random

MAX_ATTEMPTS = 3
WAIT_TIME_SECONDS = 5

app = Flask(__name__,  static_folder='static')


# Funzione per ottenere la connessione al database
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="MattSenn.mysql.pythonanywhere-services.com",
            user="MattSenn",
            password="Prova.123",
            database="MattSenn$default",
        )
        print("Connessione al database avvenuta con successo!")
        return conn
    except Exception as e:
        print(f"Si è verificato un errore durante la connessione al database: {e}")
        return None

# Inizializzazione della connessione e del cursore
conn = create_connection()
if conn:
    cursor = conn.cursor()
else:
    # Gestisci il caso in cui non sia possibile ottenere una connessione al database
    print("Impossibile ottenere una connessione al database.")


# Pagina principale
@app.route('/')
def index():
    return render_template('index.html')

# Pagina delle prenotazioni
@app.route('/prenotazione')
def prenotazione():
    return render_template('prenotazione.html')

# Cliente
@app.route('/cliente')
def cliente():
    return render_template('cliente.html')

# Dipendente
@app.route('/dipendenti')
def gestione_dipendenti():
    return render_template('dipendente.html')

# Fatturato
@app.route('/fatturato')
def fatturato():
    return render_template('fatturato.html')

# Merce
@app.route('/merce')
def merce():
    return render_template('merci.html')

#---------------------------------------------------------------------------------------------------------------------#
@app.route('/submit', methods=['POST'])
def submit():
    try:
        summary = request.form['summary'].lower()
        description = request.form['description'].lower()
        start_datetime = datetime.strptime(request.form['start_datetime'], "%Y-%m-%dT%H:%M")
        end_datetime = datetime.strptime(request.form['end_datetime'], "%Y-%m-%dT%H:%M")
        dipendente = request.form['dipendente']

        # Connessione al database e ottenimento del cursore
        conn = create_connection()
        cursor = conn.cursor()

        # Loop fino a quando non si riesce a recuperare la sede del dipendente
        while True:
            try:
                cursor.execute('''SELECT sede FROM dipendente WHERE nome = %s''', (dipendente,))
                sede = cursor.fetchone()[0]
                break
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.CR_SERVER_GONE_ERROR:
                    # Se c'è un errore di disconnessione, riconnetti il client
                    conn = create_connection()
                    cursor = conn.cursor()
                else:
                    # Gestisci altri errori sollevando l'eccezione
                    raise

        prezzo = request.form['prezzo']

        # Inserimento dei dati nella tabella prenotazione
        cursor.execute('''INSERT INTO prenotazione (nome, descrizione, dipendente, sede, data_inizio, data_fine, prezzo) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                       (summary, description, dipendente, sede, start_datetime, end_datetime, prezzo))
        conn.commit()
        print("Prenotazione salvata nel database 'raffaele'")

        # Chiusura della connessione e del cursore
        cursor.close()
        conn.close()

        return jsonify({'success': True})  # Risposta JSON per indicare il successo
    except Exception as e:
        print(f"Si è verificato un errore durante il salvataggio della prenotazione nel database: {e}")
        return jsonify({'success': False, 'error': str(e)})


import json

def load_employee_colors():
    with open('employee_colors.json') as f:
        return json.load(f)

from flask import jsonify
from datetime import datetime

from flask import jsonify
from datetime import datetime


@app.route('/get_daily_schedule')
def get_daily_schedule(max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            daily_schedule = {}

            current_date = datetime.now().date()

            cursor.execute("SELECT id, HOUR(data_inizio), HOUR(data_fine), dipendente, nome, descrizione FROM prenotazione WHERE DATE(data_inizio) = %s AND sede = 'Frattamaggiore'", (current_date,))
            prenotazioni = cursor.fetchall()

            # Ottieni la lista dei dipendenti
            employees = leggi_dipendenti()

            # Leggi i colori per i dipendenti dal file JSON
            employee_colors = load_employee_colors()

            for prenotazione in prenotazioni:
                prenotazione_id = prenotazione[0]  # ID della prenotazione
                ora_inizio = prenotazione[1]
                ora_fine = prenotazione[2]
                dipendente = prenotazione[3]
                cliente = prenotazione[4]
                descrizione = prenotazione[5]

                for ora in range(ora_inizio, ora_fine + 1):
                    ora_str = str(ora).zfill(2)

                    if ora_str not in daily_schedule:
                        daily_schedule[ora_str] = {}

                    if dipendente not in daily_schedule[ora_str]:
                        daily_schedule[ora_str][dipendente] = []

                    daily_schedule[ora_str][dipendente].append({'id': prenotazione_id, 'cliente': cliente.lower(), 'descrizione': descrizione.lower()})

            html_table = '<table border="1"><tr><th>Ora</th>'
            for dipendente in employees:
                # Usa i colori caricati dal file JSON per i dipendenti
                employee_color = employee_colors.get(dipendente, '#FFFFFF')  # Default to white if color not found
                html_table += f'<th style="background-color: {employee_color}">{dipendente}</th>'
            html_table += '</tr>'

            for ora in range(7, 23):
                ora_str = str(ora).zfill(2)
                html_table += f'<tr><td>{ora_str}:00</td>'
                for dipendente in employees:
                    prenotazioni = daily_schedule.get(ora_str, {}).get(dipendente, [])
                    cell_content = ''
                    for prenotazione in prenotazioni:
                        prenotazione_id = prenotazione['id']
                        cliente = prenotazione['cliente']
                        descrizione = prenotazione['descrizione']
                        # Usa i colori caricati dal file JSON per le celle delle prenotazioni
                        employee_color = employee_colors.get(dipendente, '#FFFFFF')  # Default to white if color not found
                        cell_content += f'<div style="background-color: {employee_color};">'
                        cell_content += f'{cliente}<br><span style="font-size: 12px;">{descrizione}</span><br>'
                        cell_content += f'<span style="cursor: pointer;" onclick="eliminaPrenotazione({prenotazione_id}, \'{cliente}\', \'{descrizione}\')"> 🗑 </span>'
                        cell_content += f'<span style="cursor: pointer;" onclick="modificaPrenotazione({prenotazione_id})"> 📝 </span>'
                        cell_content += f'<span style="cursor: pointer;" onclick="modificaPrenotazione_ora({prenotazione_id})"> 🕒 </span><br>'
                        cell_content += '</div>'

                    html_table += f'<td>{cell_content}</td>'
                html_table += '</tr>'

            return html_table
        except Exception as e:
            # Gestisci l'errore di disconnessione riconnettendoti al server MySQL e riprova l'operazione
            print(f"Si è verificato un errore durante l'accesso al database: {e}")
            attempts += 1
            if attempts >= max_attempts:
                return jsonify({'success': False, 'error': str(e)})
            else:
                # Riconnessione al database
                conn = create_connection()
                cursor = conn.cursor()

@app.route('/get_daily_schedule_aversa')
def get_daily_schedule_aversa(max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            daily_schedule = {}

            current_date = datetime.now().date()

            cursor.execute("SELECT id, HOUR(data_inizio), HOUR(data_fine), dipendente, nome, descrizione FROM prenotazione WHERE DATE(data_inizio) = %s AND sede = 'Aversa'", (current_date,))
            prenotazioni = cursor.fetchall()

            # Ottieni la lista dei dipendenti
            employees = leggi_dipendenti_aversa()

            # Leggi i colori per i dipendenti dal file JSON
            employee_colors = load_employee_colors()

            for prenotazione in prenotazioni:
                prenotazione_id = prenotazione[0]  # ID della prenotazione
                ora_inizio = prenotazione[1]
                ora_fine = prenotazione[2]
                dipendente = prenotazione[3]
                cliente = prenotazione[4]
                descrizione = prenotazione[5]

                for ora in range(ora_inizio, ora_fine + 1):
                    ora_str = str(ora).zfill(2)

                    if ora_str not in daily_schedule:
                        daily_schedule[ora_str] = {}

                    if dipendente not in daily_schedule[ora_str]:
                        daily_schedule[ora_str][dipendente] = []

                    daily_schedule[ora_str][dipendente].append({'id': prenotazione_id, 'cliente': cliente.lower(), 'descrizione': descrizione.lower()})

            html_table = '<table border="1"><tr><th>Ora</th>'
            for dipendente in employees:
                # Usa i colori caricati dal file JSON per i dipendenti
                employee_color = employee_colors.get(dipendente, '#FFFFFF')  # Default to white if color not found
                html_table += f'<th style="background-color: {employee_color}">{dipendente}</th>'
            html_table += '</tr>'

            for ora in range(7, 23):
                ora_str = str(ora).zfill(2)
                html_table += f'<tr><td>{ora_str}:00</td>'
                for dipendente in employees:
                    prenotazioni = daily_schedule.get(ora_str, {}).get(dipendente, [])
                    cell_content = ''
                    for prenotazione in prenotazioni:
                        prenotazione_id = prenotazione['id']
                        cliente = prenotazione['cliente']
                        descrizione = prenotazione['descrizione']
                        # Usa i colori caricati dal file JSON per le celle delle prenotazioni
                        employee_color = employee_colors.get(dipendente, '#FFFFFF')  # Default to white if color not found
                        cell_content += f'<div style="background-color: {employee_color};">'
                        cell_content += f'{cliente}<br><span style="font-size: 12px;">{descrizione}</span><br>'
                        cell_content += f'<span style="cursor: pointer;" onclick="eliminaPrenotazione({prenotazione_id}, \'{cliente}\', \'{descrizione}\')"> 🗑 </span>'
                        cell_content += f'<span style="cursor: pointer;" onclick="modificaPrenotazione({prenotazione_id})"> 📝 </span>'
                        cell_content += f'<span style="cursor: pointer;" onclick="modificaPrenotazione_ora({prenotazione_id})"> 🕒 </span><br>'
                        cell_content += '</div>'

                    html_table += f'<td>{cell_content}</td>'
                html_table += '</tr>'

            return html_table
        except Exception as e:
            # Gestisci l'errore di disconnessione riconnettendoti al server MySQL e riprova l'operazione
            print(f"Si è verificato un errore durante l'accesso al database: {e}")
            attempts += 1
            if attempts >= max_attempts:
                return jsonify({'success': False, 'error': str(e)})
            else:
                # Riconnessione al database
                conn = create_connection()  # Sostituisci con la funzione appropriata per ottenere una nuova connessione al database
                cursor = conn.cursor()


@app.route('/get_weekly_schedule', methods=['POST'])
def get_weekly_schedule():
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            daily_schedule = {}

            # Ottenere la data e la sede dal parametro della richiesta
            request_data = request.json
            current_date_str = request_data.get('data')
            current_sede = request_data.get('sede')

            if current_date_str is None or current_sede is None:
                return "Seleziona una data e una sede"

            try:
                current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
            except ValueError:
                return "Seleziona una data e una sede"

            if current_sede.lower() == 'aversa':
                cursor.execute("SELECT id, HOUR(data_inizio), HOUR(data_fine), dipendente, nome, descrizione FROM prenotazione WHERE DATE(data_inizio) = %s AND sede = 'Aversa'", (current_date,))
            else:
                cursor.execute("SELECT id, HOUR(data_inizio), HOUR(data_fine), dipendente, nome, descrizione FROM prenotazione WHERE DATE(data_inizio) = %s AND sede = 'Frattamaggiore'", (current_date,))

            prenotazioni = cursor.fetchall()

            for prenotazione in prenotazioni:
                prenotazione_id = prenotazione[0]
                ora_inizio = prenotazione[1]
                ora_fine = prenotazione[2]
                dipendente = prenotazione[3]
                cliente = prenotazione[4]
                descrizione = prenotazione[5]

                for ora in range(ora_inizio, ora_fine + 1):
                    ora_str = str(ora).zfill(2)

                    if ora_str not in daily_schedule:
                        daily_schedule[ora_str] = {}

                    if dipendente not in daily_schedule[ora_str]:
                        daily_schedule[ora_str][dipendente] = []

                    daily_schedule[ora_str][dipendente].append({'id': prenotazione_id, 'cliente': cliente.lower(), 'descrizione': descrizione.lower()})

            html_table = '<table border="1"><tr><th>Ora</th>'
            if current_sede.lower() == 'aversa':
                for dipendente in leggi_dipendenti_aversa():
                    html_table += f'<th>{dipendente}</th>'
            else:
                for dipendente in leggi_dipendenti():
                    html_table += f'<th>{dipendente}</th>'
            html_table += '</tr>'

            for ora in range(7, 23):
                ora_str = str(ora).zfill(2)
                html_table += f'<tr><td>{ora_str}:00</td>'
                if current_sede.lower() == 'aversa':
                    for dipendente in leggi_dipendenti_aversa():
                        prenotazioni = daily_schedule.get(ora_str, {}).get(dipendente, [])
                        cell_content = ''
                        for prenotazione in prenotazioni:
                            prenotazione_id = prenotazione['id']
                            cliente = prenotazione['cliente']
                            descrizione = prenotazione['descrizione']
                            cell_content += f'{cliente}<br><span style="font-size: 12px;">{descrizione}</span><br>'
                        html_table += f'<td>{cell_content}</td>'
                else:
                    for dipendente in leggi_dipendenti():
                        prenotazioni = daily_schedule.get(ora_str, {}).get(dipendente, [])
                        cell_content = ''
                        for prenotazione in prenotazioni:
                            prenotazione_id = prenotazione['id']
                            cliente = prenotazione['cliente']
                            descrizione = prenotazione['descrizione']
                            cell_content += f'{cliente}<br><span style="font-size: 12px;">{descrizione}</span><br>'
                        html_table += f'<td>{cell_content}</td>'
            return html_table
        except Exception as e:
            # Gestisci l'errore di disconnessione riconnettendoti al server MySQL e riprova l'operazione
            print(f"Si è verificato un errore durante l'accesso al database: {e}")
            attempts += 1
            if attempts >= max_attempts:
                return jsonify({'success': False, 'error': str(e)})
            else:
                # Riconnessione al database
                conn = create_connection()  # Sostituisci con la funzione appropriata per ottenere una nuova connessione al database
                cursor = conn.cursor()

#---------------------------------------------------------------------------------------------------------------------#

@app.route('/modifica_prenotazione', methods=['POST'])
def modifica_prenotazione():
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            data = request.json
            prenotazione_id = data['prenotazione_id']
            nuova_descrizione = data.get('nuova_descrizione')
            nuovo_prezzo = data.get('nuovo_prezzo')

            # Verifica se ci sono sia una nuova descrizione che un nuovo prezzo
            if nuova_descrizione is not None and nuovo_prezzo is not None:
                # Converti il nuovo prezzo in un numero decimale prima di passarlo al database
                nuovo_prezzo_decimal = float(nuovo_prezzo)
                cursor.execute("UPDATE prenotazione SET descrizione = %s, prezzo = %s WHERE id = %s", (nuova_descrizione, nuovo_prezzo_decimal, prenotazione_id))
            elif nuova_descrizione is not None:
                cursor.execute("UPDATE prenotazione SET descrizione = %s WHERE id = %s", (nuova_descrizione, prenotazione_id))
            elif nuovo_prezzo is not None:
                # Converti il nuovo prezzo in un numero decimale prima di passarlo al database
                nuovo_prezzo_decimal = float(nuovo_prezzo)
                cursor.execute("UPDATE prenotazione SET prezzo = %s WHERE id = %s", (nuovo_prezzo_decimal, prenotazione_id))
            else:
                return jsonify({'error': 'Devi fornire una nuova descrizione o un nuovo prezzo per modificare la prenotazione.'}), 400

            conn.commit()
            print("Prenotazione modificata nel database 'raffaele'")
            return jsonify({'message': 'Prenotazione modificata con successo nel database'}), 200
        except Exception as e:
            # Gestisci l'errore di disconnessione riconnettendoti al server MySQL e riprova l'operazione
            print(f"Si è verificato un errore durante la modifica della prenotazione nel database: {e}")
            attempts += 1
            if attempts >= max_attempts:
                return jsonify({'error': 'Si è verificato un errore durante la modifica della prenotazione nel database.'}), 500
            else:
                # Riconnessione al database
                conn = create_connection()  # Sostituisci con la funzione appropriata per ottenere una nuova connessione al database
                cursor = conn.cursor()


@app.route('/modifica_prenotazione_ora', methods=['POST'])
def modifica_prenotazione_ora():
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            conn = create_connection()
            cursor = conn.cursor()

            data = request.json
            prenotazione_id = data.get('prenotazione_id')
            nuova_data_inizio = data.get('nuova_data_inizio')
            nuova_data_fine = data.get('nuova_data_fine')

            if prenotazione_id is None or nuova_data_inizio is None or nuova_data_fine is None:
                return jsonify({'error': 'Devi fornire prenotazione_id, nuova_data_inizio e nuova_data_fine.'}), 400

            cursor.execute("UPDATE prenotazione SET data_inizio = %s, data_fine = %s WHERE id = %s", (nuova_data_inizio, nuova_data_fine, prenotazione_id))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({'message': 'Prenotazione modificata con successo nel database'}), 200
        except Exception as e:
            print(f"Si è verificato un errore durante la modifica della prenotazione nel database: {e}")
            return jsonify({'error': 'Si è verificato un errore durante la modifica della prenotazione nel database.'}), 500
            print(f"Si è verificato un errore durante la modifica della prenotazione nel database: {e}")
            attempts += 1
            if attempts >= max_attempts:
                return jsonify({'error': 'Si è verificato un errore durante la modifica della prenotazione nel database.'}), 500
            else:
                # Riconnessione al database
                conn = create_connection()  # Sostituisci con la funzione appropriata per ottenere una nuova connessione al database
                cursor = conn.cursor()


@app.route('/elimina_prenotazione', methods=['POST'])
def elimina_prenotazione():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    conn = None
    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                data = request.json
                prenotazione_id = data['id']

                cursor.execute("DELETE FROM prenotazione WHERE id = %s", (prenotazione_id,))
                conn.commit()
                print("Prenotazione eliminata con successo!")
                return jsonify({'message': 'Prenotazione eliminata con successo!'}), 200
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({'error': 'Impossibile stabilire la connessione al database.'}), 500



@app.route('/visualizza_prenotazioni')
def visualizza_prenotazioni():
    return render_template('visualizza_prenotazioni.html')
#---------------------------------------------------------------------------------------------------------------------#
def leggi_dipendenti_aversa():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT nome FROM dipendente WHERE sede = 'Aversa' ''')
                nomi_dipendenti = cursor.fetchall()
                return sorted([nome[0] for nome in nomi_dipendenti])
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return []


def leggi_dipendenti():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT nome FROM dipendente WHERE sede = 'Frattamaggiore' ''')
                nomi_dipendenti = cursor.fetchall()
                return sorted([nome[0] for nome in nomi_dipendenti])
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return []


def leggi_dipendenti_fratta():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT nome FROM dipendente WHERE sede = 'Frattamaggiore' ''')
                nomi_dipendenti = cursor.fetchall()
                return sorted([nome[0] for nome in nomi_dipendenti])
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return []


def leggi_dipendenti_tot():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT nome FROM dipendente''')
                nomi_dipendenti = cursor.fetchall()
                return sorted([nome[0] for nome in nomi_dipendenti])
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return []



@app.route('/get_dipendenti')
def get_dipendenti():
    return jsonify(leggi_dipendenti_tot())

import re

def add_employee_to_json(nome, colore_esadecimale):
    try:
        with open('employee_colors.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Se il file non esiste, crealo con un dizionario vuoto
        data = {}

    try:
        # Verifica se il colore esadecimale è nel formato corretto (#RRGGBB)
        if not re.match(r'^#[0-9a-fA-F]{6}$', colore_esadecimale):
            raise ValueError("Il colore esadecimale deve essere nel formato '#RRGGBB'")

        # Aggiungi il colore al dizionario
        data[nome] = colore_esadecimale

        # Scrivi il dizionario aggiornato nel file JSON
        with open('employee_colors.json', 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Si è verificato un errore durante l'aggiunta del dipendente al file JSON: {e}")

def generate_pastel_color():
    # Genera un colore pastello casuale
    r = int(random.uniform(0, 256))
    g = int(random.uniform(0, 256))
    b = int(random.uniform(0, 256))
    # Mischiare i colori per renderli pastello
    r = (r + 255) // 2
    g = (g + 255) // 2
    b = (b + 255) // 2
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

@app.route('/aggiungi_dipendente', methods=['POST'])
def aggiungi_dipendente():
    nome = request.form['nome']
    sede = request.form['sede']

    # Genera un colore pastello casuale
    colore_pastello = generate_pastel_color()

    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO dipendente (nome, sede) VALUES (%s, %s)", (nome, sede))
                conn.commit()
                print("Dipendente aggiunto con successo!")

                # Aggiungi il dipendente al file JSON con un colore pastello casuale
                add_employee_to_json(nome, colore_pastello)

                return redirect(url_for('index'))
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return "Si è verificato un errore durante l'aggiunta del dipendente."


def remove_employee_from_json(nome):
    try:
        with open('employee_colors.json', 'r') as f:
            data = json.load(f)
            if nome in data:
                del data[nome]  # Rimuovi il dipendente dal dizionario JSON
                with open('employee_colors.json', 'w') as f:
                    json.dump(data, f, indent=4)  # Scrivi il dizionario aggiornato nel file JSON
    except Exception as e:
        print(f"Si è verificato un errore durante la rimozione del dipendente dal file JSON: {e}")

@app.route('/elimina_dipendente', methods=['POST'])
def elimina_dipendente():
    dipendente = request.form['dipendente']

    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dipendente WHERE nome = %s", (dipendente,))
                conn.commit()
                print("Dipendente eliminato con successo!")

                # Rimuovi il dipendente anche dal file JSON
                remove_employee_from_json(dipendente)

                return redirect(url_for('index'))
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return "Si è verificato un errore durante l'eliminazione del dipendente."

#---------------------------------------------------------------------------------------------------------------------#

@app.route('/storico_prenotazioni', methods=['POST'])
def storico_prenotazioni():
    cliente = request.form['cliente'].lower()

    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT dipendente, nome, descrizione, data_inizio, prezzo, sede, id FROM prenotazione WHERE nome = %s ORDER BY data_inizio DESC", (cliente,))
                storico_prenotazioni = cursor.fetchall()
                return render_template('cliente.html', storico_prenotazioni=storico_prenotazioni, cliente=cliente)
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return "Si è verificato un errore durante il recupero dello storico delle prenotazioni."
#---------------------------------------------------------------------------------------------------------------------#
@app.route('/get_schedule')
def get_schedule():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                period = request.args.get('period')  # period può essere 'daily', 'monthly', 'annual'
                print(f"Periodo richiesto: {period}")
                schedule = {}
                current_date = datetime.now().date()

                cursor.execute("SELECT DISTINCT dipendente FROM prenotazione")
                dipendenti = cursor.fetchall()
                print("Dipendenti:", dipendenti)

                for dipendente in dipendenti:
                    dipendente_id = dipendente[0]
                    if period == 'giornaliero':
                        cursor.execute("SELECT SUM(prezzo) FROM prenotazione WHERE DATE(data_inizio) = %s AND dipendente = %s", (current_date, dipendente_id))
                    elif period == 'mensile':
                        cursor.execute("SELECT SUM(prezzo) FROM prenotazione WHERE YEAR(data_inizio) = YEAR(CURDATE()) AND MONTH(data_inizio) = MONTH(CURDATE()) AND dipendente = %s", (dipendente_id,))
                    elif period == 'annuale':
                        selected_year = request.args.get('anno')  # Ottieni l'anno selezionato dall'utente
                        if not selected_year:  # Se il parametro anno è vuoto, usa l'anno attuale
                            selected_year = datetime.now().year
                        cursor.execute("SELECT SUM(prezzo) FROM prenotazione WHERE YEAR(data_inizio) = %s AND dipendente = %s", (selected_year, dipendente_id))

                    fatturato = cursor.fetchone()[0]
                    print(f"Fatturato per dipendente {dipendente_id}: {fatturato}")
                    if fatturato is not None:
                        schedule[dipendente_id] = {'fatturato': float(fatturato)}
                    else:
                        schedule[dipendente_id] = {'fatturato': 0}

                print("Programma di fatturazione:", schedule)
                return jsonify(schedule)
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({'error': 'Impossibile stabilire la connessione al database.'}), 500


#---------------------------------------------------------------------------------------------------------------------#
@app.route('/carica_merce', methods=['POST'])
def carica_merce():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()

                id_merce = request.form['id_merce']
                nome_merce = request.form['nome_merce']
                descrizione_merce = request.form['descrizione_merce']
                quantita_merce = int(request.form['quantita_merce'])
                prezzo_merce = float(request.form['prezzo_merce'])
                data_carico = datetime.utcnow()

                cursor.execute("INSERT INTO merci (ID, nome, descrizione, quantita, prezzo, data_carico) VALUES (%s, %s, %s, %s, %s, %s)",
                               (id_merce, nome_merce, descrizione_merce, quantita_merce, prezzo_merce, data_carico))
                conn.commit()

                # Restituisci un messaggio di successo senza visualizzare una schermata
                return jsonify({"success": True, "message": "Carico avvenuto con successo!"}), 200
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({"error": "Impossibile stabilire la connessione al database."}), 500



@app.route('/scarica_merce', methods=['POST'])
def scarica_merce():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()

                id_merce = request.form['id_merceS']
                quantita_scarico = int(request.form['quantita_scarico'])

                # Verifica se la merce esiste
                cursor.execute("SELECT quantita FROM merci WHERE ID = %s", (id_merce,))
                result = cursor.fetchone()

                if result:
                    quantita_attuale = result[0]
                    if quantita_scarico <= quantita_attuale:
                        # Aggiorna la quantità di merce nel database
                        nuova_quantita = quantita_attuale - quantita_scarico
                        cursor.execute("UPDATE merci SET quantita = %s WHERE ID = %s", (nuova_quantita, id_merce))
                        conn.commit()
                        # Restituisci un messaggio di successo senza visualizzare una schermata
                        return jsonify({"success": True, "message": "Scarico avvenuto con successo!"}), 200
                    else:
                        return jsonify({"error": "Quantità da scaricare superiore alla quantità attuale."}), 400
                else:
                    return jsonify({"error": "Merce non trovata."}), 404
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({"error": "Impossibile stabilire la connessione al database."}), 500


@app.route('/visualizza_merce', methods=['GET'])
def visualizza_merce():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()

                cursor.execute("SELECT ID, nome, descrizione, quantita, prezzo, data_carico FROM merci")
                merci = cursor.fetchall()
                if merci:
                    return jsonify(merci)
                else:
                    return jsonify([])
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({"error": "Impossibile stabilire la connessione al database."}), 500


@app.route('/elimina_merce', methods=['POST'])
def elimina_merce():
    attempts = 0
    max_attempts = 3
    wait_time_seconds = 5

    while attempts < max_attempts:
        try:
            conn = create_connection()
            if conn:
                cursor = conn.cursor()

                id_merce = request.json['id_merce']
                cursor.execute("DELETE FROM merci WHERE ID = %s", (id_merce,))
                conn.commit()
                return jsonify({'success': True, 'message': 'Merce eliminata con successo!'})
        except Exception as e:
            print(f"Tentativo di connessione fallito. Riprovo tra {wait_time_seconds} secondi...")
            print(f"Errore: {e}")
            time.sleep(wait_time_seconds)
            attempts += 1
        finally:
            if conn:
                conn.close()

    print(f"Numero massimo di tentativi raggiunto ({max_attempts}). Impossibile stabilire la connessione al database.")
    return jsonify({'success': False, 'error': "Impossibile stabilire la connessione al database."})
#---------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)
