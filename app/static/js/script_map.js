import AMapLoader from "@amap/amap-jsapi-loader";
window._AMapSecurityConfig = {
  securityJsCode: "「你申请的安全密钥」",
};
AMapLoader.load({
  key: "替换为你申请的 key", //申请好的 Web 端开发者 Key，首次调用 load 时必填
  version: "2.0", //指定要加载的 JS API 的版本，缺省时默认为 1.4.15
  plugins: ["AMap.Scale"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['AMap.Scale','...','...']
})
  .then((AMap) => {
    var map = new AMap.Map("container"); //"container"为 <div> 容器的 id
  })
  .catch((e) => {
    console.log(e);
  });

window.onLoad  = function(){
      var map = new AMap.Map('container');
}
var url = 'https://webapi.amap.com/maps?v=1.4.15&key=您申请的key值&callback=onLoad';
var jsapi = doc.createElement('script');
jsapi.charset = 'utf-8';
jsapi.src = url;
document.head.appendChild(jsapi);
