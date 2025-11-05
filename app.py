from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Create upload folder if missing
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Create DB if not exists
def init_db():
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    category TEXT,
                    name TEXT,
                    usn TEXT,
                    contact TEXT,
                    details TEXT,
                    date TEXT,
                    img TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ✅ HOME ROUTE
@app.route('/')
def home():
    return render_template("miniproject.html")

# ✅ GET ITEMS
@app.route('/get_items', methods=['GET'])
def get_items():
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "type": r[1],
            "category": r[2],
            "name": r[3],
            "usn": r[4],
            "contact": r[5],
            "details": r[6],
            "date": r[7],
            "img": r[8]
        })

    return jsonify(items)

# ✅ SUBMIT ITEM
@app.route('/submit', methods=['POST'])
def submit():
    try:
        item_type = request.form['type']
        category = request.form['category']
        name = request.form['name']
        usn = request.form['usn']
        contact = request.form['contact']
        details = request.form['details']
        date = request.form['date']

        img_path = ""

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != "":
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                image.save(save_path)

                # ✅ Correct web path for browser
                img_path = f"/static/uploads/{filename}"

        conn = sqlite3.connect('items.db')
        c = conn.cursor()
        c.execute("INSERT INTO items (type, category, name, usn, contact, details, date, img) VALUES (?,?,?,?,?,?,?,?)",
                  (item_type, category, name, usn, contact, details, date, img_path))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error"})

# ✅ DELETE ITEM
@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        item_id = request.form['id']
        user_usn = request.form['usn']   # ✅ logged-in user trying to delete

        conn = sqlite3.connect('items.db')
        c = conn.cursor()

        # ✅ Only delete if the same USN reported it
        c.execute("DELETE FROM items WHERE id=? AND usn=?", (item_id, user_usn))
        conn.commit()
        conn.close()

        # ✅ If no row deleted → unauthorized delete
        if c.rowcount == 0:
            return jsonify({"status": "unauthorized"})

        return jsonify({"status": "deleted"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ Serve uploaded images
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


