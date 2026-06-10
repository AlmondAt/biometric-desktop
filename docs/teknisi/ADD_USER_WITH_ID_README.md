# 🔧 Fix User ID Sequence Issue

Ketika user manual ditambahkan ke database, AUTOINCREMENT sequence bisa tidak ter-reset dengan benar, sehingga user ID baru langsung lompat ke nomor tinggi (contoh: dari 2 langsung ke 10).

## 📋 Solusi: Tambah User Dengan ID Spesifik

### 🚀 Quick Start

1. **Pastikan aplikasi sedang berjalan:**
   ```powershell
   npm run dev
   ```

2. **Di terminal lain, jalankan script:**
   ```powershell
   node add-user-with-id.js --id 1 --name "Nama User"
   ```

### 📝 Contoh Penggunaan

#### Tambah user biasa (member) dengan ID 1:
```powershell
node add-user-with-id.js --id 1 --name "John Doe"
```

#### Tambah admin dengan ID 1:
```powershell
node add-user-with-id.js --id 1 --name "John Doe" --role admin
```

#### Tambah coadmin dengan ID 1:
```powershell
node add-user-with-id.js --id 1 --name "John Doe" --role coadmin
```

### 📊 Output Contoh

```
📝 Menambahkan user...
   ID: 1
   Nama: John Doe
   Role: member

✅ User "John Doe" berhasil ditambahkan dengan ID 1

Detail user:
  ID: 1
  Nama: John Doe
  Role: member
  Terdaftar: 29/4/2026 14:30:45
```

---

## 🔍 Troubleshooting

### ❌ "Connection refused"
→ Aplikasi tidak sedang berjalan. Jalankan `npm run dev` terlebih dahulu.

### ❌ "User dengan ID 1 sudah ada"
→ ID 1 sudah ada di database. Gunakan ID lain, contoh: `--id 2`, `--id 3`, dll.

### ❌ "Nama lengkap diperlukan"
→ Gunakan opsi `--name` dengan nama yang valid.

---

## 🎯 API Endpoint (Manual)

Jika ingin manual via curl atau Postman:

### POST /api/users/add-with-id

**Request:**
```json
POST http://localhost:3001/api/users/add-with-id

{
  "id": 1,
  "fullName": "John Doe",
  "role": "member"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "✅ User \"John Doe\" berhasil ditambahkan dengan ID 1",
  "user": {
    "id": 1,
    "fullName": "John Doe",
    "role": "member",
    "registrationDate": "2026-04-29T14:30:45.000Z",
    ...
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "User dengan ID 1 sudah ada"
}
```

---

## 💡 Tips

- **Cek user yang sudah ada:**
  Buka aplikasi → Tab "Users" untuk melihat semua user dan ID mereka

- **Role options:**
  - `member` - User biasa (default)
  - `coadmin` - Co-Administrator
  - `admin` - Administrator

- **Bulk add users:**
  ```powershell
  # Tambah beberapa user sekaligus
  node add-user-with-id.js --id 1 --name "User 1"
  node add-user-with-id.js --id 2 --name "User 2"
  node add-user-with-id.js --id 3 --name "User 3"
  ```

---

## ✅ Next Step

Setelah user ditambahkan dengan ID 1, user ID berikutnya akan auto-increment dari database sequence dengan benar!

```
Existing: ID 2, 3, 10
↓ Tambah dengan script
Tambah User dengan ID 1
↓ User baru di tambahkan
Database: ID 1, 2, 3, 10
↓ Auto-increment berikutnya
Next new user: ID 11 (atau ID terkecil yang belum ada)
```

🎯 **Sequence sudah fixed!**
