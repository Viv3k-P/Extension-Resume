document.addEventListener('DOMContentLoaded', () => {
  const submitBtn = document.getElementById('submitBtn');
  const extractBtn = document.getElementById('extractBtn');
  const textPreview = document.getElementById('textPreview');
  const matchScore = document.getElementById('matchScore');

  async function loadSelection() {
    const { selectedText = '', currentTabUrl = '' } = await browser.storage.local.get([
      'selectedText',
      'currentTabUrl',
    ]);
    const {
      selectedText = '',
      currentTabUrl = '',
      lastMatchScore,
    } = await browser.storage.local.get(['selectedText', 'currentTabUrl', 'lastMatchScore']);
    document.getElementById('companyLink').value = currentTabUrl;

    if (selectedText) {
      const maxLength = 100;
      textPreview.textContent =
        selectedText.length > maxLength ? selectedText.slice(0, maxLength) + '...' : selectedText;
    } else {
      textPreview.textContent =
        'No text selected. Please select text and right-click to use this extension.';
    }

    const storedRating = Number(lastMatchScore);
    if (!Number.isNaN(storedRating)) {
      matchScore.textContent = `Match: ${storedRating}%`;
    } else {
      matchScore.textContent = '';
    }

    const tabs = await browser.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    const { canExtract } = await browser.runtime.sendMessage({ action: 'canExtract', tabId: currentTab.id });
    extractBtn.disabled = !canExtract;
  }

  function setLoading(isLoading) {
    submitBtn.textContent = isLoading ? 'Sending...' : 'Submit';
    submitBtn.disabled = isLoading;
    extractBtn.disabled = isLoading;
  }

  async function sendToApi(data) {
    await browser.storage.local.remove('lastMatchScore');
    matchScore.textContent = '';
    setLoading(true);
    const response = await browser.runtime.sendMessage({ action: 'sendToApi', data });
    setLoading(false);
    if (response?.success) {
      document.getElementById('companyName').value = '';
      document.getElementById('companyLink').value = '';
      textPreview.textContent = 'Sent successfully!';
      browser.storage.local.remove(['selectedText', 'currentTabUrl']);
      setTimeout(() => window.close(), 1500);

      const rating = Number(response.rating);
      if (!Number.isNaN(rating)) {
        matchScore.textContent = `Match: ${rating}%`;
        await browser.storage.local.set({ lastMatchScore: rating });
        // Keep the popup open so the user can see the rating
      } else {
        setTimeout(() => window.close(), 1500);
      }
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

  extractBtn.addEventListener('click', async () => {
    await browser.storage.local.remove('lastMatchScore');
    matchScore.textContent = '';
    const companyName = document.getElementById('companyName').value;
    const tabs = await browser.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];
    const currentLink = currentTab.url;
    document.getElementById('companyLink').value = currentLink;

    const { selectedText = '' } = await browser.storage.local.get(['selectedText']);
    const resumeType = document.getElementById('resumeType').value;
    setLoading(true);

    // Prefer enhanced flow that may return a rating; background can also treat this as addJob.
    const response = await browser.runtime.sendMessage({
      action: 'extractAndRate',
      companyName,
      companyLink: currentLink,
      tabId: currentTab.id,
      resumeType,
      fallbackText: selectedText,
    });

    setLoading(false);

    if (response?.success) {
      document.getElementById('companyName').value = '';
      document.getElementById('companyLink').value = '';
      textPreview.textContent = 'Sent successfully!';
      browser.storage.local.remove(['selectedText', 'currentTabUrl']);

      if (typeof response.rating === 'number') {
        matchScore.textContent = `Match: ${response.rating}%`;
      const rating = Number(response.rating);
      if (!Number.isNaN(rating)) {
        matchScore.textContent = `Match: ${rating}%`;
        await browser.storage.local.set({ lastMatchScore: rating });
        // Keep the popup open so the user can see the rating
      } else {
        setTimeout(() => window.close(), 1500);
      }
    } else {
      alert('Error: ' + (response ? response.error : 'Unknown error'));
    }
  });

  loadSelection();
});