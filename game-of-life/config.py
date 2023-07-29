WIDTH = 1200 
HEIGTH = 800 
BLOB_SIZE = 20

if WIDTH % BLOB_SIZE or HEIGTH % BLOB_SIZE:
    raise ValueError("WIDHT and HEIGTH must be divisable by BLOB_SIZE")