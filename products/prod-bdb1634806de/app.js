// AI-Factory Generated Application
// Main application logic

const API_BASE = '/api';

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}/${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Application initialized');
    
    // Check API health
    fetchData('health').then(data => {
        if (data) {
            console.log('API Status:', data.status);
        }
    }).catch(err => {
        console.warn('API not available - running in standalone mode');
    });
});

export { fetchData };