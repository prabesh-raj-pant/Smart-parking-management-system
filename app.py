from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'prabesh',
    'password': 'PASSWORD',
    'database': 'parking_management',
}

# Function to establish a connection to the database
def get_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    try:
        # Display user panel
        with get_connection() as conn, conn.cursor() as cursor:
            # Fetch available_spaces
            cursor.execute("SELECT available_spaces FROM parking_space")
            result = cursor.fetchall()
            available_spaces = result[0][0] if result else 0

            # Fetch parked_vehicles
            cursor.execute("SELECT COUNT(*) FROM entry_exit_log WHERE exit_time IS NULL")
            result = cursor.fetchall()
            parked_vehicles = result[0][0] if result else 0

        return render_template('user_panel.html', available_spaces=available_spaces, parked_vehicles=parked_vehicles)

    except Exception as e:
        # Log the exception details
        print(f"Error in index route: {str(e)}")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    search_query = request.args.get('search', '')
    
    if request.method == 'POST':
        # Process vehicle entry
        vehicle_plate = request.form['vehicle_plate']
        entry_time = datetime.now()

        with get_connection() as conn, conn.cursor() as cursor:
            cursor.execute("INSERT INTO entry_exit_log (vehicle_plate, entry_time) VALUES (%s, %s)", (vehicle_plate, entry_time))
            conn.commit()

            # Update available_spaces
            cursor.execute("UPDATE parking_space SET available_spaces = available_spaces - 1")
            conn.commit()

    # Fetch and display entry_exit_logs based on the search query
    with get_connection() as conn, conn.cursor() as cursor:
        if search_query:
            cursor.execute("SELECT * FROM entry_exit_log WHERE vehicle_plate LIKE %s ORDER BY entry_time", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT * FROM entry_exit_log ORDER BY entry_time")

        entry_exit_logs = cursor.fetchall()

    return render_template('admin_panel.html', entry_exit_logs=entry_exit_logs)



@app.route('/entry', methods=['POST'])
def entry():
    # Process vehicle entry
    vehicle_plate = request.form['vehicle_plate']
    entry_time = datetime.now()

    # Check if the vehicle with the same plate has an open exit entry
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id FROM entry_exit_log WHERE vehicle_plate = %s AND exit_time IS NULL", (vehicle_plate,))
        existing_entry = cursor.fetchone()

        if existing_entry:
            return "This vehicle has not exited yet and cannot re-enter."

        cursor.execute("INSERT INTO entry_exit_log (vehicle_plate, entry_time) VALUES (%s, %s)", (vehicle_plate, entry_time))
        conn.commit()

        # Update available_spaces
        cursor.execute("UPDATE parking_space SET available_spaces = available_spaces - 1")
        conn.commit()

        # Calculate parking cost
        # Assuming a rate of Rs. 10 per hour
        parking_cost = ((datetime.now() - entry_time).total_seconds() / 3600) * 10
        cursor.execute("UPDATE entry_exit_log SET parking_cost = %s WHERE vehicle_plate = %s AND exit_time IS NULL", (parking_cost, vehicle_plate))
        conn.commit()

    return redirect('/admin')

@app.route('/exit/<int:log_id>', methods=['POST'])
def exit(log_id):
    # Process vehicle exit
    exit_time = datetime.now()

    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT entry_time, parking_cost FROM entry_exit_log WHERE id = %s", (log_id,))
        entry_data = cursor.fetchone()

        if not entry_data:
            return "Invalid log ID."

        entry_time, initial_parking_cost = entry_data

        # Calculate parking duration
        duration_minutes = (exit_time - entry_time).total_seconds() / 60

        # Calculate parking cost based on duration (replace the formula as needed)
        parking_cost = duration_minutes * 0.1  # Adjust the rate as needed

        cursor.execute("UPDATE entry_exit_log SET exit_time = %s, parking_cost = %s WHERE id = %s",
                       (exit_time, parking_cost, log_id))
        conn.commit()

        # Update available_spaces
        cursor.execute("UPDATE parking_space SET available_spaces = available_spaces + 1")
        conn.commit()

    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
