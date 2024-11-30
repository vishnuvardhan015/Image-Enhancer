from flask import Flask, request, render_template
from PIL import Image, ImageEnhance, ImageFilter, ImageChops
import base64
from io import BytesIO
import os

app = Flask(__name__)
os.makedirs('templates', exist_ok=True)

# **Manual Unsharp Masking for Sharpening**
def advanced_sharpen(image):
    """
    Apply unsharp masking to an image for sharpening.

    Steps:
    1. Blur the image to create a softened version.
    2. Calculate the difference (mask) between the original and blurred image.
    3. Blend the mask with the original image to enhance sharpness.
    """
    # **Step 1: Blur the Image**
    blurred = image.filter(ImageFilter.GaussianBlur(radius=2))

    # **Step 2: Calculate the Mask**
    mask = ImageChops.subtract(image, blurred)

    # **Step 3: Add the Mask Back with a Sharpening Factor**
    sharpening_factor = 1.5  # Controls the intensity of sharpening
    # Scale and offset values must be integers
    sharpened = ImageChops.add(image, mask, scale=int(sharpening_factor), offset=0)

    return sharpened

# **Contrast Enhancement with Adjustment**
def advanced_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

# **Noise Reduction with Median Filter**
def reduce_noise(image):
    return image.filter(ImageFilter.MedianFilter(size=3))

# **Color Enhancement with Balance**
def enhance_color(image, factor):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No image part'
        file = request.files['image']
        if file.filename == '':
            return 'No selected image'
        if file:
            img = Image.open(file)
            
            # **Process Image**
            sharpened = advanced_sharpen(img)
            contrast_factor = float(request.form.get('contrast_factor', 1.5))
            contrast_enhanced = advanced_contrast(sharpened, contrast_factor)
            noise_reduced = reduce_noise(contrast_enhanced)
            color_factor = float(request.form.get('color_factor', 1.2))
            final_image = enhance_color(noise_reduced, color_factor)
            
            # **Save to Memory Buffers**
            buf_original = BytesIO()
            buf_processed = BytesIO()
            img.save(buf_original, format='JPEG', quality=90)
            final_image.save(buf_processed, format='JPEG', quality=90)
            
            # **Convert to Base64**
            original_img_str = base64.b64encode(buf_original.getvalue()).decode('utf-8')
            processed_img_str = base64.b64encode(buf_processed.getvalue()).decode('utf-8')
            
            return render_template('display_images.html', 
                                   original_img=original_img_str, 
                                   processed_img=processed_img_str,
                                   contrast_factor=contrast_factor,
                                   color_factor=color_factor)
    return render_template('upload_image.html')

# HTML templates
with open('templates/upload_image.html', 'w') as f:
    f.write("""\
<html>
<body>
<h1>Image Upload, Enhance, and Display</h1>
<form method="post" enctype="multipart/form-data">
<input type="file" name="image" accept="image/*">
<br><br>
<label for="contrast_factor">Contrast Enhancement (Default=1.5):</label>
<input type="number" step="0.1" name="contrast_factor" value="1.5">
<br><br>
<label for="color_factor">Color Enhancement (Default=1.2):</label>
<input type="number" step="0.1" name="color_factor" value="1.2">
<br><br>
<input type="submit" value="Upload and Process">
</form>
</body>
</html>
""")

with open('templates/display_images.html', 'w') as f:
    f.write("""\
<html>
<body>
<h1>Image Upload and Enhancement</h1>

<div style="display: flex; justify-content: space-between;">
    <!-- Original Image -->
    <div style="flex: 1; padding: 10px;">
        <h2>Original Image</h2>
        <img src="data:image/jpeg;base64,{{ original_img }}" style="width: 100%; max-width: 500px;"/>
    </div>
    
    <!-- Processed Image -->
    <div style="flex: 1; padding: 10px;">
        <h2>Processed Image</h2>
        <img src="data:image/jpeg;base64,{{ processed_img }}" style="width: 100%; max-width: 500px;"/>
    </div>
</div>

<h2>Applied Settings:</h2>
<p><strong>Contrast Factor:</strong> {{ contrast_factor }}</p>
<p><strong>Color Factor:</strong> {{ color_factor }}</p>

</body>
</html>
""")

if __name__ == '__main__':
    app.run(debug=True)
