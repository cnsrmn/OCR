import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image, ImageTk, UnidentifiedImageError
import pytesseract
from pytesseract import TesseractError
import hashlib

# Initialize a global variable to store the hash of the current image on canvas
current_image_hash = None



def toggle_button_states():
    if auto_extract_var.get():
        # If the checkbox is checked, disable the buttons
        extract_button.config(state='disabled')
        copy_button.config(state='disabled')
        clear_button.config(state='disabled')
    else:
        # If the checkbox is unchecked, enable the buttons
        extract_button.config(state='normal')
        copy_button.config(state='normal')
        clear_button.config(state='normal')



def start_application():
    # Delay the initial clipboard check to allow the canvas to initialize
    root.after(500, check_clipboard)

def get_image_hash(image):
    image_bytes = image.tobytes()
    return hashlib.md5(image_bytes).hexdigest()

def display_image_on_canvas(image):
    global current_image_hash
    current_image_hash = get_image_hash(image)
    canvas.delete("all")  # Clear the canvas before displaying a new image
    canvas.image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=canvas.image)
    extract_button.config(state='normal')  # Enable the button
    #copy_button.config(state='normal')  # Enable the button
    clear_button.config(state='normal')  # Enable the button


def display_message_on_canvas(message):
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
                if auto_extract_var.get():  # Check if the AutoExtractCopyText is enabled
                    toggle_button_states()
                    extract_text_from_clipboard()  # Automatically extract text
        else:
            display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
    except UnidentifiedImageError:
        messagebox.showerror("Error", "Unsupported image format.")
    except Exception as e:
        messagebox.showerror("Error", "An unexpected error occurred: " + str(e))
    finally:
        root.after(1500, check_clipboard)

def extract_text_from_clipboard():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            extracted_text = pytesseract.image_to_string(image)
            text_box.delete('1.0', tk.END)
            text_box.insert(tk.END, extracted_text)
            copy_button.config(state='normal')  # Enable the button since there possibly is now text to copy.
            if auto_extract_var.get():  # Check if the AutoExtractCopyText is enabled
                toggle_button_states()
                copy_text_to_clipboard()  # Automatically copy text if checkbox is selected
        else:
            messagebox.showinfo("No Image", "Clipboard does not contain an image.")
            extract_button.config(state='disabled')  # Disable the button
    except TesseractError as e:
        messagebox.showerror("OCR Error", "Failed to extract text: " + str(e))
    except Exception as e:
        messagebox.showerror("Error", "An unexpected error occurred: " + str(e))

def clear_all():
    global current_image_hash
    text_box.delete('1.0', tk.END)
    root.clipboard_clear()
    display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
    extract_button.config(state='disabled')  # Disable the button
    copy_button.config(state='disabled')  # Disable the button
    clear_button.config(state='disabled')  # Disable the button
    current_image_hash = None  # Reset the hash
def copy_text_to_clipboard():
    global current_image_hash
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    display_message_on_canvas("Clipboard populated with text.")
    current_image_hash = None  # Reset the hash

root = tk.Tk()
root.title("Clipboard Text Extractor")
root.geometry("800x600")  # Set initial size of the window

canvas = tk.Canvas(root, height=300, width=800)
canvas.pack(padx=10, pady=10, fill='both', expand=True)

text_box = tk.Text(root, height=10, width=50)
text_box.pack(padx=10, pady=10, fill='both', expand=True)

button_frame = tk.Frame(root)
button_frame.pack(fill='x', expand=False)

extract_button = tk.Button(button_frame, text="Extract Text from Clipboard", command=extract_text_from_clipboard, state='disabled')
extract_button.pack(side='left', padx=10, pady=10)

clear_button = tk.Button(button_frame, text="Clear All", command=clear_all, state='disabled')
clear_button.pack(side='left', padx=10, pady=10)

copy_button = tk.Button(button_frame, text="Copy Text", command=copy_text_to_clipboard, state='disabled')
copy_button.pack(side='left', padx=10, pady=10)

auto_extract_var = tk.BooleanVar()  # Variable to track the checkbox state
auto_extract_checkbox = tk.Checkbutton(root, text="Auto Extract and Copy Text", variable=auto_extract_var, command=toggle_button_states)
auto_extract_checkbox.pack(side='left', padx=10, pady=10)


toggle_button_states()  # Set the initial state of buttons


start_application()


root.mainloop()