document.addEventListener('DOMContentLoaded', function() {
    const platformSelect = document.getElementById('platformSelect');
    const criteriaContainer = document.getElementById('criteriaContainer');
    const saveCriteriaButton = document.getElementById('saveCriteria');
    const platformCriteria = document.getElementById('platformCriteria');
    const saveApiKeyButton = document.getElementById('saveApiKey');
    const apiKeyInput = document.getElementById('apiKey');
    const toggleApiKeyButton = document.getElementById('toggleApiKey');
    
    // API key'i localStorage'dan al ve metin kutusuna yerleştir
    const savedApiKey = localStorage.getItem('apiKey');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // API key'in görünürlüğünü toggle etmek için
    toggleApiKeyButton.addEventListener('click', function() {
        if (apiKeyInput.type === "password") {
            apiKeyInput.type = "text";
            toggleApiKeyButton.textContent = "Hide";
        } else {
            apiKeyInput.type = "password";
            toggleApiKeyButton.textContent = "Show";
        }
    });

    // API key kaydet
    saveApiKeyButton.addEventListener('click', function() {
        const apiKey = apiKeyInput.value;

        if (apiKey) {
            localStorage.setItem('apiKey', apiKey);
            alert('Your API key has been saved successfully!');
        } else {
            alert('Please enter an API key.');
        }
    });

    // Platform seçildiğinde, kriterleri localStorage'dan al ve göster
    platformSelect.addEventListener('change', function() {
        const platform = platformSelect.value;
        if (platform) {
            const savedCriteria = localStorage.getItem(`criteria_${platform}`);
            platformCriteria.value = savedCriteria ? savedCriteria : '';
            criteriaContainer.style.display = 'block';
        } else {
            criteriaContainer.style.display = 'none';
        }
    });

    // Kriterleri kaydet
    saveCriteriaButton.addEventListener('click', function() {
        const platform = platformSelect.value;
        const criteria = platformCriteria.value;

        if (platform && criteria) {
            localStorage.setItem(`criteria_${platform}`, criteria);
            alert('Your data has been saved successfully!');
        } else {
            alert('Please select a platform and enter criteria.');
        }
    });
});
