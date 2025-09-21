/**
 * API клиент для работы с HR Консультант API
 * Обрабатывает все HTTP запросы к серверу
 */

class APIClient {
    constructor() {
        this.baseURL = '/api/v1';
        this.token = null;
        this.refreshToken = null;
        
        // Загружаем токены из localStorage
        this.loadTokens();
    }
    
    /**
     * Загрузка токенов из localStorage
     */
    loadTokens() {
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }
    
    /**
     * Сохранение токенов в localStorage
     */
    saveTokens(accessToken, refreshToken) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }
    
    /**
     * Очистка токенов
     */
    clearTokens() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
    
    /**
     * Выполнение HTTP запроса
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Добавляем токен авторизации если есть
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        try {
            console.log('Making API request to:', url, 'with config:', config);
            const response = await fetch(url, config);
            console.log('API response status:', response.status, response.statusText);
            
            // Обработка ошибок авторизации
            if (response.status === 401) {
                await this.handleUnauthorized();
                // Повторяем запрос с новым токеном
                if (this.token) {
                    config.headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, config);
                }
            }
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    console.log('Error response data:', errorData);
                    
                    // Обработка различных форматов ошибок
                    if (Array.isArray(errorData.detail)) {
                        // FastAPI validation errors
                        errorMessage = errorData.detail.map(err => 
                            `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`
                        ).join(', ');
                    } else if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    } else if (typeof errorData === 'string') {
                        errorMessage = errorData;
                    } else if (errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch (parseError) {
                    // Если не удалось распарсить JSON, используем стандартное сообщение
                    console.warn('Could not parse error response:', parseError);
                }
                throw new Error(errorMessage);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            // Убеждаемся, что ошибка имеет строковое сообщение
            if (error instanceof Error) {
                throw error;
            } else {
                throw new Error('Произошла неизвестная ошибка при обращении к серверу');
            }
        }
    }
    
    /**
     * Обработка ошибки 401 (Unauthorized)
     */
    async handleUnauthorized() {
        if (this.refreshToken) {
            try {
                const response = await fetch(`${this.baseURL}/auth/refresh`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        refresh_token: this.refreshToken
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.saveTokens(data.access_token, data.refresh_token);
                    return;
                }
            } catch (error) {
                console.error('Token refresh failed:', error);
            }
        }
        
        // Если не удалось обновить токен, перенаправляем на страницу входа
        this.clearTokens();
        window.location.href = '/';
    }
    
    // ==================== АУТЕНТИФИКАЦИЯ ====================
    
    /**
     * Регистрация нового сотрудника
     */
    async register(userData) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
    
    /**
     * Вход в систему
     */
    async login(loginData) {
        try {
            console.log('Attempting login with data:', loginData);
            const response = await this.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify(loginData)
            });
            
            console.log('Login response:', response);
            
            // Сохраняем токены из cookies (если сервер их устанавливает)
            this.loadTokens();
            
            return response;
        } catch (error) {
            console.error('Login API call failed:', error);
            throw error;
        }
    }
    
    /**
     * Выход из системы
     */
    async logout() {
        try {
            await this.request('/auth/logout', {
                method: 'POST'
            });
        } finally {
            this.clearTokens();
        }
    }
    
    /**
     * Получение информации о текущем пользователе
     */
    async getCurrentUser() {
        return await this.request('/auth/me');
    }
    
    // ==================== ПРОФИЛЬ СОТРУДНИКА ====================
    
    /**
     * Получение профиля сотрудника
     */
    async getProfile() {
        return await this.request('/employees/profile');
    }
    
    /**
     * Обновление профиля сотрудника
     */
    async updateProfile(profileData) {
        return await this.request('/employees/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }
    
    /**
     * Добавление навыка
     */
    async addSkill(skillName) {
        return await this.request(`/employees/skills/${encodeURIComponent(skillName)}`, {
            method: 'POST'
        });
    }
    
    /**
     * Удаление навыка
     */
    async removeSkill(skillId) {
        return await this.request(`/employees/skills/${skillId}`, {
            method: 'DELETE'
        });
    }
    
    /**
     * Получение всех навыков
     */
    async getAllSkills() {
        return await this.request('/employees/skills');
    }
    
    /**
     * Добавление опыта работы
     */
    async addWorkExperience(experienceData) {
        return await this.request('/employees/work-experience', {
            method: 'POST',
            body: JSON.stringify(experienceData)
        });
    }
    
    /**
     * Добавление образования
     */
    async addEducation(educationData) {
        return await this.request('/employees/education', {
            method: 'POST',
            body: JSON.stringify(educationData)
        });
    }
    
    // ==================== ИИ-КОНСУЛЬТАНТ ====================
    
    /**
     * Запрос карьерных рекомендаций
     */
    async getCareerRecommendations(requestData) {
        return await this.request('/ai/career-recommendation', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }
    
    /**
     * Получение истории запросов к ИИ
     */
    async getCareerRequests() {
        return await this.request('/ai/career-requests');
    }
    
    /**
     * Получение приветственного сообщения от ассистента
     */
    async getAssistantWelcome() {
        return await this.request('/ai/assistant/welcome');
    }
    
    /**
     * Отправка сообщения ассистенту
     */
    async sendAssistantMessage(messageData) {
        return await this.request('/ai/assistant/chat', {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    }
    
    // ==================== HR ПОИСК ====================
    
    /**
     * Поиск сотрудников
     */
    async searchEmployees(query) {
        return await this.request(`/hr/search?query=${encodeURIComponent(query)}`);
    }
    
    /**
     * Получение истории поисков
     */
    async getSearchHistory() {
        return await this.request('/hr/search-history');
    }
    
    /**
     * Получение всех сотрудников
     */
    async getAllEmployees(skip = 0, limit = 100) {
        return await this.request(`/hr/employees?skip=${skip}&limit=${limit}`);
    }
    
    /**
     * Получение аналитики по сотрудникам
     */
    async getEmployeeAnalytics() {
        return await this.request('/hr/analytics');
    }
    
    // ==================== ГЕЙМИФИКАЦИЯ ====================
    
    /**
     * Получение статистики геймификации
     */
    async getGamificationStats() {
        return await this.request('/gamification/stats');
    }
    
    /**
     * Получение таблицы лидеров
     */
    async getLeaderboard(limit = 10) {
        return await this.request(`/gamification/leaderboard?limit=${limit}`);
    }
    
    /**
     * Получение всех достижений
     */
    async getAchievements() {
        return await this.request('/gamification/achievements');
    }
}

// Глобальный экземпляр API клиента
const apiClient = new APIClient();

// Экспорт для использования в других модулях
window.apiClient = apiClient;
