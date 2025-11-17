const API_URL = 'http://localhost:5000/api';
let allExpenses = [];
let currencySymbol = '$';
let chartInstances = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadExpenses();
    setDefaultDate();
    initializeTheme();
    setupCharts();
});

// Theme Toggle
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcon();
    }
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    updateThemeIcon();
    updateCharts();
}

function updateThemeIcon() {
    const icon = document.getElementById('theme-toggle').querySelector('i');
    const isDark = document.body.classList.contains('dark-mode');
    icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
}

// Event Listeners
function initializeEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });

    // Forms
    document.getElementById('expense-form').addEventListener('submit', handleAddExpense);
    document.getElementById('currency').addEventListener('change', handleCurrencyChange);
    document.getElementById('clear-all-btn').addEventListener('click', handleClearAll);

    // Filters
    document.getElementById('filter-category').addEventListener('change', filterExpenses);
    document.getElementById('filter-type').addEventListener('change', filterExpenses);
}

function handleNavigation(e) {
    const page = e.currentTarget.dataset.page;
    showPage(page);
}

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Remove active from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected page
    document.getElementById(pageName).classList.add('active');
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');

    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        expenses: 'All Expenses',
        analytics: 'Analytics',
        settings: 'Settings'
    };
    document.getElementById('page-title').textContent = titles[pageName] || 'Dashboard';

    // Update charts if analytics page
    if (pageName === 'analytics') {
        setTimeout(updateCharts, 100);
    }
}

// Expense Management
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
}

async function handleAddExpense(e) {
    e.preventDefault();

    const expense = {
        description: document.getElementById('description').value,
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        date: document.getElementById('date').value,
        type: document.getElementById('type').value
    };

    try {
        const response = await fetch(`${API_URL}/expenses`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(expense)
        });

        if (!response.ok) throw new Error('Failed to add expense');

        loadExpenses();
        e.target.reset();
        setDefaultDate();
        showNotification('Expense added successfully!', 'success');
    } catch (error) {
        console.error('Error adding expense:', error);
        showNotification('Error adding expense', 'error');
    }
}

async function loadExpenses() {
    try {
        const response = await fetch(`${API_URL}/expenses`);
        if (!response.ok) throw new Error('Failed to load expenses');
        
        allExpenses = await response.json();
        updateDashboard();
        displayTransactions();
        displayExpensesTable();
        updateCharts();
    } catch (error) {
        console.error('Error loading expenses:', error);
        showNotification('Error loading expenses', 'error');
    }
}

async function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) return;

    try {
        const response = await fetch(`${API_URL}/expenses/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete expense');

        loadExpenses();
        showNotification('Expense deleted successfully!', 'success');
    } catch (error) {
        console.error('Error deleting expense:', error);
        showNotification('Error deleting expense', 'error');
    }
}

// Dashboard Updates
function updateDashboard() {
    const income = allExpenses
        .filter(e => e.type === 'income')
        .reduce((sum, e) => sum + e.amount, 0);

    const expenses = allExpenses
        .filter(e => e.type === 'expense')
        .reduce((sum, e) => sum + e.amount, 0);

    const balance = income - expenses;

    document.getElementById('income-total').textContent = formatCurrency(income);
    document.getElementById('expense-total').textContent = formatCurrency(expenses);
    document.getElementById('balance-total').textContent = formatCurrency(balance);
}

function displayTransactions() {
    const container = document.getElementById('transactions-list');
    const recent = allExpenses.slice(-5).reverse();

    if (recent.length === 0) {
        container.innerHTML = '<p class="text-muted">No transactions yet. Add one to get started!</p>';
        return;
    }

    container.innerHTML = recent.map(expense => `
        <div class="transaction-item ${expense.type}">
            <div class="transaction-content">
                <div class="transaction-description">${escape(expense.description)}</div>
                <div class="transaction-meta">${expense.category} • ${new Date(expense.date).toLocaleDateString()}</div>
            </div>
            <div class="transaction-amount ${expense.type}">
                ${expense.type === 'income' ? '+' : '-'}${formatCurrency(expense.amount)}
            </div>
        </div>
    `).join('');
}

function displayExpensesTable() {
    const tbody = document.getElementById('expenses-tbody');
    const filtered = filterExpensesList();

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No transactions yet</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(expense => `
        <tr>
            <td>${new Date(expense.date).toLocaleDateString()}</td>
            <td>${escape(expense.description)}</td>
            <td>${expense.category}</td>
            <td class="amount ${expense.type}">${expense.type === 'income' ? '+' : '-'}${formatCurrency(expense.amount)}</td>
            <td><span class="badge bg-${expense.type === 'income' ? 'success' : 'danger'}">${expense.type}</span></td>
            <td>
                <button class="btn btn-small btn-danger" onclick="deleteExpense(${expense.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

function filterExpensesList() {
    const category = document.getElementById('filter-category').value;
    const type = document.getElementById('filter-type').value;

    return allExpenses.filter(expense => {
        const categoryMatch = !category || expense.category === category;
        const typeMatch = !type || expense.type === type;
        return categoryMatch && typeMatch;
    }).sort((a, b) => new Date(b.date) - new Date(a.date));
}

function filterExpenses() {
    displayExpensesTable();
}

// Charts
function setupCharts() {
    const categoryCtx = document.getElementById('categoryChart');
    const monthlyCtx = document.getElementById('monthlyChart');

    if (categoryCtx) {
        chartInstances.category = new Chart(categoryCtx, {
            type: 'doughnut',
            data: { labels: [], datasets: [{ data: [], backgroundColor: [] }] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    if (monthlyCtx) {
        chartInstances.monthly = new Chart(monthlyCtx, {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

function updateCharts() {
    updateCategoryChart();
    updateMonthlyChart();
    updateCategoryBreakdown();
}

function updateCategoryChart() {
    if (!chartInstances.category) return;

    const expenses = allExpenses.filter(e => e.type === 'expense');
    const categoryData = {};

    expenses.forEach(e => {
        categoryData[e.category] = (categoryData[e.category] || 0) + e.amount;
    });

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);

    chartInstances.category.data = {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderWidth: 2,
            borderColor: document.body.classList.contains('dark-mode') ? '#1f2937' : 'white'
        }]
    };
    chartInstances.category.update();
}

function updateMonthlyChart() {
    if (!chartInstances.monthly) return;

    const monthlyData = {};
    allExpenses.forEach(e => {
        const month = new Date(e.date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
        if (!monthlyData[month]) {
            monthlyData[month] = { income: 0, expense: 0 };
        }
        monthlyData[month][e.type] += e.amount;
    });

    const labels = Object.keys(monthlyData);
    const incomeData = labels.map(m => monthlyData[m].income);
    const expenseData = labels.map(m => monthlyData[m].expense);

    chartInstances.monthly.data = {
        labels: labels,
        datasets: [
            {
                label: 'Income',
                data: incomeData,
                backgroundColor: '#10b981',
                borderColor: '#10b981',
                borderWidth: 1
            },
            {
                label: 'Expenses',
                data: expenseData,
                backgroundColor: '#ef4444',
                borderColor: '#ef4444',
                borderWidth: 1
            }
        ]
    };
    chartInstances.monthly.update();
}

function updateCategoryBreakdown() {
    const container = document.getElementById('category-breakdown');
    const expenses = allExpenses.filter(e => e.type === 'expense');
    const categoryData = {};

    expenses.forEach(e => {
        categoryData[e.category] = (categoryData[e.category] || 0) + e.amount;
    });

    if (Object.keys(categoryData).length === 0) {
        container.innerHTML = '<p class="text-muted">No expense data available yet</p>';
        return;
    }

    const total = Object.values(categoryData).reduce((a, b) => a + b, 0);

    container.innerHTML = Object.entries(categoryData)
        .sort((a, b) => b[1] - a[1])
        .map(([category, amount]) => {
            const percentage = ((amount / total) * 100).toFixed(1);
            return `
                <div class="breakdown-item">
                    <div>
                        <div class="breakdown-label">${category}</div>
                        <div style="font-size: 0.75rem; color: #9ca3af;">${percentage}%</div>
                    </div>
                    <div class="breakdown-value">${formatCurrency(amount)}</div>
                </div>
            `;
        })
        .join('');
}

// Settings
function handleCurrencyChange(e) {
    const currency = e.target.value;
    const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹' };
    currencySymbol = symbols[currency];
    localStorage.setItem('currency', currency);
    localStorage.setItem('currencySymbol', currencySymbol);
    updateDashboard();
    displayTransactions();
    displayExpensesTable();
}

async function handleClearAll() {
    if (!confirm('Are you sure you want to delete ALL expenses? This cannot be undone!')) return;

    try {
        const response = await fetch(`${API_URL}/expenses`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to clear all');

        loadExpenses();
        showNotification('All expenses cleared!', 'success');
    } catch (error) {
        console.error('Error clearing expenses:', error);
        showNotification('Error clearing expenses', 'error');
    }
}

// Utilities
function formatCurrency(amount) {
    return currencySymbol + amount.toFixed(2);
}

function escape(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    alert.style.zIndex = '9999';
    alert.textContent = message;
    document.body.appendChild(alert);

    setTimeout(() => alert.remove(), 3000);
}
