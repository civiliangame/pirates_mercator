
# mercator = Image.open("results/03_13_09_48_2023/Year_AD1952.png").convert("RGBA")
from PIL import Image
import numpy as np
import pyproj

# Open the Mercator map
mercator = Image.open("results/03_13_09_48_2023/Year_AD1952.png").convert("RGBA")

# Define the Mercator and equirectangular projections
mercator_proj = pyproj.Proj(proj="merc", ellps="WGS84")
equirectangular_proj = pyproj.Proj(proj="eqc", ellps="WGS84")

# Create a grid of longitude and latitude values for the Mercator projection
x, y = np.meshgrid(
    np.linspace(-20037508.342789, 20037508.342789, mercator.width),
    np.linspace(-20037508.342789, 20037508.342789, mercator.height),
)

# Convert the longitude and latitude values to the Mercator projection
lon, lat = pyproj.transform(mercator_proj, equirectangular_proj, x, y, radians=False)

# Create a new image for the equirectangular representation
equirectangular = Image.new("RGBA", (2048, 4096))

# Paste the reprojected Mercator map onto the equirectangular representation
equirectangular_pixels = np.zeros((4096, 2048, 4), dtype=np.uint8)
equirectangular_pixels[:,:] = mercator.getpixel((0,0))
for i in range(mercator.width):
    for j in range(mercator.height):
        x, y = int(np.floor((lon[j,i] + 180) / 360 * 2048)), int(np.floor((lat[j,i] + 90) / 180 * 4096))
        equirectangular_pixels[y,x,:] = mercator.getpixel((i,j))
equirectangular = Image.fromarray(equirectangular_pixels)

# Save the equirectangular representation
equirectangular.save("results/03_13_09_48_2023/equirectangular.png")

