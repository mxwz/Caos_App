// 确保DOM完全加载后再执行JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // 日夜模式切换
    document.getElementById('theme-toggle').addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        document.querySelector('header').classList.toggle('dark-theme');
        document.querySelector('footer').classList.toggle('dark-theme');
    });

    // 背景图片更改
    document.getElementById('background-image').addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.querySelector('header').style.backgroundImage = `url('${e.target.result}')`;
            };
            reader.readAsDataURL(file);
        }
    });

    // 更新签名
    // document.getElementById('update-bio').addEventListener('click', function() {
    //     const newBio = document.getElementById('bio-input').value;
    //     if (newBio) {
    //         document.getElementById('bio').innerText = newBio;
    //         fetch('/api/profile', {
    //             method: 'PUT',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             },
    //             body: JSON.stringify({ bio: newBio })
    //         }).then(response => response.json())
    //           .then(data => console.log(data))
    //           .catch(error => console.error('Error updating bio:', error));
    //     }
    // });

    // 获取用户信息
    // fetch('/api/profile')
    //     .then(response => response.json())
    //     .then(data => {
    //         document.getElementById('phone-number').innerText = data.phone_number || '未填写';
    //         document.getElementById('gender').innerText = data.gender || '未填写';
    //         document.getElementById('age').innerText = data.age || '未填写';
    //         document.getElementById('industry').innerText = data.industry || '未填写';
    //         document.getElementById('interests').innerText = data.interests || '未填写';
    //         document.getElementById('location').innerText = data.location || '未填写';
    //     })
    //     .catch(error => console.error('Error fetching user profile:', error));
});