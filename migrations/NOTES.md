- FLASK_RUN_CERT=C:\Users\yang\localhost.pem;FLASK_RUN_KEY=C:\Users\yang\localhost-key.pem;FLASK_DEBUG=0;FLASK_HOST=0.0.0.0;FLASK_PORT=5036

- <li><a href="https://www.china.com" target="_blank"></a></li>，如果去掉target则实现不新开页面切换

- session.pop('email_code', None)
- session.pop('email_sent_time', None)

- redirect(url_for("register"))比render_template好处在刷新不会提示重新提交表单

- 第一次访问是get请求，提交表单时使用render_template，需要处理每一个网页对于get的请求，否则会访问频繁且死循环访问

- <form action="">可以重定向到指定路径

- @login_required用于保护路由，确保只有经过身份验证的用户才能访问，意味着该函数只能由已经登录的用户访问。\
- 如果未登录的用户尝试访问这个视图，Flask-Login 会拦截请求，并将用户重定向到一个登录页面。\
- @login_required 装饰器检查当前是否有用户登录。这通常是通过检查 Flask 的会话来完成的，Flask-Login 在用户登录时会将会话标记为已登录。\
- 如果用户未登录，@login_required 会自动将用户重定向到登录视图。默认情况下，这个视图的端点是 'login'，但您可以通过配置 Flask-Login 来更改它。

- 删除当前会话的所有内容  session.clear()，然后再重新使用session['xxx']=''即可重新创建会话ID

- readonly字段只读，required字段必填

- 如果<form>元素没有定义action属性，那么表单提交时默认会提交到当前页面所在的URL

- 多个浏览器标签或窗口：如果用户在提交位置信息后，打开了另一个浏览器标签或窗口访问例如/3D_map，那么新的标签或窗口将不会拥有之前的session数据。

- user_activity = UserActivity.query.filter_by(user_id=current_user.id).first()中current_user.id可以获取登录状态的用户id


- FLASK_RUN_CERT=C:\Users\yang\localhost.pem;FLASK_RUN_KEY=C:\Users\yang\localhost-key.pem;FLASK_DEBUG=0;FLASK_HOST=0.0.0.0;FLASK_PORT=5036
- <li><a href="https://www.china.com" target="_blank">中华网</a></li>，如果去掉target则实现不新开页面切换

- session.pop('email_code', None)
- session.pop('email_sent_time', None)

- redirect(url_for("register"))比render_template好处在刷新不会提示重新提交表单

- 第一次访问是get请求，提交表单时使用render_template，需要处理每一个网页对于get的请求，否则会访问频繁且死循环访问

- <form action="">可以重定向到指定路径

- @login_required用于保护路由，确保只有经过身份验证的用户才能访问，意味着该函数只能由已经登录的用户访问。\
- 如果未登录的用户尝试访问这个视图，Flask-Login 会拦截请求，并将用户重定向到一个登录页面。\
- @login_required 装饰器检查当前是否有用户登录。这通常是通过检查 Flask 的会话来完成的，Flask-Login 在用户登录时会将会话标记为已登录。\
- 如果用户未登录，@login_required 会自动将用户重定向到登录视图。默认情况下，这个视图的端点是 'login'，但您可以通过配置 Flask-Login 来更改它。

- 删除当前会话的所有内容  session.clear()，然后再重新使用session['xxx']=''即可重新创建会话ID

- readonly字段只读，required字段必填

- 如果<form>元素没有定义action属性，那么表单提交时默认会提交到当前页面所在的URL

- 多个浏览器标签或窗口：如果用户在提交位置信息后，打开了另一个浏览器标签或窗口访问例如/3D_map，那么新的标签或窗口将不会拥有之前的session数据。

- user_activity = UserActivity.query.filter_by(user_id=current_user.id).first()中current_user.id可以获取登录状态的用户id

- [Flask-admin管理界面](https://blog.csdn.net/2401_87170412/article/details/142501422)

- update roles set name = 'admin', description = 'administrator' where user_id = 1;

- g和session都可以保存数据，但g.user只能保存当前用户信息，而session可以保存多个用户信息
- g只能在当前请求中访问，而session可以在多个请求间访问，但g.user只能保存当前用户信息，而session可以保存多个用户信息