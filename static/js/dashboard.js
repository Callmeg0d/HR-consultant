/**
 * Логика панели управления
 * Обрабатывает навигацию, отображение данных и геймификацию
 */

// Глобальные переменные
let currentUser = null;
let currentTab = null;
let achievements = [];
let employees = [];
let notifications = [];
let sortState = { column: null, direction: 'asc' };

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Инициализация панели управления
 */
function initializeDashboard() {
    // Проверка авторизации
    if (!checkAuth()) {
        window.location.href = 'index.html';
        return;
    }
    
    // Загрузка данных пользователя
    loadUserData();
    
    // Инициализация компонентов
    initializeNavigation();
    initializeProfile();
    initializeAchievements();
    initializeEmployees();
    initializeAssistant();
    initializeNotifications();
    initializeSidebar();
    initializeTheme();
    initializeBackToTop();
    
    // Показ приветственного сообщения
    showWelcomeMessage();
}

/**
 * Проверка авторизации
 */
function checkAuth() {
    const userData = localStorage.getItem('currentUser');
    if (!userData) {
        return false;
    }
    
    currentUser = JSON.parse(userData);
    return true;
}

/**
 * Загрузка данных пользователя
 */
function loadUserData() {
    if (!currentUser) return;
    
    // Обновление информации о пользователе в интерфейсе
    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('userRole').textContent = currentUser.role === 'worker' ? 'Работник' : 'Менеджер';
    
    // Показ соответствующих вкладок
    showRelevantTabs();
    
    // Установка активной вкладки по умолчанию
    const defaultTab = currentUser.role === 'worker' ? 'profile' : 'employees';
    switchTab(defaultTab);
}

/**
 * Показ соответствующих вкладок в зависимости от роли
 */
function showRelevantTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const tab = item.dataset.tab;
        const isWorkerTab = ['profile', 'development', 'leaderboard'].includes(tab);
        const isManagerTab = ['employees', 'assistant'].includes(tab);
        
        if (currentUser.role === 'worker' && isWorkerTab) {
            item.style.display = 'block';
        } else if (currentUser.role === 'manager' && isManagerTab) {
            item.style.display = 'block';
        }
    });
}

/**
 * Инициализация навигации
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Обработка кликов по навигации
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tab = this.closest('.nav-item').dataset.tab;
            switchTab(tab);
        });
    });
    
    // Обработка переключения сайдбара на мобильных
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Обработка выхода
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

/**
 * Переключение вкладок
 */
function switchTab(tabName) {
    // Скрытие всех панелей
    const panels = document.querySelectorAll('.tab-panel');
    panels.forEach(panel => {
        panel.style.display = 'none';
    });
    
    // Удаление активного класса с навигации
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // Показ выбранной панели
    const targetPanel = document.getElementById(tabName);
    if (targetPanel) {
        targetPanel.style.display = 'block';
        targetPanel.classList.add('fade-in');
    }
    
    // Активация соответствующей навигации
    const activeNavLink = document.querySelector(`[data-tab="${tabName}"] .nav-link`);
    if (activeNavLink) {
        activeNavLink.classList.add('active');
    }
    
    // Обновление заголовка страницы
    updatePageTitle(tabName);
    
    currentTab = tabName;
    
    // Загрузка данных для конкретной вкладки
    loadTabData(tabName);
}

/**
 * Обновление заголовка страницы
 */
function updatePageTitle(tabName) {
    const titles = {
        profile: 'Мой профиль',
        development: 'Пути развития',
        leaderboard: 'Таблица лидеров',
        employees: 'Сотрудники',
        assistant: 'ИИ-ассистент'
    };
    
    const pageTitle = document.getElementById('pageTitle');
    if (pageTitle && titles[tabName]) {
        pageTitle.textContent = titles[tabName];
    }
}

/**
 * Загрузка данных для конкретной вкладки
 */
function loadTabData(tabName) {
    switch (tabName) {
        case 'profile':
            loadProfileData();
            break;
        case 'development':
            // Данные загружаются при необходимости
            break;
        case 'leaderboard':
            loadLeaderboardData();
            break;
        case 'employees':
            loadEmployeesData();
            break;
        case 'assistant':
            // Данные загружаются при необходимости
            break;
    }
}

/**
 * Инициализация профиля
 */
function initializeProfile() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileSubmit);
    }
}

/**
 * Загрузка данных профиля
 */
async function loadProfileData() {
    if (!currentUser) return;
    
    try {
        // Загружаем актуальные данные профиля с сервера
        const profileData = await apiClient.getProfile();
        
        // Обновляем данные пользователя
        currentUser = { ...currentUser, ...profileData };
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Заполнение полей формы
        document.getElementById('fullName').value = profileData.full_name || '';
        document.getElementById('position').value = profileData.position || '';
        document.getElementById('department').value = profileData.department || '';
        document.getElementById('experience').value = profileData.experience_years || '';
        document.getElementById('skills').value = profileData.skills?.map(s => s.name).join(', ') || '';
        document.getElementById('goals').value = profileData.goals || '';
        
        // Обновление отображения профиля
        document.getElementById('profileName').textContent = profileData.full_name || 'Не указано';
        document.getElementById('profilePosition').textContent = profileData.position || 'Не указано';
        
        // Обновление прогресс-бара
        updateProfileProgress();
        
    } catch (error) {
        console.error('Error loading profile:', error);
        
        // Определяем тип ошибки и показываем соответствующее сообщение
        let errorMessage = 'Ошибка загрузки профиля';
        if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
            errorMessage = 'Сервер временно недоступен. Используются локальные данные.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = 'Нет подключения к серверу. Используются локальные данные.';
        } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            errorMessage = 'Сессия истекла. Пожалуйста, войдите заново.';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
        
        showNotification(errorMessage, 'warning');
        
        // Fallback к данным из localStorage
        document.getElementById('fullName').value = currentUser.name || '';
        document.getElementById('position').value = currentUser.position || '';
        document.getElementById('department').value = currentUser.department || '';
        document.getElementById('experience').value = currentUser.experience || '';
        document.getElementById('skills').value = currentUser.skills || '';
        document.getElementById('goals').value = currentUser.goals || '';
        
        document.getElementById('profileName').textContent = currentUser.name || 'Не указано';
        document.getElementById('profilePosition').textContent = currentUser.position || 'Не указано';
        
        updateProfileProgress();
    }
}

/**
 * Обработка сохранения профиля
 */
async function handleProfileSubmit(event) {
    event.preventDefault();
    
    try {
        // Показываем индикатор загрузки
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
        submitBtn.disabled = true;
        
        // Сбор данных формы
        const formData = {
            full_name: document.getElementById('fullName').value,
            position: document.getElementById('position').value,
            department: document.getElementById('department').value,
            experience_years: parseInt(document.getElementById('experience').value) || 0,
            goals: document.getElementById('goals').value
        };
        
        // Отправляем данные на сервер
        const updatedProfile = await apiClient.updateProfile(formData);
        
        // Обновляем данные пользователя
        currentUser = { ...currentUser, ...updatedProfile };
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Обрабатываем навыки отдельно
        const skillsText = document.getElementById('skills').value;
        if (skillsText.trim()) {
            const skills = skillsText.split(',').map(s => s.trim()).filter(s => s);
            
            // Получаем все доступные навыки
            const allSkills = await apiClient.getAllSkills();
            
            // Добавляем новые навыки
            for (const skillName of skills) {
                const existingSkill = allSkills.find(s => s.name.toLowerCase() === skillName.toLowerCase());
                if (existingSkill) {
                    try {
                        await apiClient.addSkill(existingSkill.name);
                    } catch (error) {
                        console.log(`Skill ${skillName} already exists or error adding:`, error);
                    }
                }
            }
        }
        
        // Пересчет заполненности профиля
        currentUser.profileComplete = calculateProfileCompleteness(formData);
        
        // Инициализация системы опыта если не существует
        if (!currentUser.xp_points) {
            currentUser.xp_points = 0;
            currentUser.level = 1;
            currentUser.achievements = [];
        }
        
        // Обновление отображения
        await loadProfileData();
        
        // Проверка достижений и начисление опыта
        checkAchievementsAndXP();
        
        // Показ уведомления
        showNotification('Профиль успешно сохранен!', 'success');
        
    } catch (error) {
        console.error('Error saving profile:', error);
        showNotification('Ошибка сохранения профиля: ' + error.message, 'error');
    } finally {
        // Восстанавливаем кнопку
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

/**
 * Расчет заполненности профиля
 */
function calculateProfileCompleteness(data) {
    const fields = ['full_name', 'position', 'department', 'experience_years', 'goals'];
    const filledFields = fields.filter(field => {
        const value = data[field];
        return value !== null && value !== undefined && value !== '' && value !== 0;
    });
    return Math.round((filledFields.length / fields.length) * 100);
}

/**
 * Обновление прогресс-бара профиля
 */
function updateProfileProgress() {
    const progressFill = document.getElementById('profileProgressFill');
    const progressText = document.getElementById('profileProgressText');
    
    if (progressFill && progressText) {
        const percentage = currentUser.profileComplete || 0;
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${percentage}% заполнено`;
    }
}

/**
 * Инициализация системы достижений
 */
function initializeAchievements() {
    // Определение достижений
    achievements = [
        {
            id: 'first_step',
            title: 'Первый шаг',
            description: 'Заполните основную информацию',
            icon: 'fas fa-user',
            condition: (user) => user.name && user.position,
            unlocked: false,
            xpReward: 50
        },
        {
            id: 'skill_master',
            title: 'Мастер навыков',
            description: 'Укажите ваши навыки',
            icon: 'fas fa-tools',
            condition: (user) => user.skills && user.skills.trim() !== '',
            unlocked: false,
            xpReward: 75
        },
        {
            id: 'goal_setter',
            title: 'Постановщик целей',
            description: 'Определите цели развития',
            icon: 'fas fa-bullseye',
            condition: (user) => user.goals && user.goals.trim() !== '',
            unlocked: false,
            xpReward: 100
        },
        {
            id: 'profile_complete',
            title: 'Профиль завершен',
            description: 'Заполните профиль на 100%',
            icon: 'fas fa-trophy',
            condition: (user) => user.profileComplete >= 100,
            unlocked: false,
            xpReward: 200
        },
        {
            id: 'experienced_worker',
            title: 'Опытный сотрудник',
            description: 'Опыт работы 3+ лет',
            icon: 'fas fa-star',
            condition: (user) => user.experience && parseInt(user.experience) >= 3,
            unlocked: false,
            xpReward: 150
        },
        {
            id: 'team_player',
            title: 'Командный игрок',
            description: 'Укажите отдел',
            icon: 'fas fa-users',
            condition: (user) => user.department && user.department.trim() !== '',
            unlocked: false,
            xpReward: 80
        },
        {
            id: 'level_5',
            title: 'Пятый уровень',
            description: 'Достигните 5 уровня',
            icon: 'fas fa-medal',
            condition: (user) => user.level && user.level >= 5,
            unlocked: false,
            xpReward: 300
        },
        {
            id: 'level_10',
            title: 'Десятый уровень',
            description: 'Достигните 10 уровня',
            icon: 'fas fa-crown',
            condition: (user) => user.level && user.level >= 10,
            unlocked: false,
            xpReward: 500
        }
    ];
    
    // Проверка достижений
    checkAchievements();
}

/**
 * Проверка достижений и начисление опыта
 */
async function checkAchievementsAndXP() {
    try {
        // Загружаем актуальную статистику геймификации с сервера
        const gamificationStats = await apiClient.getGamificationStats();
        
        // Обновляем данные пользователя
        currentUser.xp_points = gamificationStats.xp_points || 0;
        currentUser.level = gamificationStats.level || 1;
        currentUser.achievements = gamificationStats.achievements || [];
        
        // Сохранение обновленных данных
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Обновление отображения
        updateProfileProgress();
        updateAchievementsDisplay();
        
        // Проверяем новые достижения локально
        if (window.gamification) {
            const { achievementSystem } = window.gamification;
            const newAchievements = achievementSystem.checkAllAchievements(currentUser);
            
            if (newAchievements.length > 0) {
                newAchievements.forEach(achievement => {
                    if (!currentUser.achievements.includes(achievement.id)) {
                        showAchievementUnlocked(achievement);
                    }
                });
            }
        }
        
    } catch (error) {
        console.error('Error loading gamification stats:', error);
        
        // Fallback к локальной геймификации
        if (window.gamification) {
            const { achievementSystem, experienceSystem } = window.gamification;
            
            // Инициализация достижений если их нет
            if (!currentUser.achievements) {
                currentUser.achievements = [];
            }
            
            // Проверка новых достижений
            const newAchievements = achievementSystem.checkAllAchievements(currentUser);
            
            if (newAchievements.length > 0) {
                newAchievements.forEach(achievement => {
                    if (!currentUser.achievements.includes(achievement.id)) {
                        currentUser.achievements.push(achievement.id);
                        currentUser.xp_points = (currentUser.xp_points || 0) + achievement.xpReward;
                        showAchievementUnlocked(achievement);
                    }
                });
                
                // Пересчет уровня
                if (experienceSystem) {
                    const levelData = experienceSystem.calculateProgressToNextLevel(currentUser.xp_points);
                    currentUser.level = levelData.currentLevel;
                }
                
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                updateProfileProgress();
                updateAchievementsDisplay();
            }
        }
    }
}

/**
 * Проверка и обновление достижений (старая версия для совместимости)
 */
function checkAchievements() {
    checkAchievementsAndXP();
}

/**
 * Показ разблокированного достижения
 */
function showAchievementUnlocked(achievement) {
    // Добавляем уведомление в систему
    addNotification('achievement', 'Достижение разблокировано!', achievement.title);
    
    // Показываем специальное уведомление о достижении
    const notification = document.createElement('div');
    notification.className = 'achievement-notification';
    notification.innerHTML = `
        <div class="achievement-notification-content">
            <i class="${achievement.icon}"></i>
            <div>
                <h4>🏆 Достижение разблокировано!</h4>
                <p>${achievement.title}</p>
                <small>+${achievement.xpReward} XP</small>
            </div>
        </div>
    `;
    
    // Стили уведомления
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #f59e0b, #f97316);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 300px;
        border: 2px solid #fbbf24;
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Автоматическое скрытие
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

/**
 * Обновление отображения достижений
 */
function updateAchievementsDisplay() {
    const achievementsGrid = document.getElementById('achievementsGrid');
    if (!achievementsGrid) return;
    
    achievementsGrid.innerHTML = '';
    
    achievements.forEach(achievement => {
        const achievementElement = document.createElement('div');
        achievementElement.className = `achievement ${achievement.unlocked ? 'unlocked' : 'locked'}`;
        achievementElement.innerHTML = `
            <div class="achievement-icon">
                <i class="${achievement.icon}"></i>
            </div>
            <div class="achievement-tooltip">
                <div class="achievement-tooltip-title">${achievement.title}</div>
                <div class="achievement-tooltip-description">${achievement.description}</div>
                <div class="achievement-tooltip-xp">+${achievement.xpReward || 0} XP</div>
            </div>
        `;
        
        achievementsGrid.appendChild(achievementElement);
    });
}

/**
 * Загрузка данных таблицы лидеров
 */
async function loadLeaderboardData() {
    const tableBody = document.getElementById('leaderboardTableBody');
    const statsContainer = document.getElementById('leaderboardStats');
    
    if (!tableBody) return;
    
    try {
        // Показываем индикатор загрузки
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;"><i class="fas fa-spinner fa-spin"></i> Загрузка таблицы лидеров...</td></tr>';
        
        // Загружаем данные с сервера
        const leaderboardData = await apiClient.getLeaderboard(20);
        
        // Очищаем таблицу
        tableBody.innerHTML = '';
        
        if (leaderboardData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Данные не найдены</td></tr>';
            return;
        }
        
        // Отображаем данные в таблице
        leaderboardData.forEach((employee, index) => {
            const row = document.createElement('tr');
            const position = index + 1;
            const isCurrentUser = currentUser && employee.id === currentUser.id;
            
            row.className = isCurrentUser ? 'current-user' : '';
            row.innerHTML = `
                <td>
                    <div class="position-badge position-${position <= 3 ? position : 'other'}">
                        ${position <= 3 ? '🏆' : position}
                    </div>
                </td>
                <td>
                    <div class="employee-info">
                        <strong>${employee.full_name || 'Не указано'}</strong>
                        ${isCurrentUser ? '<span class="current-user-badge">Вы</span>' : ''}
                    </div>
                </td>
                <td>
                    <div class="level-badge">
                        <i class="fas fa-star"></i>
                        ${employee.level || 1}
                    </div>
                </td>
                <td>
                    <div class="xp-info">
                        <span class="xp-amount">${employee.xp_points || 0}</span>
                        <span class="xp-label">XP</span>
                    </div>
                </td>
                <td>
                    <div class="achievements-count">
                        <i class="fas fa-trophy"></i>
                        ${employee.achievements ? employee.achievements.length : 0}
                    </div>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Обновляем статистику
        if (statsContainer) {
            const currentUserStats = leaderboardData.find(emp => emp.id === currentUser.id);
            const totalEmployees = leaderboardData.length;
            const currentUserPosition = currentUserStats ? leaderboardData.indexOf(currentUserStats) + 1 : null;
            
            statsContainer.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${totalEmployees}</div>
                            <div class="stat-label">Всего сотрудников</div>
                        </div>
                    </div>
                    ${currentUserPosition ? `
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-medal"></i>
                            </div>
                            <div class="stat-content">
                                <div class="stat-value">${currentUserPosition}</div>
                                <div class="stat-label">Ваше место</div>
                            </div>
                        </div>
                    ` : ''}
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${currentUserStats ? currentUserStats.level : 1}</div>
                            <div class="stat-label">Ваш уровень</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        
        // Определяем тип ошибки и показываем соответствующее сообщение
        let errorMessage = 'Ошибка загрузки таблицы лидеров';
        if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
            errorMessage = 'Сервер временно недоступен. Показываются демо-данные.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = 'Нет подключения к серверу. Показываются демо-данные.';
        } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            errorMessage = 'Сессия истекла. Пожалуйста, войдите заново.';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
        
        // Fallback к демо-данным
        loadDemoLeaderboardData();
        showNotification(errorMessage, 'warning');
    }
}

/**
 * Загрузка демо-данных для таблицы лидеров (fallback)
 */
function loadDemoLeaderboardData() {
    const tableBody = document.getElementById('leaderboardTableBody');
    const statsContainer = document.getElementById('leaderboardStats');
    
    if (!tableBody) return;
    
    // Демо-данные для таблицы лидеров
    const demoLeaderboardData = [
        {
            id: 1,
            full_name: 'Алексей Иванов',
            level: 5,
            xp_points: 1250,
            achievements: ['Первые шаги', 'Активный пользователь', 'Командный игрок']
        },
        {
            id: 2,
            full_name: 'Мария Петрова',
            level: 4,
            xp_points: 980,
            achievements: ['Первые шаги', 'Активный пользователь']
        },
        {
            id: 3,
            full_name: 'Дмитрий Сидоров',
            level: 3,
            xp_points: 750,
            achievements: ['Первые шаги']
        },
        {
            id: 4,
            full_name: 'Анна Козлова',
            level: 2,
            xp_points: 450,
            achievements: ['Первые шаги']
        },
        {
            id: 5,
            full_name: 'Сергей Волков',
            level: 2,
            xp_points: 380,
            achievements: ['Первые шаги']
        }
    ];
    
    // Очищаем таблицу
    tableBody.innerHTML = '';
    
    // Отображаем демо-данные
    demoLeaderboardData.forEach((employee, index) => {
        const row = document.createElement('tr');
        const position = index + 1;
        const isCurrentUser = currentUser && employee.id === currentUser.id;
        
        row.className = isCurrentUser ? 'current-user' : '';
        row.innerHTML = `
            <td>
                <div class="position-badge position-${position <= 3 ? position : 'other'}">
                    ${position <= 3 ? '🏆' : position}
                </div>
            </td>
            <td>
                <div class="employee-info">
                    <strong>${employee.full_name}</strong>
                    ${isCurrentUser ? '<span class="current-user-badge">Вы</span>' : ''}
                </div>
            </td>
            <td>
                <div class="level-badge">
                    <i class="fas fa-star"></i>
                    ${employee.level}
                </div>
            </td>
            <td>
                <div class="xp-info">
                    <span class="xp-amount">${employee.xp_points}</span>
                    <span class="xp-label">XP</span>
                </div>
            </td>
            <td>
                <div class="achievements-count">
                    <i class="fas fa-trophy"></i>
                    ${employee.achievements.length}
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Обновляем статистику
    if (statsContainer) {
        const currentUserStats = demoLeaderboardData.find(emp => emp.id === currentUser.id);
        const totalEmployees = demoLeaderboardData.length;
        const currentUserPosition = currentUserStats ? demoLeaderboardData.indexOf(currentUserStats) + 1 : null;
        
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${totalEmployees}</div>
                        <div class="stat-label">Всего сотрудников</div>
                    </div>
                </div>
                ${currentUserPosition ? `
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-medal"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${currentUserPosition}</div>
                            <div class="stat-label">Ваше место</div>
                        </div>
                    </div>
                ` : ''}
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-star"></i>
                    </div>
                    <div class="stat-content">
                        <div class="stat-value">${currentUserStats ? currentUserStats.level : 1}</div>
                        <div class="stat-label">Ваш уровень</div>
                    </div>
                </div>
            </div>
        `;
    }
}

/**
 * Инициализация данных сотрудников
 */
function initializeEmployees() {
    // Генерация демо-данных сотрудников
    employees = [
        {
            id: 1,
            name: 'Алексей Иванов',
            position: 'Junior Developer',
            department: 'IT',
            profileComplete: 75
        },
        {
            id: 2,
            name: 'Елена Смирнова',
            position: 'UI/UX Designer',
            department: 'Design',
            profileComplete: 90
        },
        {
            id: 3,
            name: 'Дмитрий Козлов',
            position: 'Senior Developer',
            department: 'IT',
            profileComplete: 100
        },
        {
            id: 4,
            name: 'Анна Петрова',
            position: 'Project Manager',
            department: 'Management',
            profileComplete: 60
        },
        {
            id: 5,
            name: 'Михаил Волков',
            position: 'QA Engineer',
            department: 'IT',
            profileComplete: 45
        }
    ];
}

/**
 * Загрузка данных сотрудников
 */
async function loadEmployeesData() {
    const tableBody = document.getElementById('employeesTableBody');
    if (!tableBody) return;
    
    try {
        // Показываем индикатор загрузки
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;"><i class="fas fa-spinner fa-spin"></i> Загрузка сотрудников...</td></tr>';
        
        // Загружаем данные с сервера
        const employeesData = await apiClient.getAllEmployees();
        
        // Обновляем глобальный массив сотрудников
        employees = employeesData;
        
        // Очищаем таблицу
        tableBody.innerHTML = '';
        
        if (employees.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Сотрудники не найдены</td></tr>';
            return;
        }
        
        employees.forEach(employee => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${employee.full_name || 'Не указано'}</td>
                <td>${employee.position || 'Не указано'}</td>
                <td>${employee.department || 'Не указано'}</td>
                <td>
                    <div class="employee-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${employee.profileComplete || 0}%"></div>
                        </div>
                        <span class="progress-text">${employee.profileComplete || 0}%</span>
                    </div>
                </td>
                <td>
                    <button class="btn btn-secondary" onclick="viewEmployee(${employee.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Инициализация поиска и сортировки
        initializeEmployeeSearch();
        initializeTableSorting();
        
    } catch (error) {
        console.error('Error loading employees:', error);
        
        // Определяем тип ошибки и показываем соответствующее сообщение
        let errorMessage = 'Ошибка загрузки списка сотрудников';
        if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
            errorMessage = 'Сервер временно недоступен. Попробуйте позже.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = 'Нет подключения к серверу. Проверьте интернет-соединение.';
        } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            errorMessage = 'Сессия истекла. Пожалуйста, войдите заново.';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
        
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--error-color);">Ошибка загрузки сотрудников</td></tr>';
        showNotification(errorMessage, 'warning');
    }
}

/**
 * Инициализация поиска сотрудников
 */
function initializeEmployeeSearch() {
    const searchInput = document.getElementById('employeeSearch');
    const positionFilter = document.getElementById('positionFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterEmployees);
    }
    
    if (positionFilter) {
        positionFilter.addEventListener('change', filterEmployees);
    }
}

/**
 * Фильтрация сотрудников
 */
async function filterEmployees() {
    const searchTerm = document.getElementById('employeeSearch').value.toLowerCase();
    const positionFilter = document.getElementById('positionFilter').value;
    
    try {
        let filteredEmployees = employees;
        
        // Если есть поисковый запрос, используем API поиска
        if (searchTerm.trim()) {
            const searchResults = await apiClient.searchEmployees(searchTerm);
            filteredEmployees = searchResults;
        }
        
        // Дополнительная фильтрация по должности
        if (positionFilter) {
            filteredEmployees = filteredEmployees.filter(employee => 
                employee.position && employee.position.toLowerCase().includes(positionFilter.toLowerCase())
            );
        }
        
        // Обновление таблицы
        const tableBody = document.getElementById('employeesTableBody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (filteredEmployees.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Сотрудники не найдены</td></tr>';
            return;
        }
        
        filteredEmployees.forEach(employee => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${employee.full_name || 'Не указано'}</td>
                <td>${employee.position || 'Не указано'}</td>
                <td>${employee.department || 'Не указано'}</td>
                <td>
                    <div class="employee-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${employee.profileComplete || 0}%"></div>
                        </div>
                        <span class="progress-text">${employee.profileComplete || 0}%</span>
                    </div>
                </td>
                <td>
                    <button class="btn btn-secondary" onclick="viewEmployee(${employee.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error filtering employees:', error);
        showNotification('Ошибка поиска сотрудников', 'error');
    }
}

/**
 * Инициализация ассистента
 */
function initializeAssistant() {
    const assistantSubmitBtn = document.getElementById('assistantSubmitBtn');
    if (assistantSubmitBtn) {
        assistantSubmitBtn.addEventListener('click', handleAssistantRequest);
    }
    
    // Инициализация ИИ-запросов для работника
    const aiSubmitBtn = document.getElementById('aiSubmitBtn');
    if (aiSubmitBtn) {
        aiSubmitBtn.addEventListener('click', handleAIRequest);
    }
}

/**
 * Обработка ИИ-запроса работника
 */
async function handleAIRequest() {
    const request = document.getElementById('aiRequest').value;
    
    if (!request.trim()) {
        showNotification('Пожалуйста, введите ваш запрос', 'error');
        return;
    }
    
    try {
        // Показ индикатора загрузки
        const submitBtn = document.getElementById('aiSubmitBtn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        submitBtn.disabled = true;
        
        // Отправляем запрос к ИИ-ассистенту
        const response = await apiClient.getCareerRecommendations({
            request_text: request
        });
        
        // Отображаем результаты
        displayAIRecommendations(response);
        
        // Восстановление кнопки
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
    } catch (error) {
        console.error('Error getting AI recommendations:', error);
        showNotification('Ошибка получения рекомендаций: ' + error.message, 'error');
        
        // Fallback к локальному ИИ-ассистенту
        if (window.aiAssistant) {
            const results = window.aiAssistant.processRequest(request, currentUser);
            displayAIRecommendations(results);
        } else {
            const results = generateSimpleRecommendations(request);
            displayAIRecommendations(results);
        }
        
        // Восстановление кнопки
        const submitBtn = document.getElementById('aiSubmitBtn');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

/**
 * Обработка запроса к ассистенту (для менеджера)
 */
function handleAssistantRequest() {
    const request = document.getElementById('assistantRequest').value;
    
    if (!request.trim()) {
        showNotification('Пожалуйста, введите ваш запрос', 'error');
        return;
    }
    
    // Имитация обработки запроса
    const results = generateAssistantResults(request);
    displayAssistantResults(results);
}

/**
 * Генерация результатов ассистента
 */
function generateAssistantResults(request) {
    // Простая имитация ИИ-анализа
    const lowCompletionEmployees = employees.filter(emp => emp.profileComplete < 70);
    const highCompletionEmployees = employees.filter(emp => emp.profileComplete >= 90);
    
    return {
        request: request,
        analysis: `На основе вашего запроса "${request}"`,
        recommendations: [
            {
                title: 'Сотрудники с низкой заполненностью профиля',
                employees: lowCompletionEmployees,
                priority: 'high'
            },
            {
                title: 'Сотрудники с высокой заполненностью профиля',
                employees: highCompletionEmployees,
                priority: 'low'
            }
        ]
    };
}

/**
 * Отображение ИИ-рекомендаций для работника
 */
function displayAIRecommendations(results) {
    const recommendationsContainer = document.getElementById('recommendations');
    const recommendationsList = document.getElementById('recommendationsList');
    
    if (!recommendationsContainer || !recommendationsList) return;
    
    // Обрабатываем разные форматы ответов от API
    let recommendations = [];
    let title = 'Рекомендации по развитию';
    
    if (results.recommendations) {
        recommendations = results.recommendations;
        title = results.title || title;
    } else if (Array.isArray(results)) {
        recommendations = results;
    } else {
        // Если это строка (текстовый ответ от ИИ)
        recommendations = [{
            title: 'Рекомендации ИИ',
            description: results,
            priority: 5
        }];
    }
    
    recommendationsList.innerHTML = `
        <div class="ai-analysis-header">
            <h4>${title}</h4>
            <p>Персонализированные рекомендации на основе вашего запроса</p>
        </div>
        
        <div class="recommendations-grid">
            ${recommendations.map((rec, index) => `
                <div class="recommendation-card" style="animation-delay: ${index * 0.1}s">
                    <div class="recommendation-header">
                        <h5>${rec.title || 'Рекомендация'}</h5>
                        ${rec.priority ? `
                            <span class="priority-badge priority-${rec.priority > 7 ? 'high' : rec.priority > 4 ? 'medium' : 'low'}">
                                ${rec.priority > 7 ? 'Высокий' : rec.priority > 4 ? 'Средний' : 'Низкий'} приоритет
                            </span>
                        ` : ''}
                    </div>
                    
                    <div class="recommendation-content">
                        <p class="recommendation-description">${rec.description || rec}</p>
                        
                        ${rec.roadmap ? `
                            <div class="roadmap-section">
                                <h6>План развития:</h6>
                                <ol class="roadmap-steps">
                                    ${rec.roadmap.slice(0, 3).map(step => `
                                        <li>
                                            <strong>${step.skill || step}</strong>
                                            ${step.difficulty ? `<span class="step-difficulty">${step.difficulty}</span>` : ''}
                                            ${step.timeToLearn ? `<span class="step-time">${step.timeToLearn}</span>` : ''}
                                        </li>
                                    `).join('')}
                                </ol>
                            </div>
                        ` : ''}
                        
                        ${rec.resources ? `
                            <div class="resources-section">
                                <h6>Рекомендуемые ресурсы:</h6>
                                <ul class="resources-list">
                                    ${rec.resources.slice(0, 3).map(resource => `
                                        <li><i class="fas fa-book"></i> ${resource}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${rec.estimatedTime ? `
                            <div class="time-estimate">
                                <i class="fas fa-clock"></i>
                                <span>Примерное время: ${rec.estimatedTime}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    recommendationsContainer.style.display = 'block';
    recommendationsContainer.classList.add('fade-in');
    
    // Анимация появления карточек
    const cards = recommendationsList.querySelectorAll('.recommendation-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Генерация простых рекомендаций (fallback)
 */
function generateSimpleRecommendations(request) {
    const recommendations = [
        {
            title: 'Изучение Python',
            description: 'Python - один из самых популярных языков программирования',
            resources: ['Курс "Python для начинающих"', 'Практические проекты', 'Официальная документация'],
            estimatedTime: '3-6 месяцев',
            priority: 8
        },
        {
            title: 'Развитие навыков лидерства',
            description: 'Лидерские качества помогут в карьерном росте',
            resources: ['Книги по лидерству', 'Практика управления проектами', 'Менторство'],
            estimatedTime: '6-12 месяцев',
            priority: 7
        },
        {
            title: 'Изучение современных фреймворков',
            description: 'React, Vue или Angular для frontend разработки',
            resources: ['Официальная документация', 'Онлайн курсы', 'Практические проекты'],
            estimatedTime: '2-4 месяца',
            priority: 6
        }
    ];
    
    return {
        title: 'Рекомендации по развитию',
        recommendations: recommendations.slice(0, 3)
    };
}

/**
 * Отображение результатов ассистента (для менеджера)
 */
function displayAssistantResults(results) {
    const resultsContainer = document.getElementById('assistantResults');
    const resultsContent = document.getElementById('resultsContent');
    
    if (!resultsContainer || !resultsContent) return;
    
    resultsContent.innerHTML = `
        <div class="analysis-summary">
            <h4>Анализ запроса</h4>
            <p>${results.analysis}</p>
        </div>
        
        <div class="recommendations">
            ${results.recommendations.map(rec => `
                <div class="recommendation-item ${rec.priority}">
                    <h5>${rec.title}</h5>
                    <div class="employee-list">
                        ${rec.employees.map(emp => `
                            <div class="employee-item">
                                <span class="employee-name">${emp.name}</span>
                                <span class="employee-position">${emp.position}</span>
                                <span class="employee-progress">${emp.profileComplete}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    resultsContainer.style.display = 'block';
    resultsContainer.classList.add('fade-in');
}

/**
 * Переключение сайдбара на мобильных
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

/**
 * Обработка выхода из системы
 */
async function handleLogout() {
    try {
        // Отправляем запрос на выход
        await apiClient.logout();
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Очистка данных
        localStorage.removeItem('currentUser');
        
        // Перенаправление на страницу авторизации
        window.location.href = 'index.html';
    }
}

/**
 * Показ приветственного сообщения
 */
function showWelcomeMessage() {
    setTimeout(() => {
        showNotification(`Добро пожаловать, ${currentUser.name}!`, 'success');
    }, 500);
}

/**
 * Показ уведомления
 */
function showNotification(message, type = 'info') {
    // Добавляем уведомление в систему
    addNotification(type, getNotificationTitle(type), message);
    
    // Показываем временное уведомление
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Получение заголовка уведомления
 */
function getNotificationTitle(type) {
    const titles = {
        success: 'Успешно!',
        error: 'Ошибка',
        info: 'Информация',
        achievement: 'Достижение!'
    };
    return titles[type] || 'Уведомление';
}

/**
 * Получение цвета для уведомления
 */
function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        achievement: '#f59e0b'
    };
    return colors[type] || '#3b82f6';
}

/**
 * Инициализация системы уведомлений
 */
function initializeNotifications() {
    // Загрузка уведомлений из localStorage
    const savedNotifications = localStorage.getItem('notifications');
    if (savedNotifications) {
        notifications = JSON.parse(savedNotifications);
    } else {
        // Создание демо-уведомлений
        notifications = [
            {
                id: 1,
                type: 'achievement',
                title: 'Новое достижение!',
                message: 'Вы получили достижение "Первый шаг"',
                time: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 часа назад
                read: false
            },
            {
                id: 2,
                type: 'success',
                title: 'Профиль обновлен',
                message: 'Ваш профиль был успешно сохранен',
                time: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 часов назад
                read: false
            },
            {
                id: 3,
                type: 'info',
                title: 'Добро пожаловать!',
                message: 'Добро пожаловать в HR Консультант',
                time: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 день назад
                read: true
            }
        ];
        saveNotifications();
    }
    
    // Обработчики событий
    const notificationsBtn = document.getElementById('notifications');
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    const clearBtn = document.getElementById('clearNotifications');
    
    if (notificationsBtn) {
        notificationsBtn.addEventListener('click', toggleNotifications);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllNotifications);
    }
    
    // Закрытие при клике вне области
    document.addEventListener('click', function(e) {
        if (!notificationsBtn.contains(e.target) && !notificationsDropdown.contains(e.target)) {
            notificationsDropdown.classList.remove('show');
        }
    });
    
    // Обновление отображения
    updateNotificationsDisplay();
}

/**
 * Переключение выпадающего списка уведомлений
 */
function toggleNotifications() {
    const dropdown = document.getElementById('notificationsDropdown');
    dropdown.classList.toggle('show');
}

/**
 * Обновление отображения уведомлений
 */
function updateNotificationsDisplay() {
    const badge = document.getElementById('notificationBadge');
    const list = document.getElementById('notificationsList');
    
    if (!badge || !list) return;
    
    // Подсчет непрочитанных уведомлений
    const unreadCount = notifications.filter(n => !n.read).length;
    badge.textContent = unreadCount;
    badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    
    // Отображение списка уведомлений
    list.innerHTML = '';
    
    if (notifications.length === 0) {
        list.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-muted);">Нет уведомлений</div>';
        return;
    }
    
    notifications.forEach(notification => {
        const item = document.createElement('div');
        item.className = `notification-item ${!notification.read ? 'notification-unread' : ''}`;
        item.innerHTML = `
            <div class="notification-icon ${notification.type}">
                <i class="fas fa-${getNotificationIcon(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-time">${formatTime(notification.time)}</div>
            </div>
        `;
        
        item.addEventListener('click', () => markAsRead(notification.id));
        list.appendChild(item);
    });
}

/**
 * Получение иконки для типа уведомления
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        achievement: 'trophy',
        info: 'info-circle',
        error: 'exclamation-circle'
    };
    return icons[type] || 'bell';
}

/**
 * Форматирование времени
 */
function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (minutes < 60) {
        return `${minutes} мин назад`;
    } else if (hours < 24) {
        return `${hours} ч назад`;
    } else {
        return `${days} дн назад`;
    }
}

/**
 * Отметка уведомления как прочитанного
 */
function markAsRead(notificationId) {
    const notification = notifications.find(n => n.id === notificationId);
    if (notification) {
        notification.read = true;
        saveNotifications();
        updateNotificationsDisplay();
    }
}

/**
 * Очистка всех уведомлений
 */
function clearAllNotifications() {
    notifications = [];
    saveNotifications();
    updateNotificationsDisplay();
}

/**
 * Сохранение уведомлений в localStorage
 */
function saveNotifications() {
    localStorage.setItem('notifications', JSON.stringify(notifications));
}

/**
 * Добавление нового уведомления
 */
function addNotification(type, title, message) {
    const notification = {
        id: Date.now(),
        type,
        title,
        message,
        time: new Date(),
        read: false
    };
    
    notifications.unshift(notification);
    
    // Ограничиваем количество уведомлений
    if (notifications.length > 50) {
        notifications = notifications.slice(0, 50);
    }
    
    saveNotifications();
    updateNotificationsDisplay();
}

/**
 * Инициализация сайдбара
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const trigger = document.getElementById('sidebarTrigger');
    const mainContent = document.querySelector('.main-content');
    
    if (trigger) {
        trigger.addEventListener('mouseenter', () => {
            console.log('Sidebar trigger hovered');
            sidebar.classList.add('open');
            // Обновляем основной контент
            updateMainContentLayout(true);
        });
        
        trigger.addEventListener('mouseleave', () => {
            console.log('Sidebar trigger left');
            sidebar.classList.remove('open');
            updateMainContentLayout(false);
        });
    }
    
    if (sidebar) {
        sidebar.addEventListener('mouseenter', () => {
            sidebar.classList.add('open');
            updateMainContentLayout(true);
        });
        
        sidebar.addEventListener('mouseleave', () => {
            sidebar.classList.remove('open');
            updateMainContentLayout(false);
        });
    }
    
    // Обработка клика вне сайдбара для закрытия
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !trigger.contains(e.target)) {
            sidebar.classList.remove('open');
            updateMainContentLayout(false);
        }
    });
}

/**
 * Обновление макета основного контента
 */
function updateMainContentLayout(sidebarOpen) {
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;
    
    if (sidebarOpen) {
        mainContent.style.marginLeft = '280px';
        mainContent.style.width = 'calc(100% - 280px)';
    } else {
        mainContent.style.marginLeft = '0';
        mainContent.style.width = '100%';
    }
}

/**
 * Инициализация сортировки таблицы
 */
function initializeTableSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            let newDirection;
            
            // Если кликаем по той же колонке, меняем направление
            if (sortState.column === column) {
                newDirection = sortState.direction === 'asc' ? 'desc' : 'asc';
            } else {
                // Если кликаем по новой колонке, начинаем с возрастания
                newDirection = 'asc';
            }
            
            sortState.column = column;
            sortState.direction = newDirection;
            
            console.log(`Сортировка по ${column}, направление: ${newDirection}`);
            
            // Обновление визуальных индикаторов
            updateSortIndicators(column, newDirection);
            
            // Сортировка данных
            sortEmployees(column, newDirection);
        });
    });
}

/**
 * Обновление индикаторов сортировки
 */
function updateSortIndicators(activeColumn, direction) {
    const headers = document.querySelectorAll('.sortable');
    
    headers.forEach(header => {
        const arrows = header.querySelectorAll('.sort-arrow');
        const column = header.dataset.sort;
        
        arrows.forEach(arrow => arrow.classList.remove('active'));
        
        if (column === activeColumn) {
            const activeArrow = direction === 'asc' ? arrows[0] : arrows[1];
            activeArrow.classList.add('active');
        }
    });
}

/**
 * Сортировка сотрудников
 */
function sortEmployees(column, direction) {
    employees.sort((a, b) => {
        let aValue = a[column];
        let bValue = b[column];
        
        // Обработка разных типов данных
        if (column === 'profileComplete') {
            aValue = parseInt(aValue) || 0;
            bValue = parseInt(bValue) || 0;
        } else if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase().trim();
            bValue = bValue.toLowerCase().trim();
        }
        
        // Обработка пустых значений
        if (aValue === null || aValue === undefined || aValue === '') aValue = '';
        if (bValue === null || bValue === undefined || bValue === '') bValue = '';
        
        let result = 0;
        
        if (aValue < bValue) {
            result = -1;
        } else if (aValue > bValue) {
            result = 1;
        } else {
            result = 0;
        }
        
        return direction === 'asc' ? result : -result;
    });
    
    // Перерисовка таблицы
    loadEmployeesData();
}

/**
 * Разделение заполненности профиля и уровня
 */
function updateProfileProgress() {
    const completionIcon = document.getElementById('completionIcon');
    const completionText = document.getElementById('completionText');
    
    if (completionIcon && completionText) {
        const percentage = currentUser.profileComplete || 0;
        
        // Обновление иконки и текста в зависимости от заполненности
        if (percentage >= 80) {
            completionIcon.textContent = '✓';
            completionIcon.className = 'completion-icon high';
            completionText.textContent = 'Профиль полностью заполнен';
        } else if (percentage >= 50) {
            completionIcon.textContent = '!';
            completionIcon.className = 'completion-icon medium';
            completionText.textContent = `Профиль заполнен на ${percentage}%`;
        } else {
            completionIcon.textContent = '!';
            completionIcon.className = 'completion-icon low';
            completionText.textContent = `Профиль заполнен на ${percentage}%`;
        }
    }
    
    // Добавляем отображение уровня отдельно
    updateLevelDisplay();
}

/**
 * Обновление отображения уровня
 */
function updateLevelDisplay() {
    // Создаем элемент для отображения уровня, если его нет
    let levelDisplay = document.getElementById('levelDisplay');
    if (!levelDisplay) {
        const profileInfo = document.querySelector('.profile-info');
        if (profileInfo) {
            levelDisplay = document.createElement('div');
            levelDisplay.id = 'levelDisplay';
            levelDisplay.className = 'level-display';
            profileInfo.appendChild(levelDisplay);
        }
    }
    
    if (levelDisplay) {
        const level = currentUser.level || 1;
        const xp = currentUser.xp || 0;
        
        // Расчет прогресса до следующего уровня
        let nextLevelXP = 0;
        if (window.gamification && window.gamification.experienceSystem) {
            const levelData = window.gamification.experienceSystem.calculateProgressToNextLevel(xp);
            nextLevelXP = levelData.xpNeededForNext;
        }
        
        levelDisplay.innerHTML = `
            <div class="level-info">
                <div class="level-badge">
                    <i class="fas fa-star"></i>
                    <span>Уровень ${level}</span>
                </div>
                <div class="xp-info">
                    <span>${xp} XP</span>
                    ${nextLevelXP > 0 ? `<span class="next-level">До ${level + 1} уровня: ${nextLevelXP} XP</span>` : ''}
                </div>
            </div>
            ${nextLevelXP > 0 ? `
                <div class="level-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(100, (xp / (xp + nextLevelXP)) * 100)}%"></div>
                    </div>
                    <span class="progress-text">Прогресс до следующего уровня</span>
                </div>
            ` : ''}
        `;
    }
}

/**
 * Инициализация переключателя темы
 */
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Загрузка сохраненной темы
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    if (themeToggle) {
        themeToggle.checked = savedTheme === 'dark';
        
        themeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Показ уведомления о смене темы
            showNotification(
                `Переключено на ${newTheme === 'dark' ? 'темную' : 'светлую'} тему`,
                'info'
            );
        });
    }
}

/**
 * Применение темы
 */
function applyTheme(theme) {
    const body = document.body;
    
    if (theme === 'dark') {
        body.setAttribute('data-theme', 'dark');
    } else {
        body.removeAttribute('data-theme');
    }
}

/**
 * Инициализация кнопки "Наверх"
 */
function initializeBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    if (!backToTopBtn) return;
    
    // Обработчик прокрутки
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const header = document.querySelector('.header');
        
        // Показываем кнопку если прокрутили больше чем высота хедера
        if (scrollTop > (header ? header.offsetHeight : 100)) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });
    
    // Обработчик клика
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Глобальные функции для использования в HTML
window.viewEmployee = function(employeeId) {
    const employee = employees.find(emp => emp.id === employeeId);
    if (employee) {
        showNotification(`Просмотр профиля: ${employee.name}`, 'info');
    }
};
