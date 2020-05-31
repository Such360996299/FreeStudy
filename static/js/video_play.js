$(function() {
var pipWindow;
var video = document.getElementById('example_video_1');
var pipBtn = document.getElementById('pipBtn');
if (video !== null){
  pipBtn.addEventListener('click', function(event) {
  // console.log('切换Picture-in-Picture模式...');
  // 禁用按钮，防止二次点击
  this.disabled = true;
  try {
    if (video !== document.pictureInPictureElement) {
      // 尝试进入画中画模式
      video.requestPictureInPicture();
    } else {
      // 退出画中画
      document.exitPictureInPicture();
    }
  } catch(error) {
    console.log('&gt; 出错了！' + error);
  } finally {
    this.disabled = false;
  }
});

//Scroll一定距离实现画中画
// window.addEventListener('scroll', function(event) {
//     var s = $(window).scrollTop();
//     if(s > 800 && video !== document.pictureInPictureElement) {
//         pipBtn.disabled = true;
//         // 尝试进入画中画模式
//         video.requestPictureInPicture();
//     }
//      else {
//       // 退出画中画
// 	  pipBtn.disabled = false;
//       document.exitPictureInPicture();
//     }
// });

// 点击切换按钮可以触发画中画模式，
// 在有些浏览器中，右键也可以切换，甚至可以自动进入画中画模式
// 因此，一些与状态相关处理需要在专门的监听事件API中执行
video.addEventListener('enterpictureinpicture', function(event) {
  // console.log('&gt; 视频已进入Picture-in-Picture模式');
  pipBtn.value = pipBtn.value.replace('进入', '退出');

  pipWindow = event.pictureInPictureWindow;
  // console.log('&gt; 视频窗体尺寸为：'+ pipWindow.width +' x ' + pipWindow.height);

  // 添加resize事件，一切都是为了测试API
  pipWindow.addEventListener('resize', onPipWindowResize);
});
// 退出画中画模式时候
video.addEventListener('leavepictureinpicture', function(event) {
  // console.log('&gt; 视频已退出Picture-in-Picture模式');
  pipBtn.value = pipBtn.value.replace('退出', '进入');
  // 移除resize事件
  pipWindow.removeEventListener('resize', onPipWindowResize);
});
// 视频窗口尺寸改变时候执行的事件
var onPipWindowResize = function (event) {
  // console.log('&gt; 窗口尺寸改变为：'+ pipWindow.width +' x ' + pipWindow.height);
};
/* 特征检测 */
if ('pictureInPictureEnabled' in document == false) {
  // window.alert('当前浏览器不支持视频画中画。');
  pipBtn.value = pipBtn.value.replace('点击进入画中画状态', '当前浏览器不支持视频画中画');
  pipBtn.disabled = true;
}
}

});