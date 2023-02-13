from PIL import Image, ImageOps

def add_transparent_png(background_image, overlay_image):
    bg_width, bg_height = background_image.size
    ov_width, ov_height = overlay_image.size

    position = (bg_width//2 - ov_width//2, bg_height - ov_height - 300)
    background_image.paste(overlay_image, position, overlay_image)
    return background_image

def rotate_image(image_path, degrees_to_rotate, overlay_path):
    image = Image.open(image_path)
    rotated_image = image.rotate(degrees_to_rotate)
    size = rotated_image.size
    black_background = Image.new("RGBA", size, (0,0,0,255))
    final_image = Image.alpha_composite(black_background, rotated_image)
    overlay = Image.open(overlay_path)
    final_image = add_transparent_png(final_image, overlay)
    return final_image

def rotate_and_overlay_image(image_path, degrees, overlay_path):
    return rotate_image(image_path, degrees, overlay_path)

if __name__ == '__main__':
    pass