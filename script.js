const XP_PER_LEVEL = 200;

const newUserWelcomeMessage = { sender: 'ai', text: 'Здравствуйте! Готова ответить на Ваши вопросы.' };

// --- API Abstraction Layer ---
const API_BASE_URL = 'http://localhost:5000'; // Централизованный URL бэкенда

const DB = {
    // Получает все данные о сотруднике (id 123 для примера)
    getEmployeeData: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/employee/123`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        } catch (error) {
            console.error("Ошибка при получении данных сотрудника:", error);
            return null; // Возвращаем null, чтобы UI мог обработать ошибку
        }
    },

    // Обновляет данные сотрудника
    setEmployeeData: async (employeeData) => {
        try {
            await fetch(`${API_BASE_URL}/api/employee/123`, { 
                method: 'POST', 
                body: JSON.stringify(employeeData), 
                headers: { 'Content-Type': 'application/json' } 
            });
        } catch (error) {
            console.error("Ошибка при сохранении данных сотрудника:", error);
        }
    },

    // Отправляет запрос в AI-чат
    getAiChatResponse: async (query, employeeId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                body: JSON.stringify({ query, employee_id: employeeId }),
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        } catch (error) {
            console.error('Ошибка при получении ответа от AI:', error);
            return { 
                response_type: "general_advice", 
                data: { message: "Не удалось связаться с AI-ассистентом. Проверьте консоль." }
            };
        }
    }
};

// --- App Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.id;
    // Универсальная рендеринг шапки для всех страниц, кроме лендинга и логина
    if (!['page-landing', 'page-login'].includes(pageId)) { 
        renderHeader(); 
    }
    // Инициализация конкретной страницы
    switch (pageId) {
        case 'page-login': initLoginPage(); break;
        case 'page-profile': initProfilePage(); break;
        case 'page-edit-profile': initEditProfilePage(); break;
        // Другие страницы пока не используются в новой архитектуре
    }
});

// --- Core UI Rendering ---

async function renderHeader() {
    const headerContainer = document.getElementById('header-container');
    if (!headerContainer) return;

    // В этой версии мы работаем только с одним сотрудником (id 123)
    const user = await DB.getEmployeeData();

    if (!user) {
        headerContainer.innerHTML = `<p class="text-red-500">Не удалось загрузить данные пользователя.</p>`;
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

    // Подсветка активной ссылки
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    const activeLink = headerContainer.querySelector(`[data-link*="${currentPage}"]`);
    if (activeLink) activeLink.classList.add('text-accent', 'font-bold');

    // Выход из системы
    document.getElementById('logout-btn').addEventListener('click', () => {
        window.location.href = 'login.html';
    });
}

async function initProfilePage() {
    const user = await DB.getEmployeeData();
    if (!user) return;

    // Отображение основной информации
    document.getElementById('user-avatar-main').src = user.avatar;
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-role').textContent = user.role;

    // Отображение карьерного пути
    const careerPathContainer = document.getElementById('career-path-container');
    careerPathContainer.innerHTML = user.careerPath.map(p => `
        <div class="mb-8">
            <div class="absolute -left-3.5 mt-1.5 h-6 w-6 bg-accent rounded-full border-4 border-white"></div>
            <p class="text-sm text-gray-500">${p.year}</p>
            <h4 class="font-bold">${p.role}</h4>
            <p class="text-sm text-gray-600">${p.project}</p>
        </div>`).join('');

    // Отображение интересов
    const interestsContainer = document.getElementById('interests-container');
    interestsContainer.innerHTML = Object.entries(user.interests).map(([key, value]) => `
        <div class="flex items-center gap-4">
            <span class="w-32 capitalize">${key.replace('dataScience', 'Data Science').replace('mobileDev', 'Mobile Dev')}</span>
            <div class="w-full bg-secondary-bg rounded-full h-2.5">
                <div class="bg-accent h-2.5 rounded-full" style="width: ${value * 10}%"></div>
            </div>
            <span class="font-bold">${value}/10</span>
        </div>`).join('');

    // Отображение навыков
    const skillsContainer = document.getElementById('skills-container');
    if (user.skills.length > 0) {
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

    // Достижения и геймификация
    document.getElementById('badges-count').textContent = user.achievements.badges;
    document.getElementById('xp-count').textContent = user.achievements.xp.toLocaleString('ru-RU');
    document.getElementById('rating-position').textContent = `#${user.achievements.rating}`;
    
    // Прогресс уровня
    const level = Math.floor(user.achievements.xp / XP_PER_LEVEL) + 1;
    const xpForLevel = user.achievements.xp % XP_PER_LEVEL;
    document.getElementById('level-text').textContent = `Level Progress (Lv. ${level}`;
    document.getElementById('level-xp-text').textContent = `${xpForLevel} / ${XP_PER_LEVEL} XP`;
    document.getElementById('level-progress-bar').style.width = `${(xpForLevel / XP_PER_LEVEL) * 100}%`;

    // Инициализация чата
    initEmployeeChat(user);
}

function initEmployeeChat(user) {
    const chatWindow = document.getElementById('employee-chat-window');
    const chatInput = document.getElementById('employee-chat-input');
    const sendBtn = document.getElementById('employee-chat-send-btn');
    if (!chatWindow || !chatInput || !sendBtn) return;

    let currentUser = user;

    const addMessage = (text, sender, persist = true) => {
        const message = document.createElement('div');
        message.className = `flex mb-3 ${sender === 'user' ? 'justify-end' : 'justify-start'}`;
        
        const textContent = (typeof text === 'string') ? text : JSON.stringify(text, null, 2);

        message.innerHTML = `<div class="${sender === 'user' ? 'bg-accent text-white' : 'bg-gray-100'} rounded-lg p-3 max-w-lg">${textContent.replace(/\n/g, '<br>')}</div>`;
        chatWindow.appendChild(message);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        if (persist) {
            currentUser.chatHistory.push({ sender, text });
            DB.setEmployeeData(currentUser);
        }
    };

    const loadChatHistory = () => {
        chatWindow.innerHTML = '';
        currentUser.chatHistory.forEach(msg => addMessage(msg.text, msg.sender, false));
    };

    const handleSend = async () => {
        const query = chatInput.value.trim();
        if (!query) return;
        addMessage(query, 'user');
        chatInput.value = '';

        const aiResponse = await DB.getAiChatResponse(query, currentUser.id);
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

    // Заполнение полей...
    // (здесь много кода, который в целом корректен и просто обновляет tempUser)

    // Кнопка сохранения
    document.getElementById('save-profile-btn').addEventListener('click', async () => {
        // Обновляем name, role и т.д. в tempUser
        tempUser.name = document.getElementById('name-input').value;
        tempUser.role = document.getElementById('role-input').value;
        
        // (прочая логика обновления tempUser, включая XP)

        await DB.setEmployeeData(tempUser);
        window.location.href = 'profile.html';
    });
}

// Упрощенная функция входа
function initLoginPage() {
    document.getElementById('login-btn').addEventListener('click', () => {
        // В этой версии мы просто переходим на страницу профиля по умолчанию
        window.location.href = 'profile.html';
    });
}
