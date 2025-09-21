const XP_PER_LEVEL = 200;
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
        if (!response.ok) return null;
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
    const nonAuthPages = ['page-login', 'page-register', 'page-landing'];

    if (!nonAuthPages.includes(pageId) && !document.querySelector('html[data-page="index"]')) {
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
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessage.textContent = '';
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
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessage.textContent = '';
        const email = form.email.value;
        const password = form.password.value;
        const confirmPassword = form['confirm-password'].value;

        if (password !== confirmPassword) {
            errorMessage.textContent = 'Пароли не совпадают';
            return;
        }

        const result = await DB.register(email, password);

        if (result.employee_id) {
            localStorage.setItem('employeeId', result.employee_id);
            window.location.href = 'profile.html';
        } else {
            errorMessage.textContent = result.error || 'Произошла ошибка';
        }
    });
}

// --- Core UI Rendering ---
async function renderHeader() {
    const headerContainer = document.getElementById('header-container');
    if (!headerContainer) return;

    const user = await DB.getEmployeeData();

    if (!user) {
        localStorage.removeItem('employeeId');
        window.location.href = 'login.html';
        return;
    }

    const navLinks = `
        <a href="profile.html" class="text-gray-500 hover:text-accent transition-colors" data-link="profile">My Profile</a>
        <a href="#" class="text-gray-500 hover:text-accent transition-colors">Applications</a>
        <a href="#" class="text-gray-500 hover:text-accent transition-colors">Gifts</a>
    `;

    headerContainer.innerHTML = `
        <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="profile.html" class="text-xl font-bold text-text-dark">Career on Autopilot</a>
            <div class="flex items-center space-x-8">${navLinks}</div>
            <div class="flex items-center space-x-6">
                <img class="h-10 w-10 rounded-full object-cover" src="${user.avatar}" alt="User Avatar">
                <button id="logout-btn" class="text-sm text-gray-500 hover:text-accent">Выйти</button>
            </div>
        </nav>`;

    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    const activeLink = headerContainer.querySelector(`[data-link*="${currentPage}"]`);
    if (activeLink) activeLink.classList.add('text-accent', 'font-bold');

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('employeeId');
        window.location.href = 'index.html';
    });
}

async function initProfilePage() {
    const user = await DB.getEmployeeData();
    if (!user) return;

    document.getElementById('user-avatar-main').src = user.avatar;
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-role').textContent = user.role;

    const careerPathContainer = document.getElementById('career-path-container');
    if(user.careerPath && user.careerPath.length > 0) {
        careerPathContainer.innerHTML = user.careerPath.map(p => `
        <div class="mb-8">
            <div class="absolute -left-3.5 mt-1.5 h-6 w-6 bg-accent rounded-full border-4 border-white"></div>
            <p class="text-sm text-gray-500">${p.year}</p>
            <h4 class="font-bold">${p.role}</h4>
            <p class="text-sm text-gray-600">${p.project}</p>
        </div>`).join('');
    } else {
        careerPathContainer.innerHTML = '<p class="text-gray-500">Карьерный путь пока не заполнен.</p>';
    }
    
    const interestsContainer = document.getElementById('interests-container');
    interestsContainer.innerHTML = Object.entries(user.interests).map(([key, value]) => `
        <div class="flex items-center gap-4">
            <span class="w-32 capitalize">${key.replace('dataScience', 'Data Science').replace('mobileDev', 'Mobile Dev')}</span>
            <div class="w-full bg-secondary-bg rounded-full h-2.5">
                <div class="bg-accent h-2.5 rounded-full" style="width: ${value * 10}%"></div>
            </div>
            <span class="font-bold">${value}/10</span>
        </div>`).join('');

    const skillsContainer = document.getElementById('skills-container');
    if (user.skills && user.skills.length > 0) {
        skillsContainer.innerHTML = user.skills.map(skill => `
            <div>
                <div class="flex justify-between mb-1">
                    <span class="font-bold">${skill.name}</span>
                    <span class="text-sm text-gray-500">${skill.level}</span>
                </div>
                <div class="w-full bg-secondary-bg rounded-full h-2.5">
                    <div class="bg-accent h-2.5 rounded-full" style="width: ${{Beginner: 25, Intermediate: 50, Advanced: 75, Proficient: 100}[skill.level] || 10}%"></div>
                </div>
            </div>`).join('');
    } else {
        skillsContainer.innerHTML = `<p class="text-gray-500">Навыки не добавлены. <a href="edit-profile.html" class="text-accent underline">Добавить</a>.</p>`
    }

    document.getElementById('badges-count').textContent = user.achievements.badges;
    document.getElementById('xp-count').textContent = user.achievements.xp.toLocaleString('ru-RU');
    document.getElementById('rating-position').textContent = `#${user.achievements.rating}`;
    
    const level = Math.floor(user.achievements.xp / XP_PER_LEVEL) + 1;
    const xpForLevel = user.achievements.xp % XP_PER_LEVEL;
    document.getElementById('level-text').textContent = `Level Progress (Lv. ${level}`;
    document.getElementById('level-xp-text').textContent = `${xpForLevel} / ${XP_PER_LEVEL} XP`;
    document.getElementById('level-progress-bar').style.width = `${(xpForLevel / XP_PER_LEVEL) * 100}%`;

    initEmployeeChat(user);
}

function initEmployeeChat(user) {
    const chatWindow = document.getElementById('employee-chat-window');
    const chatInput = document.getElementById('employee-chat-input');
    const sendBtn = document.getElementById('employee-chat-send-btn');
    if (!chatWindow || !chatInput || !sendBtn) return;

    let currentUserData = user;

    const addMessage = (text, sender, persist = true) => {
        const message = document.createElement('div');
        message.className = `flex mb-3 ${sender === 'user' ? 'justify-end' : 'justify-start'}`;
        const textContent = (typeof text === 'string') ? text : JSON.stringify(text, null, 2);
        message.innerHTML = `<div class="${sender === 'user' ? 'bg-accent text-white' : 'bg-gray-100'} rounded-lg p-3 max-w-lg">${textContent.replace(/\n/g, '<br>')}</div>`;
        chatWindow.appendChild(message);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        if (persist) {
            currentUserData.chatHistory.push({ sender, text });
            DB.setEmployeeData(currentUserData);
        }
    };

    const loadChatHistory = () => {
        chatWindow.innerHTML = '';
        if (currentUserData.chatHistory && currentUserData.chatHistory.length > 0) {
            currentUserData.chatHistory.forEach(msg => addMessage(msg.text, msg.sender, false));
        } else {
            addMessage('Здравствуйте! Готова ответить на Ваши вопросы.', 'ai', true);
        }
    };

    const handleSend = async () => {
        const query = chatInput.value.trim();
        if (!query) return;
        addMessage(query, 'user');
        chatInput.value = '';

        const aiResponse = await DB.getAiChatResponse(query);
        addMessage(aiResponse.data.message || aiResponse.data, 'ai');
    };

    sendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });

    loadChatHistory();
}

async function initEditProfilePage() {
    const user = await DB.getEmployeeData();
    if (!user) return;

    let tempUser = JSON.parse(JSON.stringify(user));

    document.getElementById('name-input').value = tempUser.name;
    document.getElementById('role-input').value = tempUser.role;
    
    // ... (тут может быть больше полей для заполнения)

    document.getElementById('save-profile-btn').addEventListener('click', async () => {
        tempUser.name = document.getElementById('name-input').value;
        tempUser.role = document.getElementById('role-input').value;
        
        // ... (логика обновления других полей, если они есть)

        await DB.setEmployeeData(tempUser);
        window.location.href = 'profile.html';
    });
}
