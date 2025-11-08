import qrcode
url="https://lost-found-git.onrender.com" 
img=qrcode.make(url)
img.save("qr.png")
print("QR code saved as qr.png")