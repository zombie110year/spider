# 如何下载 Bilibili 错误漫画

在出错页面, 发现 `/html/body/div[2]/div[3]/a[1]` 处的按钮 "换一张" 绑定了一个事件:

```javascript
function(o) {
  if (r("a.change-img-btn", l).hasClass("off")) {
    return
  }
  var t = r("img", l).attr("src");
  rec_rp("event", "errorPage_btnrefresh_click", {
    pic: t,
    url: window.location.href,
    errorType: options.type
  });
  r("img", l).attr("src", e(t)).one("load", function() {
    r("a.change-img-btn", l).removeClass("off");
    clearTimeout(p);
    rec_rp("event", "errorpage_pageshow", {
      pic: r("img", l).attr("src"),
      url: window.location.href,
      errorType: options.type
    })
  });
  r(this).addClass("off");
  p = setTimeout(function() {
    r("a.change-img-btn", l).removeClass("off")
  }, 3e3);
  f++;
  if (f == 100) {
    (new MessageBox).show(r(this), "别刷了，其实一共就" + (a.length + 1) + "张(笑)", 3e3)
  } else if (f == 200) {
    (new MessageBox).show(r(this), "好吧骗你的，其实一共就" + a.length + "张(笑)", 3e3)
  }
}
```

光从这里找不出有意义的信息, 所以查找了对应的 js 文件 `https://static.hdslb.com/error/dist/error.js`,
在里面发现了一个 url: `//www.bilibili.com/activity/web/view/data/31`,
发现这个请求将会返回一组图片地址.

并且没有任何限制, 可以直接下载.

于是就简单地 requests 走起.
