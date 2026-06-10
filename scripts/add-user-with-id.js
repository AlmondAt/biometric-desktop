#!/usr/bin/env node

/**
 * Script untuk tambah user dengan ID spesifik
 * Berguna untuk fix sequence issue di database
 * 
 * Usage:
 *   node add-user-with-id.js --id 1 --name "Nama User" [--role admin]
 * 
 * Example:
 *   node add-user-with-id.js --id 1 --name "John Doe" --role admin
 */

const API_BASE = 'http://localhost:3001'

async function addUserWithId(userId, fullName, role = 'member') {
  console.log(`\n📝 Menambahkan user...`)
  console.log(`   ID: ${userId}`)
  console.log(`   Nama: ${fullName}`)
  console.log(`   Role: ${role}`)

  try {
    const response = await fetch(`${API_BASE}/api/users/add-with-id`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: userId,
        fullName,
        role
      })
    })

    const data = await response.json()

    if (!response.ok || !data.success) {
      console.error(`❌ Gagal: ${data.message}`)
      process.exit(1)
    }

    console.log(`✅ ${data.message}`)
    console.log(`\nDetail user:`)
    console.log(`  ID: ${data.user.id}`)
    console.log(`  Nama: ${data.user.fullName}`)
    console.log(`  Role: ${data.user.role}`)
    console.log(`  Terdaftar: ${new Date(data.user.registrationDate).toLocaleString('id-ID')}`)
  } catch (error) {
    console.error(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    console.error(`\n💡 Pastikan aplikasi sedang berjalan (npm run dev)`)
    process.exit(1)
  }
}

// Parse arguments
const args = process.argv.slice(2)
let userId = null
let fullName = null
let role = 'member'

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--id' && args[i + 1]) {
    userId = Number(args[i + 1])
    i++
  } else if (args[i] === '--name' && args[i + 1]) {
    fullName = args[i + 1]
    i++
  } else if (args[i] === '--role' && args[i + 1]) {
    role = args[i + 1]
    i++
  }
}

if (!userId || !fullName) {
  console.log(`\n📖 Usage: node add-user-with-id.js --id <ID> --name "<Nama>" [--role <role>]`)
  console.log(`\nContoh:`)
  console.log(`  node add-user-with-id.js --id 1 --name "John Doe"`)
  console.log(`  node add-user-with-id.js --id 1 --name "John Doe" --role admin`)
  console.log(`\nRole options: admin, coadmin, member (default: member)`)
  process.exit(1)
}

addUserWithId(userId, fullName, role)
