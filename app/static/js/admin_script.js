function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('expanded');
}

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.querySelector('.toggle-btn');

    // 鼠标悬停时展开侧边栏
    sidebar.addEventListener('mouseenter', () => {
        sidebar.classList.add('expanded');
    });

    // 鼠标离开时收缩侧边栏
    sidebar.addEventListener('mouseleave', () => {
        sidebar.classList.remove('expanded');
    });
});
