# Baby Name Voting App

A simple Flask application that allows users to vote between two baby names in an A/B testing style interface.

## Features

- Clean, modern UI using Tailwind CSS
- Real-time vote counting and statistics
- SQLite database for vote storage
- Responsive design that works on both desktop and mobile

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## How to Use

1. The application will display two names side by side
2. Click on your preferred name to cast your vote
3. The results will update automatically, showing:
   - Total number of votes
   - Number of votes for each name
   - Percentage distribution
   - Visual progress bar

## Customization

To change the names being voted on, modify the `current_names` dictionary in `app.py`. In a production environment, you might want to:

- Add more names to vote on
- Randomize the name pairs
- Add user authentication
- Implement rate limiting
- Add more detailed statistics 