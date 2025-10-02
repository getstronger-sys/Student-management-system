// 模拟后端API的基础URL
const API_BASE_URL = 'http://localhost:8000';

// 全局变量
let currentUser = null;
let connected = false;

// DOM元素
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const statusMessage = document.getElementById('status-message');
const loginButton = document.getElementById('login-button');
const registerButton = document.getElementById('register-button');
const cancelButton = document.getElementById('cancel-button');
const registerModal = document.getElementById('register-modal');
const registerForm = document.getElementById('register-form');
const closeModal = document.getElementsByClassName('close')[0];

// 初始化
function init() {
    // 尝试连接服务器
    connectToServer();
    
    // 绑定事件监听器
    loginForm.addEventListener('submit', handleLogin);
    registerButton.addEventListener('click', openRegisterModal);
    cancelButton.addEventListener('click', handleCancel);
    closeModal.addEventListener('click', closeRegisterModal);
    registerForm.addEventListener('submit', handleRegister);
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === registerModal) {
            closeRegisterModal();
        }
    });
    
    // 键盘事件
    usernameInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            passwordInput.focus();
        }
    });
    
    passwordInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && loginButton.disabled === false) {
            handleLogin(event);
        }
    });
}

// 连接到服务器（模拟）
function connectToServer() {
    statusMessage.textContent = '正在连接服务器...';
    statusMessage.className = 'status';
    
    // 模拟连接延迟
    setTimeout(() => {
        connected = true;
        statusMessage.textContent = '服务器连接成功';
        statusMessage.className = 'status success';
        loginButton.disabled = false;
        registerButton.disabled = false;
        usernameInput.focus();
    }, 1500);
}

// 处理登录
function handleLogin(event) {
    event.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    // 验证输入
    if (!username) {
        showError('请输入用户名');
        usernameInput.focus();
        return;
    }
    
    if (!password) {
        showError('请输入密码');
        passwordInput.focus();
        return;
    }
    
    // 检查连接状态
    if (!connected) {
        showError('未连接到服务器');
        connectToServer();
        return;
    }
    
    // 禁用登录按钮，防止重复点击
    loginButton.disabled = true;
    statusMessage.textContent = '正在登录...';
    statusMessage.className = 'status';
    
    // 模拟登录请求
    setTimeout(() => {
        // 模拟不同用户的登录结果
        let userInfo = null;
        
        if (username === 'admin' && password === 'admin123') {
            userInfo = {
                id: 1,
                username: 'admin',
                role: 'admin',
                name: '管理员'
            };
        } else if (username === 'student' && password === 'student123') {
            userInfo = {
                id: 2,
                username: 'student',
                role: 'student',
                name: '学生用户',
                student_id: '20230001',
                major: '计算机科学',
                class: '计科2301'
            };
        } else if (username === 'teacher' && password === 'teacher123') {
            userInfo = {
                id: 3,
                username: 'teacher',
                role: 'teacher',
                name: '教师用户',
                teacher_id: 'T001'
            };
        } else {
            showError('用户名或密码错误');
            loginButton.disabled = false;
            passwordInput.value = '';
            passwordInput.focus();
            return;
        }
        
        // 登录成功
        currentUser = userInfo;
        loginSuccess();
    }, 1500);
}

// 登录成功后的处理
function loginSuccess() {
    statusMessage.textContent = '登录成功，正在跳转...';
    statusMessage.className = 'status success';
    
    // 保存用户信息到本地存储
    saveUserInfo(currentUser);
    
    // 延迟跳转到主页面
    setTimeout(() => {
        // 根据用户角色跳转到不同的仪表盘
        if (currentUser.role === 'student') {
            window.location.href = 'student_dashboard.html';
        } else if (currentUser.role === 'teacher') {
            window.location.href = 'teacher_dashboard.html';
        } else if (currentUser.role === 'admin') {
            window.location.href = 'admin_dashboard.html';
        }
    }, 1000);
}

// 打开注册模态框
function openRegisterModal() {
    registerModal.style.display = 'block';
    // 清空表单
    registerForm.reset();
}

// 关闭注册模态框
function closeRegisterModal() {
    registerModal.style.display = 'none';
}

// 处理注册
function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const name = document.getElementById('reg-name').value.trim();
    const role = document.getElementById('reg-role').value;
    
    // 验证输入
    if (!username) {
        alert('请输入用户名');
        return;
    }
    
    if (!password) {
        alert('请输入密码');
        return;
    }
    
    if (!name) {
        alert('请输入姓名');
        return;
    }
    
    // 模拟注册请求
    setTimeout(() => {
        alert('注册成功！请使用新账号登录');
        closeRegisterModal();
        // 回填用户名到登录框
        usernameInput.value = username;
        passwordInput.focus();
    }, 1000);
}

// 处理取消
function handleCancel() {
    if (confirm('确定要退出系统吗？')) {
        // 模拟断开连接
        if (connected) {
            connected = false;
        }
        // 清空输入
        usernameInput.value = '';
        passwordInput.value = '';
        // 重置状态
        statusMessage.textContent = '正在连接服务器...';
        statusMessage.className = 'status';
        loginButton.disabled = true;
        registerButton.disabled = true;
    }
}

// 显示错误消息
function showError(message) {
    statusMessage.textContent = message;
    statusMessage.className = 'status error';
    
    // 3秒后恢复正常状态
    setTimeout(() => {
        if (connected) {
            statusMessage.textContent = '服务器连接成功';
            statusMessage.className = 'status success';
        } else {
            statusMessage.textContent = '正在连接服务器...';
            statusMessage.className = 'status';
        }
    }, 3000);
}

// 保存用户信息到本地存储
function saveUserInfo(userInfo) {
    localStorage.setItem('currentUser', JSON.stringify(userInfo));
    localStorage.setItem('loginStatus', 'true');
}

// 从本地存储获取用户信息
function getUserInfo() {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
}

// 清除本地存储的用户信息
function clearUserInfo() {
    localStorage.removeItem('currentUser');
}

// 模拟API请求
function apiRequest(action, params = {}, callback) {
    // 在实际应用中，这里会发送真实的HTTP请求
    console.log(`API请求: ${action}`, params);
    
    // 模拟网络延迟
    setTimeout(() => {
        // 根据不同的action返回模拟数据
        let response = { success: true };
        
        switch (action) {
            case 'get_student_info':
                response.student = {
                    student_id: '20230001',
                    name: '学生用户',
                    gender: '男',
                    birth: '2005-01-15',
                    major: '计算机科学',
                    class: '计科2301'
                };
                break;
            case 'get_my_scores':
                response.scores = [
                    {
                        course_code: 'CS101',
                        course_name: '计算机基础',
                        credits: 4,
                        score: 85,
                        semester: '2023-2024第一学期',
                        teacher_name: '王老师'
                    },
                    {
                        course_code: 'CS102',
                        course_name: '高等数学',
                        credits: 5,
                        score: 90,
                        semester: '2023-2024第一学期',
                        teacher_name: '李老师'
                    },
                    {
                        course_code: 'CS103',
                        course_name: '程序设计',
                        credits: 4,
                        score: 88,
                        semester: '2023-2024第一学期',
                        teacher_name: '张老师'
                    }
                ];
                response.gpa = 3.6;
                break;
            case 'get_student_courses':
                response.courses = [
                    {
                        course_id: 1,
                        course_code: 'CS101',
                        course_name: '计算机基础',
                        credits: 4,
                        teacher_name: '王老师',
                        class_time: '周一 1-2节',
                        class_room: 'A101'
                    },
                    {
                        course_id: 2,
                        course_code: 'CS102',
                        course_name: '高等数学',
                        credits: 5,
                        teacher_name: '李老师',
                        class_time: '周二 3-4节',
                        class_room: 'B202'
                    },
                    {
                        course_id: 3,
                        course_code: 'CS103',
                        course_name: '程序设计',
                        credits: 4,
                        teacher_name: '张老师',
                        class_time: '周四 5-6节',
                        class_room: 'C303'
                    }
                ];
                break;
            default:
                response.success = true;
        }
        
        if (callback) {
            callback(response);
        }
    }, 800);
}

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', init);