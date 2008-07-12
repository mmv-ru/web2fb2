$(document).ready(function(){
	
	
	a1 = $('<img>').attr('src','/misc/done.gif');
	a2 = $('<img>').attr('src','/misc/blank.gif');
	a3 = $('<img>').attr('src','/misc/progress.gif');
	a4 = $('<img>').attr('src','/misc/progress_mid.gif');
	
	$("#descr_div").hide();
	$(".error").hide()
	$(".result").hide()
	$(".progres").hide()
	$(".try").hide()
	$(".cancel").hide()
	
	autodetect_change()
	

	$("#descr_tab").click(function(){
		$("#descr_div").slideToggle("fast")
	});
	
	$("#descr_div #autodetect").change(
		function(){
			autodetect_change()
		}
	);
	
	$("#cancel").click(
		function(){
			CANCEL = true;
			do_cancel()
		}
	);
	
	$("form").submit(
		function(){
			$(".error").html('')
			$(".error").hide()
			$(".try").html('')
			$(".try").hide()
			$(".result").html('')
			$(".result").hide('')
			$(".cancel").show('')
			$(".progres").show('')
			$(".progres").html('<center><img src = "/misc/progress_mid.gif" /></center>')
			
			work_disable();
			CANCEL = false;
			
			$(".error").ajaxError(function(event, request, settings){
				$(this).html("<li>Ajax error requesting page " + settings.url + "</li>");
				$(".progres").hide('');
				$(".error").show();
			});
			get_ans()
			
			return false
		}
	)
	
	function autodetect_change()
	{
		if( $("#descr_div #autodetect").attr('checked') )
			$(".descr").attr({disabled: true})
		else
			$(".descr").attr({disabled: false})
	}
	
	function work_disable()
	{
		$(".descr").attr({disabled: true});
		$("form input").attr({disabled: true});
	}
	
	function work_enable()
	{
		$(".descr").attr({disabled: false});
		$("form input").attr({disabled: false});
		autodetect_change()
	}
	
	function get_ans()
	{

		if (CANCEL)
		{
			
		}
		else
		{
			$.getJSON(
				"",
				{
					'ajax':1,
					
					'url': $('#weburl').val(),
					'img': $('#img').attr('checked'),
					'yah2fb': $('#yah2fb').attr('checked'),
					
					'autodetect': $('#autodetect').attr('checked'),
					'title': $('#title').val(),
					'author_first':$('#author_first').val(),
					'author_middle':$('#author_middle').val(),
					'author_last':$('#author_last').val(),
					'genre': $('#genre').val(),
					'lang':$('#lang').val()
				},
				onAjaxSuccess
			)
		}
	}
	
	function do_cancel()
	{
		work_enable();
		$(".progres").hide()
		$(".try").hide()
		$(".cancel").hide()
		$(".result").hide()
		$(".error").hide()
	}
	
	function onAjaxSuccess(obj)
	{
		
		if(CANCEL)
		{
		
		}
		else if (obj.error)
		{
			work_enable();
			$(".progres").hide()
			$(".cancel").hide()
			$(".try").hide()
			$(".error").show()
			$(".error").html(obj.error)
		}
		else if(obj.result)
		{
			work_enable();
			$(".progres").hide()
			$(".cancel").hide()
			$(".try").hide()
			$(".result").show()
			$(".result").html(obj.result)
			
			$('#title').val(obj.descr['title'])
			$('#author_first').val(obj.descr['author_first'])
			$('#author_middle').val(obj.descr['author_middle'])
			$('#author_last').val(obj.descr['author_last'])
			$('#genre').val(obj.descr['genre']);
			$('#lang').val(obj.descr['lang'])
		}
		else if(obj.progres)
		{
			
			$(".try").hide()
			$(".progres").show()
			$(".progres").html(obj.progres)
			window.setTimeout(get_ans, 2000);
		}
		else if(obj.tryagain)
		{
			$(".progres").hide()
			$(".try").show()
			$(".try").html(obj.tryagain)
			window.setTimeout(get_ans, 20000);
		}
		else
		{
			work_enable();
			$(".progres").hide()
			$(".try").hide()
			$(".cancel").hide()
			$(".error").show()
			$(".error").html('Ajax error')
		}
	}
	
	if ($("form #doit").attr('value'))
	{
		$("form ").submit()
	}
	
});