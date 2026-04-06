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


// ============= WebSocket Configuration =============
let socket;
const calendareDiv = document.getElementById('calendare');
const ROOM_ID = parseInt(calendareDiv.dataset.roomId, 10);

/* ============================================================
   CALENDAR.JS  –  cleaned-up, duplicate-free version
   ============================================================ */

// ── WebSocket ────────────────────────────────────────────────

function initializeWebSocket() {
    console.log('🔌 Initializing WebSocket connection...');

    socket = io.connect(window.location.origin, {
        transports: ['websocket', 'polling']
    });

    socket.on('connect', function () {
        console.log('✅ WebSocket connected:', socket.id);
        socket.emit('join_calendar_room', { room_id: ROOM_ID });
    });

    socket.on('disconnect', function () {
        console.log('❌ WebSocket disconnected');
    });

    socket.on('status', function (data) {
        console.log('📡 WebSocket status:', data.message);
    });

    // FIX: WebSocket delivers full API payload, so update allCalendarData
    // then re-render the current page – don't pass raw data to renderCalendarCards.
    socket.on('calendar_update', function (data) {
        console.log('📅 Calendar update received:', data);
        if (String(data.room_id) === String(ROOM_ID)) {
            allCalendarData = data.data?.data || [];
            totalItems     = allCalendarData.length;
            currentPage    = 1;
            renderCurrentPage();
        }
    });

    socket.on('connect_error', function (error) {
        console.error('❌ WebSocket connection error:', error);
    });
}


// ── Data-loading helpers ─────────────────────────────────────

async function loadRooms(localId) {
    const roomSelect = document.getElementById('eventRooms');
    if (!roomSelect) return console.error('Room select not found');

    _destroySelectpicker(roomSelect);
    roomSelect.innerHTML = '<option value="" selected disabled>Select a Room</option>';

    try {
        const response = await fetch(`/get-room-local/${localId}`, {
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const { data: rooms } = await response.json();

            if (Array.isArray(rooms) && rooms.length > 0) {
                rooms.forEach(room => _addOption(roomSelect, room.id, room.name));
            } else {
                _addOption(roomSelect, '', 'No rooms available', true);
            }
        } else {
            _addOption(roomSelect, '', 'Error loading rooms', true);
        }
    } catch {
        _addOption(roomSelect, '', 'Connection error', true);
    }

    $(roomSelect).selectpicker('refresh');
}

async function loadGroups(accountId, sessionId) {
    const groupSelect = document.getElementById('group_id');
    if (!groupSelect) return console.error('Group select not found');

    _destroySelectpicker(groupSelect);
    groupSelect.innerHTML = '<option value="" selected disabled>Select a Group</option>';
    groupSelect.disabled = false;
    groupSelect.style.background = 'white';

    try {
        const response = await fetch(`/get-group-session/${accountId}/${sessionId}`, {
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const result  = await response.json();
            const groups  = result.data || result;

            if (Array.isArray(groups) && groups.length > 0) {
                groups.forEach(g => _addOption(groupSelect, g.id, g.name));
            } else {
                _addOption(groupSelect, '', 'No groups available', true);
            }
        } else {
            const err = await response.json();
            console.error('Error fetching groups:', err.Message);
            _addOption(groupSelect, '', 'Error loading groups', true);
        }
    } catch {
        _addOption(groupSelect, '', 'Connection error', true);
    }

    $(groupSelect).selectpicker('refresh');
}

function clearGroups() {
    const groupSelect = document.getElementById('group_id');
    if (!groupSelect) return;
    _destroySelectpicker(groupSelect);
    groupSelect.innerHTML = '<option value="" selected disabled>Select a Group</option>';
    groupSelect.disabled = true;
    groupSelect.style.background = '#f5f5f5';
    $(groupSelect).selectpicker('refresh');
}

async function loadSessions(accountId) {
    const sessionSelect = document.getElementById('session');
    if (!sessionSelect) return console.error('Session select not found');

    _destroySelectpicker(sessionSelect);
    sessionSelect.innerHTML = '<option value="" selected disabled>Select Session</option>';

    try {
        const response = await fetch(`/get-session/${accountId}`, {
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const result   = await response.json();
            const sessions = result.data || result;

            if (Array.isArray(sessions) && sessions.length > 0) {
                sessions.forEach(s => _addOption(sessionSelect, s.id, s.name));
            } else {
                _addOption(sessionSelect, '', 'No sessions available', true);
            }
        } else {
            const err = await response.json();
            console.error('Error fetching sessions:', err.Message);
            _addOption(sessionSelect, '', 'Error loading sessions', true);
        }
    } catch {
        _addOption(sessionSelect, '', 'Connection error', true);
    }

    $(sessionSelect).selectpicker('refresh');
}

async function loadTeachers(sessionId, groupId) {
    const teacherSelect = document.getElementById('eventSubject');
    if (!teacherSelect) return console.error('Teacher select not found');

    _destroySelectpicker(teacherSelect);
    teacherSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';
    teacherSelect.disabled = false;
    teacherSelect.style.background = 'white';
    if (!sessionId || !groupId) {
        _addOption(teacherSelect, '', 'Please select a session and group first', true);
        $(teacherSelect).selectpicker('refresh');
        return;
    }

    try {
        const response = await fetch(`/get-teacher/${groupId}`, {
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const result   = await response.json();
            const teachers = result.data || result;

            if (Array.isArray(teachers) && teachers.length > 0) {
                teachers.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.setAttribute('data-subject', t.subject_id);
                    opt.setAttribute('data-user',    t.user_id);
                    opt.textContent = `Subject : ${t.subject_name} - Teacher : ${t.full_name}`;
                    teacherSelect.appendChild(opt);
                });
            } else {
                _addOption(teacherSelect, '', 'No teachers available for this group', true);
            }
        } else {
            const err = await response.json();
            console.error('Error fetching teachers:', err.Message);
            _addOption(teacherSelect, '', 'Error loading teachers', true);
        }
    } catch {
        _addOption(teacherSelect, '', 'Connection error', true);
    }

    $(teacherSelect).selectpicker('refresh');
}

function clearTeachers() {
    const teacherSelect = document.getElementById('eventSubject');
    if (!teacherSelect) return;
    _destroySelectpicker(teacherSelect);
    teacherSelect.innerHTML = '<option value="" selected disabled>Select a Subject and Teacher</option>';
    teacherSelect.disabled = true;
    teacherSelect.style.background = '#f5f5f5';
    $(teacherSelect).selectpicker('refresh');
}


// ── Calendar API ─────────────────────────────────────────────

// FIX: was defined twice – now defined once.
async function fetchCalendarRequests(roomId) {
    try {
        console.log('Fetching calendar data for room:', roomId);
        const response = await fetch(`/get-calander-request/${roomId}`);

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        return await response.json();
    } catch (error) {
        console.error('Error fetching calendar requests:', error);
        return null;
    }
}

async function createCalendarEvent(formData) {
    try {
        const response = await fetch('/api/create-calender-tablet', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id:      formData.session_id,
                group_id:        formData.group_id,
                type:            formData.type,
                room_id:         formData.room_id,
                subject_id:      formData.subject_id,
                teacher_id:      formData.user_id,
                duplicate:       formData.duplicate,
                start_date:      formData.start_date,
                start_time:      `${formData.start_date} ${formData.start_time}`,  // ← combined
                end_time:        `${formData.start_date} ${formData.end_time}`,    // ← combined
                end_date:        formData.end_date || null,                        // ← empty string → null
                description:     formData.description,
                title:           formData.description,
                account_id:      formData.account_id,
                local_id:        formData.local_id,
                completion_tags: formData.completion_tags
            })
        });

        const result = await response.json();

        if (response.ok) {
            return { success: true,  data:  result };
        } else {
            return { success: false, error: result.Message };
        }
    } catch (error) {
        console.error('❌ Network error:', error);
        return { success: false, error: 'Connection error. Please try again.' };
    }
}


// ── Pagination ───────────────────────────────────────────────

let currentPage    = 1;
const itemsPerPage = 3;
let totalItems     = 0;
let allCalendarData = [];

function getTotalPages()      { return Math.ceil(totalItems / itemsPerPage); }

function getCurrentPageItems() {
    const start = (currentPage - 1) * itemsPerPage;
    return allCalendarData.slice(start, start + itemsPerPage);
}

function updatePaginationUI() {
    const totalPages        = getTotalPages();
    const paginationContainer = document.getElementById('pagination-container');
    const prevButton        = document.getElementById('prev-page');
    const nextButton        = document.getElementById('next-page');
    const currentPageSpan   = document.getElementById('current-page');
    const totalPagesSpan    = document.getElementById('total-pages');

    if (!paginationContainer) return;

    paginationContainer.style.display = totalItems <= itemsPerPage ? 'none' : 'block';

    if (currentPageSpan) currentPageSpan.textContent = currentPage;
    if (totalPagesSpan)  totalPagesSpan.textContent  = totalPages;
    if (prevButton)      prevButton.disabled = currentPage === 1;
    if (nextButton)      nextButton.disabled = currentPage === totalPages;
}

function renderCurrentPage() {
    renderCalendarCards({ Message: 'Success', data: getCurrentPageItems() });
    updatePaginationUI();

    document.getElementById('calendar-cards-container')?.scrollIntoView({
        behavior: 'smooth', block: 'start'
    });
}

function setupPaginationListeners() {
    document.getElementById('prev-page')?.addEventListener('click', function () {
        if (currentPage > 1) { currentPage--; renderCurrentPage(); }
    });

    document.getElementById('next-page')?.addEventListener('click', function () {
        if (currentPage < getTotalPages()) { currentPage++; renderCurrentPage(); }
    });
}


// ── Rendering ────────────────────────────────────────────────

function renderCalendarCards(calendarData) {
    const container = document.getElementById('calendar-cards-container');
    if (!container) return console.error('Container element not found!');

    if (!calendarData || calendarData.Message !== 'Success' ||
        !Array.isArray(calendarData.data) || calendarData.data.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-center">No calendar requests found</p></div>';
        return;
    }

    const cardClasses = ['schedule-card', 'schedule-card-1', 'schedule-card-2', 'schedule-card-3'];

    container.innerHTML = calendarData.data.map((item, index) => {
        const cardClass     = cardClasses[index % cardClasses.length];
        const formattedDate = item.start_date
            ? new Date(item.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
            : 'Date not available';
        const timeRange = `${item.start_time || '00:00:00'} - ${item.end_time || '00:00:00'}`;

        return `
        <div class="col-12 col-md-12 col-xl-12 calendar-card-item" data-card-id="${item.id}">
            <div class="card ${cardClass}">
                <div class="card-body">
                    <h4 class="mb-0">${item.subject_name || 'No Subject'}</h4>
                    <p>${item.group_name || 'No Group'} - ${item.session_name || 'No Session'}</p>
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <ul>
                                <li class="mb-2">
                                    <svg class="me-2" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M18 5.25H16.5V4.5C16.5 4.30109 16.421 4.11032 16.2803 3.96967C16.1397 3.82902 15.9489 3.75 15.75 3.75C15.5511 3.75 15.3603 3.82902 15.2197 3.96967C15.079 4.11032 15 4.30109 15 4.5V5.25H12.75V4.5C12.75 4.30109 12.671 4.11032 12.5303 3.96967C12.3897 3.82902 12.1989 3.75 12 3.75C11.8011 3.75 11.6103 3.82902 11.4697 3.96967C11.329 4.11032 11.25 4.30109 11.25 4.5V5.25H9V4.5C9 4.30109 8.92098 4.11032 8.78033 3.96967C8.63968 3.82902 8.44891 3.75 8.25 3.75C8.05109 3.75 7.86032 3.82902 7.71967 3.96967C7.57902 4.11032 7.5 4.30109 7.5 4.5V5.25H6C5.40326 5.25 4.83097 5.48705 4.40901 5.90901C3.98705 6.33097 3.75 6.90326 3.75 7.5V18C3.75 18.5967 3.98705 19.169 4.40901 19.591C4.83097 20.0129 5.40326 20.25 6 20.25H18C18.5967 20.25 19.169 20.0129 19.591 19.591C20.0129 19.169 20.25 18.5967 20.25 18V7.5C20.25 6.90326 20.0129 6.33097 19.591 5.90901C19.169 5.48705 18.5967 5.25 18 5.25ZM5.25 7.5C5.25 7.30109 5.32902 7.11032 5.46967 6.96967C5.61032 6.82902 5.80109 6.75 6 6.75H7.5V7.5C7.5 7.69891 7.57902 7.88968 7.71967 8.03033C7.86032 8.17098 8.05109 8.25 8.25 8.25C8.44891 8.25 8.63968 8.17098 8.78033 8.03033C8.92098 7.88968 9 7.69891 9 7.5V6.75H11.25V7.5C11.25 7.69891 11.329 7.88968 11.4697 8.03033C11.6103 8.17098 11.8011 8.25 12 8.25C12.1989 8.25 12.3897 8.17098 12.5303 8.03033C12.671 7.88968 12.75 7.69891 12.75 7.5V6.75H15V7.5C15 7.69891 15.079 7.88968 15.2197 8.03033C15.3603 8.17098 15.5511 8.25 15.75 8.25C15.9489 8.25 16.1397 8.17098 16.2803 8.03033C16.421 7.88968 16.5 7.69891 16.5 7.5V6.75H18C18.1989 6.75 18.3897 6.82902 18.5303 6.96967C18.671 7.11032 18.75 7.30109 18.75 7.5V9.75H5.25V7.5ZM18.75 18C18.75 18.1989 18.671 18.3897 18.5303 18.5303C18.3897 18.671 18.1989 18.75 18 18.75H6C5.80109 18.75 5.61032 18.671 5.46967 18.5303C5.32902 18.3897 5.25 18.1989 5.25 18V11.25H18.75V18Z" fill="#FB7D5B"/>
                                    </svg>
                                    ${formattedDate}
                                </li>
                                <li>
                                    <svg class="me-2 ms-1" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M10 0C8.02219 0 6.08879 0.58649 4.4443 1.6853C2.79981 2.78412 1.51809 4.3459 0.761209 6.17317C0.00433284 8.00043 -0.193701 10.0111 0.192152 11.9509C0.578004 13.8907 1.53041 15.6725 2.92894 17.0711C4.32746 18.4696 6.10929 19.422 8.0491 19.8079C9.98891 20.1937 11.9996 19.9957 13.8268 19.2388C15.6541 18.4819 17.2159 17.2002 18.3147 15.5557C19.4135 13.9112 20 11.9778 20 10C20 8.68678 19.7413 7.38642 19.2388 6.17317C18.7363 4.95991 17.9997 3.85752 17.0711 2.92893C16.1425 2.00035 15.0401 1.26375 13.8268 0.761205C12.6136 0.258658 11.3132 0 10 0ZM10 18C8.41775 18 6.87104 17.5308 5.55544 16.6518C4.23985 15.7727 3.21447 14.5233 2.60897 13.0615C2.00347 11.5997 1.84504 9.99113 2.15372 8.43928C2.4624 6.88743 3.22433 5.46197 4.34315 4.34315C5.46197 3.22433 6.88743 2.4624 8.43928 2.15372C9.99113 1.84504 11.5997 2.00346 13.0615 2.60896C14.5233 3.21447 15.7727 4.23984 16.6518 5.55544C17.5308 6.87103 18 8.41775 18 10C18 12.1217 17.1572 14.1566 15.6569 15.6569C14.1566 17.1571 12.1217 18 10 18Z" fill="#FCC43E"/>
                                        <path d="M13 9H11V5C11 4.73478 10.8946 4.48043 10.7071 4.29289C10.5196 4.10536 10.2652 4 10 4C9.73478 4 9.48043 4.10536 9.29289 4.29289C9.10536 4.48043 9 4.73478 9 5V10C9 10.2652 9.10536 10.5196 9.29289 10.7071C9.48043 10.8946 9.73478 11 10 11H13C13.2652 11 13.5196 10.8946 13.7071 10.7071C13.8946 10.5196 14 10.2652 14 10C14 9.73478 13.8946 9.48043 13.7071 9.29289C13.5196 9.10536 13.2652 9 13 9Z" fill="#FCC43E"/>
                                    </svg>
                                    ${timeRange}
                                </li>
                            </ul>
                        </div>
                        <div class="d-flex flex-column align-items-center text-center">
                            <img src="/api/get-profile-image/${item.user_id}"
                                 alt="${item.username || 'Teacher'}"
                                 style="width: 45px; height: 45px; border-radius: 50%; object-fit: cover;">
                            <p class="mb-0 fw-bold mt-1">${item.username || 'No Teacher'}</p>
                        </div>
                    </div>
                    ${item.description ? `
                    <div class="mt-3 text-center">
                        <button class="btn light btn-light" type="button"
                                data-bs-toggle="collapse"
                                data-bs-target="#description-${item.id}"
                                aria-expanded="false">
                            see more
                        </button>
                        <div class="collapse mt-3" id="description-${item.id}">
                            <div class="description-box">
                                <p class="mb-0">${item.description}</p>
                            </div>
                        </div>
                    </div>` : ''}
                </div>
            </div>
        </div>`;
    }).join('');
}


// ── Calendar init ─────────────────────────────────────────────

async function initCalendar() {
    const calendareDiv = document.getElementById('calendare');
    const roomId       = calendareDiv ? parseInt(calendareDiv.dataset.roomId, 10) : null;

    if (!roomId) return console.error('❌ Room ID not found!');

    const calendarData = await fetchCalendarRequests(roomId);

    if (calendarData && calendarData.Message === 'Success') {
        allCalendarData = calendarData.data || [];
        totalItems      = allCalendarData.length;
        currentPage     = 1;
        renderCurrentPage();
    } else {
        const container = document.getElementById('calendar-cards-container');
        if (container) container.innerHTML =
            '<div class="col-12"><p class="text-center text-danger">Failed to load calendar requests</p></div>';
    }
}


// ── Save-event handler ────────────────────────────────────────

function _buildAutoDescription(formData, groupSelect, teacherSelect) {
    const groupName  = groupSelect.options[groupSelect.selectedIndex]?.textContent || 'Group';
    const teacherText = teacherSelect.options[teacherSelect.selectedIndex]?.textContent || '';

    let subjectName = 'Unknown Subject';
    let teacherName = 'Unknown Teacher';

    for (const pat of [/Subject\s*:\s*(.+?)(?:\s*-|$)/i, /(.+?)\s*-\s*Teacher/i]) {
        const m = teacherText.match(pat);
        if (m?.[1]) { subjectName = m[1].trim(); break; }
    }
    for (const pat of [/Teacher\s*:\s*(.+?)$/i, /-\s*(.+?)$/i]) {
        const m = teacherText.match(pat);
        if (m?.[1]) { teacherName = m[1].trim(); break; }
    }

    let formattedStart = formData.start_time;
    let formattedEnd   = formData.end_time;

    if (formData.start_date) {
        try {
            const fmt = d => {
                const pad = n => String(n).padStart(2, '0');
                return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
            };
            const s = new Date(`${formData.start_date}T${formData.start_time}`);
            const e = new Date(`${formData.start_date}T${formData.end_time}`);
            if (!isNaN(s) && !isNaN(e)) { formattedStart = fmt(s); formattedEnd = fmt(e); }
        } catch { /* keep raw times */ }
    }

    return `Group "${groupName}" has learning from ${formattedStart} to ${formattedEnd} on Subject "${subjectName}" with Teacher "${teacherName}"`;
}

function _validateFormData(formData) {
    const checks = [
        [!formData.session_id,              'Please select a session'],
        [!formData.group_id,                'Please select a group'],
        [!formData.type,                    'Please select a type'],
        [!formData.room_id,                 'Please select a room'],
        [!formData.subject_id || !formData.user_id, 'Please select a teacher and subject'],
        [!formData.duplicate,               'Please select duplicate option'],
        [!formData.start_date,              'Please select a start date'],
    ];
    for (const [fail, text] of checks) {
        if (fail) return text;
    }
    return null; // valid
}

function _attachSaveHandler() {
    document.getElementById('saveEventButton')?.addEventListener('click', async function () {
        const sessionSelect  = document.getElementById('session');
        const groupSelect    = document.getElementById('group_id');
        const teacherSelect  = document.getElementById('eventSubject');

        const formData = {
            session_id:      sessionSelect.value,
            group_id:        groupSelect.value,
            type:            document.getElementById('typeSessionSelect').value,
            room_id:         document.getElementById('eventRooms').value,
            subject_id:      teacherSelect.selectedOptions[0]?.getAttribute('data-subject'),
            user_id:         teacherSelect.selectedOptions[0]?.getAttribute('data-user'),
            completion_tags: Array.from(document.getElementById('eventCompletionTagCalander').selectedOptions).map(o => o.value),
            duplicate:       document.getElementById('eventDuplicate').value,
            start_date:      document.getElementById('eventStartDate').value,
            start_time:      document.getElementById('eventStartTime').value,
            end_time:        document.getElementById('eventEndTime').value,
            end_date:        document.getElementById('eventEndDate').value,
            description:     document.getElementById('eventDescription').value,
            account_id:      document.getElementById('eventAccountId').value,
            local_id:        document.getElementById('eventLocalId').value,
        };

        // Auto-generate description when empty
        if (!formData.description?.trim()) {
            if (groupSelect.value && teacherSelect.value && formData.start_time && formData.end_time) {
                formData.description = _buildAutoDescription(formData, groupSelect, teacherSelect);
            } else {
                formData.description = `Learning session for ${groupSelect.options[groupSelect.selectedIndex]?.textContent || 'Group'}`;
            }
        }

        const validationError = _validateFormData(formData);
        if (validationError) {
            Swal.fire({ icon: 'warning', title: 'Missing Information', text: validationError, confirmButtonColor: '#3085d6' });
            return;
        }

        Swal.fire({ title: 'Creating Event...', text: 'Please wait', allowOutsideClick: false, allowEscapeKey: false, didOpen: () => Swal.showLoading() });

        const result = await createCalendarEvent(formData);

        if (result.success) {
            Swal.fire({ icon: 'success', title: 'Success!', text: 'Calendar event created successfully!', confirmButtonColor: '#28a745', timer: 2000 })
                .then(() => { $('#eventModal').modal('hide'); location.reload(); });
        } else {
            Swal.fire({ icon: 'error', title: 'Oops...', text: `Failed to create calendar event: ${result.error}`, confirmButtonColor: '#d33' });
        }
    });
}


// ── Private utilities ─────────────────────────────────────────

function _destroySelectpicker(el) {
    if ($(el).data('selectpicker')) $(el).selectpicker('destroy');
}

function _addOption(select, value, text, disabled = false) {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = text;
    if (disabled) opt.disabled = true;
    select.appendChild(opt);
}


// ── Single DOMContentLoaded ───────────────────────────────────
// FIX: merged two separate DOMContentLoaded listeners into one.

document.addEventListener('DOMContentLoaded', function () {

        // Modal open → load sessions, rooms, clear dependent selects
        document.getElementById('eventModal')?.addEventListener('shown.bs.modal', function () {
            const accountId = document.getElementById('eventAccountId').value;
            const localId   = document.getElementById('eventLocalId').value;
            if (accountId) loadSessions(accountId);
            if (localId)   loadRooms(localId);
            clearGroups();
            clearTeachers();
            document.getElementById('group-hint').style.display = 'block';    // ← add this
            document.getElementById('teacher-hint').style.display = 'block';  // ← add this
        });

    // Session change → load groups, clear teachers
    $('#session').on('change', function () {
        const sessionId = this.value;  // ← use this.value instead of $(this).val()
        const accountId = document.getElementById('eventAccountId').value;
        const groupHint = document.getElementById('group-hint');

        if (sessionId && accountId) {
            loadGroups(accountId, sessionId);
            clearTeachers();
            if (groupHint) groupHint.style.display = 'none';
        } else {
            clearGroups();
            clearTeachers();
            if (groupHint) groupHint.style.display = 'block';
        }
    });

    // Group change → load teachers
    $('#group_id').on('change', function () {
        const groupId   = this.value;  // ← use this.value
        const sessionId = document.getElementById('session').value;
        const teacherHint = document.getElementById('teacher-hint');

        if (groupId && sessionId) {
            loadTeachers(sessionId, groupId);
            if (teacherHint) teacherHint.style.display = 'none';
        } else {
            clearTeachers();
            if (teacherHint) teacherHint.style.display = 'block';
        }
    });

    // Save button
    _attachSaveHandler();

    // Pagination
    setupPaginationListeners();

    // WebSocket
    if (typeof initializeWebSocket === 'function') initializeWebSocket();

    // Initial data load
    initCalendar();
});


// ── Auto-refresh every 5 minutes ──────────────────────────────
setInterval(initCalendar, 2 * 60 * 1000);