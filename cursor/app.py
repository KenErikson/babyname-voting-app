from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
from collections import defaultdict
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_a = db.Column(db.String(100), nullable=False)
    name_b = db.Column(db.String(100), nullable=False)
    winner = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=False)  # 'boy' or 'girl'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

def load_names():
    boy_names = set()
    girl_names = set()
    current_category = None
    
    with open('names.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                if 'Boy' in line:
                    current_category = 'boy'
                elif 'Girl' in line:
                    current_category = 'girl'
                continue
            
            if current_category == 'boy':
                boy_names.add(line)
            elif current_category == 'girl':
                girl_names.add(line)
    
    return {
        'boy': boy_names,
        'girl': girl_names,
        'both': boy_names.intersection(girl_names)
    }

def get_random_name_pair(gender):
    names = load_names()
    available_names = list(names[gender])
    
    if len(available_names) < 2:
        return None, None
    
    name_a = random.choice(available_names)
    name_b = random.choice([n for n in available_names if n != name_a])
    return name_a, name_b

def get_name_stats(gender):
    votes = Vote.query.filter_by(gender=gender).all()
    name_votes = defaultdict(int)
    
    for vote in votes:
        if vote.winner:  # Skip null winners (skipped votes)
            name_votes[vote.winner] += 1
    
    # Convert to list of tuples (name, votes) and sort by votes
    stats = [(name, votes) for name, votes in name_votes.items()]
    return sorted(stats, key=lambda x: x[1], reverse=True)

def merge_votes(partner_votes_json, gender):
    try:
        partner_votes = json.loads(partner_votes_json)
        if not isinstance(partner_votes, dict):
            return False, "Invalid vote format"
        
        names = load_names()
        for name, votes in partner_votes.items():
            if name not in names[gender]:
                continue
            # Add partner's votes to existing votes
            for _ in range(votes):
                vote = Vote(
                    name_a=name,  # These are dummy values since we only care about the winner
                    name_b="dummy",
                    winner=name,
                    gender=gender
                )
                db.session.add(vote)
        
        db.session.commit()
        return True, "Votes merged successfully"
    except json.JSONDecodeError:
        return False, "Invalid JSON format"
    except Exception as e:
        return False, f"Error merging votes: {str(e)}"

def export_votes(gender):
    votes = Vote.query.filter_by(gender=gender).all()
    name_votes = defaultdict(int)
    
    for vote in votes:
        if vote.winner:
            name_votes[vote.winner] += 1
    
    return json.dumps(dict(name_votes))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    gender = request.args.get('gender', 'boy')  # Default to boy names
    if gender not in ['boy', 'girl']:
        gender = 'boy'
        
    name_a, name_b = get_random_name_pair(gender)
    if not name_a or not name_b:
        return render_template('index.html', 
                             names={'name_a': 'No names', 'name_b': 'No names'},
                             total_votes=0,
                             name_a_votes=0,
                             name_b_votes=0,
                             toplist=[],
                             current_gender=gender,
                             vote_data=export_votes(gender))
    
    # Get vote statistics
    total_votes = Vote.query.filter_by(gender=gender).filter(Vote.winner.isnot(None)).count()
    name_a_votes = Vote.query.filter_by(gender=gender, winner=name_a).count()
    name_b_votes = Vote.query.filter_by(gender=gender, winner=name_b).count()
    
    # Get toplist
    toplist = get_name_stats(gender)
    
    return render_template('index.html', 
                         names={'name_a': name_a, 'name_b': name_b},
                         total_votes=total_votes,
                         name_a_votes=name_a_votes,
                         name_b_votes=name_b_votes,
                         toplist=toplist,
                         current_gender=gender,
                         vote_data=export_votes(gender))

@app.route('/vote', methods=['POST'])
def vote():
    winner = request.form.get('winner')
    name_a = request.form.get('name_a')
    name_b = request.form.get('name_b')
    gender = request.form.get('gender', 'boy')
    
    if not name_a or not name_b:
        return redirect(url_for('index', gender=gender))
    
    vote = Vote(
        name_a=name_a,
        name_b=name_b,
        winner=winner,
        gender=gender
    )
    
    db.session.add(vote)
    db.session.commit()
    
    return redirect(url_for('index', gender=gender))

@app.route('/merge', methods=['POST'])
def merge():
    partner_votes = request.form.get('partner_votes')
    gender = request.form.get('gender', 'boy')
    
    success, message = merge_votes(partner_votes, gender)
    if not success:
        flash(message)
    
    return redirect(url_for('index', gender=gender))

if __name__ == '__main__':
    app.run(debug=True) 