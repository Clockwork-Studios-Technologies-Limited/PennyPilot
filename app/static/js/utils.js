const server = ''

async function sendRequest(url, method, data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
    }
    if (data) {
        options.body = JSON.stringify(data)
    }
    const response = await fetch(url, options)
    return await response.json()
}

function toast(msg) {
    alert(msg)
}
