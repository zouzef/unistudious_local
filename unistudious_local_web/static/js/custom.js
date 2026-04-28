var Akademi  = function(){
	"use strict"
   /* Search Bar ============ */
   var screenWidth = $( window ).width();
   var screenHeight = $( window ).height();

   var handlePreloader = function(){
          window.addEventListener('load', function() {
            jQuery('#preloader').fadeOut(500, function() {
              jQuery(this).remove();
            });
            $('#main-wrapper').addClass('show');
          });
   }




// Call it immediately
handlePreloader();
   var handleMetisMenu = function() {
	   if(jQuery('#menu').length > 0 ){
		   $("#menu").metisMenu();
	   }
	   jQuery('.metismenu > .mm-active ').each(function(){
		   if(!jQuery(this).children('ul').length > 0)
		   {
			   jQuery(this).addClass('active-no-child');
		   }
	   });
   }
   var handleAllChecked = function() {
	   $("#checkAll").on('change',function() {
		   $("td input, .email-list .custom-checkbox input").prop('checked', $(this).prop("checked"));
	   });
   }
   var handleNavigation = function() {
    $(".hamburger").on('click', function() {
        console.log("Hamburger clicked!"); // TEST
        $('#main-wrapper').toggleClass("menu-toggle");
        $(this).toggleClass("is-active");
    });
}
   var handleCurrentActive = function() {
	   for (var nk = window.location,
		   o = $("ul#menu a").filter(function() {
			   
			   return this.href == nk;
			   
		   })
		   .addClass("mm-active")
		   .parent()
		   .addClass("mm-active");;) 
	   {
		   
		   if (!o.is("li")) break;
		   
		   o = o.parent()
			   .addClass("mm-show")
			   .parent()
			   .addClass("mm-active");
	   }
   }
   var handleMiniSidebar = function() {
	   $("ul#menu>li").on('click', function() {
		   const sidebarStyle = $('body').attr('data-sidebar-style');
		   if (sidebarStyle === 'mini') {
			   console.log($(this).find('ul'))
			   $(this).find('ul').stop()
		   }
	   })
   }
   var handleMinHeight = function() {
	   var win_h = window.outerHeight;
	   var win_h = window.outerHeight;
	   if (win_h > 0 ? win_h : screen.height) {
		   $(".content-body").css("min-height", (win_h + 60) + "px");
	   };
   }
   var handleDataAction = function() {
	   $('a[data-action="collapse"]').on("click", function(i) {
		   i.preventDefault(),
			   $(this).closest(".card").find('[data-action="collapse"] i').toggleClass("mdi-arrow-down mdi-arrow-up"),
			   $(this).closest(".card").children(".card-body").collapse("toggle");
	   });

	   $('a[data-action="expand"]').on("click", function(i) {
		   i.preventDefault(),
			   $(this).closest(".card").find('[data-action="expand"] i').toggleClass("icon-size-actual icon-size-fullscreen"),
			   $(this).closest(".card").toggleClass("card-fullscreen");
	   });



	   $('[data-action="close"]').on("click", function() {
		   $(this).closest(".card").removeClass().slideUp("fast");
	   });

	   $('[data-action="reload"]').on("click", function() {
		   var e = $(this);
		   e.parents(".card").addClass("card-load"),
			   e.parents(".card").append('<div class="card-loader"><i class=" ti-reload rotate-refresh"></div>'),
			   setTimeout(function() {
				   e.parents(".card").children(".card-loader").remove(),
					   e.parents(".card").removeClass("card-load")
			   }, 2000)
	   });
   }
   var handleHeaderHight = function() {
	   const headerHight = $('.header').innerHeight();
	   $(window).scroll(function() {
		   if ($('body').attr('data-layout') === "horizontal" && $('body').attr('data-header-position') === "static" && $('body').attr('data-sidebar-position') === "fixed")
			   $(this.window).scrollTop() >= headerHight ? $('.dlabnav').addClass('fixed') : $('.dlabnav').removeClass('fixed')
	   });
   }
   var handleDzScroll = function() {
	   jQuery('.dlab-scroll').each(function(){
		   var scroolWidgetId = jQuery(this).attr('id');
		   const ps = new PerfectScrollbar('#'+scroolWidgetId, {
			 wheelSpeed: 2,
			 wheelPropagation: true,
			 minScrollbarLength: 20
		   });
		   ps.isRtl = false;
	   })
   }
   var handleMenuTabs = function() {
	   if(screenWidth <= 991 ){
		   jQuery('.menu-tabs .nav-link').on('click',function(){
			   if(jQuery(this).hasClass('open'))
			   {
				   jQuery(this).removeClass('open');
				   jQuery('.fixed-content-box').removeClass('active');
				   jQuery('.hamburger').show();
			   }else{
				   jQuery('.menu-tabs .nav-link').removeClass('open');
				   jQuery(this).addClass('open');
				   jQuery('.fixed-content-box').addClass('active');
				   jQuery('.hamburger').hide();
			   }
			   //jQuery('.fixed-content-box').toggleClass('active');
		   });
		   jQuery('.close-fixed-content').on('click',function(){
			   jQuery('.fixed-content-box').removeClass('active');
			   jQuery('.hamburger').removeClass('is-active');
			   jQuery('#main-wrapper').removeClass('menu-toggle');
			   jQuery('.hamburger').show();
		   });
	   }
   }
   var handleChatbox = function() {
	   jQuery('.bell-link').on('click',function(){
		   jQuery('.chatbox').addClass('active');
	   });
	   jQuery('.chatbox-close').on('click',function(){
		   jQuery('.chatbox').removeClass('active');
	   });
   }
   var handleMenuWallet = function() {
	   jQuery('.menu-wallet').on('click',function(){
		   jQuery('.wallet-bar').toggleClass('active');
		   jQuery('.wallet-open').toggleClass('active');
			   $(this).toggleClass("main");
	   });
	   jQuery('.wallet-bar-close').on('click',function(){
		   jQuery('.wallet-bar').removeClass('active');
		   jQuery('.wallet-open').removeClass('active');
	   });
	   setTimeout(() => {
		   if ($(window).width() <= 1400) { 
			   jQuery('.wallet-open').removeClass('active');
		   }else{
			   jQuery('.wallet-open').addClass('active');
		   }
	   }, 500);
   }
   var handlePerfectScrollbar = function() {
	   if(jQuery('.dlabnav-scroll').length > 0)
	   {
		   //const qs = new PerfectScrollbar('.dlabnav-scroll');
		   const qs = new PerfectScrollbar('.dlabnav-scroll');
		   
		   qs.isRtl = false;
	   }
   }
   var handleBtnNumber = function() {
	   $('.btn-number').on('click', function(e) {
		   e.preventDefault();

		   fieldName = $(this).attr('data-field');
		   type = $(this).attr('data-type');
		   var input = $("input[name='" + fieldName + "']");
		   var currentVal = parseInt(input.val());
		   if (!isNaN(currentVal)) {
			   if (type == 'minus')
				   input.val(currentVal - 1);
			   else if (type == 'plus')
				   input.val(currentVal + 1);
		   } else {
			   input.val(0);
		   }
	   });
   }
   var handleDzChatUser = function() {
	   jQuery('.dlab-chat-user-box .dlab-chat-user').on('click',function(){
		   jQuery('.dlab-chat-user-box').addClass('d-none');
		   jQuery('.dlab-chat-history-box').removeClass('d-none');
		   //$(".chatbox .msg_card_body").height(vHeightArea());
		   //$(".chatbox .msg_card_body").css('height',vHeightArea());
	   }); 
	   
	   jQuery('.dlab-chat-history-back').on('click',function(){
		   jQuery('.dlab-chat-user-box').removeClass('d-none');
		   jQuery('.dlab-chat-history-box').addClass('d-none');
	   }); 
	   
	   jQuery('.dz-fullscreen').on('click',function(){
		   jQuery('.dz-fullscreen').toggleClass('active');
	   });
   }
   /* WOW ANIMATION ============ */
   var wow_animation = function(){
	   if($('.wow').length > 0)
	   {
		   var wow = new WOW(
		   {
			 boxClass:     'wow',      // animated element css class (default is wow)
			 animateClass: 'animated', // animation css class (default is animated)
			 offset:       0,          // distance to the element when triggering the animation (default is 0)
			 mobile:       false       // trigger animations on mobile devices (true is default)
		   });
		   wow.init();	
	   }	
   }
   var handleshowPass = function(){
	   jQuery('.show-pass').on('click',function(){
		   jQuery(this).toggleClass('active');
		   if(jQuery('#dlab-password').attr('type') == 'password'){
			   jQuery('#dlab-password').attr('type','text');
		   }else if(jQuery('#dlab-password').attr('type') == 'text'){
			   jQuery('#dlab-password').attr('type','password');
		   }
	   });
   }
   var heartBlast = function (){
	   $(".heart").on("click", function() {
		   $(this).toggleClass("heart-blast");
	   });
   }
   var handleDzLoadMore = function() {
	   $(".dlab-load-more").on('click', function(e)
	   {
		   e.preventDefault();	//STOP default action
		   $(this).append(' <i class="fas fa-sync"></i>');
		   
		   var dlabLoadMoreUrl = $(this).attr('rel');
		   var dlabLoadMoreId = $(this).attr('id');
		   
		   $.ajax({
			   method: "POST",
			   url: dlabLoadMoreUrl,
			   dataType: 'html',
			   success: function(data) {
				   $( "#"+dlabLoadMoreId+"Content").append(data);
				   $('.dlab-load-more i').remove();
			   }
		   })
	   });
   }
   var handleLightgallery = function(){
       if (typeof $.fn.lightGallery === 'undefined') return;
	   if(jQuery('#lightgallery ,#lightgallery-2').length > 0){
		   $('#lightgallery ,#lightgallery-2').lightGallery({
			   loop:true,
			   thumbnail:true,
			   exThumbImage: 'data-exthumbimage'
		   });
	   }
   }
   var handleLightgallery1 = function(){
	   if(jQuery('#lightgallery-1').length > 0){
		   $('#lightgallery-1').lightGallery({
			   loop:true,
			   thumbnail:true,
			   exThumbImage: 'data-exthumbimage'
		   });
	   }
   }
   var handleCustomFileInput = function() {
	   $(".custom-file-input").on("change", function() {
		   var fileName = $(this).val().split("\\").pop();
		   $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
	   });
   }
   var vHeight = function(){
	   var ch = $(window).height() - 206;
	   $(".chatbox .msg_card_body").css('height',ch);
   }
   var domoPanel = function(){
	   if(jQuery(".dlab-demo-content").length>0) {
		   const ps = new PerfectScrollbar('.dlab-demo-content');
		   $('.dlab-demo-trigger').on('click', function() {
				   $('.dlab-demo-panel').addClass('show');
		   });
		   $('.dlab-demo-close, .bg-close').on('click', function() {
				   $('.dlab-demo-panel').removeClass('show');
		   });
		   
		   $('.dlab-demo-bx').on('click', function() {
			   $('.dlab-demo-bx').removeClass('demo-active');
			   $(this).addClass('demo-active');
		   });
	   }
   }
    var handleDatetimepicker = function(){
        if (
            jQuery("#datetimepicker1").length > 0 &&
            typeof $.fn.datetimepicker === "function"
        ) {
            $('#datetimepicker1').datetimepicker({
                inline: true,
            });

            setTimeout(function() {
                $('#datetimepicker1').next('.bootstrap-datetimepicker-widget')
                    .find('li')
                    .removeClass('collapsing')
                    .each(function() {
                        if ($(this).hasClass('collapse') && !$(this).hasClass('show')) {
                            // leave hidden ones as they are
                        } else {
                            $(this).removeClass('collapse').addClass('show');
                        }
                    });
            }, 0);
        }
    };

   var handleCkEditor = function(){
	   if(jQuery("#ckeditor").length>0) {
		   ClassicEditor
		   .create( document.querySelector( '#ckeditor' ), {
			   // toolbar: [ 'heading', '|', 'bold', 'italic', 'link' ]
		   } )
		   .then( editor => {
			   window.editor = editor;
		   } )
		   .catch( err => {
			   console.error( err.stack );
		   } );
	   }
   }
   var handleMenuPosition = function(){
	   
	   if(screenWidth > 1024){
		   $(".metismenu  li").unbind().each(function (e) {
			   if ($('ul', this).length > 0) {
				   var elm = $('ul:first', this).css('display','block');
				   var off = elm.offset();
				   var l = off.left;
				   var w = elm.width();
				   var elm = $('ul:first', this).removeAttr('style');
				   var docH = $("body").height();
				   var docW = $("body").width();
				   
				   if(jQuery('html').hasClass('rtl')){
					   var isEntirelyVisible = (l + w <= docW);	
				   }else{
					   var isEntirelyVisible = (l > 0)?true:false;	
				   }
					   
				   if (!isEntirelyVisible) {
					   $(this).find('ul:first').addClass('left');
				   } else {
					   $(this).find('ul:first').removeClass('left');
				   }
			   }
		   });
	   }
   }
   var handleCustomActions = function(){
	   jQuery('.w3-delete').on('click',function(){
		   jQuery(this).parents('tr').attr('style','background-color:red !important').fadeOut('slow',function(){
			   jQuery(this).remove();
		   });
	   });
   }
   var handleImageSelect = function(){
	   if(jQuery(".image-select").length>0) {
	   
		   const $_SELECT_PICKER = $('.image-select');
		   $_SELECT_PICKER.find('option').each((idx, elem) => {
			   const $OPTION = $(elem);
			   const IMAGE_URL = $OPTION.attr('data-thumbnail');
			   if (IMAGE_URL) {
				   $OPTION.attr('data-content', "<img src='%i'/> %s".replace(/%i/, IMAGE_URL).replace(/%s/, $OPTION.text()))
			   }
		   });
	   
			   $_SELECT_PICKER.selectpicker();
	   }
	   
   }
   var onePageLayout = function() {
	   'use strict';
	   if($('.header').length > 0 && $(".scroll").length > 0)
	   {
		   var headerHeight =   parseInt($('.header').css('height'), 10);
		   //alert(headerHeight); 
		   
		   $(".scroll").unbind().on('click',function(event) 
		   {
			   event.preventDefault();
			   
			   if (this.hash !== "") {
				   var hash = this.hash;	
				   var seactionPosition = $(hash).offset().top;
				   var headerHeight =   parseInt($('.header').css('height'), 10);
				   
				   
				   $('body').scrollspy({target: ".navbar", offset: headerHeight+2}); 
				   
				   var scrollTopPosition = seactionPosition - (headerHeight);
				   
				   $('html, body').animate({
					   scrollTop: scrollTopPosition
				   }, 800, function(){
					   
				   });
			   }   
		   });
		   $('body').scrollspy({target: ".navbar", offset: headerHeight + 2});  
	   }
   }
    var handelBootstrapSelect = function(){
        if(jQuery('select').length > 0){
            jQuery('select').not('.modal select, .no-selectpicker').selectpicker(); // 👈 exclude yours
        }
    }
   /* Header Fixed ============ */
   var headerFix = function(){
	   'use strict';
	   /* Main navigation fixed on top  when scroll down function custom */		
	   jQuery(window).on('scroll', function () {
		   
		   if(jQuery('.header').length > 0){
			   var menu = jQuery('.header');
			   $(window).scroll(function(){
				 var sticky = $('.header'),
					 scroll = $(window).scrollTop();

				 if (scroll >= 100){ sticky.addClass('is-fixed');
								   }else {sticky.removeClass('is-fixed');}
			   });				
		   }
		   
	   });
	   /* Main navigation fixed on top  when scroll down function custom end*/
   }
   var handleDraggableCard = function() {
	   var dzCardDraggable = function () {
		return {
		 //main function to initiate the module
		 init: function () {
		  var containers = document.querySelectorAll('.draggable-zone');

		  if (containers.length === 0) {
		   return false;
		  }

		  var swappable = new Sortable.default(containers, {
		   draggable: '.draggable',
		   handle: '.draggable.draggable-handle',
		   mirror: {
			appendTo: 'body',
			constrainDimensions: true
		   }
		   
		  });
		  swappable.on('drag:stop', () => {
			   setTimeout(function(){
				   setBoxCount();
			   }, 200);
			   
		   })
		 }
		};
	   }();

	   jQuery(document).ready(function () {
		dzCardDraggable.init();
	   });
	   
	   
	   function setBoxCount(){
		   var cardCount = 0;
		   jQuery('.dropzoneContainer').each(function(){
			   cardCount = jQuery(this).find('.draggable-handle').length;
			   jQuery(this).find('.totalCount').html(cardCount);
		   });
	   }
   }
   var handleThemeMode = function() {
		if(jQuery(".dz-theme-mode").length>0) {
			jQuery('.dz-theme-mode').on('click',function(){
				jQuery(this).toggleClass('active');
				if(jQuery(this).hasClass('active')){
					jQuery('body').attr('data-theme-version','dark');
					setCookie('version', 'dark');
					jQuery('#theme_version').val('dark');
				}else{
					jQuery('body').attr('data-theme-version','light');
					setCookie('version', 'light');
					jQuery('#theme_version').val('light');					
				}
				$('.default-select').selectpicker('refresh');
			});
			var version = getCookie('version');
			
			jQuery('body').attr('data-theme-version', version);
			jQuery('.dz-theme-mode').removeClass('active');
			setTimeout(function(){
				if(jQuery('body').attr('data-theme-version') === "dark")
				{
					jQuery('.dz-theme-mode').addClass('active');
				}
			},1500)
		}
	}
   var handleDzFullScreen = function() {
	   jQuery('.dz-fullscreen').on('click',function(e){
		   if(document.fullscreenElement||document.webkitFullscreenElement||document.mozFullScreenElement||document.msFullscreenElement) { 
			   /* Enter fullscreen */
			   if(document.exitFullscreen) {
				   document.exitFullscreen();
			   } else if(document.msExitFullscreen) {
				   document.msExitFullscreen(); /* IE/Edge */
			   } else if(document.mozCancelFullScreen) {
				   document.mozCancelFullScreen(); /* Firefox */
			   } else if(document.webkitExitFullscreen) {
				   document.webkitExitFullscreen(); /* Chrome, Safari & Opera */
			   }
		   } 
		   else { /* exit fullscreen */
			   if(document.documentElement.requestFullscreen) {
				   document.documentElement.requestFullscreen();
			   } else if(document.documentElement.webkitRequestFullscreen) {
				   document.documentElement.webkitRequestFullscreen();
			   } else if(document.documentElement.mozRequestFullScreen) {
				   document.documentElement.mozRequestFullScreen();
			   } else if(document.documentElement.msRequestFullscreen) {
				   document.documentElement.msRequestFullscreen();
			   }
		   }		
	   });
   }
   /* Handle Page On Scroll ============ */
   /* Handle Page On Scroll ============ */
   var handlePageOnScroll = function(event){
	   
	   'use strict';
	   var headerHeight = parseInt($('.header').css('height'), 10);
	   
	   $('.navbar-nav .scroll').on('click', function(event) 
	   {
		   event.preventDefault();

		   jQuery('.navbar-nav .scroll').parent().removeClass('active');
		   jQuery(this).parent().addClass('active');
		   
		   if (this.hash !== "") {
			   var hash = this.hash;	
			   var seactionPosition = parseInt($(hash).offset().top, 10);
			   var headerHeight =   parseInt($('.header').css('height'), 10);
			   
			   var scrollTopPosition = seactionPosition - headerHeight;
			   $('html, body').animate({
				   scrollTop: scrollTopPosition
			   }, 800, function(){
				   
			   });
		   }   
	   });
	   
	   pageOnScroll();
   }

   /* Page On Scroll ============ */
   var pageOnScroll = function(event){
	   
	   if(jQuery('.navbar-nav').length > 0){
		   
		   var headerHeight = parseInt(jQuery('.header').height(), 10);
		   
		   jQuery(document).on("scroll", function(){
			   
			   var scrollPos = jQuery(this).scrollTop();
			   jQuery('.navbar-nav .scroll').each(function () {
				   var elementLink = jQuery(this);
				   
				   //console.log(this.hash);
				   //console.log(jQuery(this.hash).offset());
				   
				   var refElement = jQuery(elementLink.attr("href"));
				   
				   if(jQuery(this.hash).offset() != undefined){
					   var seactionPosition = parseInt(jQuery(this.hash).offset().top, 10);
				   }else{
					   var seactionPosition = 0;
				   }
				   var scrollTopPosition = (seactionPosition - headerHeight);

				   if (scrollTopPosition <= scrollPos){
					   elementLink.parent().addClass("active");
					   elementLink.parent().siblings().removeClass("active");
				   }
			   });
			   
		   });
	   }
   } 
   

   
	   

   /* Function ============ */
   return {
	   init:function(){
		   handleMetisMenu();
		   handleAllChecked();
		   handleNavigation();
		   handleCurrentActive();
		   handleMiniSidebar();
		   handleMinHeight();
		   handleDataAction();
		   handleHeaderHight();
		   //handleDzScroll();
		   handleMenuTabs();
		   handleChatbox();
		   handleMenuWallet();
		   //handlePerfectScrollbar();
		   handleBtnNumber();
		   handleDzChatUser();
		   //handleDzFullScreen();
		   handleshowPass();
		   heartBlast();
		   wow_animation();
		   handleDzLoadMore();
		   handleLightgallery();
		   handleCustomFileInput();
		   vHeight();
		   domoPanel();
		   handleDatetimepicker();
		   handleCkEditor();
		   handleImageSelect();
		   //headerFix();
		   handelBootstrapSelect();
		   //onePageLayout();
		   //handleResizeElement();
		   handleDraggableCard();
		   handleThemeMode();
		   handleDzFullScreen();
		   handlePageOnScroll();
		   handleLightgallery1();
		   
	   },

	   
	   load:function(){
		   handlePreloader();
		   /* handleNiceSelect(); */
		   //handleMenuWallet();
		   handleCustomActions();
	   },
	   
	   resize:function(){
		   vHeight();
		   //handleMenuWallet();
	   },
	   
	   handleMenuPosition:function(){
		   
		   handleMenuPosition();
	   },
   }
   
}();

/* Document.ready Start */	
jQuery(document).ready(function() {
   $('[data-bs-toggle="popover"]').popover();
   'use strict';
   Akademi.init();
   
});
/* Document.ready END */

/* Window Load START */
jQuery(window).on('load',function () {
   'use strict'; 
   Akademi.load();
   setTimeout(function(){
		   Akademi.handleMenuPosition();
   }, 1000);
   
});
/*  Window Load END */
/* Window Resize START */
jQuery(window).on('resize',function () {
   'use strict'; 
   Akademi.resize();
   setTimeout(function(){
		   Akademi.handleMenuPosition();
   }, 1000);
});
/*  Window Resize END */





const protocol = window.location.protocol;
const host = window.location.host;

const socket = io(`${protocol}//${host}`, {
    transports: ["websocket"],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
});

socket.on('connect', function() {
    console.log("✅ Socket connected:", socket.id);

    const accountId = window.ACCOUNT_ID;
    socket.emit('register_admin', { account_id: accountId });
});

socket.on('registration_success', function(data) {
    console.log("✅ Registered as admin:", data);
});

socket.on('registration_failed', function(data) {
    console.error("❌ Registration failed:", data);
});

socket.on('disconnect', function(reason) {
    console.log("❌ Socket disconnected:", reason);
});

socket.on('connect_error', function(error) {
    console.error("Connection error:", error);
});

socket.on('disconnect', function(reason) {
    console.log("❌ Socket disconnected:", reason);
    console.trace(); // ← shows the call stack
});
// ============ FETCH NOTIFICATIONS FROM DATABASE ============
async function loadNotifications() {
    const accountId = window.ACCOUNT_ID;

    try {
        const response = await fetch(`/api/get-notification/${accountId}`);
        const data = await response.json();

        if (data.success && data.notifications) {
            const notificationList = document.querySelector('#DZ_W_Notification1 ul.timeline');

            if (!notificationList) {
                console.error("❌ Notification list not found!");
                return;
            }

            // Clear existing notifications
            notificationList.innerHTML = '';

            // Add each notification to the list
            data.notifications.forEach(notification => {
                addNotificationToUI(notification);
            });

            // Update badge count
            updateNotificationBadge(data.unread_count);

            console.log(`✅ Loaded ${data.total} notifications (${data.unread_count} unread)`);
        }
    } catch (error) {
        console.error("❌ Error loading notifications:", error);
    }
}

// ============ ADD NOTIFICATION TO UI ============

function addNotificationToUI(notification) {
    const notificationList = document.querySelector('#DZ_W_Notification1 ul.timeline');

    if (!notificationList) {
        console.error("❌ Notification list not found!");
        return;
    }

    const li = document.createElement('li');
    li.dataset.notificationId = notification.id;
    li.className = notification.is_read ? 'read' : 'unread';

    // Format the time
    const timeAgo = formatTimeAgo(notification.created_at);

    // Determine notification label and icon based on type
    let notificationLabel = '';
    let iconHtml = '';

    switch(notification.type) {
        case 'tablet_notif':
            notificationLabel = 'Notification From the tablet';
            iconHtml = '<i class="fas fa-tablet-alt" style="font-size: 24px; color: #3b82f6;"></i>';
            break;
        case 'general':
            notificationLabel = 'New Notification';
            iconHtml = '<i class="fas fa-bell" style="font-size: 24px; color: #6c757d;"></i>';
            break;
        case 'alert':
            notificationLabel = 'Alert';
            iconHtml = '<i class="fas fa-exclamation-triangle" style="font-size: 24px; color: #f59e0b;"></i>';
            break;
        case 'reminder':
            notificationLabel = 'Reminder';
            iconHtml = '<i class="fas fa-clock" style="font-size: 24px; color: #8b5cf6;"></i>';
            break;
        default:
            notificationLabel = 'New Notification';
            iconHtml = '<i class="fas fa-bell" style="font-size: 24px; color: #6c757d;"></i>';
    }

    li.innerHTML = `
        <div class="timeline-panel">
            <div class="media me-2">
                ${iconHtml}
            </div>
            <div class="media-body">
                <h6 class="mb-1">${notificationLabel}</h6>
                <small class="d-block"><strong>${notification.title}</strong></small>
                <small class="d-block">${notification.message}</small>
                <small class="d-block text-muted">${timeAgo}</small>
            </div>
        </div>
    `;

    // Add to the TOP of the list (prepend)
    notificationList.prepend(li);
}

// ============ UPDATE NOTIFICATION BADGE ============
function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationCount');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// ============ FORMAT TIME AGO ============
function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return time.toLocaleDateString();
}

// ============ REAL-TIME NOTIFICATION LISTENER ============
socket.on('calendar_notification', function(notification) {
    console.log("📩 Real-time notification received:", notification);

    // Add new notification at the TOP
    addNotificationToUI({
        id: Date.now(), // Temporary ID (will be replaced on reload)
        title: notification.title,
        message: notification.message || '',
        is_read: false,
        created_at: new Date().toISOString(),
        data: notification
    });

    // Update badge count
    const badge = document.getElementById('notificationCount');
    if (badge) {
        const currentCount = parseInt(badge.textContent) || 0;
        updateNotificationBadge(currentCount + 1);
    }

    console.log("✅ Real-time notification added to UI");
});

// ============ NOTIFICATION DROPDOWN TOGGLE ============
document.addEventListener('DOMContentLoaded', function() {
    // Load notifications when page loads
    loadNotifications();

    const notificationToggle = document.getElementById('notificationToggle');
    const notificationDropdown = document.getElementById('notificationDropdown');

    if (notificationToggle && notificationDropdown) {
        notificationToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');

            // Reload notifications when dropdown is opened
            if (notificationDropdown.classList.contains('show')) {
                loadNotifications();
            }
        });

        document.addEventListener('click', function(e) {
            if (!notificationToggle.contains(e.target) && !notificationDropdown.contains(e.target)) {
                notificationDropdown.classList.remove('show');
            }
        });

        notificationDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});


document.getElementById('session_logoFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('imagePreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById('remove-img').addEventListener('click', function() {
    document.getElementById('imagePreview').src = '/static/assets/images/session-defult.png';
    document.getElementById('session_logoFile').value = '';
});