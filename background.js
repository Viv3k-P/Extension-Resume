// Create context menu item
browser.contextMenus.create({
  id: "send-to-api",
  title: "Send Selected Text to API",
  contexts: ["selection"]
}, () => {
  if (browser.runtime.lastError) {
    console.error(browser.runtime.lastError);
  } else {
    console.log("Context menu item created");
  }
});

// Handle context menu clicks
browser.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-to-api") {
    console.log("Selected text:", info.selectionText);
    // Save selected text and tab URL
    browser.storage.local.set({
      selectedText: info.selectionText,
      currentTabUrl: tab.url
    }, () => {
      browser.browserAction.openPopup();
    });
  }
});

// Listen for messages from popup.js
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "sendToApi") {
    console.log("Sending data to API:", message.data);
    fetch("http://localhost:5000/save-text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(message.data)
    })
    .then(response => {
      if (response.ok) {
        console.log("Data successfully sent to API.");
        browser.notifications.create({
          type: "basic",
          iconUrl: "icon.png",
          title: "Success",
          message: "Data successfully sent to API."
        });
        sendResponse({ success: true });
      } else {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
    })
    .catch(error => {
      console.error("Fetch error:", error);
      browser.notifications.create({
        type: "basic",
        iconUrl: "icon.png",
        title: "Error",
        message: error.message
      });
      sendResponse({ success: false, error: error.message });
    });
    return true; // async response
  }

  if (message.action === "clearSelectedText") {
    browser.storage.local.set({ selectedText: '' });
    sendResponse({ success: true });
  }
});
