# WebNgan

cài python

curl -o python-installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

# Kiểm tra xem python đã cài đặt được hay chưa
python --version
pip --version


# Cài flask
pip install Flask

# Cài sqlite3
curl -O https://www.sqlite.org/2024/sqlite-tools-win32-x86-3440200.zip
tar -xf sqlite-tools-win32-x86-3440200.zip
sqlite3 --version


# Chạy file
python app.py

# Hướng dẫn
/add để thêm vào 
/edit để chỉnh sửa


