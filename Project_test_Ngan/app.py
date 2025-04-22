from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cấu hình thư mục upload
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Số sản phẩm mỗi trang
PRODUCTS_PER_PAGE = 8

# Tạo thư mục upload nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Kiểm tra file có hợp lệ không
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
def init_db():
    with sqlite3.connect('products.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     price REAL NOT NULL,
                     image TEXT,
                     description TEXT,
                     created_at TEXT)''')
        conn.commit()

# Create database if not exists
if not os.path.exists('products.db'):
    init_db()

@app.route('/')
def index():
    # Lấy tham số tìm kiếm và trang
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PRODUCTS_PER_PAGE

    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    # Tìm kiếm và phân trang
    if search_query:
        c.execute('SELECT COUNT(*) FROM products WHERE name LIKE ?', ('%' + search_query + '%',))
        total_products = c.fetchone()[0]
        c.execute('SELECT * FROM products WHERE name LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
                 ('%' + search_query + '%', PRODUCTS_PER_PAGE, offset))
    else:
        c.execute('SELECT COUNT(*) FROM products')
        total_products = c.fetchone()[0]
        c.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT ? OFFSET ?',
                 (PRODUCTS_PER_PAGE, offset))
    
    products = c.fetchall()
    conn.close()

    # Tính tổng số trang
    total_pages = (total_products + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE

    # Xác định sản phẩm "Mới" (dưới 24 giờ)
    products_with_new = []
    for product in products:
        created_at = datetime.fromisoformat(product[5])
        is_new = (datetime.now() - created_at) < timedelta(hours=24)
        products_with_new.append(product + (is_new,))

    return render_template('index.html', products=products_with_new, page=page, total_pages=total_pages, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        
        if 'image' not in request.files:
            return "Không có file ảnh!", 400
        file = request.files['image']
        if file.filename == '':
            return "Chưa chọn file ảnh!", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
            file.save(file_path)
            image_path = os.path.join('images', filename).replace('\\', '/')
            
            conn = sqlite3.connect('products.db')
            c = conn.cursor()
            c.execute('INSERT INTO products (name, price, image, description, created_at) VALUES (?, ?, ?, ?, ?)',
                     (name, price, image_path, description, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "Định dạng file không được hỗ trợ! Chỉ hỗ trợ PNG, JPG, JPEG, GIF.", 400
    return render_template('add_product.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        
        image_path = request.form['current_image'].replace('\\', '/')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')
                file.save(file_path)
                image_path = os.path.join('images', filename).replace('\\', '/')
        
        c.execute('UPDATE products SET name=?, price=?, image=?, description=? WHERE id=?',
                 (name, price, image_path, description, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    c.execute('SELECT * FROM products WHERE id=?', (id,))
    product = c.fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/delete/<int:id>')
def delete_product(id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)