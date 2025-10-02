// 管理员仪表盘JavaScript

// 全局变量 - 使用script.js中已定义的currentUser
// 初始化管理员信息（如果需要）
if (!currentUser) {
    currentUser = {
        username: 'admin',
        role: 'admin',
        name: '管理员'
    };
}

// DOM元素获取
const tabButtons = document.querySelectorAll('.tab-button[data-tab]');
const tabContents = document.querySelectorAll('.tab-content');
const logoutBtn = document.getElementById('logout-btn');
const refreshBtn = document.getElementById('refresh-btn');
const backupBtn = document.getElementById('backup-btn');
const selectAllCheckbox = document.getElementById('select-all');
const userSearchInput = document.getElementById('user-search');
const userSearchBtn = document.getElementById('user-search-btn');
const userRoleFilter = document.getElementById('user-role-filter');
const addUserBtn = document.getElementById('add-user-btn');
const batchDeleteBtn = document.getElementById('batch-delete-btn');
const batchExportBtn = document.getElementById('batch-export-btn');
const addUserModal = document.getElementById('add-user-modal');
const modalClose = document.querySelector('.modal .close');
const modalCancel = document.querySelector('.modal .cancel');
const addUserForm = document.getElementById('add-user-form');
const selectedCountElement = document.getElementById('selected-count');

// 仪表盘初始化
function initDashboard() {
    // 初始化标签页导航
    initTabs();
    
    // 初始化仪表盘图表
    initCharts();
    
    // 初始化表格操作
    initTableOperations();
    
    // 初始化模态框
    initModals();
    
    // 初始化其他交互事件
    initEventListeners();
}

// 标签页导航初始化
function initTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.add('hidden'));
            
            // 添加当前活动状态
            this.classList.add('active');
            const targetTab = document.getElementById(this.dataset.tab);
            targetTab.classList.remove('hidden');
        });
    });
}

// 图表初始化
function initCharts() {
    // 用户增长趋势图表
    const userGrowthCtx = document.getElementById('userGrowthChart').getContext('2d');
    const userGrowthChart = new Chart(userGrowthCtx, {
        type: 'line',
        data: {
            labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
            datasets: [
                {
                    label: '学生',
                    data: [320, 345, 360, 380, 410, 486],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                },
                {
                    label: '教师',
                    data: [30, 32, 35, 38, 40, 42],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 专业分布饼图
    const majorDistributionCtx = document.getElementById('majorDistributionChart').getContext('2d');
    const majorDistributionChart = new Chart(majorDistributionCtx, {
        type: 'pie',
        data: {
            labels: ['计算机科学与技术', '软件工程', '网络工程', '人工智能', '数据科学'],
            datasets: [{
                data: [180, 120, 90, 50, 46],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value}人 (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 表格操作初始化
function initTableOperations() {
    // 全选功能
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.user-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectedCount();
        });
    }
    
    // 用户选择框变更
    const userCheckboxes = document.querySelectorAll('.user-select');
    userCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
    
    // 搜索功能
    if (userSearchBtn) {
        userSearchBtn.addEventListener('click', performUserSearch);
    }
    if (userSearchInput) {
        userSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performUserSearch();
            }
        });
    }
    
    // 角色筛选
    if (userRoleFilter) {
        userRoleFilter.addEventListener('change', filterUsersByRole);
    }
}

// 更新已选择的数量
function updateSelectedCount() {
    const selectedCheckboxes = document.querySelectorAll('.user-select:checked');
    const count = selectedCheckboxes.length;
    selectedCountElement.textContent = count;
    
    // 更新批量删除按钮状态
    if (batchDeleteBtn) {
        batchDeleteBtn.disabled = count === 0;
    }
}

// 执行用户搜索
function performUserSearch() {
    const searchTerm = userSearchInput.value.toLowerCase();
    const rows = document.querySelectorAll('#user-management tbody tr');
    
    rows.forEach(row => {
        const username = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const name = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        
        if (username.includes(searchTerm) || name.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// 按角色筛选用户
function filterUsersByRole() {
    const roleFilter = userRoleFilter.value;
    const rows = document.querySelectorAll('#user-management tbody tr');
    
    rows.forEach(row => {
        const roleCell = row.querySelector('td:nth-child(4)');
        const roleText = roleCell.textContent.toLowerCase();
        
        if (roleFilter === 'all' || roleText.includes(roleFilter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// 模态框初始化
function initModals() {
    // 添加用户模态框
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            addUserModal.classList.remove('hidden');
        });
    }
    
    // 关闭模态框
    if (modalClose) {
        modalClose.addEventListener('click', function() {
            addUserModal.classList.add('hidden');
        });
    }
    
    if (modalCancel) {
        modalCancel.addEventListener('click', function() {
            addUserModal.classList.add('hidden');
        });
    }
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === addUserModal) {
            addUserModal.classList.add('hidden');
        }
    });
    
    // 表单提交处理
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // 在实际应用中，这里会发送请求到服务器添加用户
            alert('用户添加成功！');
            addUserModal.classList.add('hidden');
            addUserForm.reset();
        });
    }
    
    // 根据角色显示不同的表单字段
    const roleSelect = addUserForm.querySelector('select');
    const studentInfo = document.getElementById('student-info');
    const teacherInfo = document.getElementById('teacher-info');
    
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            if (this.value === 'student') {
                studentInfo.style.display = 'block';
                teacherInfo.style.display = 'none';
            } else if (this.value === 'teacher') {
                studentInfo.style.display = 'none';
                teacherInfo.style.display = 'block';
            } else {
                studentInfo.style.display = 'none';
                teacherInfo.style.display = 'none';
            }
        });
    }
}

// 事件监听器初始化
function initEventListeners() {
    // 退出登录
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('确定要退出登录吗？')) {
                // 清除登录状态
                localStorage.removeItem('loginStatus');
                localStorage.removeItem('currentUser');
                // 跳转到登录页面
                window.location.href = 'index.html';
            }
        });
    }
    
    // 刷新功能
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // 在实际应用中，这里会重新加载数据
            alert('数据已刷新！');
        });
    }
    
    // 备份功能
    if (backupBtn) {
        backupBtn.addEventListener('click', function() {
            if (confirm('确定要备份系统数据吗？')) {
                // 在实际应用中，这里会执行备份操作
                alert('系统数据备份成功！');
            }
        });
    }
    
    // 批量删除
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            const selectedCount = document.querySelectorAll('.user-select:checked').length;
            if (selectedCount > 0 && confirm(`确定要删除选中的 ${selectedCount} 个用户吗？`)) {
                // 在实际应用中，这里会执行批量删除操作
                alert(`已删除 ${selectedCount} 个用户！`);
                updateSelectedCount();
            }
        });
    }
    
    // 批量导出
    if (batchExportBtn) {
        batchExportBtn.addEventListener('click', function() {
            // 在实际应用中，这里会执行数据导出操作
            alert('数据导出成功！');
        });
    }
}

// 模拟API请求函数
function fetchUsers() {
    // 模拟异步请求
    return new Promise((resolve) => {
        setTimeout(() => {
            // 返回模拟数据
            resolve({
                success: true,
                data: [
                    { id: 1, username: 'admin', name: '管理员', role: 'admin', status: 'active', createTime: '2023-09-01' },
                    { id: 2, username: 'student', name: '张小明', role: 'student', status: 'active', createTime: '2023-09-05' },
                    { id: 3, username: 'teacher', name: '李明', role: 'teacher', status: 'active', createTime: '2023-09-03' }
                ]
            });
        }, 500);
    });
}

function fetchCourses() {
    // 模拟异步请求
    return new Promise((resolve) => {
        setTimeout(() => {
            // 返回模拟数据
            resolve({
                success: true,
                data: [
                    { id: 1, code: 'CS101', name: '计算机基础', credit: 4, teacher: '王老师', studentCount: 40, status: 'active' },
                    { id: 2, code: 'CS102', name: '高等数学', credit: 5, teacher: '李老师', studentCount: 35, status: 'active' },
                    { id: 3, code: 'CS103', name: '程序设计', credit: 4, teacher: '张老师', studentCount: 45, status: 'active' }
                ]
            });
        }, 500);
    });
}

function fetchClasses() {
    // 模拟异步请求
    return new Promise((resolve) => {
        setTimeout(() => {
            // 返回模拟数据
            resolve({
                success: true,
                data: [
                    { id: 1, name: '计科2301', major: '计算机科学与技术', grade: 2023, studentCount: 40, headTeacher: '王老师', createTime: '2023-09-01' },
                    { id: 2, name: '计科2302', major: '计算机科学与技术', grade: 2023, studentCount: 35, headTeacher: '李老师', createTime: '2023-09-01' },
                    { id: 3, name: '软工2301', major: '软件工程', grade: 2023, studentCount: 45, headTeacher: '张老师', createTime: '2023-09-01' }
                ]
            });
        }, 500);
    });
}

function fetchScores() {
    // 模拟异步请求
    return new Promise((resolve) => {
        setTimeout(() => {
            // 返回模拟数据
            resolve({
                success: true,
                data: [
                    { id: 1, studentId: '20230001', studentName: '张小明', courseName: '高等数学', semester: '2023-2024第一学期', score: 90, teacherName: '李老师', createTime: '2023-12-10' },
                    { id: 2, studentId: '20230002', studentName: '李小华', courseName: '计算机基础', semester: '2023-2024第一学期', score: 85, teacherName: '王老师', createTime: '2023-12-09' },
                    { id: 3, studentId: '20230003', studentName: '王小强', courseName: '程序设计', semester: '2023-2024第一学期', score: 92, teacherName: '张老师', createTime: '2023-12-11' }
                ]
            });
        }, 500);
    });
}

// 页面加载完成后初始化仪表盘
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    const loginStatus = localStorage.getItem('loginStatus');
    const storedUser = localStorage.getItem('currentUser');
    
    if (!loginStatus || !storedUser) {
        // 未登录，跳转到登录页面
        window.location.href = 'index.html';
        return;
    }
    
    // 解析用户信息
    try {
        currentUser = JSON.parse(storedUser);
        // 确保是管理员角色
        if (currentUser.role !== 'admin') {
            alert('您没有权限访问此页面！');
            window.location.href = 'index.html';
            return;
        }
    } catch (e) {
        console.error('解析用户信息失败:', e);
        window.location.href = 'index.html';
        return;
    }
    
    // 初始化仪表盘
    initDashboard();
    
    // 加载数据
    loadDashboardData();
});

// 加载仪表盘数据
async function loadDashboardData() {
    try {
        // 加载各类数据
        const [users, courses, classes, scores] = await Promise.all([
            fetchUsers(),
            fetchCourses(),
            fetchClasses(),
            fetchScores()
        ]);
        
        // 在实际应用中，这里会根据返回的数据更新UI
        console.log('用户数据:', users);
        console.log('课程数据:', courses);
        console.log('班级数据:', classes);
        console.log('成绩数据:', scores);
        
        // 模拟数据加载完成
        console.log('仪表盘数据加载完成');
    } catch (error) {
        console.error('加载仪表盘数据失败:', error);
        alert('加载数据失败，请刷新页面重试！');
    }
}