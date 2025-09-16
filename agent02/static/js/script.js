document.addEventListener('DOMContentLoaded', function() {
    const inputText = document.getElementById('inputText');
    const addBtn = document.getElementById('addBtn');
    const loading = document.getElementById('loading');
    const resultMessage = document.getElementById('resultMessage');
    const messageText = document.getElementById('messageText');
    const tasksList = document.getElementById('tasksList');
    const emptyState = document.getElementById('emptyState');

    // 页面加载时获取所有任务
    loadAllTasks();

    // 添加任务按钮点击事件
    addBtn.addEventListener('click', addTask);

    // 输入框回车快捷键
    inputText.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            addTask();
        }
    });

    async function addTask() {
        const text = inputText.value.trim();
        
        if (!text) {
            showMessage('请输入提醒事项内容', 'error');
            return;
        }

        showLoading();
        hideMessage();

        try {
            const response = await fetch('/api/add-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_input: text })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, 'success');
                inputText.value = '';
                displayTasks(data.all_tasks);
            } else {
                showMessage(data.error || '添加任务失败', 'error');
            }
        } catch (error) {
            showMessage('网络错误，请检查连接', 'error');
            console.error('Error:', error);
        } finally {
            hideLoading();
        }
    }

    async function loadAllTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            if (response.ok) {
                displayTasks(data.tasks);
            }
        } catch (error) {
            console.error('加载任务失败:', error);
        }
    }

    // ...existing code...
    function displayTasks(tasks) {
        if (!tasks || tasks.length === 0) {
            emptyState.style.display = 'block';
            tasksList.innerHTML = '';
            return;
        }

        emptyState.style.display = 'none';
        tasksList.innerHTML = '';

        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-card';
            
            taskElement.innerHTML = `
                <div class="task-header">
                    <div class="task-time">${task.time}</div>
                    <div class="task-location">${task.location}</div>
                </div>
                <div class="task-content">${task.task_content}</div>
                ${task.weather_info ? `<div class="task-weather">${task.weather_info}</div>` : ''}
                <button class="delete-btn" data-id="${task.id}">删除</button>
            `;
            
            // 删除按钮事件
            const deleteBtn = taskElement.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', async function() {
                if (confirm('确定要删除该任务吗？')) {
                    await deleteTask(task.id);
                }
            });

            tasksList.appendChild(taskElement);
        });
    }

    async function deleteTask(taskId) {
        showLoading();
        hideMessage();
        try {
            const response = await fetch('/api/delete-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ task_id: Number(taskId) })
            });
            const data = await response.json();
            if (response.ok) {
                showMessage(data.message, 'success');
                displayTasks(data.all_tasks);
            } else {
                showMessage(data.error || '删除任务失败', 'error');
            }
        } catch (error) {
            showMessage('网络错误，请检查连接', 'error');
            console.error('Error:', error);
        } finally {
            hideLoading();
        }
    }
// ...existing code...

    function showLoading() {
        loading.style.display = 'block';
    }

    function hideLoading() {
        loading.style.display = 'none';
    }

    function showMessage(message, type) {
        messageText.textContent = message;
        resultMessage.className = `result-message ${type}-message`;
        resultMessage.style.display = 'block';
    }

    function hideMessage() {
        resultMessage.style.display = 'none';
    }
});