var arr = ["❤富强❤", "❤民主❤", "❤文明❤", "❤和谐❤", "❤自由❤", "❤平等❤", "❤公正❤", "❤法治❤", "❤爱国❤",
        "❤敬业❤", "❤诚信❤", "❤友善❤"]
function getRandomColor() {
var letters = '0123456789ABCDEF';
var color = '#';
for (var i = 0; i < 6; i++) {
color += letters[Math.floor(Math.random() * 16)];
}
return color;
}
document.onclick = function (x) {
// 创建元素节点对象
var span = document.createElement("span")
span.id = "aaa"
// 获取当前鼠标的坐标
span.style.left = x.clientX + "px"
span.style.top = x.clientY + "px"
// 让span的值为arr数组内随机的一个值
span.innerHTML = arr[Math.floor(Math.random() * arr.length)]
 // 设置span的背景颜色为随机颜色
span.style.color = getRandomColor();
// 设置span的动画效果（这里可以自行）
setTimeout(function () {
    span.style.opacity = "0.5"
    span.style.transform = "translateY(-100px)"
}, 100)
setTimeout(function () {
    span.style.opacity = "0"
    span.style.transform = "translateY(-230px)"
}, 1500)
// 最后一步是清掉opacirt为0的span
setTimeout(function () {
    var chi = document.getElementsByTagName("span")
    chi.id = "aaa"
    for (var i = 0; i < chi.length; i++) {
        if (chi[i].style.opacity == "0") {
            document.body.removeChild(chi[i])
        }
    }
}, 1000)
// 将span添加到body里
document.body.appendChild(span)
}