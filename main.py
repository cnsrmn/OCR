import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image, ImageTk
import pytesseract
import hashlib


# Initialize a global variable to store the hash of the current image on canvas
current_image_hash = None

def get_image_hash(image):
    """ Compute the hash of an image. """
    image_bytes = image.tobytes()
    return hashlib.md5(image_bytes).hexdigest()

def display_image_on_canvas(image):
    global current_image_hash
    current_image_hash = get_image_hash(image)
    canvas.delete("all")  # Clear the canvas before displaying a new image
    canvas.image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=canvas.image)
    extract_button.config(state='normal')  # Enable the button
def display_message_on_canvas(message):
    """ Display a message on the canvas. """
    canvas.delete("all")  # Clear the canvas first
    formatted_message = message.replace(". ", ".\n")
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2,
                       text=formatted_message, fill="black",
                       font=('Helvetica', 16, 'bold'), anchor='center')

def check_clipboard():
    global current_image_hash
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            clipboard_image_hash = get_image_hash(image)
            if clipboard_image_hash != current_image_hash:
                display_image_on_canvas(image)
        else:
            # Display a message if the clipboard does not contain an image
            display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
    except Exception as e:
        messagebox.showerror("Error checking clipboard.", str(e))
    finally:
        # Check the clipboard again after 1000 milliseconds (1 second)
        root.after(1000, check_clipboard)


def extract_text_from_clipboard():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            extracted_text = pytesseract.image_to_string(image)
            text_box.delete('1.0', tk.END)
            text_box.insert(tk.END, extracted_text)
        else:
            #messagebox.showinfo("No Image", "Clipboard does not contain an image.")
            extract_button.config(state='disabled')  # Disable the button
    except Exception as e:
        messagebox.showerror("Error", str(e))


def clear_all():
    global current_image_hash
    text_box.delete('1.0', tk.END)
    root.clipboard_clear()
    display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
    extract_button.config(state='disabled')  # Disable the button
    current_image_hash = None  # Reset the hash
def copy_text_to_clipboard():
    global current_image_hash
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    current_image_hash = None  # Reset the hash

root = tk.Tk()
root.title("OCR from Clipboard")
root.geometry("800x600")  # Set initial size of the window

canvas = tk.Canvas(root, height=300)
canvas.pack(padx=10, pady=10, fill='both', expand=True)

text_box = tk.Text(root, height=10, width=50)
text_box.pack(padx=10, pady=10, fill='both', expand=True)

button_frame = tk.Frame(root)
button_frame.pack(fill='x', expand=False)

extract_button = tk.Button(button_frame, text="Extract Text from Clipboard", command=extract_text_from_clipboard, state='disabled')
extract_button.pack(side='left', padx=5, pady=5)

clear_button = tk.Button(button_frame, text="Clear All", command=clear_all)
clear_button.pack(side='left', padx=5, pady=5)

copy_button = tk.Button(button_frame, text="Copy Text", command=copy_text_to_clipboard)
copy_button.pack(side='left', padx=5, pady=5)



# Start the periodic clipboard check
check_clipboard()

root.mainloop()