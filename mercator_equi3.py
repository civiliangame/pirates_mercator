import cv2
import numpy as np

# Load the Mercator projection map
mercator = cv2.imread('background.png')

# Define the dimensions of the Equirectangular projection
equi_height, equi_width = 2048, 4096

# Define the coordinates of the Mercator projection
mercator_height, mercator_width = mercator.shape[:2]
mercator_lats = np.linspace(np.pi/2, -np.pi/2, mercator_height)
mercator_lons = np.linspace(-np.pi, np.pi, mercator_width)

# Define the coordinates of the Equirectangular projection
equi_lats = np.linspace(np.pi/2, -np.pi/2, equi_height)
equi_lons = np.linspace(-np.pi, np.pi, equi_width)

# Create a meshgrid of the Mercator and Equirectangular coordinates
mercator_lon_mesh, mercator_lat_mesh = np.meshgrid(mercator_lons, mercator_lats)
equi_lon_mesh, equi_lat_mesh = np.meshgrid(equi_lons, equi_lats)

# Convert the Mercator coordinates to Equirectangular coordinates
equi_x = mercator_lon_mesh
equi_y = np.arctanh(np.sin(mercator_lat_mesh))
equi_z = np.zeros_like(equi_x)

# Convert the Equirectangular coordinates to image coordinates
mercator_x_img = ((equi_x / np.pi) + 1) * (mercator_width - 1) / 2
mercator_y_img = ((-equi_y / np.pi) + 1) * (mercator_height - 1) / 2

# Use OpenCV's remap function to create the Equirectangular projection
map_x = mercator_x_img.astype(np.float32)
map_y = mercator_y_img.astype(np.float32)
equirectangular = cv2.remap(mercator, map_x, map_y, cv2.INTER_LINEAR)

# Resize the Equirectangular projection to the desired dimensions
equirectangular_resized = cv2.resize(equirectangular, (equi_width, equi_height))

# Save the Equirectangular projection as a PNG file
cv2.imwrite('equirectangular.png', equirectangular_resized)
