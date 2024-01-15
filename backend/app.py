from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, ConferenceRoom, Vote
from difflib import SequenceMatcher
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
from datetime import datetime, timedelta
import threading
import pytz
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "conference_rooms.db")}'
CORS(app, origins=["http://192.168.50.45:3000"])
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/api/conference_rooms', methods=['GET'])
def get_conference_rooms():
    conference_rooms = ConferenceRoom.query.all()
    return jsonify([room.serialize for room in conference_rooms])

@app.route('/api/conference_rooms', methods=['POST'])
def add_conference_room():
    room_name = request.json['name']
    description = request.json['description']

    # Check for similar conference room names (70% accuracy)
    existing_rooms = ConferenceRoom.query.all()
    for room in existing_rooms:
        if similar(room.name, room_name) > 0.7:
            return jsonify({'message': 'A similar conference room name already exists.'}), 400

    new_room = ConferenceRoom(name=room_name, description=description)
    db.session.add(new_room)
    db.session.commit()

    return jsonify(new_room.serialize), 201

@app.route('/api/vote', methods=['POST'])
def vote():
    room_id = request.json['room_id']
    user_ip = request.remote_addr

    # Check if user has voted more than 3 times
    user_votes = Vote.query.filter_by(ip=user_ip).count()
    if user_votes >= 5:
        return jsonify({'message': 'You have reached the maximum number of votes.'}), 400

    # Increment the vote count and store the user's IP
    room = ConferenceRoom.query.get(room_id)
    if not room:
        return jsonify({'message': 'Invalid conference room.'}), 404

    room.votes += 1
    new_vote = Vote(ip=user_ip, room_id=room_id)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote submitted successfully.'}), 200

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def send_email(subject, body, to_email, from_email, from_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

# def get_local_ip():
#     hostname = socket.gethostname()
#     local_ip = socket.gethostbyname(hostname)
#     return local_ip

def get_local_ip():
    try:
        # Connect to a public-facing server to get the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"Error getting local IP address: {e}")
        return "0.0.0.0"

def send_ip_daily(to_email, from_email, from_password):
    finnish_tz = pytz.timezone('Europe/Helsinki')
    now = datetime.now(finnish_tz)
    target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)

    wait_time = (target_time - now).total_seconds()
    threading.Timer(wait_time, send_ip_daily, args=(to_email, from_email, from_password)).start()

    local_ip = get_local_ip()
    subject = "Daily IP address"
    body = f"Local IP address: {local_ip}"
    send_email(subject, body, to_email, from_email, from_password)

if __name__ == '__main__':
    to_email = os.environ['TO_EMAIL']
    from_email = os.environ['FROM_EMAIL']
    from_password = os.environ['APP_PASSWORD']

    # Send the IP address for the first time
    local_ip = get_local_ip()
    subject = "Flask app started - IP address"
    body = f"Local IP address: {local_ip}"
    send_email(subject, body, to_email, from_email, from_password)

    # Schedule the daily IP address email at 06:00 Finnish local time
    send_ip_daily(to_email, from_email, from_password)
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
