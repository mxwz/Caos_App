// 不能改名为gpt，否则会被广告拦截器拦截

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const question = document.getElementById('question').value;
    const responseDiv = document.getElementById('response');

    // 显示用户消息
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = question;
    responseDiv.appendChild(userMessage);

    // 创建一个空的bot消息容器
    const botMessage = document.createElement('div');
    botMessage.className = 'message bot-message';
    responseDiv.appendChild(botMessage);

    // 发送POST请求
    fetch('/gpt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question })
    }).then(response => {
        if (response.ok) {
            const eventSource = new EventSource('/gpt/stream?question=' + encodeURIComponent(question));

            let accumulatedContent = '';

            eventSource.onmessage = function(event) {
                if (event.data === "[DONE]") {
                    // 结束标志，显示完整的消息
                    botMessage.textContent = accumulatedContent;
                    accumulatedContent = ''; // 重置累积内容
                } else {
                    // 累积接收到的内容并更新显示
                    accumulatedContent += event.data;
                    setTimeout(() => {
                        botMessage.textContent = accumulatedContent;
                        responseDiv.scrollTop = responseDiv.scrollHeight; // 滚动到底部
                    }, 10); // 延迟10毫秒更新内容，以获得更平滑的效果
                }
            };

            eventSource.onerror = function() {
                eventSource.close();
            };
        } else {
            console.error('Error:', response.statusText);
        }
    });

    document.getElementById('question').value = ''; // 清空输入框
});

$(document).ready(function() {
    $('#delete-conversation-btn').click(function() {
        var conversationId = $(this).data('conversation-id');
        $.ajax({
            url: '/api/delete_gptepoch/' + conversationId,
            type: 'DELETE',
            success: function(response) {
                if (response.message === '所有对话记录已删除！') {
                    alert('对话记录已删除！');
                    location.reload(); // 刷新页面
                } else {
                    alert('删除失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('请求失败: ' + error);
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    // 选择所有class为flash_msg的元素
    var flashMessages = document.querySelectorAll('.flash_msg');

    // 为每个消息设置定时器
    flashMessages.forEach(function (flashMessage) {
        // 显示消息
        flashMessage.style.display = 'block';

        // 设置定时器，两秒后隐藏消息
        setTimeout(function () {
            flashMessage.style.display = 'none';
        }, 2000);
    });
});