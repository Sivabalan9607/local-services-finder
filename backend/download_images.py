import urllib.request
import os

uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)

images = {
    "electrician.jpg": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=500&auto=format&fit=crop&q=60",
    "mechanic.jpg": "https://images.unsplash.com/photo-1517524206127-48bbd363f3d7?w=500&auto=format&fit=crop&q=60",
    "ac_tech.jpg": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?w=500&auto=format&fit=crop&q=60",
    "cleaner.jpg": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format&fit=crop&q=60",
    "painter.jpg": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=500&auto=format&fit=crop&q=60",
    "carpenter.jpg": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500&auto=format&fit=crop&q=60"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

for filename, url in images.items():
    path = os.path.join(uploads_dir, filename)
    print(f"Downloading {filename}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("Download script finished.")
