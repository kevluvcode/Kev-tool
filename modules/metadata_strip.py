def run(kevbin):
    kevbin.box.title("Metadata Stripper")
    path = kevbin.box.input("Image file path: ")
    if not path:
        return
    
    try:
        from PIL import Image
    except ImportError:
        kevbin.box.error("Pillow not installed. Install with: pip install Pillow")
        return
    
    try:
        img = Image.open(path)
    except Exception as e:
        kevbin.box.error(f"Failed to open image: {e}")
        return
    
    output_path = kevbin.box.input("Output path (default: original_stripped.ext): ")
    if not output_path:
        import os
        base, ext = os.path.splitext(path)
        output_path = f"{base}_stripped{ext}"
    
    try:
        data = list(img.getdata())
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(data)
        
        if img.format == 'JPEG':
            new_img.save(output_path, 'JPEG', quality=95)
        elif img.format == 'PNG':
            new_img.save(output_path, 'PNG')
        else:
            new_img.save(output_path)
        
        kevbin.box.success(f"Saved stripped image to: {output_path}")
    except Exception as e:
        kevbin.box.error(f"Failed to save: {e}")