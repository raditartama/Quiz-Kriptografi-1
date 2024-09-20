from flask import Flask, render_template, request, redirect, url_for
import os
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Vigenere Cipher
def vigenere_encrypt(plaintext, key):
    ciphertext = ""
    key_length = len(key)
    key_index = 0  # Untuk melacak indeks kunci yang digunakan

    for char in plaintext:
        if char.isalpha():
            # Menggunakan huruf kecil untuk penanganan
            offset = ord(key[key_index % key_length].lower()) - ord('a')
            encrypted_char = chr(((ord(char.lower()) - ord('a') + offset) % 26) + ord('a'))
            ciphertext += encrypted_char
            key_index += 1  # Hanya tambah key_index untuk karakter alfabet
        else:
            ciphertext += char  # Menjaga spasi atau karakter lainnya

    return ciphertext

# Playfair Cipher
def playfair_prepare_key(key):
    key = key.upper()
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # I/J digabungkan
    used_chars = []
    for char in key:
        if char not in used_chars and char in alphabet:
            used_chars.append(char)
    for char in alphabet:
        if char not in used_chars:
            used_chars.append(char)
    return used_chars

def playfair_encrypt(plaintext, key):
    key_matrix = playfair_prepare_key(key)
    plaintext = plaintext.upper().replace("J", "I")
    
    # Menghapus karakter non-alfabet dari plaintext
    filtered_plaintext = ''.join(filter(str.isalpha, plaintext))

    if len(filtered_plaintext) % 2 != 0:
        filtered_plaintext += 'X'  # Menambahkan X jika jumlah karakter ganjil

    ciphertext = ""
    for i in range(0, len(filtered_plaintext), 2):
        a, b = filtered_plaintext[i], filtered_plaintext[i + 1]
        a_index = key_matrix.index(a)
        b_index = key_matrix.index(b)
        row_a, col_a = divmod(a_index, 5)
        row_b, col_b = divmod(b_index, 5)

        if row_a == row_b:
            ciphertext += key_matrix[row_a * 5 + (col_a + 1) % 5]
            ciphertext += key_matrix[row_b * 5 + (col_b + 1) % 5]
        elif col_a == col_b:
            ciphertext += key_matrix[((row_a + 1) % 5) * 5 + col_a]
            ciphertext += key_matrix[((row_b + 1) % 5) * 5 + col_b]
        else:
            ciphertext += key_matrix[row_a * 5 + col_b]
            ciphertext += key_matrix[row_b * 5 + col_a]

    return ciphertext

# Hill Cipher
def hill_prepare_key(key):
    key = key.upper().replace(" ", "")  # Menghapus spasi
    size = int(len(key) ** 0.5)  # Menghitung ukuran matriks (misalnya 3x3)

    if size * size != len(key):  # Memastikan panjang kunci sesuai
        raise ValueError("Panjang kunci harus berupa kuadrat dari bilangan bulat.")

    key_matrix = []
    for i in range(size):
        row = [ord(char) - 65 for char in key[i*size:(i+1)*size]]
        key_matrix.append(row)

    return np.array(key_matrix)

def hill_encrypt(plaintext, key):
    key_matrix = hill_prepare_key(key)
    plaintext = plaintext.replace(" ", "").upper()
    
    # Menambahkan X jika jumlah karakter tidak kelipatan ukuran matriks
    while len(plaintext) % key_matrix.shape[0] != 0:
        plaintext += 'X'
    
    ciphertext = ""
    for i in range(0, len(plaintext), key_matrix.shape[0]):
        vector = np.array([ord(char) - 65 for char in plaintext[i:i+key_matrix.shape[0]]])
        encrypted_vector = np.dot(key_matrix, vector) % 26
        ciphertext += ''.join(chr(num + 65) for num in encrypted_vector)

    return ciphertext

# Halaman Utama
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                # Proses file untuk enkripsi/dekripsi
                with open(file_path, 'r') as f:
                    plaintext = f.read()
                return 'File uploaded and read successfully'

        # Handle input dari keyboard
        plaintext = request.form['plaintext']
        key = request.form['key']

        # Cek panjang kunci minimal 12 karakter
        if len(key) < 12:
            return 'Kunci harus minimal 12 karakter!'

        # Pilih metode enkripsi
        method = request.form['method']

        # Proses enkripsi
        if method == 'vigenere':
            ciphertext = vigenere_encrypt(plaintext, key)
            return f'Ciphertext (Vigenere): {ciphertext}'
        elif method == 'playfair':
            ciphertext = playfair_encrypt(plaintext, key)
            return f'Ciphertext (Playfair): {ciphertext}'
        elif method == 'hill':
            ciphertext = hill_encrypt(plaintext, key)
            return f'Ciphertext (Hill): {ciphertext}'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)