var browser = globalThis.browser || globalThis.chrome;

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
    const json = await response.json();
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    const rating = Number(json.rating);
    showNotification('Success', 'Data successfully sent to API.');
    return { success: true, rating };
  } catch (error) {
    console.error('Fetch error:', error);
    showNotification('Error', error.message);
    return { success: false, error: error.message };
  }
}

function extractJobDescription() {
  const selectors = [
    'article',
    'section',
    'div[id*="job"]',
    'div[class*="job"]',
    'div[id*="description"]',
    'div[class*="description"]',
  ];
  let best = '';
  selectors.forEach((selector) => {
    document.querySelectorAll(selector).forEach((el) => {
      const text = el.innerText.trim();
      if (text.length > best.length) {
        best = text;
      }
    });
  });
  return best;
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

  // Handle both names for the extraction flow.
  if (message.action === 'extractAndRate' || message.action === 'addJob') {
    browser.tabs
      .executeScript(message.tabId, {
        code: '(' + extractJobDescription.toString() + ')();',
      })
      .then(async (results) => {
        let text = (results && results[0] ? results[0] : '').trim();

        if (!text) {
          const { selectedText = '' } = await browser.storage.local.get(['selectedText']);
          text = selectedText.trim();
        }

        if (!text) {
          sendResponse({
            success: false,
            error: 'No job description found. Please select text manually.',
          });
          return;
        }

        const data = {
          text,
          companyName: message.companyName,
          companyLink: message.companyLink,
          type: message.resumeType || 'normal-resume',
        };

        const result = await postData(data);
        if (result.success) {
          browser.storage.local.remove(['selectedText', 'currentTabUrl']);
        }
        sendResponse(result);
      })
      .catch((error) => {
        console.error('Execution error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true;
  }

  if (message.action === 'canExtract') {
    browser.tabs
      .executeScript(message.tabId, {
        code: '(' + extractJobDescription.toString() + ')();',
      })
      .then((results) => {
        const text = (results && results[0] ? results[0] : '').trim();
        sendResponse({ canExtract: !!text });
      })
      .catch((error) => {
        console.error('Execution error:', error);
        sendResponse({ canExtract: false });
      });
    return true;
  }

  if (message.action === 'clearSelectedText') {
    browser.storage.local.set({ selectedText: '' }).then(() => sendResponse({ success: true }));
    return true;
  }

  return false;
});

createContextMenu();
