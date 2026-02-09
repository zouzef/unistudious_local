var Akademi  = function(){
	"use strict"
   /* Search Bar ============ */
   var screenWidth = $( window ).width();
   var screenHeight = $( window ).height();
   


   var handlePreloader = function(){
	   setTimeout(function() {
		   jQuery('#preloader').remove();
		   $('#main-wrapper').addClass('show');
	   },1000);	
	   
   }

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
	   $(".nav-control").on('click', function() {

		   $('#main-wrapper').toggleClass("menu-toggle");

		   $(".hamburger").toggleClass("is-active");
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
	   
	   /* var vHeight = function(){ */
		   
	   /* } */
	   
	   
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
	   if(jQuery("#datetimepicker1").length>0) {
		   $('#datetimepicker1').datetimepicker({
			   inline: true,
		   });
	   }
   }
   
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
	   /* Bootstrap Select box function by  = bootstrap-select.min.js */ 
	   if(jQuery('select').length > 0){
	   
		   jQuery('select').selectpicker();
	   /* Bootstrap Select box function by  = bootstrap-select.min.js end*/
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




/*================== ADD CALANDER FUNCTION TO LOAD DATA FROM THE BACKEND ===================*/
async function loadRooms(localId) {
    const roomSelect = document.getElementById('eventRooms');

    if (!roomSelect) {
        console.error('Room select not found');
        return;
    }

    console.log('Loading rooms...');

    // Destroy selectpicker if it exists
    if ($(roomSelect).data('selectpicker')) {
        $(roomSelect).selectpicker('destroy');
    }

    // Clear existing options
    roomSelect.innerHTML = '<option value="" selected disabled>Select a Room</option>';

    try {
        const response = await fetch(`/get-room-local/${localId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            const rooms = result.data;

            if (Array.isArray(rooms) && rooms.length > 0) {
                rooms.forEach(room => {
                    const option = document.createElement('option');
                    option.value = room.id;
                    option.textContent = room.name;
                    roomSelect.appendChild(option);
                });

                console.log('Rooms loaded successfully:', rooms.length);

                // Reinitialize selectpicker after adding options
                $(roomSelect).selectpicker('refresh');
            } else {
                roomSelect.innerHTML += '<option value="" disabled>No rooms available</option>';
                $(roomSelect).selectpicker('refresh');
            }
        } else {
            console.error('Error fetching rooms');
            roomSelect.innerHTML += '<option value="" disabled>Error loading rooms</option>';
            $(roomSelect).selectpicker('refresh');
        }
    } catch (error) {
        console.error('Network error:', error);
        roomSelect.innerHTML += '<option value="" disabled>Connection error</option>';
        $(roomSelect).selectpicker('refresh');
    }
}

//Load Group
async function loadGroups(accountId, sessionId) {
    const groupSelect = document.getElementById('group_id');

    if (!groupSelect) {
        console.error('Group select not found');
        return;
    }

    console.log('Loading groups...');

    // Destroy selectpicker if it exists
    if ($(groupSelect).data('selectpicker')) {
        $(groupSelect).selectpicker('destroy');
    }

    // Clear existing options
    groupSelect.innerHTML = '<option value="" selected disabled>Select a Group</option>';

    try {
        const response = await fetch(`/get-group-session/${accountId}/${sessionId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Full API result:', result);

            // Adjust this based on your actual response structure
            const groups = result.data || result;

            if (Array.isArray(groups) && groups.length > 0) {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name;
                    groupSelect.appendChild(option);
                });

                console.log('Groups loaded successfully:', groups.length);

                // Reinitialize selectpicker after adding options
                $(groupSelect).selectpicker('refresh');
            } else {
                groupSelect.innerHTML += '<option value="" disabled>No groups available</option>';
                $(groupSelect).selectpicker('refresh');
            }
        } else {
            const error = await response.json();
            console.error('Error fetching groups:', error.Message);
            groupSelect.innerHTML += '<option value="" disabled>Error loading groups</option>';
            $(groupSelect).selectpicker('refresh');
        }
    } catch (error) {
        console.error('Network error:', error);
        groupSelect.innerHTML += '<option value="" disabled>Connection error</option>';
        $(groupSelect).selectpicker('refresh');
    }
}

// Clear groups function
function clearGroups() {
    const groupSelect = document.getElementById('group_id');

    if (groupSelect) {
        // Destroy selectpicker if it exists
        if ($(groupSelect).data('selectpicker')) {
            $(groupSelect).selectpicker('destroy');
        }

        // Reset to default
        groupSelect.innerHTML = '<option value="" selected disabled>Select a Group</option>';
        $(groupSelect).selectpicker('refresh');
    }
}

// Load Session
async function loadSessions(accountId) {
    const sessionSelect = document.getElementById('session');

    if (!sessionSelect) {
        console.error('Session select not found');
        return;
    }

    console.log('Loading sessions...');

    // Destroy selectpicker if it exists
    if ($(sessionSelect).data('selectpicker')) {
        $(sessionSelect).selectpicker('destroy');
    }

    // Clear existing options
    sessionSelect.innerHTML = '<option value="" selected disabled>Select Session</option>';

    try {
        const response = await fetch(`/get-session/${accountId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Full API result:', result);

            // Adjust based on your actual response structure
            const sessions = result.data || result;

            if (Array.isArray(sessions) && sessions.length > 0) {
                sessions.forEach(session => {
                    const option = document.createElement('option');
                    option.value = session.id;
                    option.textContent = session.name;
                    sessionSelect.appendChild(option);
                });

                console.log('Sessions loaded successfully:', sessions.length);

                // Reinitialize selectpicker after adding options
                $(sessionSelect).selectpicker('refresh');
            } else {
                sessionSelect.innerHTML += '<option value="" disabled>No sessions available</option>';
                $(sessionSelect).selectpicker('refresh');
            }
        } else {
            const error = await response.json();
            console.error('Error fetching sessions:', error.Message);
            sessionSelect.innerHTML += '<option value="" disabled>Error loading sessions</option>';
            $(sessionSelect).selectpicker('refresh');
        }
    } catch (error) {
        console.error('Network error:', error);
        sessionSelect.innerHTML += '<option value="" disabled>Connection error</option>';
        $(sessionSelect).selectpicker('refresh');
    }
}

// Load Teachers - UPDATED to accept group_id parameter
async function loadTeachers(sessionId, groupId) {
    const teacherSelect = document.getElementById('eventSubject');

    if (!teacherSelect) {
        console.error('Teacher select not found');
        return;
    }

    console.log('Loading teachers for session:', sessionId, 'and group:', groupId);

    // Destroy selectpicker if it exists
    if ($(teacherSelect).data('selectpicker')) {
        $(teacherSelect).selectpicker('destroy');
    }

    // Clear existing options
    teacherSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';

    // Check if both sessionId and groupId are provided
    if (!sessionId || !groupId) {
        console.log('Session ID or Group ID is missing, cannot load teachers');
        teacherSelect.innerHTML += '<option value="" disabled>Please select a session and group first</option>';
        $(teacherSelect).selectpicker('refresh');
        return;
    }

    try {
        // Updated to include group_id in the API call
        const response = await fetch(`/get-teacher/${groupId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Full API result:', result);

            // Adjust based on your actual response structure
            const teachers = result.data || result;

            if (Array.isArray(teachers) && teachers.length > 0) {
                teachers.forEach(teacher => {
                    const option = document.createElement('option');
                    option.value = teacher.id; // Adjust based on your data structure
                    option.setAttribute('data-subject', teacher.subject_id); // Adjust field name
                    option.setAttribute('data-user', teacher.user_id); // Adjust field name
                    option.textContent = `Subject : ${teacher.subject_name} - Teacher : ${teacher.full_name}`; // Adjust field names
                    teacherSelect.appendChild(option);
                });

                console.log('Teachers loaded successfully:', teachers.length);

                // Reinitialize selectpicker after adding options
                $(teacherSelect).selectpicker('refresh');
            } else {
                teacherSelect.innerHTML += '<option value="" disabled>No teachers available for this group</option>';
                $(teacherSelect).selectpicker('refresh');
            }
        } else {
            const error = await response.json();
            console.error('Error fetching teachers:', error.Message);
            teacherSelect.innerHTML += '<option value="" disabled>Error loading teachers</option>';
            $(teacherSelect).selectpicker('refresh');
        }
    } catch (error) {
        console.error('Network error:', error);
        teacherSelect.innerHTML += '<option value="" disabled>Connection error</option>';
        $(teacherSelect).selectpicker('refresh');
    }
}

// Clear teachers function
function clearTeachers() {
    const teacherSelect = document.getElementById('eventSubject');

    if (teacherSelect) {
        // Destroy selectpicker if it exists
        if ($(teacherSelect).data('selectpicker')) {
            $(teacherSelect).selectpicker('destroy');
        }

        // Reset to default
        teacherSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';
        $(teacherSelect).selectpicker('refresh');
    }
}


// Function to create calendar event via API
async function createCalendarEvent(formData) {
    try {
        const response = await fetch(`/create-calander_request/${formData.session_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: formData.session_id,
                group_id: formData.group_id,
                type: formData.type,
                room_id: formData.room_id,
                subject_id: formData.subject_id,
                user_id: formData.user_id,
                duplicate: formData.duplicate,
                start_time: formData.start_time,
                end_time: formData.end_time,
                end_date: formData.end_date,
                description: formData.description,
                account_id: formData.account_id,
                tag: formData.completion_tags // The endpoint expects 'tag' not 'completion_tags'
            })
        });

        const result = await response.json();

        if (response.ok && result.Status === 'success') {
            console.log('✅ Calendar event created successfully');
            return { success: true, data: result };
        } else {
            console.error('❌ Error creating calendar event:', result.Message);
            return { success: false, error: result.Message };
        }
    } catch (error) {
        console.error('❌ Network error:', error);
        return { success: false, error: 'Connection error. Please try again.' };
    }
}

// SINGLE DOMContentLoaded with all listeners
document.addEventListener('DOMContentLoaded', function() {
    const eventModal = document.getElementById('eventModal');

    if (eventModal) {
        // When modal opens
        eventModal.addEventListener('shown.bs.modal', function() {
            const accountId = document.getElementById('eventAccountId').value;
            const localId = document.getElementById('eventLocalId').value;

            console.log('Modal shown, loading data...');

            // Load sessions first
            if (accountId) {
                loadSessions(accountId);
            }

            // Load rooms
            if (localId) {
                loadRooms(localId);
            }

            // Clear groups and teachers initially
            clearGroups();
            clearTeachers();
        });
    }

    // Listen for session selection change
    const sessionSelect = document.getElementById('session');
    if (sessionSelect) {
        // Use jQuery change event for selectpicker compatibility
        $(sessionSelect).on('change', function() {
            const selectedSessionId = $(this).val();
            const accountId = document.getElementById('eventAccountId').value;

            console.log('Session selected:', selectedSessionId);

            if (selectedSessionId && accountId) {
                // Load groups for the selected session
                loadGroups(accountId, selectedSessionId);
                // Clear teachers when session changes (will be loaded when group is selected)
                clearTeachers();
            } else {
                // Clear groups and teachers if no session selected
                clearGroups();
                clearTeachers();
            }
        });
    }

    // ADDED: Listen for group selection change
    const groupSelect = document.getElementById('group_id');
    if (groupSelect) {
        // Use jQuery change event for selectpicker compatibility
        $(groupSelect).on('change', function() {
            const selectedGroupId = $(this).val();
            const selectedSessionId = document.getElementById('session').value;

            console.log('Group selected:', selectedGroupId);
            console.log('Current session:', selectedSessionId);

            if (selectedGroupId && selectedSessionId) {
                // Load teachers for the selected session and group
                loadTeachers(selectedSessionId, selectedGroupId);
            } else {
                // Clear teachers if no group selected
                clearTeachers();
            }
        });
    }


    // ============= SAVE BUTTON HANDLER HERE =============
    const saveEventButton = document.getElementById('saveEventButton');
    if (saveEventButton) {
        saveEventButton.addEventListener('click', async function() {
            // Get all form values
            const sessionSelect = document.getElementById('session');
            const groupSelect = document.getElementById('group_id');
            const teacherSelect = document.getElementById('eventSubject');
            const startTimeInput = document.getElementById('eventStartTime');
            const endTimeInput = document.getElementById('eventEndTime');
            const descriptionInput = document.getElementById('eventDescription');

            const formData = {
                session_id: sessionSelect.value,
                group_id: groupSelect.value,
                type: document.getElementById('typeSessionSelect').value,
                room_id: document.getElementById('eventRooms').value,
                subject_id: teacherSelect.selectedOptions[0]?.getAttribute('data-subject'),
                user_id: teacherSelect.selectedOptions[0]?.getAttribute('data-user'),
                completion_tags: Array.from(document.getElementById('eventCompletionTagCalander').selectedOptions).map(opt => opt.value),
                duplicate: document.getElementById('eventDuplicate').value,
                start_time: startTimeInput.value,
                end_time: endTimeInput.value,
                end_date: document.getElementById('eventEndDate').value,
                description: descriptionInput.value,
                // Hidden fields
                account_id: document.getElementById('eventAccountId').value,
                local_id: document.getElementById('eventLocalId').value
            };

            // Generate automatic description if description is empty
            if (!formData.description || formData.description.trim() === '') {
                const selectedGroup = groupSelect.options[groupSelect.selectedIndex];
                const selectedTeacher = teacherSelect.options[teacherSelect.selectedIndex];

                if (selectedGroup && selectedTeacher && formData.start_time && formData.end_time) {
                    const groupName = selectedGroup.textContent || 'Unknown Group';
                    const teacherText = selectedTeacher.textContent;

                    let subjectName = 'Unknown Subject';
                    let teacherName = 'Unknown Teacher';

                    if (teacherText) {
                        const patterns = [
                            /Subject\s*:\s*(.+?)(?:\s*-|$)/i,
                            /Subject\s*:\s*(.+)/i,
                            /(.+?)\s*-\s*Teacher/i
                        ];

                        for (const pattern of patterns) {
                            const match = teacherText.match(pattern);
                            if (match && match[1]) {
                                subjectName = match[1].trim();
                                break;
                            }
                        }

                        const teacherPatterns = [
                            /Teacher\s*:\s*(.+?)$/i,
                            /-\s*Teacher\s*:\s*(.+?)$/i,
                            /-\s*(.+?)$/i
                        ];

                        for (const pattern of teacherPatterns) {
                            const match = teacherText.match(pattern);
                            if (match && match[1]) {
                                teacherName = match[1].trim();
                                break;
                            }
                        }

                        if (subjectName === 'Unknown Subject' && !teacherText.includes('Subject :')) {
                            subjectName = teacherText;
                        }
                    }

                    let formattedStart = formData.start_time;
                    let formattedEnd = formData.end_time;

                    try {
                        if (formData.start_time.includes('T')) {
                            const startDateTime = new Date(formData.start_time);
                            const endDateTime = new Date(formData.end_time);

                            if (!isNaN(startDateTime.getTime()) && !isNaN(endDateTime.getTime())) {
                                const formatDateTime = (date) => {
                                    const year = date.getFullYear();
                                    const month = String(date.getMonth() + 1).padStart(2, '0');
                                    const day = String(date.getDate()).padStart(2, '0');
                                    const hours = String(date.getHours()).padStart(2, '0');
                                    const minutes = String(date.getMinutes()).padStart(2, '0');
                                    return `${year}-${month}-${day} ${hours}:${minutes}`;
                                };

                                formattedStart = formatDateTime(startDateTime);
                                formattedEnd = formatDateTime(endDateTime);
                            }
                        } else if (formData.end_date) {
                            const startDateTimeStr = `${formData.end_date}T${formData.start_time}`;
                            const endDateTimeStr = `${formData.end_date}T${formData.end_time}`;

                            const startDateTime = new Date(startDateTimeStr);
                            const endDateTime = new Date(endDateTimeStr);

                            if (!isNaN(startDateTime.getTime()) && !isNaN(endDateTime.getTime())) {
                                const formatDateTime = (date) => {
                                    const year = date.getFullYear();
                                    const month = String(date.getMonth() + 1).padStart(2, '0');
                                    const day = String(date.getDate()).padStart(2, '0');
                                    const hours = String(date.getHours()).padStart(2, '0');
                                    const minutes = String(date.getMinutes()).padStart(2, '0');
                                    return `${year}-${month}-${day} ${hours}:${minutes}`;
                                };

                                formattedStart = formatDateTime(startDateTime);
                                formattedEnd = formatDateTime(endDateTime);
                            } else {
                                formattedStart = `${formData.end_date} ${formData.start_time}`;
                                formattedEnd = `${formData.end_date} ${formData.end_time}`;
                            }
                        }
                    } catch (error) {
                        console.error('Error formatting datetime:', error);
                    }

                    formData.description = `Group "${groupName}" has learning from ${formattedStart} to ${formattedEnd} on Subject "${subjectName}" with Teacher "${teacherName}"`;
                    console.log('✅ Auto-generated description:', formData.description);
                } else {
                    const groupName = groupSelect.options[groupSelect.selectedIndex]?.textContent || 'Group';
                    formData.description = `Learning session for ${groupName}`;
                }
            }

            // Display in console
            console.log('=== FORM DATA ===');
            console.log('Session ID:', formData.session_id);
            console.log('Group ID:', formData.group_id);
            console.log('Type:', formData.type);
            console.log('Room ID:', formData.room_id);
            console.log('Subject ID:', formData.subject_id);
            console.log('User ID:', formData.user_id);
            console.log('Completion Tags:', formData.completion_tags);
            console.log('Duplicate:', formData.duplicate);
            console.log('Start Time:', formData.start_time);
            console.log('End Time:', formData.end_time);
            console.log('End Date:', formData.end_date);
            console.log('Description:', formData.description);
            console.log('Account ID:', formData.account_id);
            console.log('Local ID:', formData.local_id);
            console.log('=================');

            // Validation
            if (!formData.session_id) {
                alert('Please select a session');
                return;
            }
            if (!formData.group_id) {
                alert('Please select a group');
                return;
            }
            if (!formData.type) {
                alert('Please select a type');
                return;
            }
            if (!formData.room_id) {
                alert('Please select a room');
                return;
            }
            if (!formData.subject_id || !formData.user_id) {
                alert('Please select a teacher and subject');
                return;
            }
            if (!formData.duplicate) {
                alert('Please select duplicate option');
                return;
            }

            console.log('✅ All validations passed!');

            // **NEW: Call the API to create calendar event**
            const result = await createCalendarEvent(formData);

            if (result.success) {
                alert('Calendar event created successfully!');
                // Close the modal
                $('#eventModal').modal('hide');
                // Optionally refresh the calendar or reload the page
                // location.reload();
            } else {
                alert(`Failed to create calendar event: ${result.error}`);
            }
        });
    }

    // ============= END OF SAVE BUTTON HANDLER =============
});



