document.addEventListener('DOMContentLoaded', function() {
  const submitBtn = document.getElementById('submitBtn');
  const addToJobBtn = document.getElementById('addToJobBtn');
  const textPreview = document.getElementById('textPreview');

  // Load selected text and current tab URL from storage and display it
  browser.storage.local.get(['selectedText', 'currentTabUrl'], function(result) {
    const selectedText = result.selectedText || '';
    const currentTabUrl = result.currentTabUrl || '';

    document.getElementById('companyLink').value = currentTabUrl;

    if (selectedText) {
      const maxLength = 100;
      const displayText = selectedText.length > maxLength
        ? selectedText.substring(0, maxLength) + '...'
        : selectedText;
      textPreview.textContent = displayText;
    } else {
      textPreview.textContent = 'No text selected. Please select text and right-click to use this extension.';
    }
  });

  // Function to send data to background script for API call
  function sendToApi(data) {
    submitBtn.textContent = 'Sending...';
    submitBtn.disabled = true;
    addToJobBtn.disabled = true;

    browser.runtime.sendMessage({
      action: "sendToApi",
      data: data
    }, function(response) {
      submitBtn.textContent = 'Submit';
      submitBtn.disabled = false;
      addToJobBtn.disabled = false;

      if (response && response.success) {
        document.getElementById('companyName').value = '';
        document.getElementById('companyLink').value = '';
        textPreview.textContent = 'Sent successfully!';
        browser.storage.local.remove(['selectedText', 'currentTabUrl']);
        setTimeout(() => window.close(), 1500);
      } else {
        alert("Error: " + (response ? response.error : "Unknown error"));
      }
    });
  }

  // Submit button handler
  submitBtn.addEventListener('click', function() {
    const companyName = document.getElementById('companyName').value;
    const companyLink = document.getElementById('companyLink').value;
    const resumeType = document.getElementById('resumeType').value;

    browser.storage.local.get(['selectedText'], function(result) {
      const selectedText = result.selectedText || '';
      if (!selectedText) {
        alert('No text selected. Please select text first.');
        return;
      }

      const data = {
        text: selectedText,
        companyName: companyName,
        companyLink: companyLink,
        type: resumeType
      };

      sendToApi(data);
    });
  });

  // Add to Job button handler
  addToJobBtn.addEventListener('click', function() {
    const companyName = document.getElementById('companyName').value;

    // Get current tab URL dynamically
    browser.tabs.query({ active: true, currentWindow: true }).then(tabs => {
      const currentLink = tabs[0].url;
      document.getElementById('companyLink').value = currentLink;

      // Clear selectedText before sending so text is empty
      browser.runtime.sendMessage({ action: "clearSelectedText" }, function() {
        const data = {
          text: '', // no text, for add-to-job
          companyName: companyName,
          companyLink: currentLink,
          type: 'add-to-job'
        };

        sendToApi(data);
      });
    });
  });
});
