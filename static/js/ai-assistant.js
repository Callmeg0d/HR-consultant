/**
 * ИИ-ассистент для рекомендаций по развитию
 * Обрабатывает запросы пользователей и генерирует персонализированные рекомендации
 */

class AIAssistant {
    constructor() {
        this.skillsDatabase = {
            'python': {
                name: 'Python',
                category: 'programming',
                difficulty: 'intermediate',
                resources: [
                    'Курс "Python для начинающих"',
                    'Книга "Изучаем Python"',
                    'Практические проекты на GitHub'
                ],
                timeToLearn: '3-6 месяцев'
            },
            'javascript': {
                name: 'JavaScript',
                category: 'programming',
                difficulty: 'intermediate',
                resources: [
                    'Курс "JavaScript: Полное руководство"',
                    'Практика на LeetCode',
                    'Создание веб-приложений'
                ],
                timeToLearn: '2-4 месяца'
            },
            'react': {
                name: 'React',
                category: 'frontend',
                difficulty: 'intermediate',
                resources: [
                    'Официальная документация React',
                    'Курс "React с нуля"',
                    'Создание портфолио проектов'
                ],
                timeToLearn: '2-3 месяца'
            },
            'leadership': {
                name: 'Лидерство',
                category: 'soft_skills',
                difficulty: 'advanced',
                resources: [
                    'Книга "Лидерство без титула"',
                    'Курс "Эффективное лидерство"',
                    'Практика управления командой'
                ],
                timeToLearn: '6-12 месяцев'
            },
            'project_management': {
                name: 'Управление проектами',
                category: 'management',
                difficulty: 'intermediate',
                resources: [
                    'Сертификация PMP',
                    'Курс "Agile и Scrum"',
                    'Практика с реальными проектами'
                ],
                timeToLearn: '4-8 месяцев'
            }
        };
        
        this.careerPaths = {
            'python developer': {
                title: 'Python Developer',
                description: 'Разработчик на Python',
                skills: ['python', 'django', 'flask', 'sql', 'git'],
                levels: ['junior', 'middle', 'senior']
            },
            'frontend developer': {
                title: 'Frontend Developer',
                description: 'Разработчик интерфейсов',
                skills: ['javascript', 'react', 'html', 'css', 'typescript'],
                levels: ['junior', 'middle', 'senior']
            },
            'fullstack developer': {
                title: 'Fullstack Developer',
                description: 'Полноценный разработчик',
                skills: ['javascript', 'python', 'react', 'nodejs', 'sql'],
                levels: ['junior', 'middle', 'senior']
            },
            'team lead': {
                title: 'Team Lead',
                description: 'Технический лидер команды',
                skills: ['leadership', 'project_management', 'mentoring', 'architecture'],
                levels: ['senior', 'lead', 'principal']
            }
        };
    }
    
    /**
     * Обработка запроса пользователя
     */
    processRequest(request, userProfile = null) {
        const normalizedRequest = request.toLowerCase();
        
        // Определение типа запроса
        const requestType = this.identifyRequestType(normalizedRequest);
        
        switch (requestType) {
            case 'career_path':
                return this.generateCareerPathRecommendations(normalizedRequest, userProfile);
            case 'skill_development':
                return this.generateSkillRecommendations(normalizedRequest, userProfile);
            case 'general':
            default:
                return this.generateGeneralRecommendations(normalizedRequest, userProfile);
        }
    }
    
    /**
     * Определение типа запроса
     */
    identifyRequestType(request) {
        const careerKeywords = ['стать', 'развиваться', 'карьера', 'должность', 'позиция'];
        const skillKeywords = ['навык', 'изучить', 'курс', 'обучение', 'знания'];
        
        if (careerKeywords.some(keyword => request.includes(keyword))) {
            return 'career_path';
        } else if (skillKeywords.some(keyword => request.includes(keyword))) {
            return 'skill_development';
        }
        
        return 'general';
    }
    
    /**
     * Генерация рекомендаций по карьерному пути
     */
    generateCareerPathRecommendations(request, userProfile) {
        const recommendations = [];
        
        // Поиск подходящих карьерных путей
        Object.entries(this.careerPaths).forEach(([key, path]) => {
            if (request.includes(key) || this.isPathRelevant(request, path)) {
                const recommendation = this.createCareerPathRecommendation(path, userProfile);
                recommendations.push(recommendation);
            }
        });
        
        // Если не найдено точных совпадений, предлагаем популярные пути
        if (recommendations.length === 0) {
            recommendations.push(
                this.createCareerPathRecommendation(this.careerPaths['python developer'], userProfile),
                this.createCareerPathRecommendation(this.careerPaths['frontend developer'], userProfile)
            );
        }
        
        return {
            type: 'career_path',
            title: 'Рекомендации по карьерному развитию',
            recommendations: recommendations.slice(0, 3) // Ограничиваем до 3 рекомендаций
        };
    }
    
    /**
     * Создание рекомендации по карьерному пути
     */
    createCareerPathRecommendation(path, userProfile) {
        const currentSkills = userProfile ? (userProfile.skills || '').toLowerCase().split(',').map(s => s.trim()) : [];
        const missingSkills = path.skills.filter(skill => !currentSkills.some(cs => cs.includes(skill)));
        
        return {
            title: path.title,
            description: path.description,
            currentLevel: this.assessCurrentLevel(path, userProfile),
            targetLevel: 'middle',
            skills: {
                current: path.skills.filter(skill => currentSkills.some(cs => cs.includes(skill))),
                missing: missingSkills
            },
            roadmap: this.generateRoadmap(path, missingSkills),
            estimatedTime: this.calculateEstimatedTime(missingSkills),
            priority: this.calculatePriority(path, userProfile)
        };
    }
    
    /**
     * Оценка текущего уровня пользователя
     */
    assessCurrentLevel(path, userProfile) {
        if (!userProfile) return 'junior';
        
        const experience = parseInt(userProfile.experience) || 0;
        const skillsMatch = path.skills.filter(skill => 
            (userProfile.skills || '').toLowerCase().includes(skill)
        ).length;
        
        if (experience >= 5 && skillsMatch >= path.skills.length * 0.8) {
            return 'senior';
        } else if (experience >= 2 && skillsMatch >= path.skills.length * 0.5) {
            return 'middle';
        }
        
        return 'junior';
    }
    
    /**
     * Генерация дорожной карты развития
     */
    generateRoadmap(path, missingSkills) {
        const roadmap = [];
        
        missingSkills.forEach((skill, index) => {
            const skillData = this.skillsDatabase[skill];
            if (skillData) {
                roadmap.push({
                    step: index + 1,
                    skill: skillData.name,
                    category: skillData.category,
                    difficulty: skillData.difficulty,
                    resources: skillData.resources,
                    timeToLearn: skillData.timeToLearn,
                    priority: this.calculateSkillPriority(skill, path)
                });
            }
        });
        
        // Сортировка по приоритету
        return roadmap.sort((a, b) => b.priority - a.priority);
    }
    
    /**
     * Расчет приоритета навыка
     */
    calculateSkillPriority(skill, path) {
        const coreSkills = path.skills.slice(0, 3); // Первые 3 навыка считаем основными
        return coreSkills.includes(skill) ? 10 : 5;
    }
    
    /**
     * Расчет времени обучения
     */
    calculateEstimatedTime(missingSkills) {
        const totalMonths = missingSkills.reduce((total, skill) => {
            const skillData = this.skillsDatabase[skill];
            if (skillData) {
                const timeStr = skillData.timeToLearn;
                const months = parseInt(timeStr.split('-')[1] || timeStr.split('-')[0]);
                return total + months;
            }
            return total;
        }, 0);
        
        return `${Math.ceil(totalMonths / missingSkills.length)}-${totalMonths} месяцев`;
    }
    
    /**
     * Расчет приоритета карьерного пути
     */
    calculatePriority(path, userProfile) {
        if (!userProfile) return 5;
        
        const currentSkills = (userProfile.skills || '').toLowerCase();
        const skillsMatch = path.skills.filter(skill => currentSkills.includes(skill)).length;
        const experience = parseInt(userProfile.experience) || 0;
        
        let priority = skillsMatch * 2; // Базовый приоритет на основе навыков
        priority += Math.min(experience, 5); // Бонус за опыт
        
        return Math.min(10, priority);
    }
    
    /**
     * Проверка релевантности карьерного пути
     */
    isPathRelevant(request, path) {
        const keywords = [
            path.title.toLowerCase(),
            ...path.skills,
            ...path.description.toLowerCase().split(' ')
        ];
        
        return keywords.some(keyword => request.includes(keyword));
    }
    
    /**
     * Генерация общих рекомендаций
     */
    generateGeneralRecommendations(request, userProfile) {
        const recommendations = [];
        
        // Анализ популярных навыков
        const popularSkills = ['python', 'javascript', 'react', 'leadership', 'project_management'];
        
        popularSkills.forEach(skill => {
            if (request.includes(skill) || Math.random() > 0.7) {
                const skillData = this.skillsDatabase[skill];
                if (skillData) {
                    recommendations.push({
                        title: `Изучение ${skillData.name}`,
                        description: `Рекомендуем изучить ${skillData.name} для профессионального развития`,
                        category: skillData.category,
                        difficulty: skillData.difficulty,
                        resources: skillData.resources,
                        timeToLearn: skillData.timeToLearn,
                        priority: Math.floor(Math.random() * 5) + 5
                    });
                }
            }
        });
        
        return {
            type: 'general',
            title: 'Общие рекомендации по развитию',
            recommendations: recommendations.slice(0, 3)
        };
    }
    
    /**
     * Генерация рекомендаций по навыкам
     */
    generateSkillRecommendations(request, userProfile) {
        const recommendations = [];
        
        // Поиск упомянутых навыков в запросе
        Object.entries(this.skillsDatabase).forEach(([key, skillData]) => {
            if (request.includes(key) || request.includes(skillData.name.toLowerCase())) {
                recommendations.push({
                    title: skillData.name,
                    description: `Подробный план изучения ${skillData.name}`,
                    category: skillData.category,
                    difficulty: skillData.difficulty,
                    resources: skillData.resources,
                    timeToLearn: skillData.timeToLearn,
                    priority: 8
                });
            }
        });
        
        return {
            type: 'skill_development',
            title: 'Рекомендации по развитию навыков',
            recommendations: recommendations.length > 0 ? recommendations : this.generateGeneralRecommendations(request, userProfile).recommendations
        };
    }
}

// Глобальный экземпляр ИИ-ассистента
const aiAssistant = new AIAssistant();

// Экспорт для использования в других модулях
window.aiAssistant = aiAssistant;
