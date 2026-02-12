var Akademi  = function(){
	"use strict"
   /* Search Bar ============ */
   var screenWidth = $( window ).width();
   var screenHeight = $( window ).height();

   var handlePreloader = function(){
    // Wait for the page to fully load
    window.addEventListener('load', function() {
        // Page is loaded, now hide preloader
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
    /* Bootstrap Select box function by  = bootstrap-select.min.js */
        if(jQuery('select').length > 0){
            // Only initialize selectpicker for selects NOT inside modals
            jQuery('select').not('.modal select').selectpicker();
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



/*==========================================*/
/* ======== FUNCTION TO UPDATE ATTENDANCE ========*/
/*==========================================*/
function update_attendance(attendanceId, button) {
    // Read the current status from the button's data attribute
    const currentStatus = button.getAttribute('data-status');

    // Convert string to boolean for comparison
    const isCurrentlyPresent = currentStatus === 'True' || currentStatus === 'true' || currentStatus === true;

    // Toggle the status (Present becomes 0 for Absent, Absent becomes 1 for Present)
    const newStatus = isCurrentlyPresent ? 0 : 1;

    console.log('Current Status:', currentStatus, 'Is Present:', isCurrentlyPresent, 'New Status:', newStatus);

    fetch(`/api/change-status/${newStatus}/${attendanceId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Find the row for this attendance
            const row = button.closest('tr');

            // Update the badge in the "Attendance Status" column
            const statusCell = row.querySelector('td:nth-child(3)');

            if (newStatus === 1) {
                // Mark as Present
                statusCell.innerHTML = '<span class="badge badge-success">Present</span>';
                button.classList.remove('btn-primary');
                button.classList.add('btn-warning');
                button.textContent = 'Mark as Absent';
                button.setAttribute('data-status', 'True');
            } else {
                // Mark as Absent
                statusCell.innerHTML = '<span class="badge badge-danger">Absent</span>';
                button.classList.remove('btn-warning');
                button.classList.add('btn-primary');
                button.textContent = 'Mark as Present';
                button.setAttribute('data-status', 'False');
            }

            console.log('Attendance updated successfully');
        } else {
            alert('Failed to update attendance: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update attendance');
    });
}

// Add event listener to all toggle-attendance buttons
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('toggle-attendance')) {
            const attendanceId = e.target.getAttribute('data-id');
            update_attendance(attendanceId, e.target);
        }
    });
});




/*==========================================*/
/* ======== FUNCTION TO UPDATE NOTE ========*/
/*==========================================*/

// Function to save note
function change_status() {
    const attendanceId = document.getElementById('attendanceId').value;
    const noteText = document.getElementById('noteText').value;

    fetch(`/api/change-note/${attendanceId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            note: noteText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const button = document.querySelector(`[data-id="${attendanceId}"].add-note`);
            const row = button.closest('tr');
            const noteCell = row.querySelector('td:nth-child(4) p');

            noteCell.textContent = noteText || 'N/A';
            button.setAttribute('data-note', noteText);
            button.textContent = noteText ? 'Edit Note' : 'Add Note';

            // Close the modal
            const modalElement = document.getElementById('attendanceNoteModal');
            const modal = bootstrap.Modal.getInstance(modalElement);

            if (modal) {
                modal.hide();
            }


            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());

        } else {
            alert('Failed to update note: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update note');
    });
}

//// Save note button click handler
//document.getElementById('saveNoteButton').addEventListener('click', function(e) {
//    e.preventDefault();
//    change_status();
//});


/*==========================================*/
/* ======== FUNCTION TO RESET ATTENDANCE ========*/
/*==========================================*/


/* Function to reset attendance */
function reset_attendance(calendar_id) {
    if (!confirm("Are you sure you want to reset all attendances?")) {
        return;
    }
    fetch(`/api/reset-attendance/${calendar_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else {
            alert("Unknown response from server");
        }

        // OPTIONAL: reload page or update table
        location.reload();
    })
    .catch(error => {
        console.error("Reset attendance error:", error);
        alert("An error occurred while resetting attendance.");
    });
}


/*==========================================*/
/* ======== FUNCTION TO LOAD SATISTIC ========*/
/*==========================================*/


let attendanceChart = null;
function get_statistic(calendar_id) {
    fetch(`/api/get-statistic/${calendar_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.data) {
            const stats = data.data; // { present_count, absent_count, total_count }

            const ctx = document.getElementById('attendanceStatsChart').getContext('2d');

            // Destroy old chart if exists
            if (attendanceChart) {
                attendanceChart.destroy();
            }

            // Create chart with animation
            attendanceChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Present', 'Absent'],
                    datasets: [{
                        data: [stats.present_count, stats.absent_count],
                        backgroundColor: ['#a0e7e5', '#ffb3b3'],
                        borderColor: ['#5adbb5', '#ff6b6b'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    animation: {
                        animateRotate: true, // rotate pie slices
                        animateScale: true   // scale in from center
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.label || '';
                                    let value = context.raw || 0;
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    }
                }
            });

            // Show modal
            const modalElement = document.getElementById('modalStatAttendance');
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else {
            alert(data.Message || "Unknown response from server");
        }
    })
    .catch(error => {
        console.error("Error fetching attendance statistics:", error);
        alert("An error occurred while fetching attendance statistics.");
    });
}


/*==========================================*/
/* ======== FUNCTION TO DOWNLOAD PDF ========*/
/*==========================================*/

function download_attendance_pdf() {
    const button = document.getElementById('download-attendance-pdf');
    const calendarId = button.getAttribute('data-id');

    // Get the table
    const table = document.querySelector('table#example-attendance');
    if (!table) {
        alert('Table not found');
        return;
    }

    // Get all rows from table
    const rows = table.querySelectorAll('tbody tr');
    const records = [];

    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            records.push({
                number: (index + 1).toString(),
                student_name: cells[1].textContent.trim(),
                status: cells[2].textContent.trim(),
                note: cells[3].textContent.trim()
            });
        }
    });

    // Get session info from the heading and card elements
    const heading = document.querySelector('h2.heading');
    const heading_text = heading ? heading.textContent.trim() : '';
    const group = heading_text.replace('Group Attendances:', '').trim();

    const pText = document.querySelector('.card-header .text-muted');
    const lines = pText ? pText.innerHTML.split('<br>') : [];

    let date = 'N/A';
    let startTime = 'N/A';
    let endTime = 'N/A';

    lines.forEach(line => {
        if (line.includes('Date:')) {
            date = line.replace('Date:', '').trim();
        }
        if (line.includes('Start Time:')) {
            startTime = line.replace('Start Time:', '').trim();
        }
        if (line.includes('End Time:')) {
            endTime = line.replace('End Time:', '').trim();
        }
    });

    const sessionInfo = {
        group: group || 'N/A',
        date: date,
        startTime: startTime,
        endTime: endTime
    };

    // Create HTML for PDF
    let html = `
        <h2 style="text-align: center;">Attendance List</h2>

        <div style="margin: 20px 0; line-height: 1.8;">
            <p><b>Group Attendance:</b> ${sessionInfo.group}</p>
            <p><b>Date:</b> ${sessionInfo.date}</p>
            <p><b>Start Time:</b> ${sessionInfo.startTime}</p>
            <p><b>End Time:</b> ${sessionInfo.endTime}</p>
        </div>

        <table border="1" cellpadding="10" style="width:100%;margin-top: 20px;">
            <thead>
                <tr style="background-color: #1EBA62; color: white; height:40px;">
                    <th style="padding-left:5px; border-right:1px solid grey;">#</th>
                    <th style="padding-left:5px;border-right:1px solid grey;">Full Name</th>
                    <th style="padding-left:5px;border-right:1px solid grey;">Attendance</th>
                    <th style="padding-left:5px;border-right:1px solid grey;">Note</th>
                </tr>
            </thead>
            <tbody>
    `;

    records.forEach((record) => {
        html += `
            <tr>
                <td style="padding:10px; border:1px solid grey;">${record.number}</td>
                <td style="padding:5px; border:1px solid grey;">${record.student_name}</td>
                <td style="padding:5px; border:1px solid grey;">${record.status}</td>
                <td style="padding:5px; border:1px solid grey;">${record.note}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    // Use html2pdf to generate PDF
    const element = document.createElement('div');
    element.innerHTML = html;

    const opt = {
        margin: 10,
        filename: `attendance_${calendarId}_${new Date().toISOString().split('T')[0]}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
    };

    if (typeof html2pdf === 'undefined') {
        alert('PDF library not loaded');
        return;
    }

    html2pdf().set(opt).from(element).save();
}


document.addEventListener('DOMContentLoaded', function() {
    const downloadButton = document.getElementById('download-attendance-pdf');
    if (downloadButton) {
        downloadButton.addEventListener('click', function(e) {
            e.preventDefault();
            download_attendance_pdf();
        });
    }
});


/*==========================================*/
/* ======== FUNCTION TO LOAD GROUP ========*/
/*==========================================*/

function loadGroupsToExternalEvents(accountId, sessionId) {
    fetch(`/api/get-group/${sessionId}/${accountId}`, {
        method: 'GET',
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data.data) {
            const groups = data.data;
            console.log(groups);
            const container = document.getElementById('my-custom-events');

            // Clear previous groups
            container.innerHTML = '';

            // Colors to cycle through
            const colors = ['bg-info'];

            // Create div for each group
            groups.forEach((group, index) => {
                const color = colors[index % colors.length];
                const buttonClass = color.replace('bg-', 'btn-');

                const groupDiv = document.createElement('div');
                groupDiv.className = `external-event ${buttonClass} light`;
                groupDiv.setAttribute('data-class', color);
                groupDiv.innerHTML = `
                    <i class="fa fa-move"></i>
                    <span>${group.name}</span>
                `;

                container.appendChild(groupDiv);

                console.log(`Group ${index + 1}:`, {
                    id: group.id,
                    name: group.name,
                    capacity: group.capacity,
                    session_id: group.session_id,
                    local_id: group.local_id,
                    status: group.status
                });
            });

            console.log(`Loaded ${groups.length} groups successfully`);

        } else {
            console.error('No data.data found');
        }
    })
    .catch(error => {
        console.error("Error fetching groups:", error);
    });
}


// Call it when page loads - get accountId and sessionId from data attributes
document.addEventListener('DOMContentLoaded', function() {
    // Get data from the calendar-info div
    const calendarInfo = document.getElementById('calendar-info');
    if (calendarInfo) {
        const local_id = parseInt(calendarInfo.getAttribute('data-local-id'));
        console.log('Loading rooms for local:', local_id);
        load_room(local_id);
        loadGroupsToExternalEvents(3,12)

    }
    // Removed the error log - this is normal on non-calendar pages
});


/*==========================================*/
/* ======== FUNCTION TO LOAD ROOM ========*/
/*==========================================*/


function load_room(local_id) {
    fetch(`/api/get_room/${local_id}`, {
        method: 'GET',
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data.Room) {
            const rooms = data.Room;
            console.log(rooms);

            // Get the room options container
            const roomOptions = document.querySelector('.custom-select[data-name="createEventRoom"] .options');

            if (roomOptions) {
                // Clear existing options except the first one (placeholder)
                roomOptions.innerHTML = '<div data-value="">Select a Room</div>';

                // Add rooms dynamically
                rooms.forEach(room => {
                    const optionDiv = document.createElement('div');
                    optionDiv.setAttribute('data-value', room.id);  // Assuming room has 'id' property
                    optionDiv.textContent = room.name;  // Assuming room has 'name' property
                    roomOptions.appendChild(optionDiv);
                });

                console.log(`Loaded ${rooms.length} rooms successfully`);
            } else {
                console.error('Room options container not found');
            }
        } else {
            console.error('No Room data found');
        }
    })
    .catch(error => {
        console.error("Error fetching room:", error);
    });
}


// Call it when page loads - get local_id from data attributes
document.addEventListener('DOMContentLoaded', function() {
    // Get data from the calendar-info div
    const calendarInfo = document.getElementById('calendar-info');
    if (calendarInfo) {
        const local_id = parseInt(calendarInfo.getAttribute('data-local-id'));
        console.log('Loading rooms for local:', local_id);
        load_room(local_id);
    } else {
        console.error('calendar-info element not found');
    }
});


/*==========================================*/
/* ======== FUNCTION TO LOAD TEACHER ========*/
/*==========================================*/

function load_teachers(session_id) {
    fetch(`/api/get_teacher/${session_id}`, {
        method: 'GET',
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data.teacher) {
            const teachers = data.teacher;
            console.log('Teachers:', teachers);

            // Get the teacher/subject options container
            const teacherOptions = document.querySelector('.custom-select[data-name="createEventSubject"] .options');

            if (teacherOptions) {
                // Clear existing options except the first one (placeholder)
                teacherOptions.innerHTML = '<div data-value="">Select a Subject and Teacher</div>';

                // Add teachers dynamically
                teachers.forEach(teacher => {
                    const optionDiv = document.createElement('div');

                    // Set attributes - adjust these based on your teacher object structure
                    optionDiv.setAttribute('data-value', teacher.id);  // or teacher.teacher_id
                    optionDiv.setAttribute('data-subject', teacher.subject_id || '1');  // if you have subject_id
                    optionDiv.setAttribute('data-user', teacher.id);

                    // Set text - adjust based on your teacher object structure
                    const subjectName = teacher.subject_name || 'Math';  // if you have subject_name
                    const teacherName = `${teacher.first_name} ${teacher.last_name}`;  // or teacher.full_name

                    optionDiv.textContent = `Subject : ${subjectName} - Teacher : ${teacherName}`;

                    teacherOptions.appendChild(optionDiv);
                });

                console.log(`Loaded ${teachers.length} teachers successfully`);

                // Re-initialize the click handlers for the new options
                initCustomSelects();
            } else {
                console.error('Teacher options container not found');
            }
        } else {
            console.error('No teacher data found');
        }
    })
    .catch(error => {
        console.error("Error fetching teachers:", error);
    });
}


// Update your DOMContentLoaded to also load teachers
document.addEventListener('DOMContentLoaded', function() {
    const calendarInfo = document.getElementById('calendar-info');
    if (calendarInfo) {
        const session_id = parseInt(calendarInfo.getAttribute('data-session-id'));
        const local_id = parseInt(calendarInfo.getAttribute('data-local-id'));

        console.log('Loading rooms for local:', local_id);
        load_room(local_id);

        console.log('Loading teachers for session:', session_id);
        load_teachers(session_id);
    } else {
        console.error('calendar-info element not found');
    }
});


// Add this JavaScript to handle the modal dropdown shows
document.addEventListener('DOMContentLoaded', function() {

    // Prevent Bootstrap Select from initializing on modal selects
    $('#createEventModal select, #viewEventModal select').addClass('no-selectpicker');

    // Handle when duplicate dropdown changes - CREATE MODAL (use regular change event)
    const createEventDuplicate = document.getElementById('createEventDuplicate');
    if (createEventDuplicate) {
        createEventDuplicate.addEventListener('change', function() {
            const value = this.value;
            const startTimeFields = document.getElementById('createStartTimeFields');
            const endTimeFields = document.getElementById('createEndTimeFields');
            const eventEndFields = document.getElementById('createEventEndFields');

            if (value !== 'none' && value !== '') {
                startTimeFields.style.display = 'block';
                endTimeFields.style.display = 'block';
                eventEndFields.style.display = 'block';
            } else {
                startTimeFields.style.display = 'none';
                endTimeFields.style.display = 'none';
                eventEndFields.style.display = 'none';
            }
        });
    }


    // Handle save event button for CREATE modal
    const createSaveEventButton = document.getElementById('createSaveEventButton');
    if (createSaveEventButton) {
        createSaveEventButton.addEventListener('click', function() {
            const eventForm = document.getElementById('createEventForm');

            if (!eventForm.checkValidity()) {
                alert('Please fill in all required fields');
                return;
            }

            // Get form data - using CREATE modal IDs
            const formData = {
                title: document.getElementById('createEventTitle').value,
                date: document.getElementById('createEventDate').value,
                type: document.getElementById('createTypeSessionSelect').value,
                room: document.getElementById('createEventRoom').value,
                subject: document.getElementById('createEventSubject').value,
                completionTags: (() => {
                    const element = document.getElementById('createEventCompletionTag');
                    if (!element) return [];

                    // Get all selected options (with 'selected-option' class)
                    const selectedOptions = element.querySelectorAll('.options .selected-option');

                    // Extract values from data-value attributes
                    const selectedValues = Array.from(selectedOptions).map(option =>
                        option.getAttribute('data-value')
                    ).filter(value => value !== null && value !== '');

                    return selectedValues;
                })(), // <-- Note the () at the end to execute immediately

                duplicate: (() => {
                    const element = document.getElementById('createEventDuplicate');
                    if (!element) return '';

                    const selectedElement = element.querySelector('.selected');
                    return selectedElement ? selectedElement.getAttribute('data-value') || '' : '';
                })(), // <-- Execute immediately
                duplicate: document.getElementById('createEventDuplicate').value,
                startTime: document.getElementById('createEventStartTime').value || null,
                endTime: document.getElementById('createEventEndTime').value || null,
                endDate: document.getElementById('createEventEndDate').value || null,
                description: document.getElementById('createEventDescription').value,
                groupId: document.getElementById('createEventGroupId').value,
                groupCapacity: document.getElementById('createEventGroupCapacity').value,
                sessionId: document.getElementById('createEventSessionId').value,
                accountId: document.getElementById('createEventAccountId').value,
                localId: document.getElementById('createEventLocalId').value
            };

            console.log('Form Data:', formData);

            // Send to backend
            fetch('/api/create-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.success) {
                    alert('Event created successfully!');
                    const eventModal = bootstrap.Modal.getInstance(document.getElementById('createEventModal'));
                    eventModal.hide();
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to create event');
            });
        });
    }

    // Handle save event button for VIEW modal
    const viewSaveEventButton = document.getElementById('viewSaveEventButton');
    if (viewSaveEventButton) {
        viewSaveEventButton.addEventListener('click', function() {
            const viewEventForm = document.getElementById('viewEventForm');

            if (!viewEventForm.checkValidity()) {
                alert('Please fill in all required fields');
                return;
            }

            const formData = {
                title: document.getElementById('viewEventTitle').value,
                date: document.getElementById('viewEventDate').value,
                type: document.getElementById('viewTypeSessionSelect').value,
                room: document.getElementById('viewEventRoom').value,
                subject: document.getElementById('viewEventSubject').value,
                completionTags: (() => {
                    const element = document.getElementById('createEventCompletionTag');
                    if (!element) return [];

                    // Get all selected options (with 'selected-option' class)
                    const selectedOptions = element.querySelectorAll('.options .selected-option');

                    // Extract values from data-value attributes
                    const selectedValues = Array.from(selectedOptions).map(option =>
                        option.getAttribute('data-value')
                    ).filter(value => value !== null && value !== '');

                    return selectedValues;
                })(), // <-- Note the () at the end to execute immediately

                duplicate: (() => {
                    const element = document.getElementById('createEventDuplicate');
                    if (!element) return '';

                    const selectedElement = element.querySelector('.selected');
                    return selectedElement ? selectedElement.getAttribute('data-value') || '' : '';
                })(), // <-- Execute immediately
                duplicate: document.getElementById('viewEventDuplicate').value,
                startTime: document.getElementById('viewEventStartTime').value || null,
                endTime: document.getElementById('viewEventEndTime').value || null,
                endDate: document.getElementById('viewEventEndDate').value || null,
                description: document.getElementById('viewEventDescription').value,
                groupId: document.getElementById('viewEventGroupId').value,
                groupCapacity: document.getElementById('viewEventGroupCapacity').value,
                sessionId: document.getElementById('viewEventSessionId').value,
                accountId: document.getElementById('viewEventAccountId').value,
                localId: document.getElementById('viewEventLocalId').value
            };

            console.log('View Form Data:', formData);

            fetch('/api/update-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.success) {
                    alert('Event updated successfully!');
                    const viewEventModal = bootstrap.Modal.getInstance(document.getElementById('viewEventModal'));
                    viewEventModal.hide();
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update event');
            });
        });
    }
});




/* =========================================*/
/* =========== JS MODAL ADD GROUP TO CALENDAR =========== */
/* =========================================*/

// Initialize all custom selects - GLOBAL FUNCTION
function initCustomSelects() {
    document.querySelectorAll('.custom-select').forEach(selectEl => {
        const selected = selectEl.querySelector('.selected');
        const options = selectEl.querySelector('.options');

        // Remove old event listeners to avoid duplicates
        const newSelected = selected.cloneNode(true);
        selected.parentNode.replaceChild(newSelected, selected);

        // Toggle dropdown
        newSelected.onclick = (e) => {
            e.stopPropagation();
            // Close other dropdowns
            document.querySelectorAll('.custom-select').forEach(s => {
                if (s !== selectEl) s.classList.remove('active');
            });
            selectEl.classList.toggle('active');
        };

        // Handle option selection
        const updatedOptions = selectEl.querySelector('.options');
        updatedOptions.querySelectorAll('div').forEach(opt => {
            opt.onclick = (e) => {
                e.stopPropagation();
                const value = opt.getAttribute('data-value');
                const text = opt.textContent;

                const currentSelected = selectEl.querySelector('.selected');
                currentSelected.textContent = text;
                currentSelected.setAttribute('data-value', value);
                selectEl.classList.remove('active');

                // Trigger change event for duplicate field
                if (selectEl.getAttribute('data-name') === 'createEventDuplicate') {
                    handleDuplicateChange(value);
                }
            };
        });
    });
}


// Handle duplicate field show/hide - GLOBAL FUNCTION
function handleDuplicateChange(value) {
    const startTimeFields = document.getElementById('createStartTimeFields');
    const endTimeFields = document.getElementById('createEndTimeFields');
    const eventEndFields = document.getElementById('createEventEndFields');

    if (!startTimeFields || !endTimeFields || !eventEndFields) {
        return;
    }

    if (value === 'none') {
        // "Not Duplicate" - show time fields but hide end date
        startTimeFields.style.display = 'block';
        endTimeFields.style.display = 'block';
        eventEndFields.style.display = 'none';
    } else if (value && value !== '') {
        // Any duplicate option - show all fields
        startTimeFields.style.display = 'block';
        endTimeFields.style.display = 'block';
        eventEndFields.style.display = 'block';
    } else {
        // No selection - hide all
        startTimeFields.style.display = 'none';
        endTimeFields.style.display = 'none';
        eventEndFields.style.display = 'none';
    }
}

// Get value from custom select - GLOBAL FUNCTION
function getCustomSelectValue(name) {
    const select = document.querySelector(`.custom-select[data-name="${name}"]`);
    if (select) {
        return select.querySelector('.selected').getAttribute('data-value') || '';
    }
    return '';
}


// Initialize when modal opens
document.addEventListener('DOMContentLoaded', function() {
    const createModalElement = document.getElementById('createEventModal');
    if (createModalElement) {
        createModalElement.addEventListener('shown.bs.modal', function() {
            initCustomSelects();
        });
    }

    // Handle save button
    const createSaveEventButton = document.getElementById('createSaveEventButton');
    if (createSaveEventButton) {
        createSaveEventButton.addEventListener('click', function() {
            const formData = {
                title: document.getElementById('createEventTitle').value,
                date: document.getElementById('createEventDate').value,
                type: getCustomSelectValue('createTypeSessionSelect'),
                room: getCustomSelectValue('createEventRoom'),
                subject: getCustomSelectValue('createEventSubject'),
                completionTags: (() => {
                    const element = document.getElementById('createEventCompletionTag');
                    if (!element) return [];

                    // Get all selected options (with 'selected-option' class)
                    const selectedOptions = element.querySelectorAll('.options .selected-option');

                    // Extract values from data-value attributes
                    const selectedValues = Array.from(selectedOptions).map(option =>
                        option.getAttribute('data-value')
                    ).filter(value => value !== null && value !== '');

                    return selectedValues;
                })(), // <-- Note the () at the end to execute immediately

                duplicate: (() => {
                    const element = document.getElementById('createEventDuplicate');
                    if (!element) return '';

                    const selectedElement = element.querySelector('.selected');
                    return selectedElement ? selectedElement.getAttribute('data-value') || '' : '';
                })(), // <-- Execute immediately

                startTime: document.getElementById('createEventStartTime').value || null,
                endTime: document.getElementById('createEventEndTime').value || null,
                endDate: document.getElementById('createEventEndDate').value || null,
                description: document.getElementById('createEventDescription').value,
                groupId: document.getElementById('createEventGroupId').value,
                groupCapacity: document.getElementById('createEventGroupCapacity').value,
                sessionId: document.getElementById('createEventSessionId').value,
                accountId: document.getElementById('createEventAccountId').value,
                localId: document.getElementById('createEventLocalId').value
            };

            console.log('Form Data:', formData);

            // Validate
            if (!formData.title || !formData.date || !formData.type || !formData.room || !formData.subject) {
                alert('Please fill in all required fields');
                return;
            }

            // Send to backend
            fetch('/api/create-event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Event created successfully!');
                    const eventModal = bootstrap.Modal.getInstance(document.getElementById('createEventModal'));
                    eventModal.hide();
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to create event');
            });
        });
    }
});


// Handle delete interval confirmation
document.addEventListener('DOMContentLoaded', function() {
    const confirmDeleteBtn = document.getElementById('confirmDeleteInterval');

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async function() {
            const sessionId = document.getElementById('sessionId').value;
            const startDate = document.getElementById('deleteTargetStartDate').value;
            const endDate = document.getElementById('deleteTargetEndDate').value;

            console.log('Session ID:', sessionId);
            console.log('Start Date:', startDate);
            console.log('End Date:', endDate);

            // Validate inputs
            if (!startDate || !endDate) {
                alert('Please select both start and end dates');
                return;
            }

            // Validate that end date is after start date
            if (new Date(endDate) < new Date(startDate)) {
                alert('End date must be after start date');
                return;
            }

            try {
                // Disable button to prevent double clicks
                const deleteBtn = document.getElementById('confirmDeleteInterval');
                deleteBtn.disabled = true;
                deleteBtn.textContent = 'Deleting...';

                const response = await fetch(`/api/delete-calander/${sessionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        start_date: startDate,
                        end_date: endDate
                    })
                });

                console.log('Response status:', response.status);
                console.log('Response ok:', response.ok);

                const result = await response.json();
                console.log('Response data:', result);

                if (response.ok) {
                    alert('Calendar interval deleted successfully!');

                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteIntervalModal'));
                    modal.hide();

                    // Reset form
                    document.getElementById('deleteTargetStartDate').value = '';
                    document.getElementById('deleteTargetEndDate').value = '';

                    // Optionally reload the page or update the calendar view
                    location.reload();

                } else {
                    console.error('Server error:', result);
                    alert(`Error: ${result.message || 'Failed to delete interval'}`);
                }

            } catch (error) {
                console.error('Fetch error details:', error);
                alert('An error occurred while deleting the interval. Check console for details.');
            } finally {
                // Re-enable button
                const deleteBtn = document.getElementById('confirmDeleteInterval');
                deleteBtn.disabled = false;
                deleteBtn.textContent = 'Delete';
            }
        });
    }
});


//######################### java script of group ############################


async function loadGroupsToGroupConfig(accountId, sessionId) {
    const container = document.getElementById('group-container');

    // Check if container exists (only on group page)
    if (!container) {
        return;
    }

    try {
        // Fetch groups from your API endpoint
        const response = await fetch(`/api/get-group/${sessionId}/${accountId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Print the result to console
        console.log('API Response:', result);

        // Clear the container first
        container.innerHTML = '';

        // Print the groups data
        if (result.Message === "Success" && result.data && result.data.length > 0) {
            console.log('Groups:', result.data);
            console.log('Number of groups:', result.data.length);

            // Render each group
            result.data.forEach((group, index) => {
                console.log(`Group ${index + 1}:`, group);

                // Create group card HTML
                const groupCard = createGroupCard(group);
                container.innerHTML += groupCard;
            });

            console.log('Groups rendered successfully!');
        } else {
            container.innerHTML = '<div class="col-12 text-center py-5"><p>No groups found.</p></div>';
            console.log('No groups found or error occurred');
        }

    } catch (error) {
        console.error('Error loading groups:', error);
        container.innerHTML = '<div class="col-12 text-center py-5"><p class="text-danger">Error loading groups.</p></div>';
    }
}


//=============================================
//=========delete user from the group =========
//=============================================

$(document).on('click', '.remove-user-session', async function() {
    // Get the parent div that contains all the data attributes
    const userItemDiv = $(this).closest('.user-item-session');

    // Extract the IDs from data attributes
    const relationId = userItemDiv.data('id');           // student.relation_id
    const sessionId = userItemDiv.data('session-id');    // group.session_id
    const userId = userItemDiv.data('user-id');          // student.user_id

    try {
        // Fetch groups from your API endpoint
        const response = await fetch(`/api/delete_user_f_group/${sessionId}/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok){
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        console.log('API Response:', result);

        // Optionally remove the user from the UI after successful deletion
        userItemDiv.remove();

        // Or show a success message
        alert('User successfully removed from group');

    } catch (error) {
        console.error('Error deleting user from group:', error);
        alert('Failed to remove user from group');
    }
});


// Function to create group card HTML
function createGroupCard(group) {
    // Generate student items HTML
    const studentItems = group.list_student.map(student => `
        <div class="user-item-session" data-id="${student.relation_id}" data-session-id="${group.session_id}" data-user-id="${student.user_id}">
            ${student.full_name}
            <button class="btn btn-xs btn-danger remove-user-session">x</button>
        </div>
    `).join('');

    // Create the complete group card HTML
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card contact_list text-center group-card">
                <div class="card-body">
                    <div class="user-content-session" data-group-id="${group.id}">
                        <!-- Header / Group info -->
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="user-details text-start">
                                <h4 class="user-name mb-0">${group.name}</h4>
                                <p class="mb-0 text-muted">
                                    Capacity: ${group.list_student.length}/${group.capacity}
                                </p>
                            </div>

                            <!-- Dropdown - Fixed structure -->
                            <div class="dropdown">
                                <button class="btn sharp btn-light"
                                        type="button"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false">
                                        <svg width="24" height="6" viewBox="0 0 24 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M12.0012 0.359985C11.6543 0.359985 11.3109 0.428302 10.9904 0.561035C10.67 0.693767 10.3788 0.888317 10.1335 1.13358C9.88829 1.37883 9.69374 1.67 9.56101 1.99044C9.42828 2.31089 9.35996 2.65434 9.35996 3.00119C9.35996 3.34803 9.42828 3.69148 9.56101 4.01193C9.69374 4.33237 9.88829 4.62354 10.1335 4.8688C10.3788 5.11405 10.67 5.3086 10.9904 5.44134C11.3109 5.57407 11.6543 5.64239 12.0012 5.64239C12.7017 5.64223 13.3734 5.36381 13.8686 4.86837C14.3638 4.37294 14.6419 3.70108 14.6418 3.00059C14.6416 2.3001 14.3632 1.62836 13.8677 1.13315C13.3723 0.637942 12.7004 0.359826 12 0.359985H12.0012ZM3.60116 0.359985C3.25431 0.359985 2.91086 0.428302 2.59042 0.561035C2.26997 0.693767 1.97881 0.888317 1.73355 1.13358C1.48829 1.37883 1.29374 1.67 1.16101 1.99044C1.02828 2.31089 0.959961 2.65434 0.959961 3.00119C0.959961 3.34803 1.02828 3.69148 1.16101 4.01193C1.29374 4.33237 1.48829 4.62354 1.73355 4.8688C1.97881 5.11405 2.26997 5.3086 2.59042 5.44134C2.91086 5.57407 3.25431 5.64239 3.60116 5.64239C4.30165 5.64223 4.97339 5.36381 5.4686 4.86837C5.9638 4.37294 6.24192 3.70108 6.24176 3.00059C6.2416 2.3001 5.96318 1.62836 5.46775 1.13315C4.97231 0.637942 4.30045 0.359826 3.59996 0.359985H3.60116ZM20.4012 0.359985C20.0543 0.359985 19.7109 0.428302 19.3904 0.561035C19.07 0.693767 18.7788 0.888317 18.5336 1.13358C18.2883 1.37883 18.0937 1.67 17.961 1.99044C17.8283 2.31089 17.76 2.65434 17.76 3.00119C17.76 3.34803 17.8283 3.69148 17.961 4.01193C18.0937 4.33237 18.2883 4.62354 18.5336 4.8688C18.7788 5.11405 19.07 5.3086 19.3904 5.44134C19.7109 5.57407 20.0543 5.64239 20.4012 5.64239C21.1017 5.64223 21.7734 5.36381 22.2686 4.86837C22.7638 4.37294 23.0419 3.70108 23.0418 3.00059C23.0416 2.3001 22.7632 1.62836 22.2677 1.13315C21.7723 0.637942 21.1005 0.359826 20.4 0.359985H20.4012Z" fill="#A098AE"></path>
                                        </svg>
                                </button>

                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li>
                                        <a class="dropdown-item delete-group"
                                           href="javascript:void(0);"
                                           data-id="${group.id}">
                                            Delete
                                        </a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item edit-group"
                                           href="javascript:void(0);"
                                           data-id="${group.id}"
                                           data-name="${group.name}"
                                           data-capacity="${group.capacity}"
                                           data-bs-toggle="modal"
                                           data-bs-target="#groupUpdateModal">
                                            Edit
                                        </a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item show-student"
                                           href="javascript:void(0);"
                                           data-id="${group.id}"
                                           data-name="${group.name}"
                                           data-capacity="${group.capacity}"
                                           data-bs-toggle="modal"
                                           data-bs-target="#groupShowStudentModal">
                                            Show students
                                        </a>
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <!-- Students list -->
                        <div class="droppable-area-session ui-droppable"
                             style="max-height: 250px !important; overflow-y: auto;"
                             data-group-id="${group.id}"
                             data-capacity="${group.capacity}">

                            ${studentItems || `
                                <p class="text-muted text-center mb-0">
                                    No students in this group
                                </p>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}



//======================================
//DELETE GROUP FROM THE DROP DOWN MENU
//======================================
$(document).on('click', '.delete-group', function(e) {
    e.preventDefault();
    const groupId = $(this).data('id');

    Swal.fire({
        title: 'Are you sure?',
        text: 'This Group will be deleted permanently. You will not be able to undo this action.',
        icon: 'error',
        showCancelButton: true,
        confirmButtonColor: '#dd3333',
        cancelButtonColor: '#64c5b1',
        confirmButtonText: 'Yes, delete it.',
        cancelButtonText: 'No, cancel.',
        width: '500px',
        padding: '20px'
    }).then((result) => {
        if (result.isConfirmed) {
            deleteGroup(groupId);
        }
    });
});

function deleteGroup(groupId) {
    $.ajax({
        url: `/api/delete-group/${groupId}`, // Replace with your actual endpoint
        type: 'DELETE',
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content') // If using Laravel
        },
        success: function(response) {
            Swal.fire({
                title: 'Deleted!',
                text: 'Group has been deleted successfully.',
                icon: 'success',
                confirmButtonColor: '#64c5b1',
                timer: 2000,
                showConfirmButton: false
            });

            // Remove the group card from the page
            $(`.user-content-session[data-group-id="${groupId}"]`)
                .closest('.col-md-6, .col-lg-4')
                .fadeOut(300, function() {
                    $(this).remove();
                });
        },
        error: function(xhr, status, error) {
            Swal.fire({
                title: 'Error!',
                text: 'Failed to delete the group. Please try again.',
                icon: 'error',
                confirmButtonColor: '#dd3333'
            });
        }
    });
}

// When "Delete" button is clicked for a student
$(document).on('click', '.delete-student', function(e) {
    e.preventDefault();

    const relationId = $(this).data('id');

    console.log('Student Relation ID:', relationId);

    // Or display in alert
    alert('Student ID: ' + relationId);
});


//======================================
//EDIT GROUP FROM THE DROP DOWN MENU
//======================================


$(document).on('click', '.edit-group', function(e) {
    // Get data from the button
    const groupId = $(this).data('id');
    const groupName = $(this).data('name');
    const groupCapacity = $(this).data('capacity');

    // Fill the form fields with the group data
    $('#groupId').val(groupId);
    $('#groupName').val(groupName);
    $('#groupCapacity').val(groupCapacity);

    // Clear previous relations
    $('#relation-collection').empty();

    // Now fetch the relations for this group from your backend
    // Replace '/api/groups/' with your actual endpoint
    $.ajax({
        url: `/api/groups/${groupId}`,
        type: 'GET',
        success: function(response) {
            // Assuming response.relations contains the teacher-subject relations
            if (response.relations && response.relations.length > 0) {
                response.relations.forEach(relation => {
                    addRelationItem(relation);
                });
            } else {
                // If no relations, add one empty relation
                addRelationItem();
            }
        },
        error: function() {
            // On error, add one empty relation
            addRelationItem();
        }
    });

    // The modal will open automatically because of data-bs-toggle="modal"
});



//======================================
//SHOW STUDENT FROM GROUP
//======================================
// When "Show students" button is clicked
$(document).on('click', '.show-student', function(e) {
    e.preventDefault();

    const groupId = $(this).data('id');
    const groupName = $(this).data('name');

    // Update modal title
    $('#groupShowStudentModalLabel').text(`Students - ${groupName}`);

    // Clear previous students
    $('#students-list').empty();

    // Find the group card in the DOM
    const groupCard = $(`.user-content-session[data-group-id="${groupId}"]`);

    // Get all students from the group card
    const students = groupCard.find('.user-item-session');

    // Check if there are students
    if (students.length > 0) {
        // Loop through students and add them to the modal list
        students.each(function() {
            const studentName = $(this).text().trim().replace('x', '').trim(); // Remove the 'x' button text
            const relationId = $(this).data('id');
            const sessionId = $(this).data('session-id');
            const userId = $(this).data('user-id');

            const studentItem = `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${studentName}
                    <button class="btn btn-danger btn-sm delete-student"
                            data-session-id="${sessionId}"
                            data-user-id="${userId}"
                            data-id="${relationId}"
                            data-name="${studentName}"
                            data-group-id="${groupId}">
                        Delete
                    </button>
                </li>
            `;
            $('#students-list').append(studentItem);
        });
    } else {
        // No students found
        $('#students-list').html('<li class="list-group-item text-center text-muted">No students in this group</li>');
    }

    // The modal will open automatically because of data-bs-toggle="modal" in the button
});


//===========================================================
//========== FUNCTION TO LOAD STUDENT NOT AFFECTED ==========
//===========================================================
async function loadUsersNotAffected(sessionId, accountId) {
    const container = document.getElementById('external-events');

    // Check if container exists
    if (!container) {
        console.log('external-events container not found');
        return;
    }

    try {

        // Fetch users not affected from API (now with accountId)
        const response = await fetch(`/api/show_user_not_affected/${sessionId}/${accountId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Print the result to console
        console.log('API Response:', result);

        // Remove existing user elements (keep title and search box)
        const existingUsers = container.querySelectorAll('.external-event-session');
        existingUsers.forEach(user => user.remove());

        // Render users (changed from result.data to result.students)
        if (result.Message === "Success" && result.students && result.students.length > 0) {
            console.log('Users not affected:', result.students);
            console.log('Number of users:', result.students.length);

            // Render each user
            result.students.forEach((user, index) => {
                console.log(`User ${index + 1}:`, user);

                const userElement = createUserElement(user, sessionId);
                container.appendChild(userElement);
            });

            // Re-initialize drag and drop after elements are added
            initializeDragAndDrop();

            console.log('Users rendered successfully!');
        } else {
            // No users found
            const noUsersDiv = document.createElement('div');
            noUsersDiv.className = 'text-center py-3';
            noUsersDiv.innerHTML = '<p class="text-muted">No users without groups found.</p>';
            container.appendChild(noUsersDiv);
            console.log('No users found');
        }

    } catch (error) {
        console.error('Error loading users:', error);
    }
}


// Function to create user element (updated to use new field names)
function createUserElement(user, sessionId) {
    const userDiv = document.createElement('div');
    userDiv.className = 'external-event-session btn btn-primary light';
    userDiv.setAttribute('data-id', user.userId);  // Changed from user.user_id
    userDiv.setAttribute('data-user-id', user.userId);  // Changed from user.user_id
    userDiv.setAttribute('data-count', user.sessionCount);  // Changed from user.count
    userDiv.setAttribute('data-session-id', sessionId);

    userDiv.innerHTML = `
        <i class="fa fa-move"></i>
        <span class="user-name">
            ${user.userName}
        </span>
        <small class="badge bg-warning ms-1 session-count">
            ${user.sessionCount}
        </small>
    `;

    return userDiv;
}


// Function to assign user to group via API
async function assignUserToGroup(userId, groupId, sessionId) {
    try {
        const response = await fetch(`/api/affect_user/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                group_id: groupId
            })
        });

        const result = await response.json();

        if (response.ok && result.Message === "Success") {
            console.log('User assigned successfully:', result);
            return { success: true, data: result };
        } else {
            console.error('Failed to assign user:', result.Message);
            return { success: false, message: result.Message };
        }
    } catch (error) {
        console.error('Error assigning user to group:', error);
        return { success: false, message: error.message };
    }
}


// Function to initialize drag and drop (no changes needed)
function initializeDragAndDrop() {
    if (typeof jQuery !== 'undefined' && jQuery.fn.draggable) {
        // Make user items draggable
        jQuery('.external-event-session').draggable({
            revert: 'invalid',
            helper: 'clone',
            cursor: 'move',
            zIndex: 999
        });

        // Make group drop areas droppable
        jQuery('.droppable-area-session').droppable({
            accept: '.external-event-session',
            drop: async function(event, ui) {
                const userElement = ui.draggable;
                const groupId = jQuery(this).data('group-id');
                const userId = userElement.data('user-id');
                const sessionId = userElement.data('session-id');

                console.log('Dropped user:', userId, 'into group:', groupId);

                // Call API to assign user to group
                const result = await assignUserToGroup(userId, groupId, sessionId);

                if (result.success) {
                    // Success - move the element visually
                    const clone = userElement.clone();
                    clone.removeClass('ui-draggable ui-draggable-handle');
                    clone.addClass('user-item-session');

                    // Add remove button
                    clone.append('<button class="btn btn-xs btn-danger remove-user-session">x</button>');

                    jQuery(this).append(clone);

                    // Remove from original list
                    userElement.remove();

                    // Show success message (optional)
                    alert('User successfully assigned to group!');

                    // Reload users not affected to update the list
                    loadUsersNotAffected(sessionId, accountId);
                } else {
                    // Failed - show error and revert
                    alert('Failed to assign user: ' + (result.message || 'Unknown error'));
                    console.error('Assignment failed:', result);
                }
            }
        });

        console.log('Drag and drop initialized');
    } else {
        console.error('jQuery UI not loaded - drag and drop will not work');
    }
}



//function for the relation in the add group
$(document).ready(function() {
    console.log('Script loaded');

    let relationIndex = 0;
    let subjectsData = [];
    let teachersData = [];
    let subjectsLoaded = false;
    let teachersLoaded = false;

    // Helper function to show error modal
    function showErrorModal(message) {
        $('#successMessage').text(message);
        $('#successModal .text-success').removeClass('text-success').addClass('text-danger');
        $('#successModal h3').text('Error');
        $('#successModal .btn-success').removeClass('btn-success').addClass('btn-danger');
        $('#successModal .check-icon').css('border-color', '#dc3545');
        $('#successModal .icon-line').css('background-color', '#dc3545');
        $('#successModal').modal('show');

        // Reset to success styling when closed
        $('#successModal').on('hidden.bs.modal', function() {
            $('#successModal .text-danger').removeClass('text-danger').addClass('text-success');
            $('#successModal h3').text('Success!');
            $('#successModal .btn-danger').removeClass('btn-danger').addClass('btn-success');
            $('#successModal .check-icon').css('border-color', '#4CAF50');
            $('#successModal .icon-line').css('background-color', '#4CAF50');
        });
    }

    // Helper function to show success modal
    function showSuccessModal(message) {
        $('#successMessage').text(message);
        $('#successModal').modal('show');
    }

    // Fetch subjects when page loads
    async function loadSubjects() {
        try {
            const accountId = window.ACCOUNT_ID;

            if (!accountId) {
                console.error('Account ID not found');
                return;
            }

            console.log('Loading subjects for account:', accountId);
            const response = await fetch(`/api/get_subject_group/${accountId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Subjects API Response:', result);

            if (result.Data) {
                subjectsData = result.Data;
                subjectsLoaded = true;
                console.log('Subjects loaded successfully:', subjectsData);
            }
        } catch (error) {
            console.error('Error loading subjects:', error);
            showErrorModal('Failed to load subjects. Please refresh the page.');
        }
    }

    // Fetch teachers when page loads
    async function loadTeachers() {
        try {
            const accountId = window.ACCOUNT_ID;

            if (!accountId) {
                console.error('Account ID not found');
                return;
            }

            console.log('Loading teachers for account:', accountId);
            const response = await fetch(`/api/get_teacher/${accountId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Teachers API Response:', result);

            // Check both possible response formats
            if (result.data) {
                teachersData = result.data;
                teachersLoaded = true;
                console.log('Teachers loaded successfully:', teachersData);
            } else if (result.teacher) {
                teachersData = result.teacher;
                teachersLoaded = true;
                console.log('Teachers loaded successfully:', teachersData);
            }
        } catch (error) {
            console.error('Error loading teachers:', error);
            showErrorModal('Failed to load teachers. Please refresh the page.');
        }
    }

    // Load both subjects and teachers immediately
    loadSubjects();
    loadTeachers();

    // Generate subject options HTML
    function getSubjectOptions() {
        if (subjectsData.length === 0) {
            return '<option value="" selected="selected">No subjects available</option>';
        }

        let options = '<option value="" selected="selected">Choose the Subject...</option>';
        subjectsData.forEach(subject => {
            options += `<option value="${subject.id}">${subject.subject_name}</option>`;
        });
        return options;
    }

    // Generate teacher options HTML
    function getTeacherOptions() {
        if (teachersData.length === 0) {
            return '<option value="" selected="selected">No teachers available</option>';
        }

        let options = '<option value="" selected="selected">Choose the Teacher...</option>';
        teachersData.forEach(teacher => {
            // Use full_name from the API response
            const teacherName = teacher.full_name || teacher.username || teacher.email || 'Unknown';
            options += `<option value="${teacher.id}">${teacherName}</option>`;
        });
        return options;
    }

    // Check if button exists
    const addButton = $('#add-relationn');
    console.log('Add relation button found:', addButton.length);

    // Handle "Add Relation" button click
    $('#add-relationn').on('click', function(e) {
        e.preventDefault();
        console.log('Add Relation button clicked!');
        console.log('Subjects loaded?', subjectsLoaded);
        console.log('Teachers loaded?', teachersLoaded);

        const $collectionHolder = $('#relation_group_local_session_relationTeacherToSubjectGroups');

        // Check if both subjects and teachers are loaded
        if (!subjectsLoaded || !teachersLoaded) {
            showErrorModal('Please wait, loading data...');
            return;
        }

        // Create the new relation form HTML with dynamic subjects AND teachers
        const newRelationForm = `
            <div class="form-group relation-item mb-3 p-3 border rounded" data-index="${relationIndex}">
                <div id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}">
                    <div class="mb-3">
                        <label for="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_subject" class="required" style="display: block; margin-bottom: 0.5rem; font-weight: bold; color: #333;">
                            Subject
                        </label>
                        <select id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_subject"
                                name="relation_group_local_session[relationTeacherToSubjectGroups][${relationIndex}][subject]"
                                required="required"
                                class="form-control relation-subject"
                                style="width: 100%; box-sizing: border-box;">
                            ${getSubjectOptions()}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_user" class="required" style="display: block; margin-bottom: 0.5rem; font-weight: bold; color: #333;">
                            Teacher
                        </label>
                        <select id="relation_group_local_session_relationTeacherToSubjectGroups_${relationIndex}_user"
                                name="relation_group_local_session[relationTeacherToSubjectGroups][${relationIndex}][user]"
                                required="required"
                                class="form-control relation-teacher"
                                style="width: 100%; box-sizing: border-box;">
                            ${getTeacherOptions()}
                        </select>
                    </div>
                </div>
                <button type="button" class="btn btn-danger remove-relation" style="width: 100%; text-align: center; border-radius: 5px; padding: 0.5rem;">
                    Remove
                </button>
            </div>
        `;

        $collectionHolder.append(newRelationForm);
        console.log('Form added! Index:', relationIndex);

        relationIndex++;
    });

    // Handle "Remove" button click
    $(document).on('click', '.remove-relation', function() {
        console.log('Remove button clicked');
        $(this).closest('.relation-item').remove();
    });

    // Handle form submission
    $('#group-local-session-form').on('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted!');

        const sessionId = window.SESSION_ID;
        const accountId = window.ACCOUNT_ID;

        // Validate session and account IDs
        if (!sessionId || !accountId) {
            showErrorModal('Missing session or account information');
            return;
        }

        // Get form values
        const groupName = $('#relation_group_local_session_name').val().trim();
        const capacity = $('#relation_group_local_session_capacity').val();

        // Validate basic fields
        if (!groupName) {
            showErrorModal('Please enter a group name');
            return;
        }

        if (!capacity || capacity <= 0) {
            showErrorModal('Please enter a valid capacity');
            return;
        }

        // Get all relations (subject + teacher pairs)
        const relations = [];
        $('.relation-item').each(function() {
            const subjectId = $(this).find('.relation-subject').val();
            const teacherId = $(this).find('.relation-teacher').val();

            if (subjectId && teacherId) {
                relations.push({
                    subject_id: parseInt(subjectId),
                    teacher_id: parseInt(teacherId)
                });
            }
        });

        // Validate at least one relation
        if (relations.length === 0) {
            showErrorModal('Please add at least one subject and teacher relation');
            return;
        }

        // Use the first relation for the main group (as per your backend structure)
        const firstRelation = relations[0];

        // Prepare data
        const formData = {
            group_name: groupName,
            capacity: parseInt(capacity),
            subject_id: firstRelation.subject_id,
            teacher_id: firstRelation.teacher_id,
            account_id: accountId,
            local_id: window.LOCAL_ID,

            access_type: 0
        };

        console.log('Sending data:', formData);

        try {
            // Show loading state
            const submitButton = $(this).find('button[type="submit"]');
            const originalText = submitButton.text();
            submitButton.prop('disabled', true).text('Creating...');

            const response = await fetch(`/api/create_group/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            console.log('Server response:', result);

            if (response.ok) {
                // Hide the group modal first
                $('#groupModal').modal('hide');

                // Wait for modal to close, then show success
                setTimeout(() => {
                    // Show success modal
                    showSuccessModal(`Group "${groupName}" created successfully!`);

                    // Auto-reload after success modal is closed
                    $('#successModal').on('hidden.bs.modal', function() {
                        location.reload();
                    });
                }, 300);
            } else {
                showErrorModal('Error: ' + (result.Message || 'Failed to create group'));
            }

            // Restore button state
            submitButton.prop('disabled', false).text(originalText);

        } catch (error) {
            console.error('Error creating group:', error);
            showErrorModal('Failed to create group. Please try again.');

            // Restore button state
            const submitButton = $(this).find('button[type="submit"]');
            submitButton.prop('disabled', false).text('Create');
        }
    });

    // Reset form when modal is closed
    $('#groupModal').on('hidden.bs.modal', function() {
        console.log('Modal closed, resetting form');
        $('#relation_group_local_session_relationTeacherToSubjectGroups').empty();
        relationIndex = 0;
        $('#group-local-session-form')[0].reset();
    });
});



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

// ============ ADD THIS - NOTIFICATION LISTENER ============
socket.on('calendar_notification', function(notification) {
    console.log("📩 Notification received:", notification);

    const notificationList = document.querySelector('#DZ_W_Notification1 ul.timeline');

    if (!notificationList) {
        console.error("❌ Notification list not found!");
        return;
    }

    const li = document.createElement('li');
    li.innerHTML = `
        <div class="timeline-panel">
            <div class="media me-2">
                <img alt="image" width="50" src="${notification.avatar || '/static/assets/images/avatar/1.jpg'}">
            </div>
            <div class="media-body">
                <h6 class="mb-1">${notification.title}</h6>
                <small class="d-block">${notification.time}</small>
            </div>
        </div>
    `;
    notificationList.prepend(li);

    // Update notification count badge (if you have one)
    const badge = document.getElementById('notificationCount');
    if (badge) {
        const currentCount = parseInt(badge.textContent) || 0;
        badge.textContent = currentCount + 1;
        badge.style.display = 'inline-block';
    }

    console.log("✅ Notification added to UI");
});
// ========================================================

document.addEventListener('DOMContentLoaded', function() {
    const notificationToggle = document.getElementById('notificationToggle');
    const notificationDropdown = document.getElementById('notificationDropdown');

    if (notificationToggle && notificationDropdown) {
        notificationToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');
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