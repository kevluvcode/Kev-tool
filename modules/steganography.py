def run(kevbin):
    kevbin.box.title("LSB Steganography")
    mode = kevbin.box.select("Mode", ["Hide text in image", "Extract text from image"])
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
        img = img.convert('RGB')
        pixels = img.load()
        width, height = img.size
    except Exception as e:
        kevbin.box.error(f"Failed to open image: {e}")
        return
    
    if mode == "Hide text in image":
        text = kevbin.box.input("Text to hide: ")
        if not text:
            return
        
        binary = ''.join(format(ord(c), '08b') for c in text)
        binary += '00000000'  # Null terminator
        
        if len(binary) > width * height * 3:
            kevbin.box.error("Text too large for image")
            return
        
        idx = 0
        for y in range(height):
            for x in range(width):
                if idx >= len(binary):
                    break
                r, g, b = pixels[x, y]
                if idx < len(binary):
                    r = (r & 0xFE) | int(binary[idx])
                    idx += 1
                if idx < len(binary):
                    g = (g & 0xFE) | int(binary[idx])
                    idx += 1
                if idx < len(binary):
                    b = (b & 0xFE) | int(binary[idx])
                    idx += 1
                pixels[x, y] = (r, g, b)
            if idx >= len(binary):
                break
        
        output = kevbin.box.input("Output path (default: original_stego.png): ")
        if not output:
            import os
            base, _ = os.path.splitext(path)
            output = f"{base}_stego.png"
        
        try:
            img.save(output, 'PNG')
            kevbin.box.success(f"Hidden text saved to: {output}")
        except Exception as e:
            kevbin.box.error(f"Failed to save: {e}")
    
    else:
        binary = ""
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary += str(r & 1)
                binary += str(g & 1)
                binary += str(b & 1)
        
        chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) < 8:
                break
            if byte == '00000000':
                break
            chars.append(chr(int(byte, 2)))
        
        result = ''.join(chars)
        if result:
            kevbin.box.code(result)
        else:
            kevbin.box.info("No hidden text found (or empty)")