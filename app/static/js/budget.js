async function displayBudgets(data) {
    let result = document.querySelector('#budgetList')
    result.innerHTML = ''
    let html = ''

    if ('error' in data) {
        html += `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <p>Error: ${data.error}</p>
            </div>`
    } else {
        for (let b of data) {
            const pct   = b.amount > 0 ? Math.min((b.spent / b.amount) * 100, 100).toFixed(1) : 0
            const color = b.spent > b.amount ? 'red' : b.color

            html += `
                <div class="budget-item">
                    <div class="budget-item-top">
                        <div class="budget-item-left">
                            <span class="budget-icon">${b.icon}</span>
                            <div>
                                <div class="budget-name">${b.name}</div>
                                <div class="budget-sub">$${b.spent.toFixed(2)} spent of $${b.amount.toFixed(2)} limit</div>
                            </div>
                        </div>
                        <div class="budget-item-right">
                            <span class="budget-pct" style="color:var(--accent-${color})">${pct}%</span>
                            <button class="btn-delete" onclick="deleteBudget(${b.id})">✕</button>
                        </div>
                    </div>
                    <div class="progress-bar-bg" style="margin-bottom:0">
                        <div class="progress-bar-fill" style="width:${pct}%; background:var(--accent-${color})"></div>
                    </div>
                </div>`
        }
    }

    result.innerHTML = html
}

async function loadView() {
    let budgets = await sendRequest(`${server}/api/budgets`, 'GET')
    displayBudgets(budgets)
}

loadView()

async function addBudget() {
    const data = {
        name:   document.getElementById('budName').value.trim(),
        amount: parseFloat(document.getElementById('budAmount').value),
        color:  document.getElementById('budColor').value,
        icon:   document.getElementById('budIcon').value.trim() || '💰',
    }

    if (!data.name || !data.amount) {
        toast('Please provide a name and amount')
        return
    }

    let result = await sendRequest(`${server}/api/budgets`, 'POST', data)

    if ('error' in result) {
        toast('Error: ' + result.error)
    } else {
        toast('Budget category added!')
        clearForm()
    }

    loadView()
}

function clearForm() {
    document.getElementById('budName').value   = ''
    document.getElementById('budAmount').value = ''
    document.getElementById('budIcon').value   = ''
}

async function deleteBudget(id) {
    let result = await sendRequest(`${server}/api/budgets/${id}`, 'DELETE')

    if ('error' in result) {
        toast('Error: Could not delete')
    } else {
        toast('Budget removed')
    }

    loadView()
}
