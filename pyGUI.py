import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import END, TOP, Label, Entry, ALL
import time
# Constants
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_PADDING = 10
MAPS_FOLDER = './maps'
BACKGROUND_PATH = './background.png'
RESULT_IMAGE_PATH = './result.png'
IMAGE_SIZE = (4096, 4096)
ZOOM_FACTOR = 1.2
# Define constants for window sizes and padding
# WINDOW_WIDTH = 1900
# WINDOW_HEIGHT = 1000
WINDOW_PADDING = 10
from functools import partial

# Define the dimensions of canvas2
CANVAS2_WIDTH = 600
CANVAS2_HEIGHT = 600

# Define the path to the maps folder
MAPS_FOLDER = "./maps"

# Global variables
current_map_path = None
selected_pixels = None



# Helper functions
def update_window2_image(file_path):
    """Update canvas2 with the selected map image."""
    print(f"Selected file: {file_path}")

    # Clear the current image item from canvas2
    canvas2.delete("all")

    # Load the selected image into memory
    try:
        img = Image.open(file_path)
    except Exception as e:
        print(f"Failed to open image: {e}")
        return

    # Resize the image to fit within the canvas2 window
    img = img.resize((CANVAS2_WIDTH, CANVAS2_HEIGHT))

    # Convert the image to PhotoImage format and add it to canvas2
    photo_img = ImageTk.PhotoImage(img)
    canvas2.image = photo_img  # store a reference to prevent garbage collection
    canvas2.create_image(0, 0, anchor="nw", image=photo_img)
    print("Image loaded successfully")


def update_window1_list(search_term=""):
    """Update the list of files in Window 1."""
    # Get a list of all files in the MAPS_FOLDER
    files = os.listdir(MAPS_FOLDER)

    # Filter the list of files based on the search term
    filtered_files = [file for file in files if search_term.lower() in file.lower()]

    # Update the listbox with the filtered files
    listbox.delete(0, END)
    for file in filtered_files:
        listbox.insert(END, file)


def search_window1(search_entry):
    """Search for a file in Window 1."""
    search_term = search_entry.get()
    update_window1_list(search_term)



# def drag_canvas(canvas, event):
#     """Drag the given canvas view based on the mouse movement."""
#     canvas.scan_dragto(event.x, event.y, gain=1)

def select_pixels(event):
    """Select all adjacent pixels with the same color as the clicked pixel."""
    global selected_pixels
    # Convert mouse click coordinates from screen to canvas coordinates
    canvas_x, canvas_y = canvas2.canvasx(event.x), canvas2.canvasy(event.y)
    # Get the color of the clicked pixel using the canvas image
    pixel_color = canvas2.image.getpixel((canvas_x, canvas_y))
    # Use a recursive function to select all adjacent pixels with the same color
    def select_adjacent_pixels(x, y):
        if x < 0 or y < 0 or x >= IMAGE_SIZE[0] or y >= IMAGE_SIZE[1]:
            return
        if canvas2.image.getpixel((x, y)) != pixel_color:
            return
        if selected_pixels is None:
            selected_pixels = set()
        selected_pixels.add((x, y))
        # Highlight the selected pixel in red
        canvas2.create_rectangle(x, y, x+1, y+1, outline="red")
        # Recursively select adjacent pixels
        select_adjacent_pixels(x+1, y)
        select_adjacent_pixels(x-1, y)
        select_adjacent_pixels(x, y+1)
        select_adjacent_pixels(x, y-1)
    select_adjacent_pixels(canvas_x, canvas_y)

def paste_pixels():
    """Copy selected pixels from canvas2 and paste them onto canvas3."""
    global selected_pixels
    if selected_pixels is None:
        return
    # Open the background image using PIL
    bg_img = Image.open(BACKGROUND_PATH)
    # Loop through the selected pixels and copy their color to the background image
    for x, y in selected_pixels:
        bg_img.putpixel((x, y), canvas2.image.getpixel((x, y)))
    # Convert the modified background image to a PhotoImage using ImageTk
    bg_photo_img = ImageTk.PhotoImage(bg_img)
    # Update the canvas3 widget with the new image
    canvas3.itemconfig(image_item, image=bg_photo_img)
    # Enable the 'Render' button
    render_button.config(state='normal')

    # Convert the modified background image to a PhotoImage using ImageTk
    bg_photo_img = ImageTk.PhotoImage(bg_img)
    # Update the canvas3 widget with the new image
    canvas3.itemconfig(image_item, image=bg_photo_img)
    # Enable the 'Render' button
    render_button.config(state='normal')

def render_image():
    """Save the modified background image to a file."""
    # Get the modified background image from canvas3
    bg_img = Image.frombytes('RGBA', IMAGE_SIZE, canvas3.postscript(colormode='coloralpha'), 'RGBA')
    # Save the modified image to a file
    bg_img.save(RESULT_IMAGE_PATH)

# Create the main window
root = tk.Tk()
root.title("Map Editor")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Create a frame to hold the listbox and scrollbar
# frame1 = tk.Frame(root, width=300, height=WINDOW_HEIGHT - 2 * WINDOW_PADDING, padx=WINDOW_PADDING, pady=WINDOW_PADDING,highlightbackground="black", highlightthickness=1)
frame1 = tk.Frame(root, width=300, height=WINDOW_HEIGHT, padx=WINDOW_PADDING, pady=WINDOW_PADDING,highlightbackground="black", highlightthickness=1)
frame1.grid(row=0, column=0, sticky="nsew")
# Create a search box for Window 1
search_label = Label(frame1, text="Search:")
search_label.pack(side=TOP, padx=5, pady=5)
search_entry = Entry(frame1)
search_entry.pack(side=TOP, padx=5, pady=5)
search_entry.bind("<KeyRelease>", lambda event: search_window1(search_entry))


# Create a listbox to show the map files
listbox = tk.Listbox(frame1, selectmode=tk.SINGLE, font=("Courier", 12))
listbox.pack(side="left", fill="both", expand=True)
# Add a scrollbar to the frame
scrollbar = tk.Scrollbar(frame1, orient="vertical")
scrollbar.pack(side="right", fill="y")
# Link the scrollbar to the listbox
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)
# Load the map files into the listbox
for file_name in os.listdir(MAPS_FOLDER):
    if file_name.endswith('.png') and os.path.isfile(os.path.join(MAPS_FOLDER, file_name)):
        listbox.insert(tk.END, file_name)
# Bind a function to the listbox selection event
listbox.bind("<ButtonRelease-1>", lambda event: update_window2_image(os.path.join(MAPS_FOLDER, listbox.get(tk.ACTIVE))))



# Create a frame to hold canvas2 and its buttons
# frame2 = tk.Frame(root, width=400, bd=50, height=WINDOW_HEIGHT - 2 * WINDOW_PADDING, padx=WINDOW_PADDING, pady=WINDOW_PADDING, highlightbackground="red", highlightthickness=1)
frame2 = tk.Frame(root, width=CANVAS2_WIDTH, height=CANVAS2_HEIGHT + 200, highlightbackground="red", highlightthickness=1)
frame2.grid(row=0, column=1, sticky="nsew")

# Create canvas2 to show the selected map image
# canvas2 = tk.Canvas(frame2,  width=IMAGE_SIZE[0], height=IMAGE_SIZE[1], )
canvas2 = tk.Canvas(frame2,  width=CANVAS2_WIDTH, height=CANVAS2_HEIGHT, confine=True)
# canvas2.pack(side="left", fill="both", expand=True)
canvas2.pack(side="top", fill="both", expand=False)
# Load the default image into canvas2





#
default_img = Image.new('RGBA', IMAGE_SIZE, (255, 255, 255, 0))
default_photo_img = ImageTk.PhotoImage(default_img)


image_item = canvas2.create_image(0, 0, anchor=tk.NW, image=default_photo_img)





# Create buttons for canvas2
# button_frame = tk.Frame(frame2)
# button_frame.pack(side="bottom", fill="x")
#
# center_x = canvas2.winfo_width() / 2
# center_y = canvas2.winfo_height() / 2
# zoom_in_button = tk.Button(button_frame, text="Zoom In (+)", font=("Arial", 14), command=zoom_canvas(canvas2, 1))
# zoom_out_button = tk.Button(button_frame, text="Zoom Out (-)", font=("Arial", 14), command=lambda event: zoom_canvas(canvas2, -1))





# zoom_in_button = tk.Button(button_frame, text="Zoom In (+)", font=("Arial", 14), command=lambda: zoom_canvas(canvas2, 1))
# zoom_in_button.pack(side="left", fill="both", padx=10, pady=10)
# zoom_out_button.pack(side="right", fill="both", padx=10, pady=10)


# # Add bindings for canvas2 events
# canvas2.bind("<MouseWheel>", lambda event: zoom_canvas(canvas2, event.delta, event))




# root.bind_all("<KeyPress-q>", lambda event: zoom_canvas(canvas2, event, 1.2))
# root.bind_all("<KeyPress-w>", lambda event: zoom_canvas(canvas2, event, 0.8))



# canvas2.bind("<ButtonPress-1>", lambda event: canvas2.scan_mark(event.x, event.y))


# canvas2.bind("<B1-Motion>", lambda event: drag_canvas(canvas2, event))
# canvas2.bind("<ButtonRelease-3>", select_pixels)
# canvas2.bind("<ButtonRelease-2>", paste_pixels)
# canvas2.bind("<ButtonRelease-1>", lambda event: canvas2.scan_dragto(event.x, event.y, gain=1))
#

#
#
#
#
#
# print("Here yet?")
# print(zoom_in_button)
# print(zoom_out_button)
#
# # Create a frame to hold canvas3 and its buttons
frame3 = tk.Frame(root, width=400, height=WINDOW_HEIGHT - 2 * WINDOW_PADDING, padx=WINDOW_PADDING, pady=WINDOW_PADDING, highlightbackground="green", highlightthickness=1)
frame3.grid(row=0, column=2, sticky="nsew")

# Create canvas3 to show the modified background image
canvas3 = tk.Canvas(frame3, width=IMAGE_SIZE[0], height=IMAGE_SIZE[1])
canvas3.pack(side="left", fill="both", expand=True)
# Load the default image into canvas3
default_photo_img = ImageTk.PhotoImage(default_img)
image_item = canvas3.create_image(0, 0, anchor=tk.NW, image=default_photo_img)
# Add bindings for canvas3 events
# canvas3.bind("<MouseWheel>", lambda event: zoom_canvas(canvas3, event.delta, event))
canvas3.bind("<ButtonPress-1>", lambda event: canvas3.scan_mark(event.x, event.y))
# canvas3.bind("<B1-Motion>", lambda event: drag_canvas(canvas3, event))
canvas3.bind("<ButtonRelease-1>", lambda event: canvas3.scan_dragto(event.x, event.y, gain=1))

# Create buttons for canvas3
button_frame = tk.Frame(frame3)
button_frame.pack(side="right", fill="y")
# zoom_in_button = tk.Button(button_frame, text="Zoom In (+)", font=("Arial", 14), command=lambda: zoom_canvas(canvas3, 1))
# zoom_in_button.pack(fill="x", padx=10, pady=10)
# zoom_out_button = tk.Button(button_frame, text="Zoom Out (-)", font=("Arial", 14), command=lambda: zoom_canvas(canvas3, -1))
# zoom_out_button.pack(fill="x", padx=10, pady=10)

# Create the 'Render' button
render_button = tk.Button(root, text="Render", font=("Arial", 20), state="disabled", command=render_image)
render_button.grid(row=1, column=1, pady=WINDOW_PADDING)

# Start the main loop
root.mainloop()

