import { app, BrowserWindow } from 'electron'
import path from 'path'
import { startServer } from './api'

let mainWindow: BrowserWindow | null = null

async function createWindow() {
  await startServer(app.getPath('userData'), app.getAppPath(), process.resourcesPath)

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#111827',
      symbolColor: '#ffffff',
    },
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    // mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(async () => {
  try {
    await createWindow()
  } catch (error) {
    console.error('Failed to start Electron app:', error)
    app.quit()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    void createWindow().catch((error) => {
      console.error('Failed to recreate window:', error)
    })
  }
})
