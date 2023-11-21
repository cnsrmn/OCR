import tkinter as tk
from tkinter import messagebox, Button
from PIL import ImageGrab, Image, ImageTk, UnidentifiedImageError
from PIL import Image as PILImage
import pytesseract
from pytesseract import TesseractError
import hashlib
import pystray
import threading
from tkinter.simpledialog import Dialog

class CustomDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title=None):
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Would you like to exit the program or minimize to system tray?").pack()
        return None

    def buttonbox(self):
        box = tk.Frame(self)

        exit_button = tk.Button(box, text="Exit", width=10, command=lambda: self.ok("exit"))
        minimize_button = tk.Button(box, text="Minimize", width=10, command=lambda: self.ok("minimize"))
        cancel_button = tk.Button(box, text="Cancel", width=10, command=self.cancel)

        exit_button.pack(side='left', padx=5, pady=5)
        minimize_button.pack(side='left', padx=5, pady=5)
        cancel_button.pack(side='left', padx=5, pady=5)

        self.bind("<Return>", lambda event: self.ok("exit"))
        self.bind("<Escape>", self.cancel)

        box.pack()

    def ok(self, action):
        self.user_action = action
        print(f"Action chosen: {self.user_action}")
        self.destroy()

    def cancel(self, event=None):
        self.user_action = "cancel"
        self.destroy()

def on_close_request():
    dialog = CustomDialog(root)
    print(f"User action from dialog: {dialog.user_action}")
    if dialog.user_action == "exit":
        root.destroy()
    elif dialog.user_action == "minimize":
        hide_window_to_tray()

def show_about():
    about_message = "Clipboard Text Extractor\nVersion 1.0\nDeveloped by [Can SARMAN]\n\nThis application extracts text from images in the clipboard and can run in the background."
    messagebox.showinfo("About Clipboard Text Extractor", about_message)

# Initialize a global variable to store the hash of the current image on canvas
current_image_hash = None

def show_help():
    help_message = """
    Clipboard Text Extractor - Help

    How to Use with Windows Snip Tool:
    1. Use the Windows Snip Tool to capture an area of the screen.
    2. The captured image will be automatically saved to the clipboard.
    3. The Clipboard Text Extractor will detect the image and extract text from it.

    Clipboard Functionality:
    - The application monitors your clipboard for images.
    - When an image is found, it extracts any text in the image.
    - You can then use the 'Copy Text' button to copy the extracted text to the clipboard.

    """
    messagebox.showinfo("Help - Clipboard Text Extractor", help_message)

image_on_canvas = False
text_in_textbox = False

def auto_extract_checkbox_command():
    """ Handles actions when the auto extract checkbox is clicked. """
    clear_all()
    toggle_button_states()


def toggle_button_states():
    global image_on_canvas, text_in_textbox

    if auto_extract_var.get():
        # Disable the buttons
        extract_button.config(state='disabled')
        copy_button.config(state='disabled')

    else:
        # Enable buttons based on conditions
        extract_button.config(state='normal' if image_on_canvas else 'disabled')
        copy_button.config(state='normal' if text_in_textbox else 'disabled')



def start_application():
    # Delay the initial clipboard check to allow the canvas to initialize
    root.after(500, check_clipboard)

def get_image_hash(image):
    image_bytes = image.tobytes()
    return hashlib.md5(image_bytes).hexdigest()

def display_image_on_canvas(image):
    global current_image_hash, image_on_canvas
    current_image_hash = get_image_hash(image)
    canvas.delete("all")  # Clear the canvas before displaying a new image
    canvas.image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=canvas.image)
    image_on_canvas = True
    toggle_button_states()

def display_message_on_canvas(message):
    canvas.delete("all")  # Clear the canvas first
    formatted_message = message.replace(". ", ".\n")
    canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2,
                       text=formatted_message, fill="black",
                       font=('Helvetica', 16, 'bold'), anchor='center')
    toggle_button_states()
def check_clipboard():
    global current_image_hash
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            clipboard_image_hash = get_image_hash(image)
            if clipboard_image_hash != current_image_hash:
                display_image_on_canvas(image)
                toggle_button_states()
                if auto_extract_var.get():  # Check if the AutoExtractCopyText is enabled
                    extract_text_from_clipboard()  # Automatically extract text
                    toggle_button_states()
        else:
            display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
            toggle_button_states()
    except UnidentifiedImageError:
        messagebox.showerror("Error", "Unsupported image format.")
    except Exception as e:
        messagebox.showerror("Error", "An unexpected error occurred: " + str(e))
    finally:
        root.after(1500, check_clipboard)
        toggle_button_states()
def extract_text_from_clipboard():
    global text_in_textbox
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            extracted_text = pytesseract.image_to_string(image)
            text_box.delete('1.0', tk.END)
            text_box.insert(tk.END, extracted_text)
            text_in_textbox = bool(extracted_text.strip())
            toggle_button_states()
            #copy_button.config(state='normal')  # Enable the button since there possibly is now text to copy.
            if auto_extract_var.get():  # Check if the AutoExtractCopyText is enabled
                copy_text_to_clipboard()  # Automatically copy text if checkbox is selected
                toggle_button_states()
        else:
            messagebox.showinfo("No Image", "Clipboard does not contain an image.")
            toggle_button_states()
    except TesseractError as e:
        messagebox.showerror("OCR Error", "Failed to extract text: " + str(e))
    except Exception as e:
        messagebox.showerror("Error", "An unexpected error occurred: " + str(e))

def clear_all():
    global image_on_canvas, text_in_textbox
    global current_image_hash
    text_box.delete('1.0', tk.END)
    root.clipboard_clear()
    display_message_on_canvas("No image in clipboard. Please copy an image with text to clipboard.")
    current_image_hash = None  # Reset the hash
    image_on_canvas = False
    text_in_textbox = False
    toggle_button_states()

def copy_text_to_clipboard():
    global current_image_hash
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    display_message_on_canvas("Clipboard populated with text.")
    current_image_hash = None  # Reset the hash
    toggle_button_states()

def create_tray_icon(image_path):
    """Create a system tray icon."""
    icon = pystray.Icon("clipboard_text_extractor")
    icon.icon = PILImage.open(image_path)
    icon.title = "Clipboard Text Extractor"
    icon.menu = pystray.Menu(
        pystray.MenuItem("Show", lambda: show_window(icon)),
        pystray.MenuItem("Quit", lambda: quit_application(icon))
    )
    return icon

def show_window(icon):
    """Show the application window and stop the system tray icon."""
    icon.stop()
    root.after(0, root.deiconify)  # Show the window

def quit_application(icon):
    """Stop the system tray icon and quit the application."""
    icon.stop()
    root.destroy()


def hide_window_to_tray():
    """Hide the window and show the system tray icon in a separate thread."""
    root.withdraw()  # Hide the window
    icon = create_tray_icon(r'C:\Users\cs439\PycharmProjects\ocr\system_tray_icon.png')

    # Run the pystray icon in a single separate thread
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

root = tk.Tk()
root.title("Clipboard Text Extractor")
root.geometry("800x600")
root.protocol("WM_DELETE_WINDOW", on_close_request)  # Use the new on_close_request function

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add 'About' menu
about_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="About", menu=about_menu)
about_menu.add_command(label="About Clipboard Text Extractor", command=show_about)

# Add 'Help' menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="How to Use", command=show_help)

canvas = tk.Canvas(root, height=300, width=800)
canvas.pack(padx=10, pady=10, fill='both', expand=True)

text_box = tk.Text(root, height=10, width=50)
text_box.pack(padx=10, pady=10, fill='both', expand=True)

button_frame = tk.Frame(root)
button_frame.pack(fill='x', expand=False)

extract_button: Button = tk.Button(button_frame, text="Extract Text from Clipboard", command=extract_text_from_clipboard, state='disabled')
extract_button.pack(side='left', padx=10, pady=10)

copy_button = tk.Button(button_frame, text="Copy Text", command=copy_text_to_clipboard, state='disabled')
copy_button.pack(side='left', padx=10, pady=10)


auto_extract_var = tk.BooleanVar(value=True)  # Default to True if you want the buttons to be disabled at start
auto_extract_checkbox = tk.Checkbutton(root, text="Auto Extract and Copy Text", variable=auto_extract_var, command=auto_extract_checkbox_command)
auto_extract_checkbox.pack(side='left', padx=10, pady=10)


toggle_button_states()  # Set the initial state of buttons

start_application()

root.mainloop()