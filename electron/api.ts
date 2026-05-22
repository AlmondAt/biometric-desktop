import cors from 'cors'
import express from 'express'
import fs from 'fs'
import os from 'os'
import path from 'path'
import { spawn, type ChildProcessWithoutNullStreams } from 'child_process'
import {
  createUser,
  deleteUser,
  getNextFingerprintId,
  getNextUserId,
  getSettings,
  getUserById,
  initializeDatabase,
  listLocalAccessLogs,
  listUsers,
  markFaceEnrollment,
  markFingerprintEnrollment,
  recordAccessLog,
  setSetting,
  updateUser,
  upsertRemoteUser,
  verifyLogin,
  type AccessLogRecord,
  type UserRole
} from './database'

const app = express()
app.use(cors())
app.use(express.json({ limit: '50mb' }))

const runtime = {
  server: null as ReturnType<typeof app.listen> | null,
  storageDir: '',
  projectRoot: '',
  resourcesDir: ''
}

const activeTrainingProcesses = new Map<number, ChildProcessWithoutNullStreams>()
const pendingEnrollments = new Map<number, PendingEnrollment>()

type UnifiedLog = Omit<AccessLogRecord, 'id'> & { id: number | string }

interface PendingEnrollment {
  userId: number
  fullName: string
  role: UserRole
  username: string | null
  password: string | null
  faceEmbeddingCount: number
}

interface LogDetailEntry {
  label: string
  value: string
}

type EnrichedUnifiedLog = UnifiedLog & {
  summary?: string
  detailEntries?: LogDetailEntry[]
  employeeId?: string
  domisili?: string
  akses?: string
}

function nowIso() {
  return new Date().toISOString()
}

function normalizeRole(role: unknown): UserRole {
  const value = String(role ?? 'member').toLowerCase()
  if (value === 'admin' || value === 'coadmin') {
    return value
  }
  return 'member'
}

function toPendingUserRecord(pending: PendingEnrollment) {
  return {
    id: pending.userId,
    displayNo: pending.userId,
    fullName: pending.fullName,
    role: pending.role,
    username: pending.username,
    fingerprintId: null,
    faceEmbeddingKey: pending.faceEmbeddingCount > 0 ? pending.fullName : null,
    faceEmbeddingCount: pending.faceEmbeddingCount,
    faceEnrolled: pending.faceEmbeddingCount > 0,
    fingerprintEnrolled: false,
    registrationDate: nowIso(),
    updatedAt: nowIso(),
    hasLogin: Boolean(pending.username),
    source: 'local' as const
  }
}

function getEnrollmentSubject(userId: number) {
  const localUser = getUserById(userId)
  if (localUser) {
    return {
      kind: 'local' as const,
      user: localUser
    }
  }

  const pending = pendingEnrollments.get(userId)
  if (pending) {
    return {
      kind: 'pending' as const,
      pending,
      user: toPendingUserRecord(pending)
    }
  }

  return null
}

function getEmbeddingsPath() {
  return path.join(runtime.storageDir, 'embeddings.pkl')
}

function getTempDir() {
  return path.join(runtime.storageDir, '.temp')
}

function getBundledResourcePath(...segments: string[]) {
  if (process.env.VITE_DEV_SERVER_URL) {
    return path.join(runtime.projectRoot, ...segments)
  }

  return path.join(runtime.resourcesDir, 'app-resources', ...segments)
}

function ensureTempDir() {
  const tempDir = getTempDir()
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true })
  }
  return tempDir
}

function resolvePythonCommand() {
  const candidates = [
    process.env.PYTHON_PATH,
    'C:\\Users\\Den\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
  ].filter(Boolean) as string[]

  for (const candidate of candidates) {
    if (path.isAbsolute(candidate) && fs.existsSync(candidate)) {
      return { command: candidate, prefixArgs: [] as string[] }
    }
  }

  if (process.platform === 'win32') {
    return { command: 'py', prefixArgs: ['-3'] }
  }

  return { command: 'python3', prefixArgs: [] as string[] }
}

interface RunPythonScriptOptions {
  timeoutMs?: number
  onSpawn?: (child: ChildProcessWithoutNullStreams) => void
  onSettled?: () => void
}

interface PythonRunner {
  command: string
  prefixArgs: string[]
  workingDirectory?: string
}

function resolveBundledPythonInterpreter(scriptPath: string): PythonRunner | null {
  const executableName = process.platform === 'win32' ? 'python.exe' : 'python3'
  const executablePath = getBundledResourcePath('python-runtime', 'python', executableName)

  if (!fs.existsSync(executablePath)) {
    return null
  }

  return {
    command: executablePath,
    prefixArgs: [scriptPath],
    workingDirectory: path.dirname(scriptPath)
  }
}

function resolveBundledPythonCommand(scriptPath: string): PythonRunner | null {
  const scriptName = path.parse(scriptPath).name
  const bundledDir = getBundledResourcePath('python-runtime', scriptName)
  const executableName = process.platform === 'win32' ? `${scriptName}.exe` : scriptName
  const executablePath = path.join(bundledDir, executableName)

  if (!fs.existsSync(executablePath)) {
    return null
  }

  return {
    command: executablePath,
    prefixArgs: [],
    workingDirectory: bundledDir
  }
}

function resolvePythonRunner(scriptPath: string) {
  const bundledInterpreter = resolveBundledPythonInterpreter(scriptPath)
  if (bundledInterpreter) {
    return bundledInterpreter
  }

  const bundledRunner = resolveBundledPythonCommand(scriptPath)
  if (bundledRunner) {
    return bundledRunner
  }

  const defaultRunner = resolvePythonCommand()
  return {
    ...defaultRunner,
    prefixArgs: [...defaultRunner.prefixArgs, scriptPath]
  }
}

function runPythonScript(scriptPath: string, args: string[], cwd?: string, options: RunPythonScriptOptions = {}) {
  const { timeoutMs = 60_000, onSpawn, onSettled } = options
  const python = resolvePythonRunner(scriptPath)
  return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
    const spawnArgs = [...python.prefixArgs, ...args]
    let finished = false
    let timedOut = false
    
    const child = spawn(python.command, spawnArgs, {
      cwd: python.workingDirectory ?? cwd,
      shell: false
    })

    onSpawn?.(child)

    let stdout = ''
    let stderr = ''

    const timeoutHandle = timeoutMs > 0
      ? setTimeout(() => {
          timedOut = true
          child.kill('SIGTERM')
        }, timeoutMs)
      : null

    const settle = (callback: () => void) => {
      if (finished) {
        return
      }

      finished = true
      if (timeoutHandle) {
        clearTimeout(timeoutHandle)
      }
      onSettled?.()
      callback()
    }

    const settleError = (message: string) => {
      settle(() => reject(new Error(message)))
    }

    const settleSuccess = () => {
      settle(() => resolve({ stdout, stderr }))
    }

    child.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    child.stderr.on('data', (data) => {
      stderr += data.toString()
    })

      child.on('error', (error) => settleError(error.message))
      child.on('close', (code, signal) => {
      if (code === 0) {
        settleSuccess()
        return
      }

      const output = (stderr || stdout).trim() || 'no output'

      if (timedOut) {
          settleError(`Python process timed out after ${timeoutMs / 1000}s: ${output}`)
          return
        }

      if (signal === 'SIGTERM') {
        settleError(`Python process cancelled: ${output}`)
        return
      }

        if (code === null) {
          settleError(`Python process terminated unexpectedly${signal ? ` (${signal})` : ''}: ${output}`)
          return
        }

        settleError(`[exit ${code}] ${output}`)
    })
  })
}

async function fetchJson(url: string, init?: RequestInit, timeoutMs = 4000) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const result = await fetch(url, { ...init, signal: controller.signal })
    if (!result.ok) {
      throw new Error(`${result.status} ${result.statusText}`)
    }
    return await result.json()
  } finally {
    clearTimeout(timer)
  }
}

async function postJson(url: string, body: Record<string, unknown>, timeoutMs = 6000) {
  return fetchJson(
    url,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    },
    timeoutMs
  )
}

function parseCsv(text: string, delimiter = ',') {
  const rows: string[][] = []
  let currentCell = ''
  let currentRow: string[] = []
  let inQuotes = false

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    const nextChar = text[index + 1]

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        currentCell += '"'
        index += 1
      } else {
        inQuotes = !inQuotes
      }
      continue
    }

    if (char === delimiter && !inQuotes) {
      currentRow.push(currentCell)
      currentCell = ''
      continue
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') {
        index += 1
      }

      currentRow.push(currentCell)
      rows.push(currentRow)
      currentRow = []
      currentCell = ''
      continue
    }

    currentCell += char
  }

  if (currentCell || currentRow.length > 0) {
    currentRow.push(currentCell)
    rows.push(currentRow)
  }

  return rows.filter((row) => row.some((cell) => cell.trim().length > 0))
}

function autoDetectDelimiter(text: string): string {
  const firstLine = text.split(/\r?\n/)[0] ?? ''
  const tabCount = (firstLine.match(/\t/g) ?? []).length
  const commaCount = (firstLine.match(/,/g) ?? []).length
  return tabCount > commaCount ? '\t' : ','
}

function normalizeSpreadsheetHeader(header: string) {
  return header.trim().toLowerCase().replace(/\s+/g, ' ')
}

function pickFirstValue(record: Record<string, string>, keys: string[]) {
  for (const key of keys) {
    const value = record[normalizeSpreadsheetHeader(key)]?.trim()
    if (value) {
      return value
    }
  }

  return ''
}

function toDisplayLabel(value: string) {
  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function buildSpreadsheetSummary(record: Record<string, string>) {
  const parts = [
    pickFirstValue(record, ['status']),
    pickFirstValue(record, ['akses', 'access']) ? `Akses ${pickFirstValue(record, ['akses', 'access'])}` : '',
    pickFirstValue(record, ['total shift', 'total_shift', 'totalshift'])
      ? `Total shift ${pickFirstValue(record, ['total shift', 'total_shift', 'totalshift'])}`
      : '',
    pickFirstValue(record, ['domisili'])
  ].filter(Boolean)

  return parts.join(' • ')
}

function buildSpreadsheetDetailEntries(headers: string[], record: Record<string, string>) {
  const hiddenKeys = new Set([
    'name',
    'nama',
    'tanggal',
    'date',
    'id',
    'status',
    'method',
    'metode',
    'event',
    'event type',
    'event_type',
    'timestamp',
    'datetime',
    'time',
    'waktu',
    'source'
  ])

  return headers.reduce<LogDetailEntry[]>((entries, header) => {
    const key = normalizeSpreadsheetHeader(header)
    const value = record[key]?.trim()
    if (!value || hiddenKeys.has(key)) {
      return entries
    }

    entries.push({
      label: toDisplayLabel(header),
      value
    })
    return entries
  }, [])
}

function toUnifiedLog(payload: Partial<EnrichedUnifiedLog> & { fullName?: string; name?: string; timestamp?: string }) {
  const fullName = String(payload.fullName ?? payload.name ?? 'Unknown User')
  const eventTime = String(payload.eventTime ?? payload.timestamp ?? nowIso())

  return {
    id: payload.id ?? `${fullName}-${eventTime}`,
    userId: payload.userId ?? null,
    fullName,
    eventType: payload.eventType ?? 'attendance',
    method: payload.method ?? 'unknown',
    accessStatus: payload.accessStatus ?? 'success',
    similarity: payload.similarity ?? null,
    imagePath: payload.imagePath ?? null,
    source: payload.source ?? 'local',
    eventTime,
    summary: payload.summary,
    detailEntries: payload.detailEntries,
    employeeId: payload.employeeId,
    domisili: payload.domisili,
    akses: payload.akses
  }
}

function sortLogs(logs: UnifiedLog[]) {
  return [...logs].sort((left, right) => new Date(right.eventTime).getTime() - new Date(left.eventTime).getTime())
}

function dedupeLogs(logs: UnifiedLog[]) {
  const seen = new Set<string>()
  return logs.filter((log) => {
    const key = `${log.fullName}-${log.eventTime}-${log.method}-${log.source}`
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  })
}

async function getRaspyStatus() {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()

  if (!baseUrl) {
    return { online: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  try {
    const data = await fetchJson(`${baseUrl}/api/health`)
    return { online: true, message: data.message ?? data.status ?? 'Online', payload: data }
  } catch (error) {
    return {
      online: false,
      message: error instanceof Error ? error.message : 'Tidak dapat terhubung ke Raspberry Pi'
    }
  }
}

async function notifyRaspyMode(mode: string, extraPayload: Record<string, unknown> = {}) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  const endpoint = settings.raspy_mode_endpoint?.trim() || '/api/device/mode'

  if (!baseUrl) {
    return { delivered: false, mode, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  try {
    const data = await fetchJson(`${baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, ...extraPayload })
    })

    return { delivered: true, mode, message: data.message ?? 'Signal terkirim', payload: data }
  } catch (error) {
    return {
      delivered: false,
      mode,
      message: error instanceof Error ? error.message : 'Signal gagal dikirim'
    }
  }
}

async function loadRemoteUsers() {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return [] as Array<{ id?: number | null; fullName: string; fingerprintId?: number | null; hasFingerprint?: boolean; faceEnrolled: boolean; faceEmbeddingCount: number }>
  }

  try {
    const data = await fetchJson(`${baseUrl}/api/users`)
    const records = Array.isArray(data) ? data : Array.isArray(data.users) ? data.users : []
    return records
      .map((row: Record<string, unknown>) => ({
        id: row.id === null || row.id === undefined
          ? row.user_id === null || row.user_id === undefined
            ? null
            : Number(row.user_id)
          : Number(row.id),
        fullName: String(row.full_name ?? row.name ?? row.user_name ?? ''),
        fingerprintId: Object.prototype.hasOwnProperty.call(row, 'fingerprint_id')
          ? row.fingerprint_id === null || row.fingerprint_id === undefined
            ? null
            : Number(row.fingerprint_id)
          : undefined,
        hasFingerprint: Object.prototype.hasOwnProperty.call(row, 'has_fingerprint')
          ? Boolean(row.has_fingerprint)
          : row.fingerprint_id !== null && row.fingerprint_id !== undefined,
        faceEnrolled: Number(row.embedding_count ?? row.face_enrolled ?? row.has_face ?? 0) > 0 || Boolean(row.face_embedding_path),
        faceEmbeddingCount: Number(row.embedding_count ?? row.face_embedding_count ?? (row.face_embedding_path ? 1 : 0))
      }))
      .filter((row: { fullName: string }) => row.fullName)
  } catch {
    return []
  }
}

async function syncUsersFromRaspy() {
  const remoteUsers = await loadRemoteUsers()
  for (const remoteUser of remoteUsers) {
    upsertRemoteUser(remoteUser)
  }
  return listUsers()
}

function encodeFileToBase64(filePath: string) {
  return fs.readFileSync(filePath).toString('base64')
}

async function createRemoteUser(fullName: string) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return { created: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  try {
    const data = await postJson(`${baseUrl}/api/add-user`, {
      name: fullName,
      full_name: fullName
    })

    return {
      created: true,
      message: String(data.message ?? 'User berhasil dibuat di Raspberry Pi'),
      remoteId: data.id ?? data.user_id ?? data.user?.id ?? data.data?.id ?? null,
      payload: data
    }
  } catch (error) {
    return {
      created: false,
      message: error instanceof Error ? error.message : 'Gagal membuat user di Raspberry Pi'
    }
  }
}

async function deleteRemoteUser(userId: number) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return { deleted: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  try {
    const data = await fetchJson(`${baseUrl}/api/users/${userId}`, { method: 'DELETE' })
    return {
      deleted: true,
      message: String(data.message ?? 'User berhasil dihapus di Raspberry Pi'),
      payload: data
    }
  } catch (error) {
    return {
      deleted: false,
      message: error instanceof Error ? error.message : 'Gagal menghapus user di Raspberry Pi'
    }
  }
}

async function updateRemoteUser(userId: number, fullName: string) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return { updated: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  const payload = {
    user_id: userId,
    full_name: fullName,
    name: fullName
  }

  try {
    const data = await fetchJson(`${baseUrl}/api/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    return {
      updated: true,
      message: String(data.message ?? 'User berhasil diperbarui di Raspberry Pi'),
      payload: data
    }
  } catch {
    try {
      const data = await postJson(`${baseUrl}/api/update-user`, payload)
      return {
        updated: true,
        message: String(data.message ?? 'User berhasil diperbarui di Raspberry Pi'),
        payload: data
      }
    } catch (error) {
      return {
        updated: false,
        message: error instanceof Error ? error.message : 'Gagal memperbarui user di Raspberry Pi'
      }
    }
  }
}

async function syncRemoteFaceEmbeddings(userId: number, fullName: string, embeddingsPath: string) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return { synced: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  try {
    const data = await postJson(`${baseUrl}/api/enroll-face`, {
      user_id: userId,
      full_name: fullName,
      embeddings_file_base64: encodeFileToBase64(embeddingsPath)
    }, 30000)

    return {
      synced: true,
      message: String(data.message ?? 'Embeddings berhasil dikirim ke Raspberry Pi'),
      payload: data
    }
  } catch (error) {
    return {
      synced: false,
      message: error instanceof Error ? error.message : 'Gagal mengirim embeddings ke Raspberry Pi'
    }
  }
}

async function enrollRemoteFingerprint(userId: number, fullName: string) {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return { enrolled: false, message: 'Raspberry Pi URL belum dikonfigurasi' }
  }

  const payload = {
    id: userId,
    user_id: userId,
    name: fullName,
    full_name: fullName
  }
  const candidates = [
    `${baseUrl}/api/enroll-fingerprint`,
    `${baseUrl}/api/fingerprint/enroll`,
    `${baseUrl}/api/users/${userId}/fingerprint`
  ]

  let lastErrorMessage = 'Gagal registrasi fingerprint di Raspberry Pi'

  for (const endpoint of candidates) {
    try {
      const data = await postJson(endpoint, payload, 30000)

      return {
        enrolled: true,
        message: String(data.message ?? 'Fingerprint berhasil diregistrasi'),
        fingerprintId: data.fingerprint_id ?? data.slot ?? data.data?.fingerprint_id ?? null,
        payload: data
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Gagal registrasi fingerprint di Raspberry Pi'
      lastErrorMessage = message

      if (!/404/i.test(message)) {
        break
      }
    }
  }

  return {
    enrolled: false,
    message: /404/i.test(lastErrorMessage)
      ? 'Endpoint fingerprint di Raspberry Pi belum tersedia atau URL endpoint-nya berbeda.'
      : lastErrorMessage
  }
}

function normalizeSpreadsheetTimestamp(dateValue: string, timeValue: string, explicitTimestamp: string) {
  if (explicitTimestamp) {
    return explicitTimestamp.replace(' ', 'T')
  }

  if (!dateValue) {
    return nowIso()
  }

  // dateValue may already carry time: "2026-04-15 09:42:36"
  if (/^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}/.test(dateValue)) {
    return dateValue.replace(' ', 'T')
  }

  return `${dateValue}T${timeValue || '00:00:00'}`
}

function isSubHeaderRow(row: string[]) {
  // Sub-header row: first 3 cells empty (Tanggal/ID/Nama), and contains "Ket" or "Mutu"
  const firstThreeEmpty = row.slice(0, 3).every((cell) => !cell.trim())
  const hasSubLabels = row.some((cell) => {
    const normalized = cell.trim().toLowerCase()
    return normalized === 'ket' || normalized === 'mutu'
  })
  return firstThreeEmpty && hasSubLabels
}

function buildCombinedHeaders(mainHeaders: string[], subHeaders: string[]) {
  let lastMain = ''
  return mainHeaders.map((main, i) => {
    const m = main.trim()
    const s = subHeaders[i]?.trim() ?? ''
    if (m) {
      lastMain = m
    }

    if (s) {
      return `${lastMain} ${s}`.trim()
    }

    return m
  })
}

async function loadSpreadsheetLogs() {
  const settings = getSettings()
  if (settings.spreadsheet_enabled !== '1' || !settings.spreadsheet_csv_url?.trim()) {
    return [] as EnrichedUnifiedLog[]
  }

  try {
    const response = await fetch(settings.spreadsheet_csv_url)
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`)
    }

    const text = await response.text()
    const delimiter = autoDetectDelimiter(text)
    const rows = parseCsv(text, delimiter)

    // Structure (from Apps Script):
    // Row 0: main headers  (Tanggal, ID, Nama, Shift1..., Domisili, Status, Akses, Total Shift)
    // Row 1: sub-headers   (empty, empty, empty, Ket, Mutu, Ket, Mutu, ...)
    // Row 2+: data rows
    // Data always starts at row 3 in the sheet (Math.max(lastRow+1, 3))
    // Column indices (0-based):
    //   0=Tanggal, 1=ID, 2=Nama, 3-12=Shift 1-5 Ket/Mutu, 13=Domisili, 14=Status, 15=Akses, 16=Total Shift
    const dataRows = rows.slice(2) // always skip 2 header rows

    return dataRows
      .filter((row) => row.some((cell) => cell.trim().length > 0))
      .map((row, index) => {
        const tanggal = row[0]?.trim() ?? ''
        const id      = row[1]?.trim() ?? ''
        const nama    = row[2]?.trim() ?? ''
        const domisili = row[13]?.trim() ?? ''
        const status   = row[14]?.trim() ?? ''
        const akses    = row[15]?.trim() ?? ''

        const timestamp = normalizeSpreadsheetTimestamp(tanggal, '', '')

        return toUnifiedLog({
          id: `sheet-${index}-${id || timestamp}`,
          fullName: nama || 'Unknown User',
          method: 'spreadsheet',
          accessStatus: status || 'Registered',
          eventType: 'attendance',
          source: 'spreadsheet',
          timestamp,
          employeeId: id || undefined,
          domisili: domisili || undefined,
          akses: akses || undefined,
        })
      })
  } catch {
    return []
  }
}

async function loadRemoteLogs() {
  const settings = getSettings()
  const baseUrl = settings.raspy_api_base_url?.trim()
  if (!baseUrl) {
    return [] as UnifiedLog[]
  }

  const endpoints = [`${baseUrl}/api/logs`]
  for (const endpoint of endpoints) {
    try {
      const data = await fetchJson(endpoint)
      const records = Array.isArray(data) ? data : Array.isArray(data.logs) ? data.logs : []
      return records.map((row: Record<string, unknown>, index: number) => toUnifiedLog({
        id: `raspy-${index}-${row.timestamp ?? row.event_time ?? index}`,
        fullName: String(row.name ?? row.full_name ?? 'Unknown User'),
        method: String(row.method ?? row.metode ?? 'biometrik'),
        accessStatus: String(row.status ?? 'success'),
        eventType: String(row.event_type ?? 'attendance'),
        similarity: row.similarity === null || row.similarity === undefined ? null : Number(row.similarity),
        source: 'raspy',
        timestamp: String(row.timestamp ?? row.event_time ?? nowIso())
      }))
    } catch {
      continue
    }
  }

  return []
}

async function loadUnifiedLogs(limit = 200) {
  const settings = getSettings()
  if (settings.spreadsheet_enabled === '1') {
    const spreadsheetLogs = await loadSpreadsheetLogs()
    return sortLogs(dedupeLogs(spreadsheetLogs)).slice(0, limit)
  }

  const remoteLogs = await loadRemoteLogs()
  const localLogs = listLocalAccessLogs(limit).map((log) => toUnifiedLog(log))
  return sortLogs(dedupeLogs([...remoteLogs, ...localLogs])).slice(0, limit)
}

async function runRaspyDiagnostics() {
  const settings = getSettings()
  const health = await getRaspyStatus()
  const users = settings.raspy_api_base_url?.trim()
    ? await fetchJson(`${settings.raspy_api_base_url.trim()}/api/users`)
        .then((payload) => {
          const records = Array.isArray(payload) ? payload : Array.isArray(payload.users) ? payload.users : []
          return { ok: true, count: records.length, message: undefined as string | undefined }
        })
        .catch((error) => ({ ok: false, count: 0, message: error instanceof Error ? error.message : 'Gagal membaca user' }))
    : { ok: false, count: 0, message: 'Raspberry Pi URL belum dikonfigurasi' }

  const logs = settings.raspy_api_base_url?.trim()
    ? await fetchJson(`${settings.raspy_api_base_url.trim()}/api/logs`)
        .then((payload) => {
          const records = Array.isArray(payload) ? payload : Array.isArray(payload.logs) ? payload.logs : []
          return { ok: true, count: records.length, message: undefined as string | undefined }
        })
        .catch((error) => ({ ok: false, count: 0, message: error instanceof Error ? error.message : 'Gagal membaca logs' }))
    : { ok: false, count: 0, message: 'Raspberry Pi URL belum dikonfigurasi' }

  const modeRead = settings.raspy_api_base_url?.trim()
    ? await fetchJson(`${settings.raspy_api_base_url.trim()}${settings.raspy_mode_endpoint?.trim() || '/api/device/mode'}`)
        .then((payload) => ({ ok: true, payload }))
        .catch((error) => ({ ok: false, message: error instanceof Error ? error.message : 'Gagal membaca mode device' }))
    : { ok: false, message: 'Raspberry Pi URL belum dikonfigurasi' }

  const modeWrite = await notifyRaspyMode('idle', {
    message: 'desktop diagnostics'
  })

  return {
    baseUrl: settings.raspy_api_base_url?.trim() || '',
    checks: {
      health: {
        ok: health.online,
        message: health.message
      },
      users: {
        ok: users.ok,
        count: users.count,
        message: users.message
      },
      logs: {
        ok: logs.ok,
        count: logs.count,
        message: logs.message
      },
      deviceModeRead: modeRead,
      deviceModeWrite: {
        ok: modeWrite.delivered,
        message: modeWrite.message
      }
    }
  }
}

function parseTrainingResult(stdout: string) {
  const lines = stdout.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  for (const line of lines.reverse()) {
    if (!line.startsWith('{')) {
      continue
    }

    try {
      const payload = JSON.parse(line) as { total: number; embeddingKey: string; added: number }
      if (typeof payload.total === 'number') {
        return payload
      }
    } catch {
      continue
    }
  }

  return null
}

app.post('/api/auth/login', (request, response) => {
  const { username, password } = request.body ?? {}
  if (!username || !password) {
    response.status(400).json({ success: false, message: 'Username dan password wajib diisi' })
    return
  }

  const user = verifyLogin(String(username), String(password))
  if (!user) {
    response.status(401).json({ success: false, message: 'Username atau password salah' })
    return
  }

  response.json({ success: true, user })
})

app.post('/api/auth/logout', (_request, response) => {
  response.json({ success: true })
})

app.get('/api/dashboard', async (_request, response) => {
  try {
    const users = await syncUsersFromRaspy()
    const logs = await loadUnifiedLogs(20)
    const raspyStatus = await getRaspyStatus()
    const today = new Date().toISOString().slice(0, 10)

    response.json({
      success: true,
      metrics: {
        totalUsers: users.length,
        attendanceToday: logs.filter((log) => log.eventTime.slice(0, 10) === today).length,
        systemStatus: raspyStatus.online ? 'online' : 'offline'
      },
      recentActivity: logs.slice(0, 8),
      systemStatusMessage: raspyStatus.message,
      integration: {
        spreadsheetEnabled: getSettings().spreadsheet_enabled === '1'
      }
    })
  } catch (error) {
    response.status(500).json({ success: false, message: error instanceof Error ? error.message : 'Gagal memuat dashboard' })
  }
})

app.get('/api/users', async (_request, response) => {
  try {
    response.json({ success: true, users: await syncUsersFromRaspy() })
  } catch (error) {
    response.status(500).json({ success: false, message: error instanceof Error ? error.message : 'Gagal memuat user' })
  }
})

app.get('/api/users/next-id', (_request, response) => {
  void loadRemoteUsers()
    .then((users) => {
      let nextId: number
      if (users.length) {
        nextId = users.reduce((highestId, user: { id?: number | null }) => {
          const currentId = Number(user.id ?? 0)
          return Number.isFinite(currentId) && currentId > highestId ? currentId : highestId
        }, 0) + 1
      } else {
        nextId = getNextUserId()
      }
      response.json({ success: true, nextId, displayNo: nextId })
    })
    .catch(() => {
      const nextId = getNextUserId()
      response.json({ success: true, nextId, displayNo: nextId })
    })
})

app.post('/api/users', (request, response) => {
  try {
    const user = createUser({
      fullName: String(request.body.fullName ?? ''),
      role: normalizeRole(request.body.role),
      username: request.body.username ? String(request.body.username) : null,
      password: request.body.password ? String(request.body.password) : null,
      source: 'local'
    })
    response.status(201).json({ success: true, user })
  } catch (error) {
    response.status(400).json({ success: false, message: error instanceof Error ? error.message : 'Gagal menambah user' })
  }
})

// Endpoint khusus untuk tambah user dengan ID tertentu (untuk fix sequence issue)
app.post('/api/users/add-with-id', (request, response) => {
  try {
    const userId = Number(request.body.id)
    const fullName = String(request.body.fullName ?? '')

    if (!fullName) {
      response.status(400).json({ success: false, message: 'Nama lengkap diperlukan' })
      return
    }

    if (!Number.isFinite(userId) || userId < 1) {
      response.status(400).json({ success: false, message: 'ID harus berupa angka positif' })
      return
    }

    // Check jika ID sudah ada
    const existing = getUserById(userId)
    if (existing) {
      response.status(400).json({ success: false, message: `User dengan ID ${userId} sudah ada` })
      return
    }

    const user = createUser({
      id: userId,
      fullName,
      role: normalizeRole(request.body.role ?? 'member'),
      username: request.body.username ? String(request.body.username) : null,
      password: request.body.password ? String(request.body.password) : null,
      source: request.body.source ?? 'local'
    })

    response.status(201).json({
      success: true,
      user,
      message: `✅ User "${fullName}" berhasil ditambahkan dengan ID ${userId}`
    })
  } catch (error) {
    response.status(400).json({
      success: false,
      message: error instanceof Error ? error.message : 'Gagal menambah user'
    })
  }
})

app.put('/api/users/:id', async (request, response) => {
  const userId = Number(request.params.id)
  const existing = getUserById(userId)
  if (!existing) {
    response.status(404).json({ success: false, message: 'User tidak ditemukan' })
    return
  }

  try {
    const nextFullName = String(request.body.fullName ?? existing.fullName)
    const remote = await updateRemoteUser(userId, nextFullName)
    if (!remote.updated) {
      response.status(502).json({ success: false, message: remote.message })
      return
    }

    const updated = updateUser(userId, {
      fullName: nextFullName,
      role: normalizeRole(request.body.role ?? existing.role),
      username: request.body.username ? String(request.body.username) : existing.username,
      password: request.body.password ? String(request.body.password) : null
    })

    if (existing.faceEmbeddingKey && updated && existing.fullName !== updated.fullName) {
      const embeddingScript = getBundledResourcePath('embedding_extractor', 'embedding_store.py')
      await runPythonScript(embeddingScript, ['rename', getEmbeddingsPath(), existing.faceEmbeddingKey, updated.fullName], path.dirname(embeddingScript))
      markFaceEnrollment(userId, updated.fullName, existing.faceEmbeddingCount)
    }

    response.json({ success: true, user: getUserById(userId), remote })
  } catch (error) {
    response.status(400).json({ success: false, message: error instanceof Error ? error.message : 'Gagal memperbarui user' })
  }
})

app.delete('/api/users/:id', async (request, response) => {
  const userId = Number(request.params.id)
  const user = getUserById(userId)
  if (!user) {
    response.status(404).json({ success: false, message: 'User tidak ditemukan' })
    return
  }

  try {
    const remote = await deleteRemoteUser(userId)
    if (!remote.deleted) {
      response.status(502).json({ success: false, message: remote.message })
      return
    }

    if (user.faceEmbeddingKey) {
      const embeddingScript = getBundledResourcePath('embedding_extractor', 'embedding_store.py')
      await runPythonScript(embeddingScript, ['delete', getEmbeddingsPath(), user.faceEmbeddingKey], path.dirname(embeddingScript))
    }

    deleteUser(userId)
    response.json({ success: true, remote })
  } catch (error) {
    response.status(400).json({ success: false, message: error instanceof Error ? error.message : 'Gagal menghapus user' })
  }
})

app.post('/api/enrollment/prepare', async (request, response) => {
  try {
    const fullName = String(request.body.fullName ?? '')
    const remote = await createRemoteUser(fullName)
    if (!remote.created) {
      response.status(502).json({ success: false, message: remote.message })
      return
    }

    const remoteId = remote.created && remote.remoteId !== null && remote.remoteId !== undefined
      ? Number(remote.remoteId)
      : undefined

    if (!Number.isFinite(remoteId)) {
      response.status(502).json({ success: false, message: 'Raspberry Pi tidak mengembalikan ID user baru' })
      return
    }

    const pendingEnrollment: PendingEnrollment = {
      userId: remoteId,
      fullName,
      role: normalizeRole(request.body.role),
      username: request.body.username ? String(request.body.username) : null,
      password: request.body.password ? String(request.body.password) : null,
      faceEmbeddingCount: 0
    }
    pendingEnrollments.set(remoteId, pendingEnrollment)

    const device = await notifyRaspyMode('enrollment', {
      stage: 'start',
      userId: pendingEnrollment.userId,
      fullName: pendingEnrollment.fullName
    })

    response.status(201).json({ success: true, user: toPendingUserRecord(pendingEnrollment), device, remote })
  } catch (error) {
    response.status(400).json({ success: false, message: error instanceof Error ? error.message : 'Gagal memulai enrollment' })
  }
})

app.post('/api/enrollment/face', async (request, response) => {
  const userId = Number(request.body.userId)
  const enrollmentSubject = getEnrollmentSubject(userId)
  const photos = Array.isArray(request.body.photos) ? request.body.photos : []

  if (!enrollmentSubject || photos.length === 0) {
    response.status(400).json({ success: false, message: 'User dan foto wajib tersedia' })
    return
  }

  const user = enrollmentSubject.user

  ensureTempDir()
  const trainingScript = getBundledResourcePath('embedding_extractor', 'training_api.py')
  const payloadPath = path.join(getTempDir(), `training-${Date.now()}-${userId}.json`)

  try {
    await notifyRaspyMode('capture-face', { userId, fullName: user.fullName })
    fs.writeFileSync(payloadPath, JSON.stringify({
      embeddingKey: user.fullName,
      fullName: user.fullName,
      userId,
      photos,
      embeddingsPath: getEmbeddingsPath(),
      replaceExisting: Boolean(request.body.replaceExisting || user.faceEnrolled)
    }))

    await notifyRaspyMode('training-face', { userId, fullName: user.fullName })
    const result = await runPythonScript(trainingScript, [payloadPath], path.dirname(trainingScript), {
      timeoutMs: 10 * 60_000,
      onSpawn: (child) => {
        activeTrainingProcesses.set(userId, child)
      },
      onSettled: () => {
        activeTrainingProcesses.delete(userId)
      }
    })
    const trainingPayload = parseTrainingResult(result.stdout)
    const totalEmbeddings = trainingPayload?.total ?? user.faceEmbeddingCount
    const skipFingerprint = Boolean(request.body.skipFingerprint)

    const remoteFaceSync = await syncRemoteFaceEmbeddings(userId, user.fullName, getEmbeddingsPath())
    if (!remoteFaceSync.synced) {
      response.status(502).json({ success: false, message: remoteFaceSync.message })
      return
    }

    if (enrollmentSubject.kind === 'local') {
      markFaceEnrollment(userId, user.fullName, totalEmbeddings)
    } else {
      pendingEnrollments.set(userId, {
        ...enrollmentSubject.pending,
        faceEmbeddingCount: totalEmbeddings
      })
    }

    const nextDeviceSignal = skipFingerprint
      ? await notifyRaspyMode('idle', { userId, fullName: user.fullName })
      : await notifyRaspyMode('waiting-fingerprint', { userId, fullName: user.fullName })

    const responseUser = enrollmentSubject.kind === 'local'
      ? getUserById(userId)
      : toPendingUserRecord(pendingEnrollments.get(userId) ?? enrollmentSubject.pending)

    response.json({
      success: true,
      user: responseUser,
      training: {
        totalEmbeddings,
        output: result.stdout
      },
      remote: remoteFaceSync,
      device: nextDeviceSignal,
      nextStep: skipFingerprint ? 'done' : 'fingerprint'
    })
  } catch (error) {
    response.status(500).json({ success: false, message: error instanceof Error ? error.message : 'Training wajah gagal' })
  } finally {
    if (fs.existsSync(payloadPath)) {
      fs.unlinkSync(payloadPath)
    }
  }
})

app.post('/api/enrollment/fingerprint', async (request, response) => {
  const userId = Number(request.body.userId)
  const enrollmentSubject = getEnrollmentSubject(userId)
  if (!enrollmentSubject) {
    response.status(404).json({ success: false, message: 'User tidak ditemukan' })
    return
  }

  const user = enrollmentSubject.user

  const modeSignal = await notifyRaspyMode('scan-fingerprint', { userId, fullName: user.fullName })
  const remoteEnrollment = await enrollRemoteFingerprint(userId, user.fullName)
  const remoteFingerprintId = Number(remoteEnrollment.fingerprintId ?? (modeSignal as { payload?: { fingerprint_id?: number } }).payload?.fingerprint_id ?? NaN)
  if (!remoteEnrollment.enrolled && !Number.isFinite(remoteFingerprintId)) {
    response.status(502).json({ success: false, message: remoteEnrollment.message })
    return
  }
  const fingerprintId = Number.isFinite(remoteFingerprintId) ? remoteFingerprintId : getNextFingerprintId()

  if (enrollmentSubject.kind === 'pending') {
    const createdUser = createUser({
      id: enrollmentSubject.pending.userId,
      fullName: enrollmentSubject.pending.fullName,
      role: enrollmentSubject.pending.role,
      username: enrollmentSubject.pending.username,
      password: enrollmentSubject.pending.password,
      source: 'local'
    })
    if (!createdUser) {
      response.status(500).json({ success: false, message: 'Gagal menyimpan user baru setelah fingerprint selesai' })
      return
    }

    if (enrollmentSubject.pending.faceEmbeddingCount > 0) {
      markFaceEnrollment(userId, enrollmentSubject.pending.fullName, enrollmentSubject.pending.faceEmbeddingCount)
    }
    pendingEnrollments.delete(userId)
  }

  markFingerprintEnrollment(userId, fingerprintId)
  const idleSignal = await notifyRaspyMode('idle', { userId, fullName: user.fullName })

  response.json({
    success: true,
    simulated: !Number.isFinite(remoteFingerprintId),
    fingerprintId,
    user: getUserById(userId),
    device: modeSignal,
    remote: remoteEnrollment,
    idleSignal
  })
})

app.post('/api/enrollment/cancel', async (request, response) => {
  const userId = Number(request.body.userId)
  const user = Number.isFinite(userId) ? getUserById(userId) : null
  const pending = Number.isFinite(userId) ? pendingEnrollments.get(userId) : null
  const fullName = typeof request.body.fullName === 'string' && request.body.fullName.trim()
    ? String(request.body.fullName).trim()
    : user?.fullName ?? pending?.fullName

  const activeTraining = Number.isFinite(userId) ? activeTrainingProcesses.get(userId) : null
  if (activeTraining) {
    activeTraining.kill('SIGTERM')
  }

  if (!user && pending && Number.isFinite(userId)) {
    await deleteRemoteUser(userId)
    pendingEnrollments.delete(userId)
  }

  const idleSignal = await notifyRaspyMode('idle', {
    stage: 'cancel',
    userId: Number.isFinite(userId) ? userId : undefined,
    fullName
  })

  response.json({
    success: true,
    device: idleSignal
  })
})

app.get('/api/logs', async (request, response) => {
  try {
    const limit = Number(request.query.limit ?? 200)
    response.json({ success: true, logs: await loadUnifiedLogs(limit) })
  } catch (error) {
    response.status(500).json({ success: false, message: error instanceof Error ? error.message : 'Gagal memuat access logs' })
  }
})

app.post('/api/attendance', (request, response) => {
  const userId = request.body.userId ? Number(request.body.userId) : null
  const fullName = String(request.body.fullName ?? request.body.name ?? 'Unknown User')

  recordAccessLog({
    userId,
    fullName,
    eventType: String(request.body.eventType ?? 'attendance'),
    method: String(request.body.method ?? 'biometrik'),
    accessStatus: String(request.body.accessStatus ?? 'success'),
    similarity: request.body.similarity === undefined || request.body.similarity === null ? null : Number(request.body.similarity),
    imagePath: request.body.imagePath ? String(request.body.imagePath) : null,
    source: String(request.body.source ?? 'local'),
    eventTime: String(request.body.eventTime ?? request.body.timestamp ?? nowIso())
  })

  response.json({ success: true })
})

app.get('/api/settings', (_request, response) => {
  response.json({ success: true, settings: getSettings() })
})

app.put('/api/settings', (request, response) => {
  for (const [key, value] of Object.entries(request.body ?? {})) {
    if (typeof value === 'string') {
      setSetting(key, value)
    }
  }
  response.json({ success: true, settings: getSettings() })
})

app.get('/api/spreadsheet-test', async (_request, response) => {
  const settings = getSettings()
  const url = settings.spreadsheet_csv_url?.trim()
  const enabled = settings.spreadsheet_enabled

  if (enabled !== '1') {
    response.json({ success: true, ok: false, stage: 'config', message: 'Spreadsheet belum diaktifkan (spreadsheet_enabled bukan 1)' })
    return
  }

  if (!url) {
    response.json({ success: true, ok: false, stage: 'config', message: 'Spreadsheet CSV URL belum diisi' })
    return
  }

  try {
    const fetchResponse = await fetch(url)
    if (!fetchResponse.ok) {
      response.json({ success: true, ok: false, stage: 'fetch', message: `Fetch gagal: ${fetchResponse.status} ${fetchResponse.statusText}`, url })
      return
    }

    const text = await fetchResponse.text()
    const rawPreview = text.slice(0, 800)
    const delimiter = autoDetectDelimiter(text)
    const rows = parseCsv(text, delimiter)

    if (rows.length < 3) {
      response.json({ success: true, ok: false, stage: 'parse', message: `CSV terbaca tapi hanya ${rows.length} baris (butuh minimal 3: 2 header + 1 data)`, url, rowCount: rows.length, delimiter, rawPreview })
      return
    }

    const dataRows = rows.slice(2)
    const dataRowCount = dataRows.filter((r) => r.some((c) => c.trim())).length
    const firstRow = rows[2]

    response.json({
      success: true,
      ok: true,
      stage: 'ok',
      message: `Spreadsheet OK — ${dataRowCount} baris data ditemukan (delimiter: ${delimiter === '\t' ? 'TAB' : 'COMMA'})`,
      url,
      rowCount: rows.length,
      dataRowCount,
      delimiter: delimiter === '\t' ? 'TAB' : 'COMMA',
      colCount: firstRow.length,
      sample: {
        tanggal: firstRow[0],
        id: firstRow[1],
        nama: firstRow[2],
        domisili: firstRow[13],
        status: firstRow[14],
        akses: firstRow[15]
      },
      rawPreview
    })
  } catch (error) {
    response.json({ success: true, ok: false, stage: 'fetch', message: error instanceof Error ? error.message : 'Fetch gagal', url })
  }
})

app.post('/api/settings/test-connection', async (_request, response) => {
  const status = await getRaspyStatus()
  response.json({
    success: true,
    online: status.online,
    message: status.message,
    payload: status.payload ?? null
  })
})

app.get('/api/integration/diagnostics', async (_request, response) => {
  try {
    const diagnostics = await runRaspyDiagnostics()
    response.json({
      success: true,
      diagnostics,
      message: diagnostics.checks.health.ok
        ? 'Diagnostics Raspy berhasil dijalankan'
        : diagnostics.checks.health.message
    })
  } catch (error) {
    response.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'Diagnostics Raspy gagal dijalankan'
    })
  }
})

// pip package name → actual Python import name mapping
const PIP_TO_IMPORT: Record<string, string> = {
  'torch': 'torch',
  'facenet-pytorch': 'facenet_pytorch',
  'facenet_pytorch': 'facenet_pytorch',
  'opencv-python': 'cv2',
  'Pillow': 'PIL',
  'numpy': 'numpy',
  'tqdm': 'tqdm',
}

function makeTempScript(name: string, content: string): string {
  const scriptPath = path.join(os.tmpdir(), `biometric_check_${name}_${Date.now()}.py`)
  fs.writeFileSync(scriptPath, content, { encoding: 'utf8' })
  return scriptPath
}

// Setup Wizard Endpoints
async function checkPythonExecutable() {
  let scriptPath = ''
  try {
    scriptPath = makeTempScript('python', 'import sys\nprint(sys.version)')
    const { stdout } = await runPythonScript(scriptPath, [])
    const version = stdout.trim()
    if (version.match(/3\.(10|11|12|13)/)) {
      return { success: true, message: `✅ Python ${version.split(' ')[0]} detected` }
    }
    return { success: false, message: `⚠️ Python version terlalu lama (butuh 3.10+): ${version.split(' ')[0]}`, details: { fixCommand: 'Upgrade Python ke 3.10+ dari python.org' } }
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error)
    return { success: false, message: `❌ Python tidak ditemukan`, details: { fixCommand: 'Install Python 3.10+ dari python.org', errorDetail: msg } }
  } finally {
    try { if (scriptPath) fs.unlinkSync(scriptPath) } catch {}
  }
}

async function checkPythonDependency(pipName: string, displayName: string) {
  let scriptPath = ''
  try {
    const importName = PIP_TO_IMPORT[pipName] ?? pipName.replace(/-/g, '_')
    // Use find_spec to detect module WITHOUT importing (fast, no side-effects)
    const script = `import importlib.util, sys\nspec = importlib.util.find_spec('${importName}')\nif spec:\n    print('OK')\nelse:\n    print('NOT_FOUND')\n    sys.exit(1)\n`
    scriptPath = makeTempScript(importName, script)
    const { stdout, stderr } = await runPythonScript(scriptPath, [])
    if (stdout.includes('OK')) {
      return { success: true, message: `✅ ${displayName} terinstall` }
    }
    throw new Error(stderr || 'Module not found')
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error)
    console.error(`[Setup Check] ${displayName} failed:`, msg)
    return {
      success: false,
      message: `❌ ${displayName} belum terinstall`,
      details: { fixCommand: `pip install ${pipName}`, errorDetail: msg }
    }
  } finally {
    try { if (scriptPath) fs.unlinkSync(scriptPath) } catch {}
  }
}

async function checkTorch() {
  return checkPythonDependency('torch', 'PyTorch (torch)')
}

async function checkFaceNet() {
  return checkPythonDependency('facenet-pytorch', 'FaceNet PyTorch')
}

async function checkOpenCV() {
  return checkPythonDependency('opencv-python', 'OpenCV')
}

async function checkWebcamAccess() {
  let scriptPath = ''
  try {
    // First check if cv2 is even available
    const cv2CheckScript = `import importlib.util\nspec = importlib.util.find_spec('cv2')\nif spec is None:\n    print('NO_CV2')\nelse:\n    import cv2, threading\n    result = [False, '']\n    def check_camera():\n        try:\n            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)\n            if cap.isOpened():\n                cap.release()\n                result[0] = True\n            else:\n                result[1] = 'VideoCapture returned False'\n        except Exception as e:\n            result[1] = str(e)\n    t = threading.Thread(target=check_camera, daemon=True)\n    t.start()\n    t.join(timeout=6)\n    if result[0]:\n        print('WEBCAM_OK')\n    else:\n        print('WEBCAM_FAILED:' + result[1])\n`
    scriptPath = makeTempScript('webcam', cv2CheckScript)
    const res = await runPythonScript(scriptPath, [])
    const out = res.stdout.trim()

    if (out.includes('WEBCAM_OK')) {
      return { success: true, message: '✅ Webcam terdeteksi' }
    }
    if (out.includes('NO_CV2')) {
      return {
        success: false,
        message: '❌ OpenCV (cv2) tidak ditemukan, webcam tidak dapat dicek',
        details: { fixCommand: 'pip install opencv-python' }
      }
    }
    const reason = out.replace('WEBCAM_FAILED:', '').trim()
    return {
      success: false,
      message: `❌ Webcam tidak dapat diakses${reason ? ': ' + reason : ''}`,
      details: { fixCommand: 'Pastikan webcam terhubung dan tidak dipakai aplikasi lain (Teams, Zoom, dll)', errorDetail: out }
    }
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error)
    console.error('[Setup Check] Webcam error:', msg)
    return {
      success: false,
      message: '❌ Gagal mengecek webcam',
      details: { fixCommand: 'Pastikan OpenCV terinstall dan webcam tersambung', errorDetail: msg }
    }
  } finally {
    try { if (scriptPath) fs.unlinkSync(scriptPath) } catch {}
  }
}

async function checkStorageAccess() {
  try {
    ensureTempDir()
    const testFile = path.join(getTempDir(), '.storage-test')
    try {
      fs.writeFileSync(testFile, 'test')
      fs.unlinkSync(testFile)
      return { success: true, message: `✅ Storage writable` }
    } catch (writeError) {
      return {
        success: false,
        message: `❌ Storage tidak dapat diakses`,
        details: { fixCommand: 'Check folder permissions' }
      }
    }
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error)
    return {
      success: false,
      message: `❌ Storage tidak dapat diakses: ${msg}`,
      details: { fixCommand: 'Check folder permissions' }
    }
  }
}

app.post('/api/setup/check', async (request, response) => {
  const { checkId } = request.body

  try {
    let result
    switch (checkId) {
      case 'python':
        result = await checkPythonExecutable()
        break
      case 'torch':
        result = await checkTorch()
        break
      case 'facenet':
        result = await checkFaceNet()
        break
      case 'opencv':
        result = await checkOpenCV()
        break
      case 'webcam':
        result = await checkWebcamAccess()
        break
      case 'storage':
        result = await checkStorageAccess()
        break
      default:
        result = { success: false, message: 'Unknown check' }
    }

    response.json(result)
  } catch (error) {
    response.json({
      success: false,
      message: error instanceof Error ? error.message : 'Check gagal'
    })
  }
})

app.post('/api/setup/configure', (request, response) => {
  try {
    const { raspy_api_base_url } = request.body

    if (raspy_api_base_url) {
      setSetting('raspy_api_base_url', raspy_api_base_url)
    }

    response.json({
      success: true,
      message: 'Konfigurasi berhasil disimpan'
    })
  } catch (error) {
    response.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'Gagal menyimpan konfigurasi'
    })
  }
})

export async function startServer(storageDir: string, projectRoot: string, resourcesDir: string) {
  if (runtime.server) {
    return
  }

  runtime.storageDir = storageDir
  runtime.projectRoot = projectRoot
  runtime.resourcesDir = resourcesDir
  await initializeDatabase(storageDir, projectRoot)

  const port = 3001
  runtime.server = app.listen(port, () => {
    console.log(`Internal Express API running on port ${port}`)
  })
}
