document.addEventListener('DOMContentLoaded', () => {
  const submitBtn = document.getElementById('submitBtn');
  const addToJobBtn = document.getElementById('addToJobBtn');
  const textPreview = document.getElementById('textPreview');

  async function loadSelection() {
    const { selectedText = '', currentTabUrl = '' } = await browser.storage.local.get([
      'selectedText',
      'currentTabUrl',
    ]);
    document.getElementById('companyLink').value = currentTabUrl;
    if (selectedText) {
      const maxLength = 100;
      textPreview.textContent =
        selectedText.length > maxLength ? selectedText.slice(0, maxLength) + '...' : selectedText;
    } else {
      textPreview.textContent =
        'No text selected. Please select text and right-click to use this extension.';
    }
  }

  function setLoading(isLoading) {
    submitBtn.textContent = isLoading ? 'Sending...' : 'Submit';
    submitBtn.disabled = isLoading;
    addToJobBtn.disabled = isLoading;
  }

  async function sendToApi(data) {
    setLoading(true);
    const response = await browser.runtime.sendMessage({ action: 'sendToApi', data });
    setLoading(false);
    if (response?.success) {
      document.getElementById('companyName').value = '';
      document.getElementById('companyLink').value = '';
      textPreview.textContent = 'Sent successfully!';
      browser.storage.local.remove(['selectedText', 'currentTabUrl']);
      setTimeout(() => window.close(), 1500);
    } else {
      alert('Error: ' + (response ? response.error : 'Unknown error'));
    }
  }

  submitBtn.addEventListener('click', async () => {
    const { selectedText = '' } = await browser.storage.local.get(['selectedText']);
    if (!selectedText) {
      alert('No text selected. Please select text first.');
      return;
    }
    const data = {
      text: selectedText,
      companyName: document.getElementById('companyName').value,
      companyLink: document.getElementById('companyLink').value,
      type: document.getElementById('resumeType').value,
    };
    sendToApi(data);
  });

  addToJobBtn.addEventListener('click', async () => {
    const companyName = document.getElementById('companyName').value;
    const tabs = await browser.tabs.query({ active: true, currentWindow: true });
    const currentLink = tabs[0].url;
    document.getElementById('companyLink').value = currentLink;
    await browser.runtime.sendMessage({ action: 'clearSelectedText' });
    const data = {
      text: '',
      companyName,
      companyLink: currentLink,
      type: 'add-to-job',
    };
    sendToApi(data);
  });

  loadSelection();
});
