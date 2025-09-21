/**
 * Логика авторизации
 * Обрабатывает вход в систему и перенаправление на панель управления
 */

// Демо-пользователи для тестирования
const demoUsers = {
    worker: {
        login: 'worker@example.com',  // Теперь это email
        password: '123',
        name: 'Алексей Иванов',
        role: 'worker',
        position: 'Junior Developer',
        department: 'IT',
        experience: 1,
        skills: 'JavaScript, React, HTML, CSS',
        goals: 'Стать Middle Developer',
        profileComplete: 75
    },
    manager: {
        login: 'manager@example.com',  // Теперь это email
        password: '123',
        name: 'Мария Петрова',
        role: 'manager',
        position: 'HR Manager',
        department: 'HR',
        experience: 5,
        skills: 'Управление персоналом, Аналитика, Коммуникации',
        goals: 'Развитие команды',
        profileComplete: 90
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
});

/**
 * Инициализация авторизации
 */
function initializeAuth() {
    const authForm = document.getElementById('authForm');
    const demoButtons = document.querySelectorAll('.demo-btn');
    
    // Обработка формы авторизации
    if (authForm) {
        authForm.addEventListener('submit', handleAuthSubmit);
    }
    
    // Обработка демо-кнопок
    demoButtons.forEach(button => {
        button.addEventListener('click', handleDemoLogin);
    });
    
    // Анимация появления элементов
    animateAuthElements();
}

/**
 * Обработка отправки формы авторизации
 */
async function handleAuthSubmit(event) {
    event.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    
    // Простая валидация
    if (!login || !password) {
        showNotification('Пожалуйста, заполните все поля', 'error');
        return;
    }
    
    // Сохраняем ссылку на кнопку и оригинальный текст
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Показываем индикатор загрузки
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вход...';
        submitBtn.disabled = true;
        
        // Отправляем запрос на сервер
        const response = await apiClient.login({
            email: login,  // Сервер ожидает поле email
            password: password
        });
        
        // Получаем информацию о пользователе
        const userData = await apiClient.getCurrentUser();
        
        // Сохранение данных пользователя в localStorage
        localStorage.setItem('currentUser', JSON.stringify(userData));
        
        // Анимация успешного входа
        showSuccessAnimation();
        
        // Перенаправление на панель управления
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
        
    } catch (error) {
        console.error('Login error:', error);
        
        // Улучшенная обработка ошибок
        let errorMessage = 'Ошибка входа в систему';
        
        if (error instanceof Error) {
            errorMessage = error.message;
        } else if (typeof error === 'string') {
            errorMessage = error;
        } else if (error && error.message) {
            errorMessage = error.message;
        } else if (error && error.detail) {
            errorMessage = error.detail;
        }
        
        // Проверяем на типичные ошибки сети
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
            errorMessage = 'Сервер недоступен. Используйте демо-вход для тестирования.';
        } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
            errorMessage = 'Неверный логин или пароль';
        } else if (errorMessage.includes('422') || errorMessage.includes('Unprocessable Entity')) {
            errorMessage = 'Неверный формат данных. Проверьте логин и пароль.';
        } else if (errorMessage.includes('500') || errorMessage.includes('Internal Server Error')) {
            errorMessage = 'Ошибка сервера. Попробуйте позже.';
        }
        
        showNotification(errorMessage, 'error');
        shakeForm();
        
        // Восстанавливаем кнопку
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

/**
 * Обработка демо-входа
 */
async function handleDemoLogin(event) {
    const role = event.target.dataset.role;
    const user = demoUsers[role];
    
    if (user) {
        // Сохраняем оригинальный текст кнопки
        const originalText = event.target.innerHTML;
        
        try {
            // Анимация нажатия кнопки
            event.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                event.target.style.transform = 'scale(1)';
            }, 150);
            
            // Показываем индикатор загрузки
            event.target.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вход...';
            event.target.disabled = true;
            
            // Отправляем запрос на сервер
            const response = await apiClient.login({
                email: user.login,  // Сервер ожидает поле email
                password: user.password
            });
            
            // Получаем информацию о пользователе
            const userData = await apiClient.getCurrentUser();
            
            // Сохранение данных пользователя
            localStorage.setItem('currentUser', JSON.stringify(userData));
            
            // Анимация успешного входа
            showSuccessAnimation();
            
            // Перенаправление
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
            
        } catch (error) {
            console.error('Demo login error:', error);
            
            // Улучшенная обработка ошибок для демо-входа
            let errorMessage = 'Ошибка демо-входа. Попробуйте обычный вход.';
            
            if (error instanceof Error) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error && error.message) {
                errorMessage = error.message;
            }
            
        // Проверяем на типичные ошибки сети
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
            // Если сервер недоступен, используем локальные демо-данные
            console.log('Server unavailable, using local demo data');
            localStorage.setItem('currentUser', JSON.stringify(user));
            showSuccessAnimation();
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
            return;
        } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
            errorMessage = 'Неверные данные для демо-входа';
        } else if (errorMessage.includes('500') || errorMessage.includes('Internal Server Error')) {
            errorMessage = 'Ошибка сервера. Попробуйте позже.';
        }
            
            showNotification(errorMessage, 'error');
            
            // Восстанавливаем кнопку
            event.target.innerHTML = originalText;
            event.target.disabled = false;
        }
    }
}

/**
 * Анимация появления элементов авторизации
 */
function animateAuthElements() {
    const authCard = document.querySelector('.auth-card');
    const formGroups = document.querySelectorAll('.form-group');
    const authButton = document.querySelector('.auth-button');
    const demoCredentials = document.querySelector('.demo-credentials');
    
    // Анимация карточки
    if (authCard) {
        authCard.style.opacity = '0';
        authCard.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            authCard.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            authCard.style.opacity = '1';
            authCard.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Анимация полей формы
    formGroups.forEach((group, index) => {
        group.style.opacity = '0';
        group.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            group.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            group.style.opacity = '1';
            group.style.transform = 'translateX(0)';
        }, 300 + (index * 100));
    });
    
    // Анимация кнопки
    if (authButton) {
        authButton.style.opacity = '0';
        authButton.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            authButton.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            authButton.style.opacity = '1';
            authButton.style.transform = 'translateY(0)';
        }, 600);
    }
    
    // Анимация демо-кнопок
    if (demoCredentials) {
        demoCredentials.style.opacity = '0';
        demoCredentials.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            demoCredentials.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            demoCredentials.style.opacity = '1';
            demoCredentials.style.transform = 'translateY(0)';
        }, 800);
    }
}

/**
 * Анимация успешного входа
 */
function showSuccessAnimation() {
    const authCard = document.querySelector('.auth-card');
    const authButton = document.querySelector('.auth-button');
    
    // Анимация кнопки
    if (authButton) {
        authButton.innerHTML = '<i class="fas fa-check"></i><span>Успешно!</span>';
        authButton.style.background = 'linear-gradient(135deg, #10b981, #06b6d4)';
        authButton.style.transform = 'scale(1.05)';
        
        setTimeout(() => {
            authButton.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Эффект частиц
    createParticleEffect();
}

/**
 * Создание эффекта частиц при успешном входе
 */
function createParticleEffect() {
    const authCard = document.querySelector('.auth-card');
    const rect = authCard.getBoundingClientRect();
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.width = '6px';
        particle.style.height = '6px';
        particle.style.background = 'linear-gradient(135deg, #10b981, #06b6d4)';
        particle.style.borderRadius = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '9999';
        
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        
        document.body.appendChild(particle);
        
        // Анимация частицы
        const angle = (Math.PI * 2 * i) / 20;
        const velocity = 100 + Math.random() * 50;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;
        
        particle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${vx}px, ${vy}px) scale(0)`, opacity: 0 }
        ], {
            duration: 1000,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        }).onfinish = () => {
            particle.remove();
        };
    }
}

/**
 * Анимация тряски формы при ошибке
 */
function shakeForm() {
    const authCard = document.querySelector('.auth-card');
    
    authCard.style.animation = 'shake 0.5s ease-in-out';
    
    setTimeout(() => {
        authCard.style.animation = '';
    }, 500);
}

/**
 * Показ уведомления
 */
function showNotification(message, type = 'info') {
    // Создание элемента уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Стили уведомления
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
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
    }, 3000);
}

// Добавление CSS анимации тряски
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);
