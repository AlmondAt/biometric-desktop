import { useRef, useState, useCallback } from 'react'
import Webcam from 'react-webcam'
import { Camera, Play, Loader2, CheckCircle2, AlertCircle, Trash2 } from 'lucide-react'

interface CapturedPhoto {
  id: string
  base64: string
  timestamp: number     
}

function EnrollmentView({ onClose }: { onClose: () => void }): JSX.Element {
  const webcamRef = useRef<Webcam>(null)
  const [photos, setPhotos] = useState<CapturedPhoto[]>([])
  const [userId, setUserId] = useState('')
  const [isTraining, setIsTraining] = useState(false)
  const [trainingProgress, setTrainingProgress] = useState('')
  const [trainingStatus, setTrainingStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const capturePhoto = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot()
    if (imageSrc) {
      const newPhoto: CapturedPhoto = {
        id: `photo_${Date.now()}`,
        base64: imageSrc,
        timestamp: Date.now()
      }
      setPhotos(prev => [...prev, newPhoto])
    }
  }, [])

  const removePhoto = (id: string) => {
    setPhotos(prev => prev.filter(p => p.id !== id))
  }

  const clearAll = () => {
    setPhotos([])
  }

  const startTraining = async () => {
    if (!userId.trim()) {
      setErrorMessage('User ID diperlukan!')
      return
    }

    if (photos.length === 0) {
      setErrorMessage('Ambil minimal 1 foto terlebih dahulu!')
      return
    }

    setIsTraining(true)
    setTrainingProgress('Menginisialisasi...')
    setTrainingStatus('idle')
    setErrorMessage('')

    try {
      // Call backend API untuk training
      const response = await fetch('http://localhost:3001/api/training/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId.trim(),
          photos: photos.map(p => p.base64)
        })
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(data?.message || `Training failed: ${response.statusText}`)
      }

      if (data.success) {
        setTrainingProgress('✅ Training selesai! Embeddings berhasil disimpan.')
        setTrainingStatus('success')
        // Reset form after 3 seconds
        setTimeout(() => {
          setPhotos([])
          setUserId('')
        }, 3000)
      } else {
        throw new Error(data.message || 'Training gagal')
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Training gagal'
      setTrainingProgress(`❌ ${message}`)
      setTrainingStatus('error')
      setErrorMessage(message)
    } finally {
      setIsTraining(false)
    }
  }

  return (
    <div className="enrollment-container" style={styles.container}>
      <div style={styles.header}>
        <h2>👤 Enrollment Wajah</h2>
        <button onClick={onClose} style={styles.closeBtn}>✕</button>
      </div>

      <div style={styles.content}>
        {/* Left: Webcam */}
        <div style={styles.webcamSection}>
          <div style={styles.webcamWrapper}>
            <Webcam
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              width={400}
              height={300}
              style={styles.webcam}
            />
          </div>

          <div style={styles.controls}>
            <input
              type="text"
              placeholder="User ID (e.g., 1, john, user_2)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              style={styles.input}
              disabled={isTraining}
            />
            
            <button
              onClick={capturePhoto}
              disabled={isTraining}
              style={{
                ...styles.captureBtn,
                opacity: isTraining ? 0.5 : 1,
                cursor: isTraining ? 'not-allowed' : 'pointer'
              }}
            >
              <Camera size={20} /> Ambil Foto ({photos.length})
            </button>

            {photos.length > 0 && (
              <>
                <button
                  onClick={startTraining}
                  disabled={isTraining}
                  style={{
                    ...styles.trainBtn,
                    opacity: isTraining ? 0.5 : 1,
                    cursor: isTraining ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isTraining ? (
                    <>
                      <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                      Training...
                    </>
                  ) : (
                    <>
                      <Play size={20} /> Mulai Training Wajah
                    </>
                  )}
                </button>

                {!isTraining && (
                  <button
                    onClick={clearAll}
                    style={styles.clearBtn}
                  >
                    <Trash2 size={20} /> Hapus Semua
                  </button>
                )}
              </>
            )}
          </div>

          {trainingProgress && (
            <div style={{
              ...styles.statusBox,
              borderLeft: `4px solid ${trainingStatus === 'success' ? '#10b981' : trainingStatus === 'error' ? '#ef4444' : '#3b82f6'}`
            }}>
              {trainingStatus === 'success' && <CheckCircle2 size={20} color="#10b981" />}
              {trainingStatus === 'error' && <AlertCircle size={20} color="#ef4444" />}
              {trainingStatus === 'idle' && <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />}
              <span>{trainingProgress}</span>
            </div>
          )}
        </div>

        {/* Right: Photo Grid */}
        <div style={styles.photoGrid}>
          <h3>📷 Foto Terambil ({photos.length})</h3>
          <div style={styles.grid}>
            {photos.map((photo) => (
              <div key={photo.id} style={styles.photoCard}>
                <img src={photo.base64} alt="Captured" style={styles.photoImg} />
                <button
                  onClick={() => removePhoto(photo.id)}
                  style={styles.deletePhotoBtn}
                  title="Hapus foto"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          
          <div style={styles.info}>
            <p>✓ Rekomendasi: Ambil 10-15 foto dari berbagai angle</p>
            <p>✓ Setiap foto akan di-augmentasi menjadi 50 variasi</p>
            <p>✓ Total: {photos.length} × 50 = {photos.length * 50} embeddings</p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div style={styles.errorBanner}>
          <AlertCircle size={20} />
          {errorMessage}
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100vh',
    backgroundColor: '#f3f4f6',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    backgroundColor: '#1f2937',
    color: 'white',
    borderBottom: '1px solid #374151',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '24px',
    cursor: 'pointer',
    padding: '4px 8px',
  },
  content: {
    display: 'flex',
    flex: 1,
    gap: '20px',
    padding: '20px 24px',
    overflow: 'auto',
  },
  webcamSection: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
    flex: 0.5,
  },
  webcamWrapper: {
    display: 'flex',
    justifyContent: 'center',
    backgroundColor: 'black',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  webcam: {
    width: '100%',
    height: 'auto',
  },
  controls: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  captureBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px 16px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  trainBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px 16px',
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  clearBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px 16px',
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  statusBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    backgroundColor: '#f0fdf4',
    borderRadius: '6px',
    fontSize: '14px',
    lineHeight: '1.5',
  },
  photoGrid: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
    flex: 0.5,
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '8px',
    maxHeight: '400px',
    overflowY: 'auto' as const,
  },
  photoCard: {
    position: 'relative' as const,
    borderRadius: '6px',
    overflow: 'hidden',
    backgroundColor: '#f3f4f6',
    aspectRatio: '1',
  },
  photoImg: {
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
  },
  deletePhotoBtn: {
    position: 'absolute' as const,
    top: '4px',
    right: '4px',
    width: '24px',
    height: '24px',
    background: 'rgba(0,0,0,0.7)',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  info: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
    padding: '12px',
    backgroundColor: '#dbeafe',
    borderRadius: '6px',
    fontSize: '12px',
    color: '#1e40af',
    marginTop: 'auto',
  },
  errorBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 24px',
    backgroundColor: '#fee2e2',
    color: '#991b1b',
    borderTop: '1px solid #fecaca',
  },
}

export default EnrollmentView
