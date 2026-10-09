const fs = require('node:fs');
const path = require('node:path');

// This synthetic app deliberately fails if executed. REA must only read it.
fs.writeFileSync(path.join(__dirname, '.executed'), 'Unexpected target execution');
throw new Error('This fixture is for static analysis only');

const { app, BrowserWindow, ipcMain } = require('electron');
const { searchItems } = require('./search.cjs');

ipcMain.handle('search:query', (_event, query) => searchItems(query));
app.whenReady().then(() => {
  const window = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  window.loadFile('index.html');
});
