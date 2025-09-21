const API_BASE_URL = 'http://localhost:5000';

// --- API Abstraction Layer ---
const DB = {
    login: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return response.json();
    },

    register: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return response.json();
    },

    getEmployeeData: async () => {
        const employeeId = localStorage.getItem('employeeId');
        if (!employeeId) return null;
        const response = await fetch(`${API_BASE_URL}/api/employee/${employeeId}`);
        return response.json();
    },

    setEmployeeData: async (employeeData) => {
        const employeeId = localStorage.getItem('employeeId');
        if (!employeeId) return;
        await fetch(`${API_BASE_URL}/api/employee/${employeeId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(employeeData)
        });
    },

    getAiChatResponse: async (query) => {
        const employeeId = localStorage.getItem('employeeId');
        if (!employeeId) return null;
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, employee_id: employeeId })
        });
        return response.json();
    }
};

// --- Page Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.id;

    // Если мы не на странице входа или регистрации, убедимся, что пользователь залогинен
    if (!['page-login', 'page-register', 'page-landing'].includes(pageId)) {
        if (!localStorage.getItem('employeeId')) {
            window.location.href = 'login.html';
            return;
        }
        renderHeader();
    }

    switch (pageId) {
        case 'page-login': initLoginPage(); break;
        case 'page-register': initRegisterPage(); break;
        case 'page-profile': initProfilePage(); break;
        case 'page-edit-profile': initEditProfilePage(); break;
    }
});


// --- Authentication Pages Logic ---

function initLoginPage() {
    const form = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = form.email.value;
        const password = form.password.value;
        const result = await DB.login(email, password);

        if (result.employee_id) {
            localStorage.setItem('employeeId', result.employee_id);
            window.location.href = 'profile.html';
        } else {
            errorMessage.textContent = result.error || 'Произошла ошибка';
        }
    });
}

function initRegisterPage() {
    const form = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = form.email.value;
        const password = form.password.value;
        const confirmPassword = form['confirm-password'].value;

        if (password !== confirmPassword) {
            errorMessage.textContent = 'Пароли не совпадают';
            return;
        }

        const result = await DB.register(email, password);

        if (result.employee_id) {
            // Сразу логиним пользователя после успешной регистрации
            localStorage.setItem('employeeId', result.employee_id);
            window.location.href = 'profile.html'; // Перенаправляем на профиль для заполнения данных
        } else {
            errorMessage.textContent = result.error || 'Произошла ошибка';
        }
    });
}

// --- Header Logic ---
async function renderHeader() {
    const headerContainer = document.getElementById('header-container');
    if (!headerContainer) return;
    const user = await DB.getEmployeeData();

    if (!user) {
        // Если не смогли загрузить юзера, возможно ID невалидный
        localStorage.removeItem('employeeId');
        window.location.href = 'login.html';
        return;
    }
    
    // ... остальной код рендеринга хедера без изменений, он будет использовать `user`
    headerContainer.innerHTML = `...`; // Сокращено для краткости

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('employeeId');
        window.location.href = 'index.html';
    });
}


// --- Profile and Edit-Profile Pages Logic (в основном без изменений) ---

async function initProfilePage() {
    const user = await DB.getEmployeeData();
    if (!user) return; // Защита на случай, если что-то пошло не так

    // ... весь код для отображения данных профиля остается без изменений
    // он просто будет использовать `user`, полученный по ID из localStorage
}

async function initEditProfilePage() {
    const user = await DB.getEmployeeData();
    if (!user) return;

    let tempUser = JSON.parse(JSON.stringify(user));

    // ... весь код для редактирования профиля остается без изменений

    document.getElementById('save-profile-btn').addEventListener('click', async () => {
        // ... логика обновления tempUser
        await DB.setEmployeeData(tempUser);
        window.location.href = 'profile.html';
    });
}

// ... остальные функции (initEmployeeChat и т.д.) остаются без изменений
// так как они вызываются из initProfilePage и получают `user` как аргумент
// или используют DB, который уже работает с ID из localStorage
