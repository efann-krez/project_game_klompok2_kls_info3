# project game mobil balap 

# maintener
1. efan umagapi
# dokumen/how-to
1. sri fitri wulandari
2. jelia munziana
# kontributor
1. Klara Sibu
2. refalina darwin



# DESKRIPSI PROJEK
Speed Evade adalah game balap arkade 2D berbasis Python di mana pemain harus mengendalikan mobil untuk menghindari rintangan berupa mobil musuh yang bergerak berlawanan arah secara acak. Game ini menguji ketangkasan dan waktu reaksi pemain dengan tingkat kesulitan yang meningkat seiring bertambahnya level.
•	Genre: Arcade / Endless Runner / Racing
•	Platform: PC (Windows/Linux/Mac) via Terminal/CMD
•	Target Audiens: Pemain kasual yang menyukai tantangan skor tinggi.

# MEKANIK GAME (GAMEPLAY)
1.1. Kontrol Pemain
•	Enter: Memulai permainan dari layar instruksi.
•	Tombol Panah Kiri/Kanan: Menggerakkan mobil player ke samping untuk menghindari musuh.
2.2. Aturan Permainan & Sistem Skor
•	Skor: Bertambah setiap kali mobil player berhasil melewati mobil enemy.
•	Leveling: Kecepatan mobil akan meningkat secara otomatis seiring bertambahnya level.
•	Kondisi Menang (Win): Pemain mencapai Level 5. Setelah itu, game dapat dilanjutkan sebagai mode endless.
•	Kondisi Kalah (Game Over): Mobil player bertabrakan dengan mobil enemy.
1.3. Power-Up (Item Pendukung)
Terdapat tiga item yang muncul secara acak untuk membantu pemain:
1.	Item (B) - Bonus Life: Menambah sisa nyawa/kesempatan player.
2.	Item (S) - Shield: Memberikan perlindungan sementara agar tidak hancur saat menabrak.
3.	Item (T) - Time Slow: Memperlambat kecepatan gerak mobil musuh untuk sementara waktu.

# SPESIFIKASI TEKNIS (TECHNICAL DESIGN)
2.1. Kebutuhan Perangkat Keras
•	Perangkat: Laptop/PC dengan spesifikasi standar (mendukung lingkungan Python).
2.2. Stack Teknologi
•	Bahasa Pemrograman: Python 3.x.
•	Library Utama: Pygame (untuk rendering grafis, input keyboard, dan manajemen aset).
•	Alat Bantu Pengembangan: ChatGPT (AI Assistant) untuk optimasi kode dan debugging.
2.3. Arsitektur Kode (Logika Program)
•	Loop Utama: Menangani pembaruan posisi objek, pengecekan tabrakan , dan penggambaran ulang layar 
•	Sistem Spawn: Menggunakan fungsi random untuk menentukan posisi munculnya mobil musuh dan item (B, S, T).

# ASET VISUAL DAN AUDIO
•	Player: Sprite mobil pemain.
•	Enemy: Sprite mobil musuh dengan variasi warna.
•	Icons: Simbol huruf (B, S, T) sebagai representasi item.
•	UI: Tampilan skor, level, dan instruksi "Press Enter" di awal permainan.

# PANDUAN PENGOPERASIAN (USER MANUAL)
Sebagai pengembang, Anda dapat mengikuti langkah berikut untuk menjalankan atau mendistribusikan game:
1.	Instalasi:
1.	Pastikan Python sudah terinstal di sistem.
2.	Instal library Pygame melalui CMD: pip install pygame.
2.	Menjalankan Game:
0.	Buka Command Prompt (CMD) atau Terminal.
1.	Masuk ke direktori folder proyek.
2.	Ketik perintah: python nama_file_game.py.
3.	Alur Permainan:
0.	Muncul layar instruksi. Tekan Enter.
1.	Gunakan Panah Kiri/Kanan untuk menghindar.
2.	Ambil item (B, S, T) untuk keuntungan strategis.
3.	Bertahan hingga Level 5 untuk meraih kemenangan.
