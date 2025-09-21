// =========================================================================
// API CLIENT ДЛЯ СВЯЗИ С BACKEND
// =========================================================================

class APIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async sendChatMessage(query, role, userId = 123) {
        try {
            const response = await fetch(`${this.baseURL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    role: role,
                    userId: userId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка при отправке сообщения в API:', error);
            throw error;
        }
    }

    async getEmployeeChatResponse(query, userId = 123) {
        return await this.sendChatMessage(query, 'employee', userId);
    }

    async getManagerChatResponse(query) {
        return await this.sendChatMessage(query, 'manager');
    }
}

// Создаем глобальный экземпляр API клиента
window.apiClient = new APIClient();
