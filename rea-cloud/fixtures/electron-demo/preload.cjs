const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('demo', {
  search: (query) => ipcRenderer.invoke('search:query', query)
});
