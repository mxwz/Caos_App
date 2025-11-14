document.getElementById('message-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const message = document.getElementById('message').value;

    if (name && message) {
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `name=${encodeURIComponent(name)}&message=${encodeURIComponent(message)}`
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  document.getElementById('message-form').reset();
                  location.reload();
              } else {
                  alert('提交失败，请重试。');
              }
          });
    } else {
        alert('请输入姓名和留言。');
    }
});
