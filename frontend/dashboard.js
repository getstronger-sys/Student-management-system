// 全局变量
let scoreDistributionChart = null;
let semesterComparisonChart = null;

// 使用script.js中已定义的currentUser

// DOM元素
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const logoutBtn = document.getElementById('logout-btn');
const refreshBtn = document.getElementById('refresh-btn');
const addCourseBtn = document.getElementById('add-course-btn');
const courseModal = document.getElementById('course-modal');
const closeModalBtn = document.getElementsByClassName('close')[0];

// 初始化仪表盘
function initDashboard() {
    // 从本地存储获取用户信息
    currentUser = getUserInfo();
    
    if (!currentUser) {
        // 如果没有用户信息，跳转到登录页
        window.location.href = 'index.html';
        return;
    }
    
    // 初始化标签页导航
    initTabs();
    
    // 初始化图表
    initCharts();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 加载数据
    loadDashboardData();
    
    // 设置用户信息
    setUserInfo();
}

// 初始化标签页
function initTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加当前活动状态
            button.classList.add('active');
            const target = button.getAttribute('data-tab');
            const activeContent = document.getElementById(target);
            if (activeContent) {
                activeContent.classList.add('active');
                
                // 如果切换到成绩分析面板，确保图表已初始化
                if (target === 'score-analysis' && !scoreDistributionChart) {
                    initCharts();
                }
            }
        });
    });
}

// 初始化图表
function initCharts() {
    // 成绩分布图表
    const distributionCtx = document.getElementById('scoreDistributionChart');
    if (distributionCtx && !scoreDistributionChart) {
        scoreDistributionChart = new Chart(distributionCtx, {
            type: 'bar',
            data: {
                labels: ['60-70', '70-80', '80-90', '90-100'],
                datasets: [{
                    label: '课程数量',
                    data: [0, 0, 2, 1],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(255, 159, 64, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '成绩区间分布'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    // 学期对比图表
    const semesterCtx = document.getElementById('semesterComparisonChart');
    if (semesterCtx && !semesterComparisonChart) {
        semesterComparisonChart = new Chart(semesterCtx, {
            type: 'line',
            data: {
                labels: ['2023-2024第一学期'],
                datasets: [{
                    label: '平均分',
                    data: [88],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.3
                }, {
                    label: 'GPA',
                    data: [3.6],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '学期成绩趋势'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
}

// 绑定事件监听器
function bindEventListeners() {
    // 登出按钮
    logoutBtn.addEventListener('click', handleLogout);
    
    // 刷新按钮
    refreshBtn.addEventListener('click', handleRefresh);
    
    // 添加课程按钮
    if (addCourseBtn) {
        addCourseBtn.addEventListener('click', openCourseModal);
    }
    
    // 关闭模态框按钮
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeCourseModal);
    }
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === courseModal) {
            closeCourseModal();
        }
    });
    
    // 为表格中的按钮添加事件监听器
    const tableBtns = document.querySelectorAll('.table-btn');
    tableBtns.forEach(btn => {
        btn.addEventListener('click', handleTableAction);
    });
}

// 加载仪表盘数据
function loadDashboardData() {
    // 显示加载状态
    showLoading(true);
    
    // 模拟加载数据的延迟
    setTimeout(() => {
        // 加载学生信息
        loadStudentInfo();
        
        // 加载成绩数据
        loadScores();
        
        // 加载课程数据
        loadCourses();
        
        // 隐藏加载状态
        showLoading(false);
    }, 1000);
}

// 加载学生信息
function loadStudentInfo() {
    apiRequest('get_student_info', { student_id: currentUser.student_id }, function(response) {
        if (response.success && response.student) {
            const student = response.student;
            // 更新个人信息面板
            updatePersonalInfo(student);
        }
    });
}

// 加载成绩数据
function loadScores() {
    apiRequest('get_my_scores', { student_id: currentUser.student_id }, function(response) {
        if (response.success && response.scores) {
            // 更新成绩表格
            updateScoreTable(response.scores);
            
            // 更新成绩统计
            updateScoreStats(response.scores, response.gpa);
        }
    });
}

// 加载课程数据
function loadCourses() {
    apiRequest('get_student_courses', { student_id: currentUser.student_id }, function(response) {
        if (response.success && response.courses) {
            // 更新课程表格
            updateCourseTable(response.courses);
        }
    });
}

// 更新个人信息
function updatePersonalInfo(student) {
    const infoDetails = document.querySelector('.info-details');
    if (infoDetails) {
        // 这里可以根据需要更新个人信息
        // 示例：
        // const nameElement = infoDetails.querySelector('span:nth-of-type(2)');
        // if (nameElement) nameElement.textContent = student.name;
    }
}

// 更新成绩表格
function updateScoreTable(scores) {
    const scoreTableBody = document.querySelector('#scores tbody');
    if (scoreTableBody && scores.length > 0) {
        // 清空现有表格内容
        scoreTableBody.innerHTML = '';
        
        // 添加新的表格行
        scores.forEach(score => {
            const row = document.createElement('tr');
            
            // 根据分数设置不同的样式
            let scoreClass = '';
            if (score.score >= 90) {
                scoreClass = 'score-excellent';
            } else if (score.score >= 80) {
                scoreClass = 'score-good';
            } else if (score.score >= 60) {
                scoreClass = 'score-pass';
            } else {
                scoreClass = 'score-fail';
            }
            
            row.innerHTML = `
                <td>${score.course_code || '-'}</td>
                <td>${score.course_name || '-'}</td>
                <td>${score.credits || 0}</td>
                <td class="${scoreClass}">${score.score || '-'}</td>
                <td>${score.semester || '-'}</td>
                <td>${score.teacher_name || '-'}</td>
            `;
            
            scoreTableBody.appendChild(row);
        });
    }
}

// 更新成绩统计
function updateScoreStats(scores, gpa) {
    const statItems = document.querySelectorAll('.stat-item');
    if (statItems.length > 0) {
        // 计算平均分
        const totalScore = scores.reduce((sum, score) => sum + (score.score || 0), 0);
        const avgScore = totalScore / scores.length;
        
        // 计算总学分
        const totalCredits = scores.reduce((sum, score) => sum + (score.credits || 0), 0);
        
        // 更新统计数据
        if (statItems[0]) {
            statItems[0].querySelector('.stat-value').textContent = gpa || (avgScore / 25).toFixed(1);
        }
        if (statItems[1]) {
            statItems[1].querySelector('.stat-value').textContent = Math.round(avgScore);
        }
        if (statItems[2]) {
            statItems[2].querySelector('.stat-value').textContent = totalCredits;
        }
    }
}

// 更新课程表格
function updateCourseTable(courses) {
    const courseTableBody = document.querySelector('#courses tbody');
    if (courseTableBody && courses.length > 0) {
        // 清空现有表格内容
        courseTableBody.innerHTML = '';
        
        // 添加新的表格行
        courses.forEach(course => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${course.course_code || '-'}</td>
                <td>${course.course_name || '-'}</td>
                <td>${course.credits || 0}</td>
                <td>${course.teacher_name || '-'}</td>
                <td>${course.class_time || '-'}</td>
                <td>${course.class_room || '-'}</td>
                <td>
                    <button class="table-btn danger" data-course-id="${course.course_id}">退课</button>
                </td>
            `;
            
            courseTableBody.appendChild(row);
        });
        
        // 为新添加的按钮绑定事件
        const dropBtns = document.querySelectorAll('.table-btn.danger');
        dropBtns.forEach(btn => {
            btn.addEventListener('click', handleTableAction);
        });
    }
}

// 设置用户信息
function setUserInfo() {
    // 可以在这里设置页面上其他地方的用户信息
}

// 处理登出
function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        // 清除本地存储的用户信息
        clearUserInfo();
        
        // 跳转到登录页
        window.location.href = 'index.html';
    }
}

// 处理刷新
function handleRefresh() {
    // 重新加载数据
    loadDashboardData();
    
    // 显示刷新成功提示
    showNotification('数据刷新成功', 'success');
}

// 打开课程模态框
function openCourseModal() {
    if (courseModal) {
        courseModal.classList.remove('hidden');
    }
}

// 关闭课程模态框
function closeCourseModal() {
    if (courseModal) {
        courseModal.classList.add('hidden');
    }
}

// 处理表格操作
function handleTableAction(event) {
    const btn = event.currentTarget;
    const courseId = btn.getAttribute('data-course-id');
    
    if (btn.classList.contains('danger')) {
        // 退课操作
        if (confirm('确定要退选这门课程吗？')) {
            // 模拟退课请求
            setTimeout(() => {
                showNotification('退课成功', 'success');
                
                // 重新加载课程数据
                loadCourses();
            }, 800);
        }
    } else if (btn.classList.contains('success')) {
        // 选课操作
        if (confirm('确定要选择这门课程吗？')) {
            // 模拟选课请求
            setTimeout(() => {
                showNotification('选课成功', 'success');
                
                // 关闭模态框
                closeCourseModal();
                
                // 重新加载课程数据
                loadCourses();
            }, 800);
        }
    }
}

// 显示加载状态
function showLoading(isLoading) {
    // 可以在这里实现加载状态的显示和隐藏
    // 例如显示一个加载动画
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 设置样式
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '12px 20px';
    notification.style.borderRadius = '4px';
    notification.style.color = 'white';
    notification.style.fontWeight = 'bold';
    notification.style.zIndex = '1000';
    notification.style.animation = 'slideIn 0.3s ease-out';
    
    // 根据类型设置背景色
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#4CAF50';
            break;
        case 'error':
            notification.style.backgroundColor = '#f44336';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ff9800';
            break;
        default:
            notification.style.backgroundColor = '#2196F3';
    }
    
    // 3秒后移除通知
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', initDashboard);