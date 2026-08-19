def run(kevbin):
    kevbin.box.title("Photo Metadata Extractor")
    path = kevbin.box.input("Image file path: ")
    if not path:
        return
    
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
    except ImportError:
        kevbin.box.error("Pillow not installed. Install with: pip install Pillow")
        return
    
    try:
        img = Image.open(path)
    except Exception as e:
        kevbin.box.error(f"Failed to open image: {e}")
        return
    
    kevbin.box.table(
        ["Property", "Value"],
        [["Format", img.format], ["Mode", img.mode], ["Size", f"{img.width}x{img.height}"]]
    )
    
    exif = img.getexif()
    if not exif:
        kevbin.box.info("No EXIF data found")
        return
    
    rows = []
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            gps_data = {}
            for gps_tag_id, gps_value in value.items():
                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                gps_data[gps_tag] = gps_value
            rows.append([tag, str(gps_data)])
        else:
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = f"<bytes: {len(value)}>"
            rows.append([tag, str(value)[:200]])
    
    kevbin.box.table(["Tag", "Value"], rows)