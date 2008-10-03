$(document).ready(function(){
	
	preview = $("#preview_ifame").dialog({modal: true,
		title: 'preview (Esc to close) ',
		dialogClass: 'preview_proxy',
		autoOpen: false,
		height: 500,
		width: 700,
		minHeight: 100,
		minWidth: 250,
		overlay: { opacity: 0.5, background: "black" },
		resize: function() { $('iframe').hide(); },
		resizeStop: function() { $('iframe').show(); },
		drag: function() { $('iframe').hide(); },
		dragStop: function() { $('iframe').show(); }
	});
 
	$("#preview_on").show();
	
	$("#preview_on").click(function(){
		preview.dialog( "open" );
	});
});