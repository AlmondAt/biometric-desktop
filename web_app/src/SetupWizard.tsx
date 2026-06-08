import { useEffect, useState } from 'react'
import {
  CheckCircle2,
  AlertCircle,
  Loader2,
  Settings,
  Code,
  Database,
  Monitor,
  ArrowRight
} from 'lucide-react'

type CheckStatus = 'idle' | 'checking' | 'success' | 'error' | 'warning'

interface SetupCheck {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  status: CheckStatus
  message: string
  fixCommand?: string
}

interface SetupCheckResult {
  success: boolean
  message: string
  details?: Record<string, unknown>
}

interface SetupWizardProps {
  onComplete: () => void
}

export default function SetupWizard({ onComplete }: SetupWizardProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [checks, setChecks] = useState<SetupCheck[]>([
    {
      id: 'python',
      name: 'Python Executable',
      description: 'Python 3.10+ untuk menjalankan embedding extractor',
      icon: <Code size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    },
    {
      id: 'torch',
      name: 'PyTorch (torch)',
      description: 'Framework deep learning untuk face recognition',
      icon: <Database size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    },
    {
      id: 'facenet',
      name: 'FaceNet PyTorch',
      description: 'Model pre-trained untuk face embedding extraction',
      icon: <Code size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    },
    {
      id: 'opencv',
      name: 'OpenCV',
      description: 'Computer vision library untuk image processing & face detection',
      icon: <Code size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    },
    {
      id: 'webcam',
      name: 'Webcam Access',
      description: 'Camera untuk capture foto user saat enrollment',
      icon: <Monitor size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    },
    {
      id: 'storage',
      name: 'Storage Access',
      description: 'Akses tulis ke folder project untuk menyimpan embeddings.pkl',
      icon: <Database size={20} />,
      status: 'idle',
      message: 'Menunggu...'
    }
  ])
  const [raspyUrl, setRaspyUrl] = useState('http://192.168.1.100:5000')
  const [checksCompleted, setChecksCompleted] = useState(false)

  // Derived: all non-webcam checks must pass; webcam is optional
  const hasErrors = checks.some(c => c.status === 'error' && c.id !== 'webcam')
  const allChecksPassed = checksCompleted && !hasErrors

  useEffect(() => {
    if (currentStep === 1) {
      setChecksCompleted(false)
      runSetupChecks()
    }
  }, [currentStep])

  const updateCheck = (id: string, updates: Partial<SetupCheck>) => {
    setChecks(prev =>
      prev.map(check => (check.id === id ? { ...check, ...updates } : check))
    )
  }

  const runSetupChecks = async () => {
    // Reset all to idle first
    setChecks(prev => prev.map(c => ({ ...c, status: 'idle' as CheckStatus, message: 'Menunggu...' })))
    setChecksCompleted(false)

    for (const check of checks) {
      updateCheck(check.id, { status: 'checking', message: 'Memeriksa...' })

      let result: SetupCheckResult | null = null
      try {
        result = await runCheck(check.id)

        if (result.success) {
          updateCheck(check.id, {
            status: 'success',
            message: result.message
          })
        } else {
          // Webcam failure is a warning, not blocking
          const severity = check.id === 'webcam' ? 'warning' : 'error'
          updateCheck(check.id, {
            status: severity,
            message: result.message,
            fixCommand: result.details?.fixCommand as string | undefined
          })
        }
      } catch (error) {
        const severity = check.id === 'webcam' ? 'warning' : 'error'
        updateCheck(check.id, {
          status: severity,
          message: error instanceof Error ? error.message : 'Check gagal',
          fixCommand: result?.details?.fixCommand as string | undefined
        })
      }

      await new Promise(resolve => setTimeout(resolve, 400))
    }

    setChecksCompleted(true)
  }

  const runCheck = async (checkId: string): Promise<SetupCheckResult> => {
    const response = await fetch(`http://localhost:3001/api/setup/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ checkId })
    })

    if (!response.ok) {
      throw new Error(`Check gagal: ${response.statusText}`)
    }

    return response.json()
  }

  const handleSaveConfig = async () => {
    try {
      await fetch(`http://localhost:3001/api/setup/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raspy_api_base_url: raspyUrl
        })
      })

      localStorage.setItem('setupWizardCompleted', 'true')
      onComplete()
    } catch (error) {
      console.error('Failed to save config:', error)
    }
  }

  const getStatusIcon = (status: CheckStatus) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="text-green-500" size={24} />
      case 'error':
        return <AlertCircle className="text-red-500" size={24} />
      case 'warning':
        return <AlertCircle className="text-yellow-500" size={24} />
      case 'checking':
        return <Loader2 className="animate-spin text-blue-500" size={24} />
      default:
        return <div className="w-6 h-6 border-2 border-gray-300 rounded-full" />
    }
  }

  return (
    <div style={styles.overlay}>
      <div style={styles.container}>
        {/* Header */}
        <div style={styles.header}>
          <Settings size={32} style={{ color: '#2563eb' }} />
          <h1 style={styles.title}>🚀 Setup Wizard</h1>
          <p style={styles.subtitle}>Sistem Biometrik Desktop - Verifikasi Dependensi & Konfigurasi</p>
        </div>

        {/* Content */}
        {currentStep === 1 ? (
          <div style={styles.content}>
            <h2 style={styles.stepTitle}>Step 1: Verifikasi Dependensi</h2>
            <p style={styles.stepDesc}>
              Semua dependencies berikut WAJIB tersedia untuk enrollment wajah dan face recognition berfungsi dengan baik.
            </p>

            <div style={styles.checksList}>
              {checks.map(check => (
                <div key={check.id} style={styles.checkItem}>
                  <div style={styles.checkIcon}>{getStatusIcon(check.status)}</div>

                  <div style={styles.checkContent}>
                    <div style={styles.checkName}>{check.name}</div>
                    <div style={styles.checkDesc}>{check.description}</div>
                    <div
                      style={{
                        ...styles.checkMessage,
                        color:
                          check.status === 'success'
                            ? '#10b981'
                            : check.status === 'error'
                              ? '#ef4444'
                              : '#6b7280'
                      }}
                    >
                      {check.message}
                    </div>

                    {check.status === 'error' && check.fixCommand && (
                      <div style={styles.fixCommand}>
                        <strong>Cara fix:</strong>
                        <code>{check.fixCommand}</code>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {checksCompleted && (allChecksPassed ? (
              <div style={styles.successMessage}>
                ✅ Semua dependencies OK! Lanjut ke konfigurasi Raspy.
              </div>
            ) : (
              <div style={styles.errorMessage}>
                ⚠️ Ada dependencies yang belum terinstall. Jalankan fix commands di atas lalu klik "Periksa Lagi".
              </div>
            ))}

            <div style={styles.buttonGroup}>
              <button
                onClick={runSetupChecks}
                style={styles.secondaryBtn}
              >
                🔄 Periksa Lagi
              </button>
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!allChecksPassed}
                style={{
                  ...styles.primaryBtn,
                  opacity: allChecksPassed ? 1 : 0.5,
                  cursor: allChecksPassed ? 'pointer' : 'not-allowed'
                }}
              >
                Lanjut ke Konfigurasi <ArrowRight size={18} />
              </button>
            </div>
          </div>
        ) : (
          <div style={styles.content}>
            <h2 style={styles.stepTitle}>Step 2: Konfigurasi Raspy Backend</h2>
            <p style={styles.stepDesc}>
              Masukkan alamat IP atau URL Raspberry Pi yang menjalankan backend biometrik.
            </p>

            <div style={styles.configSection}>
              <label style={styles.configLabel}>🌐 Raspberry Pi API URL</label>
              <div style={styles.configNote}>
                Alamat IP atau domain Raspberry Pi dengan port backend
              </div>
              <input
                type="text"
                value={raspyUrl}
                onChange={e => setRaspyUrl(e.target.value)}
                placeholder="http://192.168.1.100:5000"
                style={styles.configInput}
              />
              <div style={styles.helpText}>
                💡 <strong>Contoh format:</strong>
                <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                  <li>Local network: <code>http://192.168.1.100:5000</code></li>
                  <li>VPN: <code>http://vpn-raspy.domain.com:5000</code></li>
                  <li>Cloud: <code>https://api.example.com:5000</code></li>
                </ul>
              </div>
            </div>

            <div style={styles.infoBox}>
              <strong>ℹ️ Catatan:</strong>
              <p>Raspy URL dapat diubah nanti di menu Settings. Untuk sekarang, pastikan IP/URL sudah benar atau skip dengan meninggalkan default.</p>
            </div>

            <div style={styles.buttonGroup}>
              <button
                onClick={() => setCurrentStep(1)}
                style={styles.secondaryBtn}
              >
                ← Kembali
              </button>
              <button
                onClick={handleSaveConfig}
                style={{
                  ...styles.primaryBtn,
                  opacity: raspyUrl.trim() ? 1 : 0.5
                }}
              >
                ✓ Selesai Setup
              </button>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        <div style={styles.progressBar}>
          <div
            style={{
              ...styles.progressFill,
              width: `${(currentStep / 2) * 100}%`
            }}
          />
        </div>
        <div style={styles.progressText}>
          Step {currentStep} dari 2
        </div>
      </div>
    </div>
  )
}

const styles = {
  overlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999
  },
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    maxWidth: '650px',
    width: '90%',
    maxHeight: '90vh',
    overflow: 'auto',
    display: 'flex',
    flexDirection: 'column' as const
  },
  header: {
    padding: '32px 24px',
    textAlign: 'center' as const,
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '12px'
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    margin: 0
  },
  subtitle: {
    fontSize: '14px',
    color: '#6b7280',
    margin: 0
  },
  content: {
    padding: '24px',
    flex: 1,
    overflow: 'auto'
  },
  stepTitle: {
    fontSize: '20px',
    fontWeight: '600',
    marginTop: 0,
    marginBottom: '8px'
  },
  stepDesc: {
    fontSize: '14px',
    color: '#6b7280',
    marginBottom: '24px'
  },
  checksList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
    marginBottom: '24px'
  },
  checkItem: {
    display: 'flex',
    gap: '16px',
    padding: '14px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e7eb'
  },
  checkIcon: {
    flexShrink: 0,
    marginTop: '2px'
  },
  checkContent: {
    flex: 1
  },
  checkName: {
    fontWeight: '600',
    fontSize: '14px',
    marginBottom: '2px'
  },
  checkDesc: {
    fontSize: '13px',
    color: '#6b7280',
    marginBottom: '4px'
  },
  checkMessage: {
    fontSize: '13px',
    fontWeight: '500'
  },
  fixCommand: {
    marginTop: '8px',
    padding: '8px',
    backgroundColor: '#fef2f2',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace' as const,
    color: '#dc2626',
    overflow: 'auto'
  },
  successMessage: {
    padding: '14px',
    backgroundColor: '#d1fae5',
    border: '1px solid #6ee7b7',
    borderRadius: '8px',
    color: '#065f46',
    marginBottom: '24px',
    fontSize: '14px',
    fontWeight: '500'
  },
  errorMessage: {
    padding: '14px',
    backgroundColor: '#fee2e2',
    border: '1px solid #fca5a5',
    borderRadius: '8px',
    color: '#7f1d1d',
    marginBottom: '24px',
    fontSize: '14px',
    fontWeight: '500'
  },
  configSection: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px'
  },
  configLabel: {
    display: 'block',
    fontWeight: '600',
    fontSize: '14px',
    marginBottom: '8px',
    color: '#111827'
  },
  configNote: {
    fontSize: '13px',
    color: '#6b7280',
    marginBottom: '12px'
  },
  configInput: {
    width: '100%',
    padding: '10px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'monospace',
    boxSizing: 'border-box' as const,
    marginBottom: '12px',
    color: '#111827',
    backgroundColor: '#ffffff',
    outline: 'none'
  },
  helpText: {
    fontSize: '13px',
    color: '#6b7280',
    lineHeight: '1.5'
  },
  infoBox: {
    padding: '12px',
    backgroundColor: '#dbeafe',
    border: '1px solid #93c5fd',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#1e40af',
    marginBottom: '24px'
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    paddingTop: '24px',
    borderTop: '1px solid #e5e7eb'
  },
  primaryBtn: {
    padding: '10px 20px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'background-color 0.2s'
  },
  secondaryBtn: {
    padding: '10px 20px',
    backgroundColor: '#e5e7eb',
    color: '#1f2937',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  progressBar: {
    height: '4px',
    backgroundColor: '#e5e7eb',
    borderRadius: '0 0 12px 12px'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2563eb',
    transition: 'width 0.3s ease'
  },
  progressText: {
    padding: '8px 24px',
    fontSize: '12px',
    color: '#6b7280',
    textAlign: 'center' as const
  }
}

