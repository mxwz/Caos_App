// 显示闪现消息
document.querySelectorAll('.flash_msg').forEach(function(msg) {
    msg.style.display = 'block';
    setTimeout(function() {
        msg.style.display = 'none';
    }, 3000); // 消息显示3秒后消失
});
