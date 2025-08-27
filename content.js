// Create a context menu item
browser.contextMenus.create({
    id: "send-to-api",
    title: "Send Selected Text to API",
    contexts: ["selection"]  // Only show this menu item for selected text
  }, () => {
    if (browser.runtime.lastError) {
      console.error(browser.runtime.lastError);
    } else {
      console.log("Context menu item created");
    }
  });
  
  // Add a listener for the context menu item
  browser.contextMenus.onClicked.addListener((info) => {
    if (info.menuItemId === "send-to-api") {
      console.log("Sending text to API:", info.selectionText);  // Log the text being sent
      browser.runtime.sendMessage({ text: info.selectionText });
    }
  });
  