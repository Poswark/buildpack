# Expense Tracker - Setup Instructions

This is a web-based expense tracking application built with Flask and MongoDB. It provides a simple and beautiful interface for tracking expenses across different categories.

## Project Structure

```
expense-tracker/
├── app.py                # Flask application
├── templates/            # HTML templates
│   └── index.html        # Main page template
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. Create the project directory:
   ```bash
   mkdir -p expense-tracker/templates
   cd expense-tracker
   ```

2. Create the files:
   - Save `app.py` in the root directory
   - Save `index.html` in the `templates` directory
   - Save `Dockerfile`, `docker-compose.yml`, and `requirements.txt` in the root directory

3. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access the application at http://localhost:5000

### Option 2: Running Without Docker

1. Install MongoDB and start the MongoDB service

2. Create the project directory:
   ```bash
   mkdir -p expense-tracker/templates
   cd expense-tracker
   ```

3. Create the files:
   - Save `app.py` as `app.py` in the root directory
   - Save `index.html` in the `templates` directory
   - Save `requirements.txt` in the root directory

4. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the Flask application:
   ```bash
   python app.py
   ```

7. Access the application at http://localhost:5000

## Usage

1. The main screen shows a donut chart of your expenses by category
2. Use the month navigation buttons (← and →) to move between months
3. Add new expenses using the form at the bottom of the page

## Features

- Clean, modern dark-themed UI
- Interactive expense visualization
- Monthly expense breakdown by category
- Simple expense entry form
- Responsive design that works on desktop and mobile


Deudas 
   ```bash
curl --location 'http://localhost:5050/save_report' \
--header 'Content-Type: application/json' \
--data '{
    "report_id": "67f7531a4cb62de8511bb87a",
    "business1": {
        "owe": 1500,
        "owed": 1400,
        "balance": 700,
        "deuda": 700,
        "chart_data": [
            300,
            450,
            600,
            550,
            650,
            700
        ]
    },
    "business2": {
        "owe": 800,
        "owed": 1500,
        "balance": 700,
        "chart_data": [
            200,
            300,
            400,
            550,
            650,
            700
        ]
    }
}'
   ```