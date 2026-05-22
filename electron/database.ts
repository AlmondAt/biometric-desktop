import crypto from 'crypto'
import fs from 'fs'
import path from 'path'

interface SqlStatement {
  step(): boolean
  getAsObject(): Record<string, unknown>
  free(): void
}

interface SqlDatabase {
  prepare(query: string, params?: Array<string | number | null>): SqlStatement
  run(query: string, params?: Array<string | number | null>): void
  export(): Uint8Array
}

interface SqlJsStatic {
  Database: new(data?: Uint8Array | Buffer) => SqlDatabase
}

type SqlJsFactory = (config?: { locateFile?: (file: string) => string }) => Promise<SqlJsStatic>

export type UserRole = 'admin' | 'coadmin' | 'member'

export interface UserRecord {
  id: number
  displayNo: number
  fullName: string
  role: UserRole
  username: string | null
  fingerprintId: number | null
  faceEmbeddingKey: string | null
  faceEmbeddingCount: number
  faceEnrolled: boolean
  fingerprintEnrolled: boolean
  registrationDate: string
  updatedAt: string
  hasLogin: boolean
  source: 'local' | 'raspy-sync'
}

export interface AuthUser {
  accountId: number
  userId: number | null
  username: string
  fullName: string
  role: Exclude<UserRole, 'member'>
}

export interface CreateUserInput {
  id?: number
  fullName: string
  role: UserRole
  username?: string | null
  password?: string | null
  source?: 'local' | 'raspy-sync'
}

export interface UpdateUserInput {
  fullName: string
  role: UserRole
  username?: string | null
  password?: string | null
}

export interface AccessLogRecord {
  id: number
  userId: number | null
  fullName: string
  eventType: string
  method: string
  accessStatus: string
  similarity: number | null
  imagePath: string | null
  source: string
  eventTime: string
}

let SQL: SqlJsStatic | null = null
let database: SqlDatabase | null = null
let databaseFilePath = ''
let sqlJsDistPath = ''

function nowIso() {
  return new Date().toISOString()
}

function normalizeName(value: string) {
  return value.trim().replace(/\s+/g, ' ')
}

function ensureUniqueFullName(fullName: string, excludedUserId?: number) {
  const existing = typeof excludedUserId === 'number'
    ? selectOne('SELECT id FROM users WHERE full_name = ? AND id <> ?', [fullName, excludedUserId])
    : selectOne('SELECT id FROM users WHERE full_name = ?', [fullName])

  if (existing) {
    throw new Error(`Nama lengkap "${fullName}" sudah terdaftar. Gunakan nama lain atau lakukan retrain pada user yang ada.`)
  }
}

function normalizeUserPersistenceError(error: unknown) {
  if (error instanceof Error && /UNIQUE constraint failed: users\.full_name/i.test(error.message)) {
    return new Error('Nama lengkap sudah terdaftar. Gunakan nama lain atau lakukan retrain pada user yang ada.')
  }

  return error
}

function ensureDatabase() {
  if (!database) {
    throw new Error('Database belum diinisialisasi')
  }

  return database
}

function getNodeRequire() {
  if (typeof module !== 'undefined' && typeof module.require === 'function') {
    return module.require.bind(module) as (moduleId: string) => unknown
  }

  if (typeof require === 'function') {
    return require as (moduleId: string) => unknown
  }

  throw new Error('CommonJS require tidak tersedia di Electron main process.')
}

function resolveSqlJsDistDir(projectRoot: string) {
  const candidates = [
    path.join(projectRoot, 'node_modules', 'sql.js', 'dist'),
    path.join(process.cwd(), 'node_modules', 'sql.js', 'dist'),
    path.join(__dirname, '..', 'node_modules', 'sql.js', 'dist'),
    path.join(__dirname, '..', '..', 'node_modules', 'sql.js', 'dist')
  ]

  const resolved = candidates.find((candidate) => fs.existsSync(path.join(candidate, 'sql-wasm.js')))
  if (!resolved) {
    throw new Error('Folder sql.js/dist tidak ditemukan. Pastikan dependency sql.js terinstall.')
  }

  return resolved
}

async function loadSqlJs(projectRoot: string) {
  if (SQL) {
    return SQL
  }

  sqlJsDistPath = resolveSqlJsDistDir(projectRoot)
  const requireModule = getNodeRequire()
  const loadedModule = requireModule(path.join(sqlJsDistPath, 'sql-wasm.js')) as SqlJsFactory | { default?: SqlJsFactory }
  const initSqlJs = typeof loadedModule === 'function' ? loadedModule : loadedModule.default

  if (!initSqlJs) {
    throw new Error('Factory sql.js tidak dapat dimuat.')
  }

  SQL = await initSqlJs({
    locateFile: (file) => path.join(sqlJsDistPath, file)
  })

  return SQL
}

function mapUserRow(row: Record<string, unknown>): UserRecord {
  return {
    id: Number(row.id),
    displayNo: Number(row.display_no ?? row.id),
    fullName: String(row.full_name),
    role: String(row.role) as UserRole,
    username: row.username ? String(row.username) : null,
    fingerprintId: row.fingerprint_id === null || row.fingerprint_id === undefined ? null : Number(row.fingerprint_id),
    faceEmbeddingKey: row.face_embedding_key ? String(row.face_embedding_key) : null,
    faceEmbeddingCount: Number(row.face_embedding_count ?? 0),
    faceEnrolled: Number(row.face_enrolled ?? 0) === 1,
    fingerprintEnrolled: Number(row.fingerprint_enrolled ?? 0) === 1,
    registrationDate: String(row.registration_date),
    updatedAt: String(row.updated_at),
    hasLogin: Number(row.has_login ?? 0) === 1,
    source: String(row.source ?? 'local') as 'local' | 'raspy-sync'
  }
}

function withDisplayNumbers(users: UserRecord[]) {
  return users.map((user, index) => ({
    ...user,
    displayNo: index + 1
  }))
}

function selectAll(query: string, params: Array<string | number | null> = []) {
  const db = ensureDatabase()
  const statement = db.prepare(query, params)
  const rows: Record<string, unknown>[] = []

  while (statement.step()) {
    rows.push(statement.getAsObject())
  }

  statement.free()
  return rows
}

function selectOne(query: string, params: Array<string | number | null> = []) {
  const rows = selectAll(query, params)
  return rows[0] ?? null
}

function run(query: string, params: Array<string | number | null> = []) {
  const db = ensureDatabase()
  db.run(query, params)
}

function persist() {
  const db = ensureDatabase()
  fs.writeFileSync(databaseFilePath, Buffer.from(db.export()))
}

function hashPassword(password: string, salt?: string) {
  const effectiveSalt = salt ?? crypto.randomBytes(16).toString('hex')
  const passwordHash = crypto.scryptSync(password, effectiveSalt, 64).toString('hex')
  return { salt: effectiveSalt, passwordHash }
}

function ensureRoleHasLogin(role: UserRole) {
  return role === 'admin' || role === 'coadmin'
}

function createAuthAccount(userId: number | null, username: string, password: string, role: 'admin' | 'coadmin', fullName: string) {
  const { salt, passwordHash } = hashPassword(password)
  run(
    `INSERT INTO auth_accounts (user_id, username, password_hash, password_salt, role, full_name_snapshot, is_active, created_at)
     VALUES (?, ?, ?, ?, ?, ?, 1, ?)`,
    [userId, username.trim().toLowerCase(), passwordHash, salt, role, fullName, nowIso()]
  )
}

function updateAuthAccount(userId: number, username: string, password: string | null | undefined, role: 'admin' | 'coadmin', fullName: string) {
  const existing = selectOne('SELECT id, password_salt FROM auth_accounts WHERE user_id = ?', [userId])

  if (!existing) {
    if (!password) {
      throw new Error('Password wajib diisi untuk role admin atau coadmin')
    }

    createAuthAccount(userId, username, password, role, fullName)
    return
  }

  if (password) {
    const { salt, passwordHash } = hashPassword(password)
    run(
      `UPDATE auth_accounts
       SET username = ?, password_hash = ?, password_salt = ?, role = ?, full_name_snapshot = ?, is_active = 1
       WHERE user_id = ?`,
      [username.trim().toLowerCase(), passwordHash, salt, role, fullName, userId]
    )
    return
  }

  run(
    `UPDATE auth_accounts
     SET username = ?, role = ?, full_name_snapshot = ?, is_active = 1
     WHERE user_id = ?`,
    [username.trim().toLowerCase(), role, fullName, userId]
  )
}

function seedDefaults() {
  const existingSettings = Number(selectOne('SELECT COUNT(*) AS count FROM app_settings')?.count ?? 0)
  if (existingSettings === 0) {
    run('INSERT INTO app_settings (key, value) VALUES (?, ?)', ['raspy_api_base_url', 'http://127.0.0.1:5000'])
    run('INSERT INTO app_settings (key, value) VALUES (?, ?)', ['spreadsheet_csv_url', ''])
    run('INSERT INTO app_settings (key, value) VALUES (?, ?)', ['spreadsheet_enabled', '0'])
    run('INSERT INTO app_settings (key, value) VALUES (?, ?)', ['raspy_mode_endpoint', '/api/device/mode'])
  }

  const authCount = Number(selectOne('SELECT COUNT(*) AS count FROM auth_accounts')?.count ?? 0)
  if (authCount === 0) {
    createAuthAccount(null, 'admin', 'admin123', 'admin', 'System Administrator')
    createAuthAccount(null, 'coadmin', 'coadmin123', 'coadmin', 'Operations CoAdmin')
  }
}

export async function initializeDatabase(storageDir: string, projectRoot: string) {
  if (database) {
    return
  }

  if (!fs.existsSync(storageDir)) {
    fs.mkdirSync(storageDir, { recursive: true })
  }

  databaseFilePath = path.join(storageDir, 'bioadmin.sqlite')

  await loadSqlJs(projectRoot)

  database = fs.existsSync(databaseFilePath)
    ? new SQL.Database(fs.readFileSync(databaseFilePath))
    : new SQL.Database()

  run('PRAGMA foreign_keys = ON')
  run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    role TEXT NOT NULL DEFAULT 'member',
    fingerprint_id INTEGER,
    face_embedding_key TEXT,
    face_embedding_count INTEGER NOT NULL DEFAULT 0,
    face_enrolled INTEGER NOT NULL DEFAULT 0,
    fingerprint_enrolled INTEGER NOT NULL DEFAULT 0,
    registration_date TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'local'
  )`)
  run(`CREATE TABLE IF NOT EXISTS auth_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name_snapshot TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
  )`)
  run(`CREATE TABLE IF NOT EXISTS access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'attendance',
    method TEXT NOT NULL,
    access_status TEXT NOT NULL DEFAULT 'success',
    similarity REAL,
    image_path TEXT,
    source TEXT NOT NULL DEFAULT 'local',
    event_time TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
  )`)
  run(`CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  )`)

  seedDefaults()
  persist()
}

export function getSettings() {
  const rows = selectAll('SELECT key, value FROM app_settings ORDER BY key')
  return rows.reduce<Record<string, string>>((accumulator, row) => {
    accumulator[String(row.key)] = String(row.value)
    return accumulator
  }, {})
}

export function setSetting(key: string, value: string) {
  run(
    `INSERT INTO app_settings (key, value) VALUES (?, ?)
     ON CONFLICT(key) DO UPDATE SET value = excluded.value`,
    [key, value]
  )
  persist()
}

export function verifyLogin(username: string, password: string) {
  const account = selectOne(
    `SELECT a.id, a.user_id, a.username, a.password_hash, a.password_salt, a.role,
            COALESCE(u.full_name, a.full_name_snapshot) AS full_name
     FROM auth_accounts a
     LEFT JOIN users u ON u.id = a.user_id
     WHERE a.username = ? AND a.is_active = 1`,
    [username.trim().toLowerCase()]
  )

  if (!account) {
    return null
  }

  const { passwordHash } = hashPassword(password, String(account.password_salt))
  if (passwordHash !== String(account.password_hash)) {
    return null
  }

  run('UPDATE auth_accounts SET last_login_at = ? WHERE id = ?', [nowIso(), Number(account.id)])
  persist()

  return {
    accountId: Number(account.id),
    userId: account.user_id === null || account.user_id === undefined ? null : Number(account.user_id),
    username: String(account.username),
    fullName: String(account.full_name),
    role: String(account.role) as 'admin' | 'coadmin'
  } satisfies AuthUser
}

export function listUsers() {
  return withDisplayNumbers(selectAll(
    `SELECT u.*, a.username, CASE WHEN a.id IS NULL THEN 0 ELSE 1 END AS has_login
     FROM users u
     LEFT JOIN auth_accounts a ON a.user_id = u.id
     ORDER BY u.id ASC`
  ).map(mapUserRow))
}

export function getUserById(userId: number) {
  return listUsers().find((user) => user.id === userId) ?? null
}

export function getNextUserId() {
  // Follow the remote allocator behaviour: the next user gets MAX(id) + 1.
  const result = selectOne('SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM users')
  return Number(result?.next_id ?? 1)
}

export function createUser(input: CreateUserInput) {
  const fullName = normalizeName(input.fullName)
  if (!fullName) {
    throw new Error('Nama lengkap wajib diisi')
  }

  ensureUniqueFullName(fullName)

  const role = input.role
  const requiresLogin = ensureRoleHasLogin(role)
  const username = input.username?.trim() || null
  const password = input.password?.trim() || null

  if (requiresLogin && (!username || !password)) {
    throw new Error('Username dan password wajib diisi untuk admin atau coadmin')
  }

  const timestamp = nowIso()

  run('BEGIN')
  try {
    if (typeof input.id === 'number') {
      run(
        `INSERT INTO users (id, full_name, role, registration_date, updated_at, source)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [input.id, fullName, role, timestamp, timestamp, input.source ?? 'local']
      )
    } else {
      run(
        `INSERT INTO users (full_name, role, registration_date, updated_at, source)
         VALUES (?, ?, ?, ?, ?)`,
        [fullName, role, timestamp, timestamp, input.source ?? 'local']
      )
    }

    const userId = typeof input.id === 'number'
      ? input.id
      : Number(selectOne('SELECT last_insert_rowid() AS id')?.id ?? 0)
    if (requiresLogin && username && password) {
      createAuthAccount(userId, username, password, role, fullName)
    }

    run('COMMIT')
    persist()
    return getUserById(userId)
  } catch (error) {
    run('ROLLBACK')
    throw normalizeUserPersistenceError(error)
  }
}

export function updateUser(userId: number, input: UpdateUserInput) {
  const existing = getUserById(userId)
  if (!existing) {
    throw new Error('User tidak ditemukan')
  }

  const fullName = normalizeName(input.fullName)
  ensureUniqueFullName(fullName, userId)
  const role = input.role
  const requiresLogin = ensureRoleHasLogin(role)
  const username = input.username?.trim() || existing.username || null
  const password = input.password?.trim() || null

  if (requiresLogin && !username) {
    throw new Error('Username wajib diisi untuk admin atau coadmin')
  }

  run('BEGIN')
  try {
    run('UPDATE users SET full_name = ?, role = ?, updated_at = ? WHERE id = ?', [fullName, role, nowIso(), userId])

    if (requiresLogin && username) {
      updateAuthAccount(userId, username, password, role, fullName)
    } else {
      run('DELETE FROM auth_accounts WHERE user_id = ?', [userId])
    }

    run('COMMIT')
    persist()
    return getUserById(userId)
  } catch (error) {
    run('ROLLBACK')
    throw normalizeUserPersistenceError(error)
  }
}

export function deleteUser(userId: number) {
  run('DELETE FROM users WHERE id = ?', [userId])
  persist()
}

export function markFaceEnrollment(userId: number, embeddingKey: string, embeddingCount: number) {
  run(
    `UPDATE users
     SET face_embedding_key = ?, face_embedding_count = ?, face_enrolled = 1, updated_at = ?
     WHERE id = ?`,
    [embeddingKey, embeddingCount, nowIso(), userId]
  )
  persist()
}

export function markFingerprintEnrollment(userId: number, fingerprintId: number) {
  run(
    `UPDATE users
     SET fingerprint_id = ?, fingerprint_enrolled = 1, updated_at = ?
     WHERE id = ?`,
    [fingerprintId, nowIso(), userId]
  )
  persist()
}

export function getNextFingerprintId() {
  return Number(selectOne('SELECT COALESCE(MAX(fingerprint_id), 0) + 1 AS next_id FROM users')?.next_id ?? 1)
}

export function upsertRemoteUser(remoteUser: {
  id?: number | null
  fullName: string
  fingerprintId?: number | null
  hasFingerprint?: boolean
  faceEnrolled?: boolean
  faceEmbeddingCount?: number
}) {
  const fullName = normalizeName(remoteUser.fullName)
  if (!fullName) {
    return null
  }

  const fingerprintIdProvided = remoteUser.fingerprintId !== undefined
  const fingerprintId = fingerprintIdProvided
    ? remoteUser.fingerprintId === null
      ? null
      : Number(remoteUser.fingerprintId)
    : undefined
  const fingerprintEnrolled = remoteUser.hasFingerprint !== undefined
    ? (remoteUser.hasFingerprint ? 1 : 0)
    : fingerprintIdProvided
      ? (fingerprintId !== null ? 1 : 0)
      : undefined
  const fingerprintEnrolledProvided = fingerprintEnrolled !== undefined

  const existing = remoteUser.id
    ? selectOne('SELECT id FROM users WHERE id = ?', [remoteUser.id])
    : selectOne('SELECT id FROM users WHERE full_name = ?', [fullName])
  const conflictingName = remoteUser.id
    ? selectOne('SELECT id FROM users WHERE full_name = ? AND id <> ?', [fullName, remoteUser.id])
    : null

  if (!existing && conflictingName) {
    return getUserById(Number(conflictingName.id))
  }

  if (!existing) {
    const created = createUser({
      id: remoteUser.id ?? undefined,
      fullName,
      role: 'member',
      source: 'raspy-sync'
    })

    if (!created) {
      return null
    }

    run(
      `UPDATE users
       SET fingerprint_id = ?,
           fingerprint_enrolled = ?,
           face_enrolled = ?,
           face_embedding_count = ?,
           face_embedding_key = CASE WHEN ? = 1 THEN ? ELSE face_embedding_key END,
           updated_at = ?,
           source = 'raspy-sync'
       WHERE id = ?`,
      [
        fingerprintId ?? null,
        fingerprintEnrolled ?? 0,
        remoteUser.faceEnrolled ? 1 : 0,
        remoteUser.faceEmbeddingCount ?? 0,
        remoteUser.faceEnrolled ? 1 : 0,
        fullName,
        nowIso(),
        created.id
      ]
    )
    persist()
    return getUserById(created.id)
  }

  run(
    `UPDATE users
     SET full_name = ?,
         fingerprint_id = CASE WHEN ? = 1 THEN ? ELSE fingerprint_id END,
         fingerprint_enrolled = CASE WHEN ? = 1 THEN ? ELSE fingerprint_enrolled END,
         face_enrolled = ?,
         face_embedding_count = ?,
         face_embedding_key = CASE WHEN ? = 1 THEN ? ELSE face_embedding_key END,
         updated_at = ?,
         source = 'raspy-sync'
     WHERE id = ?`,
    [
      fullName,
      fingerprintIdProvided ? 1 : 0,
      fingerprintId ?? null,
      fingerprintEnrolledProvided ? 1 : 0,
      fingerprintEnrolled ?? 0,
      remoteUser.faceEnrolled ? 1 : 0,
      remoteUser.faceEmbeddingCount ?? 0,
      remoteUser.faceEnrolled ? 1 : 0,
      fullName,
      nowIso(),
      Number(existing.id)
    ]
  )
  persist()
  return getUserById(Number(existing.id))
}

export function recordAccessLog(entry: Omit<AccessLogRecord, 'id'>) {
  run(
    `INSERT INTO access_logs (user_id, full_name, event_type, method, access_status, similarity, image_path, source, event_time)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      entry.userId,
      entry.fullName,
      entry.eventType,
      entry.method,
      entry.accessStatus,
      entry.similarity,
      entry.imagePath,
      entry.source,
      entry.eventTime
    ]
  )
  persist()
}

export function listLocalAccessLogs(limit = 100) {
  return selectAll(
    `SELECT * FROM access_logs
     ORDER BY event_time DESC
     LIMIT ?`,
    [limit]
  ).map((row) => ({
    id: Number(row.id),
    userId: row.user_id === null || row.user_id === undefined ? null : Number(row.user_id),
    fullName: String(row.full_name),
    eventType: String(row.event_type),
    method: String(row.method),
    accessStatus: String(row.access_status),
    similarity: row.similarity === null || row.similarity === undefined ? null : Number(row.similarity),
    imagePath: row.image_path ? String(row.image_path) : null,
    source: String(row.source),
    eventTime: String(row.event_time)
  }))
}