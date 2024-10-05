import json
import os
import threading
import time
from pynput import mouse
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Icon

# Obtener la ruta de la carpeta Documentos
documents_folder = os.path.expanduser('~')
clicks_file = os.path.join(documents_folder, 'clicks.json')

# Cargar conteo previo de clics
try:
    with open(clicks_file, 'r') as f:
        data = json.load(f)
        click_data = data.get('click_data', {'left': 0, 'right': 0, 'middle': 0, 'scroll': 0})
except FileNotFoundError:
    click_data = {'left': 0, 'right': 0, 'middle': 0, 'scroll': 0}

# Función que se llama al hacer clic
def on_click(x, y, button, pressed):
    global click_data
    if pressed:
        if button == mouse.Button.left:
            click_data['left'] += 1
        elif button == mouse.Button.right:
            click_data['right'] += 1
        elif button == mouse.Button.middle:
            click_data['middle'] += 1
        save_clicks()

# Función que se llama al hacer scroll
def on_scroll(x, y, dx, dy):
    global click_data
    click_data['scroll'] += 1
    save_clicks()

# Guardar los clics en el archivo
def save_clicks():
    with open(clicks_file, 'w') as f:
        json.dump({'click_data': click_data}, f)

# Crear una imagen simple para el icono
def create_image():
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((10, 10, 54, 54), fill=(0, 128, 255))
    return image

def update_tooltip(icon):
    tooltip = (
        f"Clicks Izquierdos: {click_data['left']}\n"
        f"Clicks Derechos: {click_data['right']}\n"
        f"Clicks Medios: {click_data['middle']}\n"
        f"Scrolls: {click_data['scroll']}"
    )
    icon.title = tooltip  # Actualiza el tooltip

def exit_action(icon, item):
    icon.stop()

def setup(icon):
    icon.visible = True

# Configurar el icono de la bandeja
icon = Icon("Clics Tracker", create_image(), "Clics Tracker", menu=pystray.Menu(MenuItem("Salir", exit_action)))

# Escuchar eventos de clic y scroll del mouse en un hilo separado
listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
listener.start()

# Iniciar el icono en la bandeja
threading.Thread(target=icon.run, args=(setup,), daemon=True).start()

# Actualizar el tooltip cada segundo
def update_icon():
    while True:
        update_tooltip(icon)
        time.sleep(1)

# Iniciar la actualización del tooltip
threading.Thread(target=update_icon, daemon=True).start()

# Mantener la aplicación en ejecución
while True:
    time.sleep(1)  # Mantiene el hilo principal activo
