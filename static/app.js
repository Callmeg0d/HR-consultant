/**
 * Демонстрационные данные для HR Консультант
 * Содержит примеры сотрудников, навыков и рекомендаций
 */

// Демо-данные сотрудников для менеджера
const demoEmployees = [
    {
        id: 1,
        name: 'Алексей Иванов',
        position: 'Junior Developer',
        department: 'IT',
        experience: 1,
        skills: 'JavaScript, React, HTML, CSS',
        goals: 'Стать Middle Developer',
        profileComplete: 75,
        level: 3,
        xp: 150,
        achievements: ['first_profile', 'skill_master']
    },
    {
        id: 2,
        name: 'Елена Смирнова',
        position: 'UI/UX Designer',
        department: 'Design',
        experience: 3,
        skills: 'Figma, Adobe Creative Suite, User Research, Prototyping',
        goals: 'Стать Senior Designer',
        profileComplete: 90,
        level: 5,
        xp: 280,
        achievements: ['first_profile', 'skill_master', 'goal_setter', 'experienced']
    },
    {
        id: 3,
        name: 'Дмитрий Козлов',
        position: 'Senior Developer',
        department: 'IT',
        experience: 5,
        skills: 'Python, Django, PostgreSQL, Docker, AWS',
        goals: 'Стать Tech Lead',
        profileComplete: 100,
        level: 8,
        xp: 450,
        achievements: ['first_profile', 'skill_master', 'goal_setter', 'profile_complete', 'experienced', 'team_player']
    },
    {
        id: 4,
        name: 'Анна Петрова',
        position: 'Project Manager',
        department: 'Management',
        experience: 4,
        skills: 'Agile, Scrum, Jira, Team Leadership',
        goals: 'Стать Senior PM',
        profileComplete: 60,
        level: 2,
        xp: 80,
        achievements: ['first_profile']
    },
    {
        id: 5,
        name: 'Михаил Волков',
        position: 'QA Engineer',
        department: 'IT',
        experience: 2,
        skills: 'Manual Testing, Selenium, Postman, Test Planning',
        goals: 'Изучить автоматизацию тестирования',
        profileComplete: 45,
        level: 1,
        xp: 30,
        achievements: []
    },
    {
        id: 6,
        name: 'Ольга Новикова',
        position: 'HR Specialist',
        department: 'HR',
        experience: 3,
        skills: 'Recruitment, Onboarding, Employee Relations',
        goals: 'Развитие в HR Business Partner',
        profileComplete: 85,
        level: 4,
        xp: 200,
        achievements: ['first_profile', 'skill_master', 'goal_setter', 'experienced']
    },
    {
        id: 7,
        name: 'Сергей Морозов',
        position: 'DevOps Engineer',
        department: 'IT',
        experience: 4,
        skills: 'Kubernetes, Docker, AWS, CI/CD, Monitoring',
        goals: 'Стать Senior DevOps',
        profileComplete: 95,
        level: 6,
        xp: 320,
        achievements: ['first_profile', 'skill_master', 'goal_setter', 'experienced', 'team_player']
    },
    {
        id: 8,
        name: 'Татьяна Лебедева',
        position: 'Business Analyst',
        department: 'Analytics',
        experience: 2,
        skills: 'Requirements Analysis, SQL, Data Visualization',
        goals: 'Переход в Data Science',
        profileComplete: 70,
        level: 3,
        xp: 140,
        achievements: ['first_profile', 'skill_master']
    }
];

// Демо-навыки и компетенции
const demoSkills = {
    programming: [
        { name: 'Python', category: 'Backend', difficulty: 'Intermediate', demand: 'High' },
        { name: 'JavaScript', category: 'Frontend', difficulty: 'Intermediate', demand: 'High' },
        { name: 'React', category: 'Frontend', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Node.js', category: 'Backend', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Java', category: 'Backend', difficulty: 'Advanced', demand: 'Medium' },
        { name: 'C#', category: 'Backend', difficulty: 'Intermediate', demand: 'Medium' },
        { name: 'Go', category: 'Backend', difficulty: 'Advanced', demand: 'Medium' },
        { name: 'Rust', category: 'Backend', difficulty: 'Expert', demand: 'Low' }
    ],
    design: [
        { name: 'Figma', category: 'UI/UX', difficulty: 'Beginner', demand: 'High' },
        { name: 'Adobe Creative Suite', category: 'Design', difficulty: 'Intermediate', demand: 'Medium' },
        { name: 'Sketch', category: 'UI/UX', difficulty: 'Intermediate', demand: 'Medium' },
        { name: 'User Research', category: 'UX', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Prototyping', category: 'UX', difficulty: 'Intermediate', demand: 'High' }
    ],
    management: [
        { name: 'Agile', category: 'Methodology', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Scrum', category: 'Methodology', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Leadership', category: 'Soft Skills', difficulty: 'Advanced', demand: 'High' },
        { name: 'Project Management', category: 'Management', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Team Building', category: 'Soft Skills', difficulty: 'Intermediate', demand: 'Medium' }
    ],
    data: [
        { name: 'SQL', category: 'Database', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Data Analysis', category: 'Analytics', difficulty: 'Intermediate', demand: 'High' },
        { name: 'Machine Learning', category: 'AI/ML', difficulty: 'Advanced', demand: 'Medium' },
        { name: 'Statistics', category: 'Analytics', difficulty: 'Intermediate', demand: 'Medium' },
        { name: 'Python (Data)', category: 'Analytics', difficulty: 'Intermediate', demand: 'High' }
    ]
};

// Демо-карьерные пути
const demoCareerPaths = [
    {
        title: 'Frontend Developer',
        description: 'Разработка пользовательских интерфейсов',
        skills: ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript'],
        levels: [
            { name: 'Junior', experience: '0-2 года', skills: ['HTML', 'CSS', 'JavaScript'] },
            { name: 'Middle', experience: '2-4 года', skills: ['React', 'TypeScript', 'Testing'] },
            { name: 'Senior', experience: '4+ лет', skills: ['Architecture', 'Performance', 'Mentoring'] }
        ],
        salary: { junior: '80-120k', middle: '120-180k', senior: '180-250k' }
    },
    {
        title: 'Backend Developer',
        description: 'Разработка серверной части приложений',
        skills: ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
        levels: [
            { name: 'Junior', experience: '0-2 года', skills: ['Python', 'Django', 'SQL'] },
            { name: 'Middle', experience: '2-4 года', skills: ['API Design', 'Database Optimization', 'Testing'] },
            { name: 'Senior', experience: '4+ лет', skills: ['System Design', 'Microservices', 'DevOps'] }
        ],
        salary: { junior: '90-130k', middle: '130-190k', senior: '190-280k' }
    },
    {
        title: 'Fullstack Developer',
        description: 'Полноценная разработка веб-приложений',
        skills: ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Docker'],
        levels: [
            { name: 'Junior', experience: '0-2 года', skills: ['JavaScript', 'React', 'Node.js'] },
            { name: 'Middle', experience: '2-4 года', skills: ['Full Stack', 'Database Design', 'API Integration'] },
            { name: 'Senior', experience: '4+ лет', skills: ['System Architecture', 'Performance', 'Team Lead'] }
        ],
        salary: { junior: '85-125k', middle: '125-185k', senior: '185-270k' }
    },
    {
        title: 'DevOps Engineer',
        description: 'Автоматизация и инфраструктура',
        skills: ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Monitoring'],
        levels: [
            { name: 'Junior', experience: '0-2 года', skills: ['Docker', 'Linux', 'Scripting'] },
            { name: 'Middle', experience: '2-4 года', skills: ['Kubernetes', 'AWS', 'CI/CD'] },
            { name: 'Senior', experience: '4+ лет', skills: ['Architecture', 'Security', 'Team Leadership'] }
        ],
        salary: { junior: '100-140k', middle: '140-200k', senior: '200-300k' }
    }
];

// Демо-курсы и ресурсы
const demoResources = [
    {
        title: 'Python для начинающих',
        type: 'course',
        duration: '40 часов',
        difficulty: 'Beginner',
        skills: ['Python', 'Programming Basics'],
        provider: 'Coursera',
        rating: 4.8,
        price: 'Free',
        description: 'Полный курс по основам Python программирования'
    },
    {
        title: 'React - Полное руководство',
        type: 'course',
        duration: '60 часов',
        difficulty: 'Intermediate',
        skills: ['React', 'JavaScript', 'Frontend'],
        provider: 'Udemy',
        rating: 4.9,
        price: '$89',
        description: 'Изучение React с нуля до продвинутого уровня'
    },
    {
        title: 'Системное мышление',
        type: 'book',
        duration: '12 часов',
        difficulty: 'Intermediate',
        skills: ['Systems Thinking', 'Problem Solving'],
        provider: 'O\'Reilly',
        rating: 4.7,
        price: '$45',
        description: 'Развитие системного мышления для решения сложных задач'
    },
    {
        title: 'Лидерство без титула',
        type: 'book',
        duration: '8 часов',
        difficulty: 'Beginner',
        skills: ['Leadership', 'Management'],
        provider: 'Amazon',
        rating: 4.6,
        price: '$15',
        description: 'Практическое руководство по развитию лидерских качеств'
    }
];

// Демо-статистика для менеджера
const demoAnalytics = {
    totalEmployees: 8,
    averageProfileCompletion: 75,
    topSkills: ['JavaScript', 'Python', 'React', 'Leadership', 'Project Management'],
    departments: {
        'IT': 4,
        'Design': 1,
        'Management': 1,
        'HR': 1,
        'Analytics': 1
    },
    experienceDistribution: {
        '0-2 года': 3,
        '2-4 года': 3,
        '4+ лет': 2
    },
    goals: {
        'Career Growth': 5,
        'Skill Development': 2,
        'Leadership': 1
    }
};

// Экспорт данных
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        demoEmployees,
        demoSkills,
        demoCareerPaths,
        demoResources,
        demoAnalytics
    };
} else {
    window.demoData = {
        demoEmployees,
        demoSkills,
        demoCareerPaths,
        demoResources,
        demoAnalytics
    };
}
