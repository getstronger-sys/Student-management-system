// 全局变量
let teachingScoreChart = null;
let classComparisonChart = null;

// 使用script.js中已定义的currentUser

// DOM元素
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const logoutBtn = document.getElementById('logout-btn');
const refreshBtn = document.getElementById('refresh-btn');
const courseSelect = document.getElementById('course-select');
const semesterSelect = document.getElementById('semester-select');
const batchSaveBtn = document.getElementById('batch-save-btn');
const exportBtn = document.getElementById('export-btn');
const studentSearch = document.getElementById('student-search');
const searchBtn = document.getElementById('search-btn');
const gradeInputs = document.querySelectorAll('.grade-input');

// 初始化教师仪表盘
function initTeacherDashboard() {
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
                
                // 如果切换到教学分析面板，确保图表已初始化
                if (target === 'teaching-analysis' && !teachingScoreChart) {
                    initCharts();
                }
            }
        });
    });
}

// 初始化图表
function initCharts() {
    // 教学成绩图表
    const scoreCtx = document.getElementById('teachingScoreChart');
    if (scoreCtx && !teachingScoreChart) {
        teachingScoreChart = new Chart(scoreCtx, {
            type: 'bar',
            data: {
                labels: ['优秀', '良好', '中等', '及格', '不及格'],
                datasets: [{
                    label: '学生人数',
                    data: [12, 18, 8, 2, 0],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 159, 64, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(255, 99, 132, 0.5)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '课程成绩分布（高等数学）'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 2
                        }
                    }
                }
            }
        });
    }
    
    // 班级对比图表
    const classCtx = document.getElementById('classComparisonChart');
    if (classCtx && !classComparisonChart) {
        classComparisonChart = new Chart(classCtx, {
            type: 'radar',
            data: {
                labels: ['平均分', '优秀率', '及格率', '出勤率', '作业完成率'],
                datasets: [{
                    label: '计科2301',
                    data: [85, 30, 95, 90, 88],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)'
                }, {
                    label: '计科2302',
                    data: [82, 25, 92, 88, 85],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '班级表现对比'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
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
    
    // 课程选择
    if (courseSelect) {
        courseSelect.addEventListener('change', handleCourseChange);
    }
    
    // 学期选择
    if (semesterSelect) {
        semesterSelect.addEventListener('change', handleSemesterChange);
    }
    
    // 批量保存按钮
    if (batchSaveBtn) {
        batchSaveBtn.addEventListener('click', handleBatchSave);
    }
    
    // 导出按钮
    if (exportBtn) {
        exportBtn.addEventListener('click', handleExport);
    }
    
    // 搜索按钮
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }
    
    // 搜索框回车事件
    if (studentSearch) {
        studentSearch.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // 成绩输入框事件
    gradeInputs.forEach(input => {
        input.addEventListener('input', handleGradeInput);
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
        // 加载教师信息
        loadTeacherInfo();
        
        // 加载课程数据
        loadCourses();
        
        // 加载学生数据
        loadStudents();
        
        // 加载成绩数据
        loadGrades();
        
        // 隐藏加载状态
        showLoading(false);
    }, 1000);
}

// 加载教师信息
function loadTeacherInfo() {
    apiRequest('get_teacher_info', { teacher_id: currentUser.teacher_id }, function(response) {
        if (response.success && response.teacher) {
            const teacher = response.teacher;
            // 更新个人信息面板
            updateTeacherInfo(teacher);
        }
    });
}

// 加载课程数据
function loadCourses() {
    apiRequest('get_teacher_courses', { teacher_id: currentUser.teacher_id }, function(response) {
        if (response.success && response.courses) {
            // 更新课程表格
            updateCourseTable(response.courses);
        }
    });
}

// 加载学生数据
function loadStudents() {
    // 默认加载当前选中课程的学生
    const selectedCourse = courseSelect ? courseSelect.value : '';
    apiRequest('get_course_students', { course_id: selectedCourse }, function(response) {
        if (response.success && response.students) {
            // 更新学生表格
            updateStudentTable(response.students);
        }
    });
}

// 加载成绩数据
function loadGrades() {
    const selectedCourse = courseSelect ? courseSelect.value : '';
    const selectedSemester = semesterSelect ? semesterSelect.value : '';
    
    apiRequest('get_course_grades', {
        course_id: selectedCourse,
        semester: selectedSemester
    }, function(response) {
        if (response.success && response.grades) {
            // 更新成绩表格
            updateGradeTable(response.grades);
        }
    });
}

// 更新教师信息
function updateTeacherInfo(teacher) {
    const infoDetails = document.querySelector('.info-details');
    if (infoDetails) {
        // 这里可以根据需要更新教师信息
    }
}

// 更新课程表格
function updateCourseTable(courses) {
    const courseTableBody = document.querySelector('#my-courses tbody');
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
                <td>${course.class_name || '-'}</td>
                <td>${course.class_time || '-'}</td>
                <td>${course.class_room || '-'}</td>
                <td>${course.student_count || 0}</td>
                <td>
                    <button class="table-btn primary" data-course-id="${course.course_id}">查看详情</button>
                </td>
            `;
            
            courseTableBody.appendChild(row);
        });
        
        // 为新添加的按钮绑定事件
        const detailBtns = document.querySelectorAll('.table-btn.primary');
        detailBtns.forEach(btn => {
            btn.addEventListener('click', handleTableAction);
        });
    }
}

// 更新学生表格
function updateStudentTable(students) {
    const studentTableBody = document.querySelector('#student-management tbody');
    if (studentTableBody && students.length > 0) {
        // 清空现有表格内容
        studentTableBody.innerHTML = '';
        
        // 添加新的表格行
        students.forEach(student => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${student.student_id || '-'}</td>
                <td>${student.name || '-'}</td>
                <td>${student.gender || '-'}</td>
                <td>${student.class_name || '-'}</td>
                <td>${student.major || '-'}</td>
                <td>${student.phone || '-'}</td>
                <td>
                    <button class="table-btn primary" data-student-id="${student.id}">查看详情</button>
                </td>
            `;
            
            studentTableBody.appendChild(row);
        });
        
        // 为新添加的按钮绑定事件
        const detailBtns = document.querySelectorAll('#student-management .table-btn.primary');
        detailBtns.forEach(btn => {
            btn.addEventListener('click', handleTableAction);
        });
    }
}

// 更新成绩表格
function updateGradeTable(grades) {
    const gradeTableBody = document.querySelector('.grade-table tbody');
    if (gradeTableBody && grades.length > 0) {
        // 清空现有表格内容
        gradeTableBody.innerHTML = '';
        
        // 添加新的表格行
        grades.forEach(grade => {
            // 计算总评成绩
            const finalScore = calculateFinalScore(grade);
            
            // 根据分数设置不同的样式
            let scoreClass = '';
            if (finalScore >= 90) {
                scoreClass = 'score-excellent';
            } else if (finalScore >= 80) {
                scoreClass = 'score-good';
            } else if (finalScore >= 70) {
                scoreClass = 'score-medium';
            } else if (finalScore >= 60) {
                scoreClass = 'score-pass';
            } else {
                scoreClass = 'score-fail';
            }
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${grade.student_id || '-'}</td>
                <td>${grade.student_name || '-'}</td>
                <td><input type="number" class="grade-input" value="${grade.daily_score || 0}" min="0" max="100"></td>
                <td><input type="number" class="grade-input" value="${grade.midterm_score || 0}" min="0" max="100"></td>
                <td><input type="number" class="grade-input" value="${grade.final_score || 0}" min="0" max="100"></td>
                <td class="${scoreClass}">${finalScore}</td>
                <td>
                    <button class="table-btn success">保存</button>
                </td>
            `;
            
            gradeTableBody.appendChild(row);
        });
        
        // 为新添加的按钮和输入框绑定事件
        const newGradeInputs = document.querySelectorAll('.grade-input');
        newGradeInputs.forEach(input => {
            input.addEventListener('input', handleGradeInput);
        });
        
        const saveBtns = document.querySelectorAll('.grade-table .table-btn.success');
        saveBtns.forEach(btn => {
            btn.addEventListener('click', handleTableAction);
        });
    }
}

// 计算总评成绩
function calculateFinalScore(grade) {
    // 假设权重：平时成绩30%，期中成绩30%，期末成绩40%
    const daily = grade.daily_score || 0;
    const midterm = grade.midterm_score || 0;
    const final = grade.final_score || 0;
    
    return Math.round(daily * 0.3 + midterm * 0.3 + final * 0.4);
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

// 处理课程选择变更
function handleCourseChange() {
    // 重新加载该课程的学生和成绩数据
    loadStudents();
    loadGrades();
}

// 处理学期选择变更
function handleSemesterChange() {
    // 重新加载该学期的成绩数据
    loadGrades();
}

// 处理批量保存
function handleBatchSave() {
    // 显示保存中提示
    showNotification('正在批量保存成绩...', 'info');
    
    // 模拟保存请求
    setTimeout(() => {
        showNotification('成绩批量保存成功', 'success');
    }, 1500);
}

// 处理导出
function handleExport() {
    // 模拟导出请求
    showNotification('正在导出成绩数据...', 'info');
    
    setTimeout(() => {
        showNotification('成绩导出成功', 'success');
    }, 1000);
}

// 处理搜索
function handleSearch() {
    const searchTerm = studentSearch.value.trim();
    
    if (!searchTerm) {
        showNotification('请输入搜索内容', 'warning');
        return;
    }
    
    // 显示搜索中提示
    showNotification('正在搜索学生...', 'info');
    
    // 模拟搜索请求
    setTimeout(() => {
        showNotification(`搜索结果：找到 ${Math.floor(Math.random() * 5) + 1} 名学生`, 'success');
    }, 800);
}

// 处理成绩输入
function handleGradeInput(event) {
    const input = event.target;
    const row = input.closest('tr');
    const inputs = row.querySelectorAll('.grade-input');
    
    // 获取各项成绩
    const daily = parseInt(inputs[0].value) || 0;
    const midterm = parseInt(inputs[1].value) || 0;
    const final = parseInt(inputs[2].value) || 0;
    
    // 计算总评成绩
    const finalScore = Math.round(daily * 0.3 + midterm * 0.3 + final * 0.4);
    
    // 更新总评成绩
    const scoreCell = row.querySelector('td:nth-child(6)');
    if (scoreCell) {
        scoreCell.textContent = finalScore;
        
        // 更新样式
        scoreCell.className = '';
        if (finalScore >= 90) {
            scoreCell.className = 'score-excellent';
        } else if (finalScore >= 80) {
            scoreCell.className = 'score-good';
        } else if (finalScore >= 70) {
            scoreCell.className = 'score-medium';
        } else if (finalScore >= 60) {
            scoreCell.className = 'score-pass';
        } else {
            scoreCell.className = 'score-fail';
        }
    }
}

// 处理表格操作
function handleTableAction(event) {
    const btn = event.currentTarget;
    
    if (btn.classList.contains('success')) {
        // 保存单个学生成绩
        const row = btn.closest('tr');
        const studentId = row.querySelector('td:first-child').textContent;
        
        showNotification(`正在保存${studentId}的成绩...`, 'info');
        
        // 模拟保存请求
        setTimeout(() => {
            showNotification('成绩保存成功', 'success');
        }, 800);
    } else if (btn.classList.contains('primary')) {
        // 查看详情
        const courseId = btn.getAttribute('data-course-id');
        const studentId = btn.getAttribute('data-student-id');
        
        if (courseId) {
            showNotification(`正在加载课程详情...`, 'info');
        } else if (studentId) {
            showNotification(`正在加载学生详情...`, 'info');
        }
    }
}

// 显示加载状态
function showLoading(isLoading) {
    // 可以在这里实现加载状态的显示和隐藏
}

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', initTeacherDashboard);