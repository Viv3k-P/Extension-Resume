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
    if (!Number.isNaN(rating)) {
      browser.storage.local.set({ lastMatchScore: rating });
      showNotification('Match Score', `Your resume matches ${rating}%`);
    } else {
      browser.storage.local.remove('lastMatchScore');
      showNotification('Success', 'Data successfully sent to API.');
    }
    return { success: true, rating };
  } catch (error) {
    console.error('Fetch error:', error);
    showNotification('Error', error.message);
    return { success: false, error: error.message };
  }
}

function extractJobDescription() {
  const headingKeywords = [
    'responsibilities',
    'job description',
    "what you'll do",
    'requirements',
    'role',
  ];
  const ignoreHeadings = ['about us', 'about the company'];
  const sections = [];

  document
    .querySelectorAll('h1, h2, h3, h4, h5, strong, b')
    .forEach((heading) => {
      const text = heading.innerText.toLowerCase();
      if (headingKeywords.some((k) => text.includes(k))) {
        let content = '';
        let el = heading.nextElementSibling;
        while (el) {
          const elText = el.innerText.trim();
          const lower = elText.toLowerCase();
          if (
            !elText ||
            headingKeywords.some((k) => lower.includes(k)) ||
            ignoreHeadings.some((k) => lower.includes(k))
          ) {
            break;
          }
          content += elText + '\n';
          el = el.nextElementSibling;
        }
        if (content) sections.push(content.trim());
      }
    });

  let best = sections.reduce(
    (a, b) => (b.length > a.length ? b : a),
    ''
  );

  if (!best) {
    const selectors = [
      'article',
      'section',
      'div[id*="job"]',
      'div[class*="job"]',
      'div[id*="description"]',
      'div[class*="description"]',
    ];
    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((el) => {
        const text = el.innerText.trim();
        if (text.length > best.length) {
          best = text;
        }
      });
    });
  }

  ignoreHeadings.forEach((term) => {
    const regex = new RegExp(term, 'ig');
    best = best.replace(regex, '');
  });

  return best.trim();
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

        let payload = {
          companyName: message.companyName,
          companyLink: message.companyLink,
          type: message.resumeType || 'normal-resume',
        };

        if (!text) {
          const htmlResults = await browser.tabs.executeScript(message.tabId, {
            code: 'document.documentElement.outerHTML',
          });
          const html = (htmlResults && htmlResults[0] ? htmlResults[0] : '').trim();
          if (!html) {
            sendResponse({
              success: false,
              error: 'No job description found. Please select text manually.',
            });
            return;
          }
          payload.html = html;
        } else {
          payload.text = text;
        }

        const result = await postData(payload);
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
