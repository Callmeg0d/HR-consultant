/**
 * Система геймификации
 * Обрабатывает достижения, опыт, прогресс-бары и мотивационные элементы
 */

// Система опыта и уровней
class ExperienceSystem {
    constructor() {
        this.baseXP = 100; // Базовый опыт для первого уровня
        this.xpMultiplier = 1.5; // Множитель опыта для следующих уровней
    }
    
    /**
     * Расчет опыта для достижения уровня
     */
    calculateXPForLevel(level) {
        if (level <= 1) return 0;
        return Math.floor(this.baseXP * Math.pow(this.xpMultiplier, level - 2));
    }
    
    /**
     * Расчет уровня на основе опыта
     */
    calculateLevelFromXP(totalXP) {
        let level = 1;
        let requiredXP = 0;
        
        while (requiredXP <= totalXP) {
            level++;
            requiredXP += this.calculateXPForLevel(level);
        }
        
        return level - 1;
    }
    
    /**
     * Расчет прогресса до следующего уровня
     */
    calculateProgressToNextLevel(totalXP) {
        const currentLevel = this.calculateLevelFromXP(totalXP);
        const xpForCurrentLevel = this.calculateXPForLevel(currentLevel);
        const xpForNextLevel = this.calculateXPForLevel(currentLevel + 1);
        const xpInCurrentLevel = totalXP - xpForCurrentLevel;
        const xpNeededForNext = xpForNextLevel - xpForCurrentLevel;
        
        return {
            currentLevel,
            progress: Math.min(100, (xpInCurrentLevel / xpNeededForNext) * 100),
            xpInCurrentLevel,
            xpNeededForNext
        };
    }
}

// Система достижений
class AchievementSystem {
    constructor() {
        this.achievements = [
            {
                id: 'first_profile',
                title: 'Первый шаг',
                description: 'Создайте свой профиль',
                icon: 'fas fa-user-plus',
                xpReward: 50,
                condition: (user) => user.name && user.position,
                category: 'profile'
            },
            {
                id: 'skill_master',
                title: 'Мастер навыков',
                description: 'Укажите 3 или более навыков',
                icon: 'fas fa-tools',
                xpReward: 75,
                condition: (user) => {
                    if (!user.skills) return false;
                    const skills = user.skills.split(',').map(s => s.trim()).filter(s => s);
                    return skills.length >= 3;
                },
                category: 'skills'
            },
            {
                id: 'goal_setter',
                title: 'Постановщик целей',
                description: 'Определите цели развития',
                icon: 'fas fa-bullseye',
                xpReward: 100,
                condition: (user) => user.goals && user.goals.trim() !== '',
                category: 'goals'
            },
            {
                id: 'profile_complete',
                title: 'Профиль завершен',
                description: 'Заполните профиль на 100%',
                icon: 'fas fa-trophy',
                xpReward: 200,
                condition: (user) => user.profileComplete >= 100,
                category: 'profile'
            },
            {
                id: 'experienced',
                title: 'Опытный сотрудник',
                description: 'Укажите опыт работы более 3 лет',
                icon: 'fas fa-clock',
                xpReward: 150,
                condition: (user) => parseInt(user.experience) >= 3,
                category: 'experience'
            },
            {
                id: 'team_player',
                title: 'Командный игрок',
                description: 'Укажите отдел и должность',
                icon: 'fas fa-users',
                xpReward: 100,
                condition: (user) => user.department && user.position,
                category: 'team'
            },
            {
                id: 'level_5',
                title: 'Пятый уровень',
                description: 'Достигните 5 уровня',
                icon: 'fas fa-star',
                xpReward: 300,
                condition: (user) => user.level >= 5,
                category: 'level'
            },
            {
                id: 'level_10',
                title: 'Десятый уровень',
                description: 'Достигните 10 уровня',
                icon: 'fas fa-crown',
                xpReward: 500,
                condition: (user) => user.level >= 10,
                category: 'level'
            }
        ];
    }
    
    /**
     * Проверка всех достижений
     */
    checkAllAchievements(user) {
        const unlockedAchievements = [];
        
        this.achievements.forEach(achievement => {
            if (!user.achievements || !user.achievements.includes(achievement.id)) {
                if (achievement.condition(user)) {
                    unlockedAchievements.push(achievement);
                }
            }
        });
        
        return unlockedAchievements;
    }
    
    /**
     * Получение достижений по категории
     */
    getAchievementsByCategory(category) {
        return this.achievements.filter(achievement => achievement.category === category);
    }
}

// Система прогресс-баров
class ProgressBarSystem {
    constructor() {
        this.progressBars = new Map();
    }
    
    /**
     * Создание прогресс-бара
     */
    createProgressBar(elementId, options = {}) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const config = {
            value: 0,
            max: 100,
            animated: true,
            showText: true,
            color: 'primary',
            size: 'medium',
            ...options
        };
        
        this.progressBars.set(elementId, config);
        this.updateProgressBar(elementId, config.value);
    }
    
    /**
     * Обновление прогресс-бара
     */
    updateProgressBar(elementId, value, animated = true) {
        const config = this.progressBars.get(elementId);
        if (!config) return;
        
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const percentage = Math.min(100, Math.max(0, (value / config.max) * 100));
        
        // Обновление значения
        config.value = value;
        
        // Анимация
        if (animated) {
            element.style.transition = 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        element.style.width = `${percentage}%`;
        
        // Обновление текста
        if (config.showText) {
            const textElement = element.parentElement.querySelector('.progress-text');
            if (textElement) {
                textElement.textContent = `${Math.round(percentage)}%`;
            }
        }
    }
    
    /**
     * Анимация заполнения прогресс-бара
     */
    animateProgressBar(elementId, targetValue, duration = 1000) {
        const config = this.progressBars.get(elementId);
        if (!config) return;
        
        const startValue = config.value;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(1, elapsed / duration);
            
            // Easing function (ease-out)
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (targetValue - startValue) * easedProgress;
            
            this.updateProgressBar(elementId, currentValue, false);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
}

// Система уведомлений
class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.maxNotifications = 5;
    }
    
    /**
     * Показ уведомления
     */
    show(message, type = 'info', duration = 3000) {
        const notification = {
            id: Date.now(),
            message,
            type,
            duration,
            timestamp: Date.now()
        };
        
        this.notifications.push(notification);
        this.renderNotification(notification);
        
        // Автоматическое удаление
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, duration);
    }
    
    /**
     * Рендеринг уведомления
     */
    renderNotification(notification) {
        const container = this.getNotificationContainer();
        
        const element = document.createElement('div');
        element.className = `notification notification-${notification.type}`;
        element.dataset.id = notification.id;
        element.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getIconForType(notification.type)}"></i>
                <span>${notification.message}</span>
                <button class="notification-close" onclick="notificationSystem.removeNotification(${notification.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Стили
        element.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getColorForType(notification.type)};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            max-width: 400px;
            margin-bottom: 10px;
        `;
        
        container.appendChild(element);
        
        // Анимация появления
        setTimeout(() => {
            element.style.transform = 'translateX(0)';
        }, 100);
    }
    
    /**
     * Удаление уведомления
     */
    removeNotification(id) {
        const element = document.querySelector(`[data-id="${id}"]`);
        if (element) {
            element.style.transform = 'translateX(100%)';
            setTimeout(() => {
                element.remove();
            }, 300);
        }
        
        this.notifications = this.notifications.filter(n => n.id !== id);
    }
    
    /**
     * Получение контейнера уведомлений
     */
    getNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }
    
    /**
     * Получение иконки для типа уведомления
     */
    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle',
            achievement: 'trophy'
        };
        return icons[type] || 'info-circle';
    }
    
    /**
     * Получение цвета для типа уведомления
     */
    getColorForType(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            achievement: 'linear-gradient(135deg, #f59e0b, #f97316)'
        };
        return colors[type] || '#3b82f6';
    }
}

// Система мотивационных сообщений
class MotivationSystem {
    constructor() {
        this.messages = {
            profile: [
                "Отличная работа! Вы на правильном пути! 🎯",
                "Каждый шаг приближает вас к цели! 💪",
                "Продолжайте в том же духе! ⭐",
                "Ваш профиль становится все лучше! 🌟"
            ],
            achievement: [
                "Поздравляем с новым достижением! 🏆",
                "Вы настоящий профессионал! 🎉",
                "Отличная работа! Продолжайте! 🚀",
                "Новое достижение разблокировано! 🎊"
            ],
            level: [
                "Новый уровень достигнут! 🎯",
                "Вы растете как профессионал! 📈",
                "Поздравляем с повышением уровня! 🎉",
                "Отличный прогресс! Продолжайте! 💪"
            ]
        };
    }
    
    /**
     * Получение случайного мотивационного сообщения
     */
    getRandomMessage(category) {
        const messages = this.messages[category] || this.messages.profile;
        return messages[Math.floor(Math.random() * messages.length)];
    }
    
    /**
     * Показ мотивационного сообщения
     */
    showMotivation(category) {
        const message = this.getRandomMessage(category);
        notificationSystem.show(message, 'success', 4000);
    }
}

// Глобальные экземпляры систем
const experienceSystem = new ExperienceSystem();
const achievementSystem = new AchievementSystem();
const progressBarSystem = new ProgressBarSystem();
const notificationSystem = new NotificationSystem();
const motivationSystem = new MotivationSystem();

// Экспорт для использования в других модулях
window.gamification = {
    experienceSystem,
    achievementSystem,
    progressBarSystem,
    notificationSystem,
    motivationSystem
};
