//章节展开与收起
$(function() {
    var expand = true;
    ChangeAll();
    ChangFirst();
	$('.course_expand').on('click', function(){
	    var s1 = $('.course_expand').index(this);//获取当前div的序号
	    if (expand){
	        $('.state-expand').eq(s1).css("background-image","url('/static/img/open.png?v3.1')");//根据父标签的序号来改变图片
            $('.video').eq(s1).css("display","none");//根据序号来隐藏div
	        expand = false;
        }
        else{
	        $('.state-expand').eq(s1).css("background-image","url('/static/img/shrink.png?v3.1')");
	        $('.video').eq(s1).css("display","block");
	        expand = true;
        }

    });
	//初始化
	function ChangeAll() {
		$('.state-expand').css("background-image","url('/static/img/open.png?v3.1')");//全部都是收起状态的图片
		$('.video').css("display","none");//全部都隐藏
    }
    //第一个展开
    function ChangFirst() {
		$('.state-expand').eq(0).css("background-image","url('/static/img/shrink.png?v3.1')");
		$('.video').eq(0).css("display","block");
    }

    // $('.footer').eq(0).remove();
    // //滚动优化
    // window.addEventListener('scroll',function () {
	 //    var scroll_top = document.documentElement.scrollTop;
    //     if(scroll_top >= 110) {
    //          $('.aside_play').eq(0).css('top','35px');
    //          $('.content_play').eq(0).css('top','35px');
    //
    //     }else{
    //     	$('.aside_play').eq(0).css('top','188px');
    //     	$('.content_play').eq(0).css('top','188px');
		// }
    // })



});
