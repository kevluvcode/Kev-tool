import hashlib

def run(kevbin):
    kevbin.box.title("File Checksum Calculator")
    path = kevbin.box.input("File path: ")
    if not path:
        return
    
    algorithms = {
        "MD5": hashlib.md5(),
        "SHA1": hashlib.sha1(),
        "SHA256": hashlib.sha256(),
        "SHA512": hashlib.sha512(),
    }
    
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                for h in algorithms.values():
                    h.update(chunk)
    except Exception as e:
        kevbin.box.error(f"Failed to read file: {e}")
        return
    
    rows = [[name, h.hexdigest()] for name, h in algorithms.items()]
    kevbin.box.table(["Algorithm", "Hash"], rows)