function createContextMenu() {
  browser.contextMenus.create(
    {
      id: 'send-to-api',
      title: 'Send Selected Text to API',
      contexts: ['selection'],
    },
    () => browser.runtime.lastError && console.error(browser.runtime.lastError)
  );
}

function storeSelection(info, tab) {
  browser.storage.local.set(
    {
      selectedText: info.selectionText,
      currentTabUrl: tab.url,
    },
    () => browser.browserAction.openPopup()
  );
}

function showNotification(title, message) {
  browser.notifications.create({
    type: 'basic',
    iconUrl: 'icon.png',
    title,
    message,
  });
}

async function postData(data) {
  try {
    const response = await fetch('http://localhost:5000/save-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    showNotification('Success', 'Data successfully sent to API.');
    return { success: true };
  } catch (error) {
    console.error('Fetch error:', error);
    showNotification('Error', error.message);
    return { success: false, error: error.message };
  }
}

browser.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'send-to-api') {
    storeSelection(info, tab);
  }
});

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'sendToApi') {
    postData(message.data).then(sendResponse);
    return true;
  }
  if (message.action === 'clearSelectedText') {
    browser.storage.local.set({ selectedText: '' }).then(() => sendResponse({ success: true }));
    return true;
  }
  return false;
});

createContextMenu();
