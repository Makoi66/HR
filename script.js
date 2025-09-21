const XP_PER_LEVEL = 200;

const newUserWelcomeMessage = { sender: 'ai', text: 'Здравствуйте! Готова ответить на Ваши вопросы.' };
const generalEmployeeWelcomeMessage = { sender: 'ai', text: 'Здравствуйте! Готова ответить на Ваши вопросы.' };

const newEmployeeTemplate = { name: 'Новый пользователь', role: 'Должность не указана', avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1961&auto-format=fit=crop', interests: { backend: 0, frontend: 0, dataScience: 0, devops: 0, mobileDev: 0, qa: 0 }, skills: [], achievements: { xp: 0, badges: 0, rating: 999, hasUploadedAvatar: false, hasAddedFirstSkill: false, hasAddedFirstCareerPath: false }, careerPath: [], applications: [], chatHistory: [newUserWelcomeMessage] };
const newHrTemplate = { name: 'Новый HR', role: 'HR Manager', avatar: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=1974&auto-format=fit-crop', chatHistory: [ { sender: 'ai', text: 'Hello! I\'m here to help you find the best candidates.' } ] };

const DB = {
    get: async () => {
        const loggedInAs = localStorage.getItem('loggedInAs');
        const email = localStorage.getItem('loggedInUserEmail');
        if (loggedInAs === 'hr') {
            const response = await fetch(`/api/hr/${email}`);
            return response.json();
        } else {
            const response = await fetch('/api/employees/123'); // Assuming a default employee for now
            return response.json();
        }
    },
    set: async (data) => {
        const loggedInAs = localStorage.getItem('loggedInAs');
        const email = localStorage.getItem('loggedInUserEmail');
        if (loggedInAs === 'hr') {
            await fetch(`/api/hr/${email}`, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' } });
        } else {
            await fetch('/api/employees/123', { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'application/json' } });
        }
    },
    getEmployeeData: async () => {
        const response = await fetch('/api/employees/123');
        return response.json();
    },
    getCurrentUser: async () => {
        const loggedInAs = localStorage.getItem('loggedInAs');
        if (loggedInAs === 'hr') {
            const email = localStorage.getItem('loggedInUserEmail');
            const response = await fetch(`/api/hr/${email}`);
            return response.json();
        }
        const response = await fetch('/api/employees/123');
        return response.json();
    },
    setCurrentUser: async (userData) => {
        const loggedInAs = localStorage.getItem('loggedInAs');
        if (loggedInAs === 'hr') {
            const email = localStorage.getItem('loggedInUserEmail');
            await fetch(`/api/hr/${email}`, { method: 'POST', body: JSON.stringify(userData), headers: { 'Content-Type': 'application/json' } });
        } else {
            await fetch('/api/employees/123', { method: 'POST', body: JSON.stringify(userData), headers: { 'Content-Type': 'application/json' } });
        }
    },
    setEmployeeData: async (employeeData) => {
        await fetch('/api/employees/123', { method: 'POST', body: JSON.stringify(employeeData), headers: { 'Content-Type': 'application/json' } });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.id;
    if (!['page-landing', 'page-login', 'page-register'].includes(pageId)) { renderHeader(); }
    switch (pageId) {
        case 'page-login': initLoginPage(); break;
        case 'page-register': initRegisterPage(); break;
        case 'page-profile': initProfilePage(); break;
        case 'page-edit-profile': initEditProfilePage(); break;
        case 'page-applications': initApplicationsPage(); break;
        case 'page-gifts': initGiftsPage(); break;
        case 'page-hr-panel': initHrPanelPage(); break;
        case 'page-hr-profile': initHrProfilePage(); break;
        case 'page-hr-applications': initHrApplicationsPage(); break;
        case 'page-hr-edit-profile': initHrEditProfilePage(); break;
    }
});

async function renderHeader() {
    const headerContainer = document.getElementById('header-container');
    if (!headerContainer) return;
    const loggedInAs = localStorage.getItem('loggedInAs');
    const viewingAsHR = sessionStorage.getItem('viewingAsHR');
    const user = viewingAsHR ? await DB.getEmployeeData() : await DB.getCurrentUser();

    if (!user) {
        localStorage.removeItem('loggedInAs');
        localStorage.removeItem('loggedInUserEmail');
        window.location.href = 'login.html';
        return;
    }

    const effectiveRole = viewingAsHR ? 'hr' : loggedInAs;
    const employeeData = await DB.getEmployeeData();
    const hasUnreadEmployee = employeeData.applications.some(app => !app.viewedByEmployee);
    const hasUnreadHR = employeeData.applications.some(app => app.response !== 'pending' && !app.viewedByHR);
    const employeeNotification = hasUnreadEmployee ? `<span class="ml-2 w-2 h-2 bg-red-500 rounded-full inline-block notification-dot"></span>` : '';
    const hrNotification = hasUnreadHR ? `<span class="ml-2 w-2 h-2 bg-red-500 rounded-full inline-block notification-dot"></span>` : '';
    let navLinks = '';
    if (effectiveRole === 'employee') {
        navLinks = `<a href="profile.html" class="text-gray-500 hover:text-accent transition-colors" data-link="profile">My Profile</a> <a href="applications.html" class="text-gray-500 hover:text-accent transition-colors" data-link="applications">Applications${employeeNotification}</a> <a href="gifts.html" class="text-gray-500 hover:text-accent transition-colors" data-link="gifts">Gifts</a>`;
    } else if (effectiveRole === 'hr') {
        navLinks = `<a href="hr-panel.html" class="text-gray-500 hover:text-accent transition-colors" data-link="hr-panel">Candidate Search</a> <a href="hr-applications.html" class="text-gray-500 hover:text-accent transition-colors" data-link="hr-applications">Applications${hrNotification}</a>`;
    }
    headerContainer.innerHTML = `<nav class="container mx-auto px-6 py-4 flex justify-between items-center"> <a href="${effectiveRole === 'employee' ? 'profile.html' : 'hr-panel.html'}" class="text-xl font-bold text-text-dark">Career on Autopilot</a> <div class="flex items-center space-x-8">${navLinks}</div> <div class="flex items-center space-x-6"> ${effectiveRole === 'hr' ? `<a href="hr-profile.html"><img class="h-10 w-10 rounded-full object-cover" src="${user.avatar}" alt="User Avatar"></a>` : `<img class="h-10 w-10 rounded-full object-cover" src="${user.avatar}" alt="User Avatar">`} <button id="logout-btn" class="text-sm text-gray-500 hover:text-accent">Выйти</button> </div> </nav>`;
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    const activeLink = headerContainer.querySelector(`[data-link*="${currentPage}"]`);
    if (activeLink) {
        activeLink.classList.remove('text-gray-500');
        activeLink.classList.add('text-accent', 'font-bold', 'border-b-2', 'border-accent', 'pb-1');
    }
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('loggedInAs');
        localStorage.removeItem('loggedInUserEmail');
        sessionStorage.clear();
        window.location.href = 'login.html';
    });
}

async function initProfilePage() {
    const viewingAsHR = sessionStorage.getItem('viewingAsHR');
    const user = viewingAsHR ? await DB.getEmployeeData() : await DB.getCurrentUser();
    document.getElementById('user-avatar-main').src = user.avatar;
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-role').textContent = user.role;
    const careerPathContainer = document.getElementById('career-path-container');
    careerPathContainer.innerHTML = user.careerPath.map(p => `<div class="mb-8"><div class="absolute -left-3.5 mt-1.5 h-6 w-6 bg-accent rounded-full border-4 border-white"></div><p class="text-sm text-gray-500">${p.year}</p><h4 class="font-bold">${p.role}</h4><p class="text-sm text-gray-600">${p.project}</p></div>`).join('');
    const interestsContainer = document.getElementById('interests-container');
    interestsContainer.innerHTML = Object.entries(user.interests).map(([key, value]) => `<div class="flex items-center gap-4"><span class="w-32 capitalize">${key.replace('dataScience', 'Data Science').replace('mobileDev', 'Mobile Dev')}</span><div class="w-full bg-secondary-bg rounded-full h-2.5"><div class="bg-accent h-2.5 rounded-full" style="width: ${value * 10}%"></div></div><span class="font-bold">${value}/10</span></div>`).join('');
    const skillsContainer = document.getElementById('skills-container');
    skillsContainer.innerHTML = user.skills.map(skill => { const levelWidths = { 'Beginner': 25, 'Intermediate': 50, 'Advanced': 75, 'Proficient': 100 }; return `<div><div class="flex justify-between mb-1"><span class="font-bold">${skill.name}</span><span class="text-sm text-gray-500">${skill.level}</span></div><div class="w-full bg-secondary-bg rounded-full h-2.5"><div class="bg-accent h-2.5 rounded-full" style="width: ${levelWidths[skill.level] || 10}%"></div></div></div>`; }).join('');
    if (user.skills.length === 0) { skillsContainer.innerHTML = `<p class="text-gray-500">Навыки еще не добавлены. <a href="edit-profile.html" class="text-accent underline">Добавить</a>.</p>` }
    document.getElementById('badges-count').textContent = user.achievements.badges;
    document.getElementById('xp-count').textContent = user.achievements.xp.toLocaleString('ru-RU');
    document.getElementById('rating-position').textContent = `#${user.achievements.rating}`;

    const level = Math.floor(user.achievements.xp / XP_PER_LEVEL) + 1;
    const xpForLevel = user.achievements.xp % XP_PER_LEVEL;
    document.getElementById('level-text').textContent = `Level Progress (Lv. ${level}`;
    document.getElementById('level-xp-text').textContent = `${xpForLevel} / ${XP_PER_LEVEL} XP`;
    document.getElementById('level-progress-bar').style.width = `${(xpForLevel / XP_PER_LEVEL) * 100}%`;

    if (viewingAsHR) {
        document.getElementById('edit-profile-link').style.display = 'none';
        document.getElementById('ai-advisor-chat-block').style.display = 'none';
        sessionStorage.removeItem('viewingAsHR');
    } else {
        initEmployeeChat();
    }
}

async function initEmployeeChat() {
    const chatWindow = document.getElementById('employee-chat-window');
    const chatInput = document.getElementById('employee-chat-input');
    const sendBtn = document.getElementById('employee-chat-send-btn');
    const clearChatBtn = document.getElementById('clear-employee-chat-btn');
    if (!chatWindow || !chatInput || !sendBtn) return;

    let user = await DB.getCurrentUser();

    const addMessage = (text, sender, persist = true) => {
        const message = document.createElement('div');
        message.className = `flex ${sender === 'user' ? 'justify-end' : ''}`;

        let processedText = text;
        if (sender === 'ai' && typeof marked !== 'undefined') {
            processedText = marked.parse(text);
        } else {
            processedText = text.replace(/\n/g, '<br>');
        }

        message.innerHTML = `<div class="${sender === 'user' ? 'bg-accent text-white' : 'bg-gray-100'} rounded-lg p-3 max-w-sm ${sender === 'ai' ? 'prose prose-sm max-w-none' : ''}">${processedText}</div>`;
        chatWindow.appendChild(message);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        if (persist) {
            if (!user.chatHistory) user.chatHistory = [];
            user.chatHistory.push({ sender, text });
            DB.setCurrentUser(user);
        }
    };

    const loadChatHistory = () => {
        chatWindow.innerHTML = '';
        if (user.chatHistory && user.chatHistory.length > 0) {
            user.chatHistory.forEach(msg => addMessage(msg.text, msg.sender, false));
        }
    };

    const getAiResponse = async (query) => {
        try {
            const userId = user.id || 123;

            const response = await window.apiClient.getEmployeeChatResponse(query, userId);
            return response.response;
        } catch (error) {
            console.error('Ошибка при получении ответа от AI:', error);
            query = query.toLowerCase();
            if (query.includes('team lead') || query.includes('тимлид')) {
                return 'Чтобы стать Team Lead, важно развивать не только технические, но и "soft skills": лидерство, менторство, умение решать конфликты. Рекомендую пройти курс по управлению командой и взять на себя больше ответственности в текущих проектах.';
            } else if (query.includes('python') || query.includes('пайтон')) {
                return 'Python - отличный выбор! Чтобы улучшить навыки, советую поучаствовать в open-source проектах на GitHub или изучить фреймворки, такие как FastAPI для асинхронных API. Также в нашем магазине наград есть скидки на курсы.';
            } else if (query.includes('навыки') || query.includes('развивать')) {
                return 'Для персональных рекомендаций по развитию, пожалуйста, убедитесь, что ваш профиль в разделе "Skills" и "IT Interests" актуален. Система использует эти данные для подбора курсов и проектов.';
            } else {
                return 'Я могу помочь с вопросами о карьерном росте, развитии навыков и следующих шагах в вашей профессии. Попробуйте переформулировать ваш вопрос.';
            }
        }
    };

    const handleSend = async () => {
        const query = chatInput.value.trim();
        if (!query) return;
        addMessage(query, 'user');
        chatInput.value = '';

        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'flex';
        loadingMessage.innerHTML = '<div class="bg-gray-100 rounded-lg p-3 max-w-sm"><p>AI думает...</p></div>';
        chatWindow.appendChild(loadingMessage);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            const response = await getAiResponse(query);
            chatWindow.removeChild(loadingMessage);
            addMessage(response, 'ai');
        } catch (error) {
            chatWindow.removeChild(loadingMessage);
            addMessage('Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз.', 'ai');
        }
    };

    sendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });

    clearChatBtn.addEventListener('click', async () => {
        user.chatHistory = [generalEmployeeWelcomeMessage];
        await DB.setCurrentUser(user);
        loadChatHistory();
    });

    loadChatHistory();
}

async function initEditProfilePage() {
    const user = await DB.getCurrentUser();
    let tempUser = JSON.parse(JSON.stringify(user));

    const avatarPreview = document.getElementById('avatar-preview');
    const nameInput = document.getElementById('name-input');
    const roleInput = document.getElementById('role-input');
    const interestsContainer = document.getElementById('interests-edit-container');
    const skillsContainer = document.getElementById('skills-container');
    const careerPathContainer = document.getElementById('career-path-edit-container');

    avatarPreview.src = tempUser.avatar;
    nameInput.value = tempUser.name;
    roleInput.value = tempUser.role;
    interestsContainer.innerHTML = Object.entries(tempUser.interests).map(([key, value]) => `<div class="flex items-center gap-4"><span class="w-32 capitalize">${key.replace('dataScience', 'Data Science').replace('mobileDev', 'Mobile Dev')}</span><input type="range" min="0" max="10" value="${value}" data-interest="${key}" class="w-full interest-slider"><span class="font-bold w-10 text-center">${value}/10</span></div>`).join('');

    const renderSkills = () => { skillsContainer.innerHTML = tempUser.skills.map((skill, index) => ` <div class="flex items-center gap-4 p-3 bg-secondary-bg rounded-xl"><span class="font-medium flex-grow">${skill.name}</span><select data-index="${index}" class="skill-level-select border border-gray-300 rounded-lg"><option ${skill.level === 'Beginner' ? 'selected' : ''}>Beginner</option><option ${skill.level === 'Intermediate' ? 'selected' : ''}>Intermediate</option><option ${skill.level === 'Advanced' ? 'selected' : ''}>Advanced</option><option ${skill.level === 'Proficient' ? 'selected' : ''}>Proficient</option></select><button data-index="${index}" class="delete-skill-btn text-gray-400 hover:text-red-500"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 pointer-events-none" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg></button></div>`).join(''); };
    const renderCareerPath = () => { careerPathContainer.innerHTML = tempUser.careerPath.map((path, index) => `<div class="flex items-center gap-4 p-3 bg-secondary-bg rounded-xl"><div class="flex-grow grid grid-cols-3 gap-x-4"><span class="font-medium">${path.year}</span><span class="font-medium">${path.role}</span><span class="text-gray-600">${path.project}</span></div><button data-index="${index}" class="delete-path-btn text-gray-400 hover:text-red-500"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 pointer-events-none" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg></button></div>`).join(''); };
    renderSkills(); renderCareerPath();

    document.getElementById('avatar-upload').addEventListener('change', e => { const reader = new FileReader(); const file = e.target.files[0]; if (file) reader.readAsDataURL(file); reader.onload = () => avatarPreview.src = tempUser.avatar = reader.result; });
    interestsContainer.addEventListener('input', e => { if (e.target.classList.contains('interest-slider')) { const key = e.target.dataset.interest; const value = e.target.value; tempUser.interests[key] = parseInt(value); e.target.nextElementSibling.textContent = `${value}/10`; } });
    
    document.getElementById('add-skill-btn').addEventListener('click', () => { 
        const input = document.getElementById('new-skill-input'); 
        const levelSelect = document.getElementById('new-skill-level-select');
        if (input.value) { 
            let amount, message;
            if (tempUser.skills.length === 0 && !tempUser.achievements.hasAddedFirstSkill) {
                amount = 25;
                message = `Навык добавлен! +${amount} XP за первый навык.`;
                tempUser.achievements.hasAddedFirstSkill = true;
            } else {
                amount = 15;
                message = `Навык добавлен! +${amount} XP.`;
            }
            addXP(tempUser, amount, message);
            tempUser.skills.push({ name: input.value, level: levelSelect.value }); 
            input.value = ''; 
            renderSkills(); 
        } 
    });
    
    skillsContainer.addEventListener('click', e => { if (e.target.closest('.delete-skill-btn')) { tempUser.skills.splice(e.target.closest('.delete-skill-btn').dataset.index, 1); renderSkills(); } });
    skillsContainer.addEventListener('change', e => { if (e.target.classList.contains('skill-level-select')) { tempUser.skills[e.target.dataset.index].level = e.target.value; } });

    document.getElementById('add-path-btn').addEventListener('click', () => {
        const yearInput = document.getElementById('new-path-year'), roleInput = document.getElementById('new-path-role'), projectInput = document.getElementById('new-path-project');
        if (yearInput.value && roleInput.value) {
             let amount, message;
            if (tempUser.careerPath.length === 0 && !tempUser.achievements.hasAddedFirstCareerPath) {
                amount = 25;
                message = `Этап карьеры добавлен! +${amount} XP за первый этап.`;
                tempUser.achievements.hasAddedFirstCareerPath = true;
            } else {
                amount = 15;
                message = `Этап карьеры добавлен! +${amount} XP.`;
            }
            addXP(tempUser, amount, message);
            tempUser.careerPath.unshift({ year: yearInput.value, role: roleInput.value, project: projectInput.value });
            yearInput.value = '', roleInput.value = '', projectInput.value = '';
            renderCareerPath();
        } else { alert('Пожалуйста, заполните как минимум поля "Год" и "Должность".'); }
    });

    careerPathContainer.addEventListener('click', e => { const deleteBtn = e.target.closest('.delete-path-btn'); if (deleteBtn) { tempUser.careerPath.splice(deleteBtn.dataset.index, 1); renderCareerPath(); } });

    document.getElementById('save-profile-btn').addEventListener('click', async () => {
        let totalXpGained = 0;
        let alertMessages = [];

        if (user.name === 'Новый пользователь' && nameInput.value !== 'Новый пользователь') {
            totalXpGained += 100;
            alertMessages.push('+100 XP за заполнение профиля');
        }
        if (user.avatar !== tempUser.avatar && !tempUser.achievements.hasUploadedAvatar) {
            totalXpGained += 50;
            alertMessages.push('+50 XP за загрузку аватара');
            tempUser.achievements.hasUploadedAvatar = true;
        }
        
        tempUser.name = nameInput.value; 
        tempUser.role = roleInput.value;
        
        let finalAlert = 'Профиль сохранен!';
        if (alertMessages.length > 0) {
            finalAlert += `\n${alertMessages.join('\n')}`;
        }
        
        if(totalXpGained > 0) {
            addXP(tempUser, totalXpGained, finalAlert);
        } else {
            alert(finalAlert);
        }
        
        await DB.setCurrentUser(tempUser);
        window.location.href = 'profile.html';
    });
}
