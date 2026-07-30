async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);

    if (response.status === 503 || response.status === 504) {
        window.location.href = '/login?reason=server_down';
        return null;
    }

    return response;
}