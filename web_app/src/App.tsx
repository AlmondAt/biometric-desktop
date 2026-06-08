import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import Webcam from 'react-webcam'
import SetupWizard from './SetupWizard'
import {
  Camera,
  CircleAlert,
  CircleCheckBig,
  Cog,
  Fingerprint,
  History,
  LayoutDashboard,
  Loader2,
  LogOut,
  MonitorDot,
  Pencil,
  RefreshCw,
  ScanLine,
  Search,
  Shield,
  Trash2,
  UserPlus,
  Users
} from 'lucide-react'

type TabId = 'dashboard' | 'users' | 'enrollment' | 'logs' | 'settings'
type ToastKind = 'success' | 'error'
type UserRole = 'admin' | 'coadmin' | 'member'
type EnrollmentMode = 'new' | 'retrain'

interface ApiEnvelope {
  success: boolean
  message?: string
}

interface AuthUser {
  accountId: number
  userId: number | null
  username: string
  fullName: string
  role: 'admin' | 'coadmin'
}

interface UserRecord {
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

interface AccessLogRecord {
  id: number | string
  userId: number | null
  fullName: string
  eventType: string
  method: string
  accessStatus: string
  similarity: number | null
  imagePath: string | null
  source: string
  eventTime: string
  summary?: string
  detailEntries?: Array<{
    label: string
    value: string
  }>
  employeeId?: string
  domisili?: string
  akses?: string
}

interface DashboardPayload extends ApiEnvelope {
  metrics: {
    totalUsers: number
    attendanceToday: number
    systemStatus: 'online' | 'offline'
  }
  recentActivity: AccessLogRecord[]
  systemStatusMessage: string
  integration: {
    spreadsheetEnabled: boolean
  }
}

interface UsersPayload extends ApiEnvelope {
  users: UserRecord[]
}

interface LogsPayload extends ApiEnvelope {
  logs: AccessLogRecord[]
}

interface SettingsPayload extends ApiEnvelope {
  settings: Record<string, string>
}

interface ConnectionTestPayload extends ApiEnvelope {
  online: boolean
  payload?: Record<string, unknown> | null
}

interface DiagnosticsPayload extends ApiEnvelope {
  diagnostics: {
    baseUrl: string
    checks: {
      health: { ok: boolean; message: string }
      users: { ok: boolean; count: number; message?: string }
      logs: { ok: boolean; count: number; message?: string }
      deviceModeRead: { ok: boolean; payload?: Record<string, unknown>; message?: string }
      deviceModeWrite: { ok: boolean; message: string }
    }
  }
}

interface LoginPayload extends ApiEnvelope {
  user: AuthUser
}

interface PrepareEnrollmentPayload extends ApiEnvelope {
  user: UserRecord
  device?: {
    delivered?: boolean
    message?: string
  }
  remote?: {
    created?: boolean
    message?: string
  }
}

interface FaceEnrollmentPayload extends ApiEnvelope {
  user: UserRecord
  training: {
    totalEmbeddings: number
    output: string
  }
  device?: {
    message?: string
  }
  nextStep: 'fingerprint' | 'done'
}

interface FingerprintPayload extends ApiEnvelope {
  user: UserRecord
  fingerprintId: number
  simulated: boolean
  remote?: {
    message?: string
  }
}

interface EnrollmentCancelPayload extends ApiEnvelope {
  device?: {
    message?: string
  }
}

interface ToastState {
  message: string
  type: ToastKind
}

interface EditFormState {
  fullName: string
  role: UserRole
  username: string
  password: string
}

interface SettingsFormState {
  raspy_api_base_url: string
  raspy_mode_endpoint: string
  spreadsheet_csv_url: string
  spreadsheet_enabled: string
}

const API_BASE = 'http://localhost:3001'

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  const payload = (await response.json().catch(() => null)) as (ApiEnvelope & T) | null

  if (!response.ok || !payload?.success) {
    throw new Error(payload?.message || `Request gagal: ${response.status}`)
  }

  return payload as T
}

function formatDateTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

function formatRole(role: UserRole) {
  if (role === 'coadmin') {
    return 'CoAdmin'
  }
  if (role === 'admin') {
    return 'Admin'
  }
  return 'Member'
}

function formatLabel(value: string) {
  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function getStatusChipClass(status: string) {
  const normalized = status.trim().toLowerCase()
  if (/(success|registered|granted|approved|online|active|present|ok)/.test(normalized)) {
    return 'chip-success'
  }
  if (/(fail|failed|denied|rejected|offline|error|blocked)/.test(normalized)) {
    return 'chip-danger'
  }
  return 'chip-info'
}

function formatLogSummary(log: AccessLogRecord) {
  if (log.summary?.trim()) {
    return log.summary
  }

  const parts = [
    log.eventType ? formatLabel(log.eventType) : '',
    log.method && log.method !== 'unknown' ? `via ${formatLabel(log.method)}` : '',
    typeof log.similarity === 'number' ? `Similarity ${log.similarity.toFixed(3)}` : ''
  ].filter(Boolean)

  return parts.join(' • ') || '-'
}

function useToast() {
  const [toast, setToast] = useState<ToastState | null>(null)

  useEffect(() => {
    if (!toast) {
      return undefined
    }

    const timer = window.setTimeout(() => setToast(null), 3200)
    return () => window.clearTimeout(timer)
  }, [toast])

  const showToast = (message: string, type: ToastKind = 'success') => {
    setToast({ message, type })
  }

  return { toast, showToast }
}

function Toast({ toast }: { toast: ToastState | null }) {
  if (!toast) {
    return null
  }

  return (
    <div className={`toast toast-${toast.type}`}>
      {toast.type === 'success' ? <CircleCheckBig size={18} /> : <CircleAlert size={18} />}
      <span>{toast.message}</span>
    </div>
  )
}

function LoginScreen({ onLogin, loading }: { onLogin: (username: string, password: string) => Promise<void>; loading: boolean }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')

    try {
      await onLogin(username, password)
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Login gagal')
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="brand-mark">
          <Fingerprint size={30} />
        </div>
        <h1>Lab Robotika BioAdmin</h1>
        <p>Masuk untuk mengelola user, enrollment biometrik, dan log akses.</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Username
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="admin" />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" />
          </label>
          {error ? <div className="banner banner-error">{error}</div> : null}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <Shield size={18} />}
            <span>{loading ? 'Memproses...' : 'Masuk'}</span>
          </button>
        </form>

        <div className="login-help">
          <div>Default admin: admin / admin123</div>
          <div>Default coadmin: coadmin / coadmin123</div>
        </div>
      </div>
    </div>
  )
}

function Sidebar({
  activeTab,
  user,
  onSelect,
  onLogout
}: {
  activeTab: TabId
  user: AuthUser
  onSelect: (tab: TabId) => void
  onLogout: () => void
}) {
  const items = user.role === 'admin'
    ? [
        { id: 'dashboard' as const, label: 'Dashboard', icon: LayoutDashboard },
        { id: 'users' as const, label: 'User Management', icon: Users },
        { id: 'enrollment' as const, label: 'Enrollment', icon: UserPlus },
        { id: 'logs' as const, label: 'Access Logs', icon: History },
        { id: 'settings' as const, label: 'Settings', icon: Cog }
      ]
    : [
        { id: 'users' as const, label: 'User Management', icon: Users },
        { id: 'enrollment' as const, label: 'Enrollment', icon: UserPlus }
      ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon"><Fingerprint size={22} /></div>
        <div>
          <strong>BioAdmin</strong>
          <small>{formatRole(user.role)}</small>
        </div>
      </div>

      <nav className="sidebar-nav">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-button ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onSelect(item.id)}
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="current-user">
          <strong>{user.fullName}</strong>
          <span>@{user.username}</span>
        </div>
        <button type="button" className="ghost-button danger-text" onClick={onLogout}>
          <LogOut size={16} />
          <span>Log Out</span>
        </button>
      </div>
    </aside>
  )
}

function DashboardPage() {
  const [payload, setPayload] = useState<DashboardPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    const load = async () => {
      try {
        const data = await requestJson<DashboardPayload>('/api/dashboard')
        if (active) {
          setPayload(data)
          setError('')
        }
      } catch (loadError) {
        if (active) {
          setError(loadError instanceof Error ? loadError.message : 'Gagal memuat dashboard')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void load()
    const interval = window.setInterval(() => void load(), 10000)
    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [])

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Ringkasan real-time user, absensi hari ini, dan status perangkat Raspberry Pi.</p>
        </div>
      </div>

      {error ? <div className="banner banner-error">{error}</div> : null}

      <div className="stats-grid">
        <article className="stat-card">
          <span>Total Users</span>
          <strong>{loading ? '...' : payload?.metrics.totalUsers ?? 0}</strong>
          <small>Bersumber dari user management yang sudah tersinkron</small>
        </article>
        <article className="stat-card">
          <span>Attendance Today</span>
          <strong>{loading ? '...' : payload?.metrics.attendanceToday ?? 0}</strong>
          <small>Diambil dari access logs lokal, raspy, dan spreadsheet</small>
        </article>
        <article className="stat-card">
          <span>System Status</span>
          <strong className={payload?.metrics.systemStatus === 'online' ? 'online-text' : 'offline-text'}>
            <MonitorDot size={24} />
            {loading ? 'Checking...' : payload?.metrics.systemStatus === 'online' ? 'Online' : 'Offline'}
          </strong>
          <small>{payload?.systemStatusMessage ?? 'Memeriksa koneksi...'}</small>
        </article>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Recent Activity</h2>
            <p>{payload?.integration.spreadsheetEnabled ? 'Spreadsheet aktif dan ikut ditampilkan.' : 'Spreadsheet belum diaktifkan.'}</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Waktu</th>
                <th>Nama</th>
                <th>Ringkasan</th>
                <th>Status</th>
                <th>Sumber</th>
              </tr>
            </thead>
            <tbody>
              {payload?.recentActivity.length ? payload.recentActivity.map((log) => (
                <tr key={String(log.id)}>
                  <td>{formatDateTime(log.eventTime)}</td>
                  <td>{log.fullName}</td>
                  <td className="log-summary-cell">{formatLogSummary(log)}</td>
                  <td><span className={`chip ${getStatusChipClass(log.accessStatus)}`}>{formatLabel(log.accessStatus)}</span></td>
                  <td>{log.source}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="empty-cell">Belum ada activity yang bisa ditampilkan.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}

function UserEditModal({
  user,
  onClose,
  onSaved,
  showToast
}: {
  user: UserRecord
  onClose: () => void
  onSaved: () => void
  showToast: (message: string, type?: ToastKind) => void
}) {
  const [form, setForm] = useState<EditFormState>({
    fullName: user.fullName,
    role: user.role,
    username: user.username ?? '',
    password: ''
  })
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)

    try {
      await requestJson<ApiEnvelope>(`/api/users/${user.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      showToast('Data user berhasil diperbarui')
      onSaved()
      onClose()
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal memperbarui user', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <h3>Edit User</h3>
          <button type="button" className="icon-button" onClick={onClose}>×</button>
        </div>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Full Name
            <input value={form.fullName} onChange={(event) => setForm((current) => ({ ...current, fullName: event.target.value }))} />
          </label>
          <label>
            Role
            <select value={form.role} onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as UserRole }))}>
              <option value="member">Member</option>
              <option value="coadmin">CoAdmin</option>
              <option value="admin">Admin</option>
            </select>
          </label>
          <label>
            Username
            <input value={form.username} onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))} placeholder="Kosongkan untuk member" />
          </label>
          <label>
            Password Baru
            <input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder="Opsional" />
          </label>
          <div className="form-actions">
            <button type="button" className="ghost-button" onClick={onClose}>Batal</button>
            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? <Loader2 className="spin" size={16} /> : <Pencil size={16} />}
              <span>Simpan</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function UserManagementPage({
  session,
  onAddUser,
  onRetrain,
  showToast
}: {
  session: AuthUser
  onAddUser: () => void
  onRetrain: (user: UserRecord) => void
  showToast: (message: string, type?: ToastKind) => void
}) {
  const [users, setUsers] = useState<UserRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [editUser, setEditUser] = useState<UserRecord | null>(null)

  const loadUsers = async () => {
    try {
      const data = await requestJson<UsersPayload>('/api/users')
      setUsers(data.users)
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal memuat user', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadUsers()
    const interval = window.setInterval(() => void loadUsers(), 12000)
    return () => window.clearInterval(interval)
  }, [])

  const filteredUsers = useMemo(() => {
    const keyword = search.trim().toLowerCase()
    if (!keyword) {
      return users
    }

    return users.filter((user) => {
      return [String(user.displayNo ?? user.id), user.fullName, user.role, user.username ?? '']
        .some((field) => field.toLowerCase().includes(keyword))
    })
  }, [search, users])

  const handleDelete = async (user: UserRecord) => {
    const confirmed = window.confirm(`Hapus user ${user.fullName}?`)
    if (!confirmed) {
      return
    }

    try {
      await requestJson<ApiEnvelope>(`/api/users/${user.id}`, { method: 'DELETE' })
      showToast('User berhasil dihapus')
      await loadUsers()
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal menghapus user', 'error')
    }
  }

  const handleEnrollFingerprint = async (user: UserRecord) => {
    const confirmed = window.confirm(
      user.fingerprintEnrolled
        ? `Scan ulang fingerprint untuk ${user.fullName}?`
        : `Tambahkan fingerprint untuk ${user.fullName}?`
    )
    if (!confirmed) {
      return
    }

    try {
      const data = await requestJson<FingerprintPayload>('/api/enrollment/fingerprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: user.id })
      })
      showToast(`Fingerprint tersimpan untuk ${data.user.fullName}. ID: ${data.fingerprintId}`)
      await loadUsers()
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal mendaftarkan fingerprint', 'error')
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>User Management</h1>
          <p>Daftar user terdaftar, role, status login, dan status biometrik.</p>
        </div>
        <div className="header-actions">
          <button type="button" className="ghost-button" onClick={() => void loadUsers()}>
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
          <button type="button" className="primary-button" onClick={onAddUser}>
            <UserPlus size={16} />
            <span>Tambah User Baru</span>
          </button>
        </div>
      </div>

      <div className="panel compact-gap">
        <div className="toolbar">
          <label className="search-field">
            <Search size={16} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Cari nama, role, username, atau ID" />
          </label>
          <div className="toolbar-note">
            {session.role === 'admin'
              ? 'Admin dapat menambah, edit, hapus, dan membuka retrain wajah.'
              : 'CoAdmin hanya dapat melihat daftar user dan menambah user baru.'}
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nama</th>
                <th>Role</th>
                <th>Login</th>
                <th>Face</th>
                <th>Fingerprint</th>
                <th>Sumber</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="empty-cell">Memuat data user...</td>
                </tr>
              ) : filteredUsers.length ? filteredUsers.map((user) => (
                <tr key={user.id}>
                  {(() => {
                    const hasFingerprint = user.fingerprintId !== null && user.fingerprintId !== undefined
                    const fingerprintReady = user.fingerprintEnrolled || hasFingerprint

                    return (
                      <>
                  <td>{user.displayNo ?? user.id}</td>
                  <td>
                    <div className="user-cell">
                      <strong>{user.fullName}</strong>
                      <small>{formatDateTime(user.registrationDate)}</small>
                    </div>
                  </td>
                  <td><span className={`chip ${user.role === 'admin' ? 'chip-danger' : user.role === 'coadmin' ? 'chip-info' : ''}`}>{formatRole(user.role)}</span></td>
                  <td>{user.hasLogin ? user.username : '-'}</td>
                  <td>{user.faceEnrolled ? `${user.faceEmbeddingCount} embeddings` : 'Belum'}</td>
                  <td>
                    <span className={`chip ${fingerprintReady ? 'chip-success' : 'chip-info'}`}>
                      {fingerprintReady ? `ID ${user.fingerprintId}` : 'Belum'}
                    </span>
                  </td>
                  <td>{user.source}</td>
                  <td>
                    {session.role === 'admin' ? (
                      <div className="row-actions">
                        <button type="button" className="icon-button" title="Retrain wajah" onClick={() => onRetrain(user)}>
                          <Camera size={15} />
                        </button>
                        <button
                          type="button"
                          className={`icon-button ${fingerprintReady ? 'chip-success' : 'chip-info'}`}
                          title={fingerprintReady ? 'Scan ulang fingerprint' : 'Tambah fingerprint'}
                          onClick={() => void handleEnrollFingerprint(user)}
                        >
                          <Fingerprint size={15} />
                        </button>
                        <button type="button" className="icon-button" title="Edit user" onClick={() => setEditUser(user)}>
                          <Pencil size={15} />
                        </button>
                        <button type="button" className="icon-button danger-text" title="Hapus user" onClick={() => void handleDelete(user)}>
                          <Trash2 size={15} />
                        </button>
                      </div>
                    ) : (
                      <span className="muted-text">View only</span>
                    )}
                  </td>
                      </>
                    )
                  })()}
                </tr>
              )) : (
                <tr>
                  <td colSpan={8} className="empty-cell">Tidak ada user yang cocok.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {editUser ? (
        <UserEditModal
          user={editUser}
          onClose={() => setEditUser(null)}
          onSaved={() => void loadUsers()}
          showToast={showToast}
        />
      ) : null}
    </section>
  )
}

function EnrollmentPage({
  mode,
  selectedUser,
  onDone,
  onCancel,
  showToast
}: {
  mode: EnrollmentMode
  selectedUser: UserRecord | null
  onDone: () => void
  onCancel: () => void
  showToast: (message: string, type?: ToastKind) => void
}) {
  const webcamRef = useRef<Webcam | null>(null)
  const cancelRequestedRef = useRef(false)
  const [step, setStep] = useState(mode === 'retrain' ? 2 : 1)
  const [nextId, setNextId] = useState<number | null>(selectedUser?.displayNo ?? selectedUser?.id ?? null)
  const [createdUser, setCreatedUser] = useState<UserRecord | null>(selectedUser)
  const [fullName, setFullName] = useState(selectedUser?.fullName ?? '')
  const [role, setRole] = useState<UserRole>(selectedUser?.role ?? 'member')
  const [username, setUsername] = useState(selectedUser?.username ?? '')
  const [password, setPassword] = useState('')
  const [photos, setPhotos] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [canceling, setCanceling] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const [trainingSummary, setTrainingSummary] = useState('')

  useEffect(() => {
    setStep(mode === 'retrain' ? 2 : 1)
    setCreatedUser(selectedUser)
    setNextId(selectedUser?.displayNo ?? selectedUser?.id ?? null)
    setFullName(selectedUser?.fullName ?? '')
    setRole(selectedUser?.role ?? 'member')
    setUsername(selectedUser?.username ?? '')
    setPassword('')
    setPhotos([])
    setStatusMessage('')
    setTrainingSummary('')
  }, [mode, selectedUser])

  useEffect(() => {
    if (mode === 'retrain') {
      return
    }

    let active = true
    const loadNextId = async () => {
      try {
        const data = await requestJson<{ success: boolean; nextId: number; displayNo?: number }>('/api/users/next-id')
        if (active) {
          setNextId(data.displayNo ?? data.nextId)
        }
      } catch (error) {
        if (active) {
          showToast(error instanceof Error ? error.message : 'Gagal mengambil ID berikutnya', 'error')
        }
      }
    }

    void loadNextId()
    return () => {
      active = false
    }
  }, [mode, showToast])

  const capturePhoto = (webcam: Webcam | null) => {
    const snapshot = webcam?.getScreenshot()
    if (!snapshot) {
      showToast('Webcam belum siap', 'error')
      return
    }

    if (photos.length >= 10) {
      showToast('Maksimal 10 foto per sesi', 'error')
      return
    }

    setPhotos((current) => [...current, snapshot])
  }

  const handlePrepare = async () => {
    cancelRequestedRef.current = false

    if (!fullName.trim()) {
      showToast('Nama lengkap wajib diisi', 'error')
      return
    }

    if ((role === 'admin' || role === 'coadmin') && (!username.trim() || !password.trim())) {
      showToast('Username dan password wajib diisi untuk admin atau coadmin', 'error')
      return
    }

    setBusy(true)
    setStatusMessage('Mengirim sinyal enrollment ke Raspberry Pi...')

    try {
      const data = await requestJson<PrepareEnrollmentPayload>('/api/enrollment/prepare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName, role, username, password })
      })
      if (cancelRequestedRef.current) {
        return
      }

      setCreatedUser(data.user)
      setStep(2)
      setStatusMessage(data.device?.message || data.remote?.message || 'Mode enrollment aktif di Raspberry Pi')
      showToast(`User ${data.user.fullName} siap untuk capture wajah`)
    } catch (error) {
      if (cancelRequestedRef.current) {
        return
      }

      showToast(error instanceof Error ? error.message : 'Gagal memulai enrollment', 'error')
    } finally {
      if (!cancelRequestedRef.current) {
        setBusy(false)
      }
    }
  }

  const handleFaceTraining = async () => {
    cancelRequestedRef.current = false

    if (!createdUser) {
      showToast('User belum siap untuk diproses', 'error')
      return
    }

    if (photos.length < 3) {
      showToast('Ambil minimal 3 foto wajah', 'error')
      return
    }

    setBusy(true)
    setStatusMessage('Capture wajah selesai. Sistem sedang training embeddings...')

    try {
      const data = await requestJson<FaceEnrollmentPayload>('/api/enrollment/face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: createdUser.id,
          photos,
          replaceExisting: mode === 'retrain',
          skipFingerprint: mode === 'retrain'
        })
      })
      if (cancelRequestedRef.current) {
        return
      }

      setCreatedUser(data.user)
      setTrainingSummary(`${data.training.totalEmbeddings} embeddings tersimpan atas nama ${data.user.fullName}`)
      setStatusMessage(data.device?.message || 'Training wajah selesai')

      if (data.nextStep === 'done') {
        showToast('Retrain wajah selesai')
        onDone()
      } else {
        setStep(3)
        showToast('Training wajah selesai, lanjut scan fingerprint')
      }
    } catch (error) {
      if (cancelRequestedRef.current) {
        return
      }

      showToast(error instanceof Error ? error.message : 'Training wajah gagal', 'error')
    } finally {
      if (!cancelRequestedRef.current) {
        setBusy(false)
      }
    }
  }

  const handleFingerprint = async () => {
    cancelRequestedRef.current = false

    if (!createdUser) {
      return
    }

    setBusy(true)
    setStatusMessage('Meminta Raspberry Pi melakukan scan fingerprint...')

    try {
      const data = await requestJson<FingerprintPayload>('/api/enrollment/fingerprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: createdUser.id })
      })
      if (cancelRequestedRef.current) {
        return
      }

      setCreatedUser(data.user)
      setStatusMessage(data.remote?.message || (data.simulated ? 'Fingerprint memakai ID lokal fallback' : 'Fingerprint berhasil terdaftar'))
      showToast(`Enrollment lengkap. Fingerprint ID: ${data.fingerprintId}`)
      onDone()
    } catch (error) {
      if (cancelRequestedRef.current) {
        return
      }

      showToast(error instanceof Error ? error.message : 'Scan fingerprint gagal', 'error')
    } finally {
      if (!cancelRequestedRef.current) {
        setBusy(false)
      }
    }
  }

  const handleCancel = async () => {
    cancelRequestedRef.current = true
    setBusy(true)
    setCanceling(true)
    setStatusMessage('Membatalkan proses dan mengembalikan device ke mode idle...')

    try {
      const data = await requestJson<EnrollmentCancelPayload>('/api/enrollment/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: createdUser?.id,
          fullName: createdUser?.fullName || fullName
        })
      })
      showToast(data.device?.message || 'Mode idle dikirim ke Raspberry Pi')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal mengembalikan device ke mode idle', 'error')
    } finally {
      setCanceling(false)
      setBusy(false)
      onCancel()
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>{mode === 'retrain' ? 'Retrain Wajah' : 'Enrollment'}</h1>
          <p>
            {mode === 'retrain'
              ? 'Capture ulang wajah dan ganti embeddings lama menggunakan nama lengkap sebagai key.'
              : 'ID otomatis diambil dari user berikutnya, lalu proses masuk ke capture wajah, training, dan scan fingerprint.'}
          </p>
        </div>
        <div className="header-actions">
          <button type="button" className="ghost-button" onClick={() => void handleCancel()} disabled={canceling}>Kembali</button>
        </div>
      </div>

      <div className="step-indicator">
        <div className={`step-pill ${step >= 1 ? 'active' : ''}`}>1. Data User</div>
        <div className={`step-pill ${step >= 2 ? 'active' : ''}`}>2. Capture Wajah</div>
        <div className={`step-pill ${step >= 3 ? 'active' : ''}`}>3. Scan Fingerprint</div>
      </div>

      {statusMessage ? <div className="banner banner-info">{statusMessage}</div> : null}
      {trainingSummary ? <div className="banner banner-success">{trainingSummary}</div> : null}

      {step === 1 ? (
        <div className="panel form-panel">
          <div className="form-grid two-columns">
            <label>
              ID Otomatis
              <input value={nextId ?? ''} readOnly />
            </label>
            <label>
              Full Name
              <input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Nama lengkap" />
            </label>
            <label>
              Role
              <select value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
                <option value="member">Member</option>
                <option value="coadmin">CoAdmin</option>
                <option value="admin">Admin</option>
              </select>
            </label>
            <label>
              Username Login
              <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Wajib untuk admin/coadmin" />
            </label>
            <label>
              Password Login
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Wajib untuk admin/coadmin" />
            </label>
          </div>

          <div className="form-actions">
            <button type="button" className="primary-button" onClick={() => void handlePrepare()} disabled={busy}>
              {busy ? <Loader2 className="spin" size={16} /> : <Shield size={16} />}
              <span>Lanjut ke Capture</span>
            </button>
          </div>
        </div>
      ) : null}

      {step >= 2 ? (
        <div className="capture-layout">
          <div className="panel webcam-panel">
            <div className="panel-header">
              <div>
                <h2>{createdUser?.fullName ?? fullName}</h2>
                <p>User ID: {createdUser?.displayNo ?? createdUser?.id ?? nextId ?? '-'}</p>
              </div>
            </div>
            <div className="webcam-frame">
              <Webcam
                ref={(instance) => {
                  webcamRef.current = instance
                }}
                audio={false}
                screenshotFormat="image/jpeg"
                videoConstraints={{ facingMode: 'user' }}
              />
            </div>
            <div className="header-actions">
              <button type="button" className="ghost-button" onClick={() => capturePhoto(webcamRef.current)} disabled={busy}>
                <Camera size={16} />
                <span>Ambil Foto</span>
              </button>
              <button type="button" className="primary-button" onClick={() => void handleFaceTraining()} disabled={busy || step === 3}>
                {busy ? <Loader2 className="spin" size={16} /> : <ScanLine size={16} />}
                <span>{mode === 'retrain' ? 'Retrain Wajah' : 'Training Wajah'}</span>
              </button>
            </div>
            <small className="muted-text">Minimal 3 foto. Disarankan 5-10 foto dengan angle berbeda.</small>
          </div>

          <div className="panel photo-panel">
            <div className="panel-header">
              <div>
                <h2>Foto Tertangkap</h2>
                <p>{photos.length} dari maksimum 10 foto</p>
              </div>
            </div>
            <div className="photo-grid">
              {photos.map((photo, index) => (
                <div key={`${photo.slice(0, 24)}-${index}`} className="photo-card">
                  <img src={photo} alt={`capture-${index + 1}`} />
                  <button type="button" className="icon-button" onClick={() => setPhotos((current) => current.filter((_, currentIndex) => currentIndex !== index))}>×</button>
                </div>
              ))}
              {!photos.length ? <div className="empty-card">Belum ada foto yang diambil.</div> : null}
            </div>
          </div>
        </div>
      ) : null}

      {step === 3 && mode === 'new' ? (
        <div className="panel fingerprint-panel">
          <div>
            <h2>Scan Fingerprint</h2>
            <p>Setelah wajah selesai dilatih, kirim perintah ke Raspberry Pi untuk memulai scan fingerprint.</p>
          </div>
          <button type="button" className="primary-button" onClick={() => void handleFingerprint()} disabled={busy}>
            {busy ? <Loader2 className="spin" size={16} /> : <Fingerprint size={16} />}
            <span>Mulai Scan Fingerprint</span>
          </button>
        </div>
      ) : null}
    </section>
  )
}

function AccessLogsPage({ showToast }: { showToast: (message: string, type?: ToastKind) => void }) {
  const [logs, setLogs] = useState<AccessLogRecord[]>([])
  const [query, setQuery] = useState('')
  const [sourceFilter, setSourceFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const loadLogs = async () => {
    try {
      const data = await requestJson<LogsPayload>('/api/logs?limit=250')
      setLogs(data.logs)
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal memuat access logs', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLogs()
    const interval = window.setInterval(() => void loadLogs(), 10000)
    return () => window.clearInterval(interval)
  }, [])

  const filteredLogs = useMemo(() => {
    const keyword = query.trim().toLowerCase()

    return logs.filter((log) => {
      const detailValues = log.detailEntries?.map((entry) => `${entry.label} ${entry.value}`) ?? []
      const matchesKeyword = !keyword || [log.fullName, log.method, log.eventType, log.source, log.summary ?? '', ...detailValues]
        .some((field) => field.toLowerCase().includes(keyword))
      const matchesSource = sourceFilter === 'all' || log.source === sourceFilter
      return matchesKeyword && matchesSource
    })
  }, [logs, query, sourceFilter])

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Access Logs</h1>
          <p>Tampilan detail log akses yang menggabungkan sumber lokal, Raspberry Pi, dan spreadsheet.</p>
        </div>
        <div className="header-actions">
          <button type="button" className="ghost-button" onClick={() => void loadLogs()}>
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="panel compact-gap">
        <div className="toolbar split-toolbar">
          <label className="search-field">
            <Search size={16} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Cari nama, event, metode, atau sumber" />
          </label>
          <label>
            Sumber
            <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
              <option value="all">Semua</option>
              <option value="local">Local</option>
              <option value="raspy">Raspy</option>
              <option value="spreadsheet">Spreadsheet</option>
            </select>
          </label>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Waktu</th>
                <th>ID</th>
                <th>Nama</th>
                <th>Domisili</th>
                <th>Status</th>
                <th>Akses</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="empty-cell">Memuat access logs...</td>
                </tr>
              ) : filteredLogs.length ? filteredLogs.map((log) => (
                <tr key={String(log.id)}>
                  <td>{formatDateTime(log.eventTime)}</td>
                  <td>{log.employeeId ?? '-'}</td>
                  <td>{log.fullName}</td>
                  <td>{log.domisili ?? '-'}</td>
                  <td><span className={`chip ${getStatusChipClass(log.accessStatus)}`}>{formatLabel(log.accessStatus)}</span></td>
                  <td>{log.akses ?? '-'}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={6} className="empty-cell">Belum ada log yang sesuai filter.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}

function SettingsPage({
  onSettingsChanged,
  showToast
}: {
  onSettingsChanged: () => void
  showToast: (message: string, type?: ToastKind) => void
}) {
  const [form, setForm] = useState<SettingsFormState>({
    raspy_api_base_url: '',
    raspy_mode_endpoint: '/api/device/mode',
    spreadsheet_csv_url: '',
    spreadsheet_enabled: '0'
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [diagnosing, setDiagnosing] = useState(false)
  const [diagnostics, setDiagnostics] = useState<DiagnosticsPayload['diagnostics'] | null>(null)
  const [sheetTesting, setSheetTesting] = useState(false)
  const [sheetResult, setSheetResult] = useState<{ ok: boolean; message: string; stage?: string; dataRowCount?: number; headers?: string[]; firstDataRow?: string[]; rawPreview?: string; delimiter?: string; colCount?: number; rowCount?: number; sample?: Record<string, string> } | null>(null)

  const loadSettings = async () => {
    try {
      const data = await requestJson<SettingsPayload>('/api/settings')
      setForm({
        raspy_api_base_url: data.settings.raspy_api_base_url ?? '',
        raspy_mode_endpoint: data.settings.raspy_mode_endpoint ?? '/api/device/mode',
        spreadsheet_csv_url: data.settings.spreadsheet_csv_url ?? '',
        spreadsheet_enabled: data.settings.spreadsheet_enabled ?? '0'
      })
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal memuat settings', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSettings()
  }, [])

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)

    try {
      await requestJson<SettingsPayload>('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      showToast('Settings integrasi berhasil disimpan')
      onSettingsChanged()
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Gagal menyimpan settings', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleTestConnection = async () => {
    setTesting(true)
    try {
      const data = await requestJson<ConnectionTestPayload>('/api/settings/test-connection', {
        method: 'POST'
      })
      showToast(data.message || (data.online ? 'Raspy terhubung' : 'Raspy belum terhubung'), data.online ? 'success' : 'error')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Test koneksi gagal', 'error')
    } finally {
      setTesting(false)
    }
  }

  const handleDiagnostics = async () => {
    setDiagnosing(true)
    try {
      const data = await requestJson<DiagnosticsPayload>('/api/integration/diagnostics')
      setDiagnostics(data.diagnostics)
      showToast(data.message || 'Diagnostics Raspy selesai dijalankan')
    } catch (error) {
      setDiagnostics(null)
      showToast(error instanceof Error ? error.message : 'Diagnostics gagal', 'error')
    } finally {
      setDiagnosing(false)
    }
  }

  const handleTestSpreadsheet = async () => {
    setSheetTesting(true)
    setSheetResult(null)
    try {
      const data = await fetch(`${API_BASE}/api/spreadsheet-test`)
      const json = await data.json() as { ok: boolean; message: string; stage?: string; dataRowCount?: number; headers?: string[]; firstDataRow?: string[] }
      setSheetResult(json)
    } catch (error) {
      setSheetResult({ ok: false, message: error instanceof Error ? error.message : 'Gagal mengakses endpoint test' })
    } finally {
      setSheetTesting(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Atur alamat Raspy, endpoint mode alat, dan koneksi spreadsheet dari desktop.</p>
        </div>
      </div>

      <div className="panel form-panel">
        {loading ? (
          <div className="empty-card">Memuat settings...</div>
        ) : (
          <form className="form-grid settings-grid" onSubmit={handleSave}>
            <label>
              Raspy API Base URL
              <input
                value={form.raspy_api_base_url}
                onChange={(event) => setForm((current) => ({ ...current, raspy_api_base_url: event.target.value }))}
                placeholder="http://192.168.1.10:5000"
              />
            </label>
            <label>
              Device Mode Endpoint
              <input
                value={form.raspy_mode_endpoint}
                onChange={(event) => setForm((current) => ({ ...current, raspy_mode_endpoint: event.target.value }))}
                placeholder="/api/device/mode"
              />
            </label>
            <label>
              Spreadsheet CSV URL
              <input
                value={form.spreadsheet_csv_url}
                onChange={(event) => setForm((current) => ({ ...current, spreadsheet_csv_url: event.target.value }))}
                placeholder="https://docs.google.com/.../export?format=csv"
              />
            </label>
            <label>
              Spreadsheet Mode
              <select
                value={form.spreadsheet_enabled}
                onChange={(event) => setForm((current) => ({ ...current, spreadsheet_enabled: event.target.value }))}
              >
                <option value="0">Nonaktif</option>
                <option value="1">Aktif</option>
              </select>
            </label>

            <div className="form-actions settings-actions">
              <button type="submit" className="primary-button" disabled={saving}>
                {saving ? <Loader2 className="spin" size={16} /> : <Cog size={16} />}
                <span>Simpan Settings</span>
              </button>
              <button type="button" className="ghost-button" onClick={() => void handleTestConnection()} disabled={testing}>
                {testing ? <Loader2 className="spin" size={16} /> : <MonitorDot size={16} />}
                <span>Test Koneksi Raspy</span>
              </button>
              <button type="button" className="ghost-button" onClick={() => void handleDiagnostics()} disabled={diagnosing}>
                {diagnosing ? <Loader2 className="spin" size={16} /> : <RefreshCw size={16} />}
                <span>Jalankan Diagnostics</span>
              </button>
              <button type="button" className="ghost-button" onClick={() => void handleTestSpreadsheet()} disabled={sheetTesting}>
                {sheetTesting ? <Loader2 className="spin" size={16} /> : <ScanLine size={16} />}
                <span>Test Spreadsheet</span>
              </button>
            </div>
          </form>
        )}
      </div>

      {sheetResult !== null ? (
        <div className={`panel banner ${sheetResult.ok ? 'banner-success' : 'banner-error'}`} style={{ display: 'grid', gap: '10px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {sheetResult.ok ? <CircleCheckBig size={18} /> : <CircleAlert size={18} />}
            <strong>{sheetResult.message}</strong>
          </div>
          {sheetResult.ok && sheetResult.headers ? (
            <div>
              <div className="muted-text" style={{ fontSize: '12px', marginBottom: '6px' }}>Kolom terdeteksi: {sheetResult.headers.join(' · ')}</div>
              {sheetResult.firstDataRow ? (
                <div className="muted-text" style={{ fontSize: '12px' }}>Baris data pertama: {sheetResult.firstDataRow.join(' | ')}</div>
              ) : null}
            </div>
          ) : null}
          {!sheetResult.ok ? (
            <div className="muted-text" style={{ fontSize: '12px' }}>
              <div>Tahap gagal: <strong>{sheetResult.stage ?? 'unknown'}</strong></div>
              {sheetResult.rowCount !== undefined ? <div style={{ marginTop: '4px' }}>Baris terbaca: {sheetResult.rowCount}</div> : null}
              {sheetResult.delimiter ? <div style={{ marginTop: '4px' }}>Delimiter: <code>{sheetResult.delimiter}</code></div> : null}
              {sheetResult.rawPreview ? (
                <div style={{ marginTop: '8px' }}>
                  <div style={{ marginBottom: '4px' }}>Raw preview (800 char pertama):</div>
                  <pre style={{ background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '4px', fontSize: '10px', overflowX: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all', maxHeight: '200px', overflowY: 'auto' }}>{sheetResult.rawPreview}</pre>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="panel compact-gap">
        <div className="panel-header">
          <div>
            <h2>Diagnostics Raspy</h2>
            <p>Dipakai untuk mengecek health, users, logs, dan device mode dari desktop.</p>
          </div>
        </div>

        {diagnostics ? (
          <div className="diagnostics-grid">
            <article className="diagnostic-card">
              <span>Health</span>
              <strong className={diagnostics.checks.health.ok ? 'online-text' : 'offline-text'}>{diagnostics.checks.health.ok ? 'OK' : 'FAIL'}</strong>
              <small>{diagnostics.checks.health.message}</small>
            </article>
            <article className="diagnostic-card">
              <span>Users</span>
              <strong className={diagnostics.checks.users.ok ? '' : 'offline-text'}>{diagnostics.checks.users.count}</strong>
              <small>{diagnostics.checks.users.ok ? 'Daftar user terbaca' : diagnostics.checks.users.message ?? 'Gagal membaca user'}</small>
            </article>
            <article className="diagnostic-card">
              <span>Logs</span>
              <strong className={diagnostics.checks.logs.ok ? '' : 'offline-text'}>{diagnostics.checks.logs.count}</strong>
              <small>{diagnostics.checks.logs.ok ? 'Log akses terbaca' : diagnostics.checks.logs.message ?? 'Gagal membaca log'}</small>
            </article>
            <article className="diagnostic-card">
              <span>Device Mode</span>
              <strong className={diagnostics.checks.deviceModeWrite.ok ? 'online-text' : 'offline-text'}>
                {diagnostics.checks.deviceModeWrite.ok ? 'WRITE OK' : 'WRITE FAIL'}
              </strong>
              <small>{diagnostics.checks.deviceModeWrite.message}</small>
            </article>
          </div>
        ) : (
          <div className="empty-card">Belum ada hasil diagnostics. Simpan URL Raspy lalu jalankan diagnostics.</div>
        )}
      </div>
    </section>
  )
}

function AppShell({ session, onLogout, showToast }: { session: AuthUser; onLogout: () => Promise<void>; showToast: (message: string, type?: ToastKind) => void }) {
  const [activeTab, setActiveTab] = useState<TabId>(session.role === 'admin' ? 'dashboard' : 'users')
  const [enrollmentMode, setEnrollmentMode] = useState<EnrollmentMode>('new')
  const [selectedUser, setSelectedUser] = useState<UserRecord | null>(null)
  const [settingsMessage, setSettingsMessage] = useState('')

  useEffect(() => {
    if (session.role !== 'admin' && (activeTab === 'dashboard' || activeTab === 'logs' || activeTab === 'settings')) {
      setActiveTab('users')
    }
  }, [activeTab, session.role])

  const loadSettingsMessage = async () => {
    try {
      const data = await requestJson<SettingsPayload>('/api/settings')
      const raspyUrl = data.settings.raspy_api_base_url?.trim() || 'belum diatur'
      const spreadsheet = data.settings.spreadsheet_enabled === '1' ? 'Spreadsheet aktif' : 'Spreadsheet nonaktif'
      setSettingsMessage(`Raspy: ${raspyUrl} · ${spreadsheet}`)
    } catch {
      setSettingsMessage('Pengaturan integrasi belum terbaca')
    }
  }

  useEffect(() => {
    void loadSettingsMessage()
  }, [])

  const openNewEnrollment = () => {
    setEnrollmentMode('new')
    setSelectedUser(null)
    setActiveTab('enrollment')
  }

  const openRetrain = (user: UserRecord) => {
    setEnrollmentMode('retrain')
    setSelectedUser(user)
    setActiveTab('enrollment')
  }

  const handleDone = () => {
    setEnrollmentMode('new')
    setSelectedUser(null)
    setActiveTab('users')
  }

  return (
    <div className="app-shell">
      <div className="title-bar">{settingsMessage}</div>
      <Sidebar activeTab={activeTab} user={session} onSelect={setActiveTab} onLogout={() => void onLogout()} />
      <main className="main-content">
        {activeTab === 'dashboard' && session.role === 'admin' ? <DashboardPage /> : null}
        {activeTab === 'users' ? <UserManagementPage session={session} onAddUser={openNewEnrollment} onRetrain={openRetrain} showToast={showToast} /> : null}
        {activeTab === 'enrollment' ? (
          <EnrollmentPage
            mode={enrollmentMode}
            selectedUser={selectedUser}
            onDone={handleDone}
            onCancel={() => setActiveTab('users')}
            showToast={showToast}
          />
        ) : null}
        {activeTab === 'logs' && session.role === 'admin' ? <AccessLogsPage showToast={showToast} /> : null}
        {activeTab === 'settings' && session.role === 'admin' ? <SettingsPage onSettingsChanged={() => void loadSettingsMessage()} showToast={showToast} /> : null}
      </main>
    </div>
  )
}

export default function App() {
  const [session, setSession] = useState<AuthUser | null>(null)
  const [loggingIn, setLoggingIn] = useState(false)
  const [setupCompleted, setSetupCompleted] = useState(() => {
    return localStorage.getItem('setupWizardCompleted') === 'true'
  })
  const { toast, showToast } = useToast()

  const handleLogin = async (username: string, password: string) => {
    setLoggingIn(true)
    try {
      const data = await requestJson<LoginPayload>('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      setSession(data.user)
      showToast(`Login berhasil sebagai ${formatRole(data.user.role)}`)
    } finally {
      setLoggingIn(false)
    }
  }

  const handleLogout = async () => {
    await requestJson<ApiEnvelope>('/api/auth/logout', { method: 'POST' })
    setSession(null)
    showToast('Anda sudah keluar dari aplikasi')
  }

  const handleSetupComplete = () => {
    setSetupCompleted(true)
    localStorage.setItem('setupWizardCompleted', 'true')
    showToast('✅ Setup selesai! Sistem siap digunakan.')
  }

  return (
    <>
      {!setupCompleted ? (
        <SetupWizard onComplete={handleSetupComplete} />
      ) : session ? (
        <AppShell session={session} onLogout={handleLogout} showToast={showToast} />
      ) : (
        <LoginScreen onLogin={handleLogin} loading={loggingIn} />
      )}
      <Toast toast={toast} />
    </>
  )
}