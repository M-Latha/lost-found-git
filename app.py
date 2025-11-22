from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create upload folder if missing
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# admin USN (set to the value you provided)
ADMIN_USN = "3BRAMD0001"

# create DB if not exists
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

# HOME ROUTE
@app.route('/')
def home():
    return render_template("miniproject.html")

# GET ITEMS
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

# SUBMIT ITEM
@app.route('/submit', methods=['POST'])
def submit():
    try:
        item_type = request.form.get('type', '')
        category = request.form.get('category', '')
        name = request.form.get('name', '')
        usn = request.form.get('usn', '')
        contact = request.form.get('contact', '')
        details = request.form.get('details', '')
        date = request.form.get('date', '')

        img_path = ""

        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename != "":
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(save_path)
                # store path that browser can use
                img_path = f"/static/uploads/{filename}"

        conn = sqlite3.connect('items.db')
        c = conn.cursor()
        c.execute("INSERT INTO items (type, category, name, usn, contact, details, date, img) VALUES (?,?,?,?,?,?,?,?)",
                  (item_type, category, name, usn, contact, details, date, img_path))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"})
    except Exception as e:
        print("ERROR in /submit:", e)
        return jsonify({"status": "error", "message": str(e)})

# DELETE ITEM (admin OR owner allowed)
@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        item_id = request.form.get('id')
        user_usn = request.form.get('usn', '')

        if not item_id:
            return jsonify({"status": "error", "message": "no id"})

        conn = sqlite3.connect('items.db')
        c = conn.cursor()

        # find owner of item
        c.execute("SELECT usn FROM items WHERE id=?", (item_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "item not found"})

        owner_usn = row[0]

        # allow delete if requesting user is admin OR owner
        if user_usn == ADMIN_USN or user_usn == owner_usn:
            c.execute("DELETE FROM items WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            return jsonify({"status": "deleted"})
        else:
            conn.close()
            return jsonify({"status": "unauthorized"})

    except Exception as e:
        print("ERROR in /delete_item:", e)
        return jsonify({"status": "error", "message": str(e)})

# serve images
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    # for local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
