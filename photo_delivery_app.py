import os
import sqlite3
from tkinter import Tk, Label, Button, Entry, PhotoImage, filedialog
from PIL import Image, ImageTk, ImageOps
import requests

# Configuraciones iniciales
DB_NAME = "user_data.db"
CLOUD_ENDPOINT = "https://your-cloud-service.com/upload"  # Reemplazar con tu endpoint

# Crear base de datos local si no existe
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            rut TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Guardar usuario localmente
def save_user(rut, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")  # Siempre mantener un usuario
    cursor.execute("INSERT INTO users (rut, email) VALUES (?, ?)", (rut, email))
    conn.commit()
    conn.close()

# Recuperar usuario

def get_user():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT rut, email FROM users LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    return user

# Subir imagen comprimida a la nube
def upload_image(image_path):
    with open(image_path, "rb") as file:
        response = requests.post(CLOUD_ENDPOINT, files={"file": file})
        if response.status_code == 200:
            print("Imagen subida exitosamente")
        else:
            print("Error al subir la imagen")

# Ventana principal
def main_app():
    user = get_user()
    
    def capture_photo():
        file_path = filedialog.askopenfilename(title="Seleccionar una imagen", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            output_path = "compressed_image.jpg"
            image = Image.open(file_path)
            image = ImageOps.exif_transpose(image)
            image.save(output_path, "JPEG", quality=50)  # Comprimir imagen
            upload_image(output_path)

    root = Tk()
    root.title("Registro Fotográfico")
    root.geometry("300x400")

    if user:
        Label(root, text=f"Bienvenido: {user[0]} ({user[1]})", font=("Arial", 12)).pack(pady=20)
    else:
        Label(root, text="No se encontró un usuario guardado.").pack(pady=20)

    Button(root, text="Tomar Foto", command=capture_photo, width=20, height=2).pack(pady=10)
    Button(root, text="Salir", command=root.quit, width=20, height=2).pack(pady=10)

    root.mainloop()

# Ventana de inicio de sesión
def login_app():
    def login():
        rut = rut_entry.get()
        email = email_entry.get()
        if rut and email:
            save_user(rut, email)
            login_root.destroy()
            main_app()

    login_root = Tk()
    login_root.title("Login")
    login_root.geometry("300x200")

    Label(login_root, text="Ingrese sus datos", font=("Arial", 14)).pack(pady=10)

    Label(login_root, text="RUT:").pack()
    rut_entry = Entry(login_root)
    rut_entry.pack(pady=5)

    Label(login_root, text="Correo:").pack()
    email_entry = Entry(login_root)
    email_entry.pack(pady=5)

    Button(login_root, text="Ingresar", command=login, width=20, height=2).pack(pady=10)

    login_root.mainloop()

if __name__ == "__main__":
    init_db()
    user = get_user()
    if user:
        main_app()
    else:
        login_app()
