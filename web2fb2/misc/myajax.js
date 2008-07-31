function addaut(obj)
	{
		if (! $("input", $(obj).parent()).attr('disabled'))
			add_author($('input:eq(0)', $(obj).parent()).val(), $('input:eq(1)', $(obj).parent()).val(), $('input:eq(2)', $(obj).parent()).val())
	}
	
function remaut(obj)
	{
		if (! $("input", $(obj).parent()).attr('disabled'))
			if( $("#authors tr").length > 1)
				$(obj).parent().remove();
	}
	
	function add_author(first, middle, last)
	{
		id = 0
		if ($("#authors tr:last input").attr('name'))
			id = 1 + parseInt($("#authors tr:last input").attr('name').split('|')[1]);
		
		$("#authors").append("<tr><td>Author:</td><td><input class='descr' type='text' name='author_first|" + id +"'  size='20' maxlength='256' value = '" + first + "'/><br /><label style='font-size:x-small'>first name</label></td><td><input class='descr' type='text' name='author_middle|" + id +"' size='20' maxlength='256' value = '" + middle + "' /><br /><label style='font-size:x-small'>middle name</label></td><td><input class='descr' type='text' name='author_last|" + id +"' size='20' maxlength='256' value = '" + last + "' /><br /><label style='font-size:x-small'>last name</label></td><td id ='addaut' onClick = 'addaut(this)'>[+]<br />&nbsp;</td><td id ='remaut' onClick = 'remaut(this)'>[-]<br />&nbsp;</td></tr>")
		
	}


$(document).ready(function(){
	
	
	a1 = $('<img>').attr('src','/misc/done.gif');
	a2 = $('<img>').attr('src','/misc/blank.gif');
	a3 = $('<img>').attr('src','/misc/progress.gif');
	a4 = $('<img>').attr('src','/misc/progress_big.gif');
	
	$("#descr_div").hide();
	$(".error").hide()
	$(".result").hide()
	$(".progres").hide()
	$(".try").hide()
	$(".cancel").hide()
	
	add_author('', '', '')
	
	autodetect_change()
	
	

	$("#descr_tab").click(function(){
		$("#descr_div").slideToggle("fast")
	});
	
	$("#addurl").click(function(){
		
		if (! $("input", $(this).parent()).attr('disabled'))
			if( $("#urls tr").length < 5)
				$(this).parent().clone(true).appendTo($("#urls"));
	});
	
	$("#remurl").click(function(){
		
		if (! $("input", $(this).parent()).attr('disabled'))
			if( $("#urls tr").length > 1)
				$(this).parent().remove();
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
			$(".progres").html('<center><img src = "/misc/progress_big.gif" /></center>')
			
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
			work_enable();
			var str = $("#f").serialize()
			work_disable();
			$.getJSON("?ajax=1&" +str, onAjaxSuccess)
			
			/*
			$.getJSON(
				"",
				{
					'ajax':1,
					
					'url': $('#weburl').val(),
					'img': $('#img').attr('checked'),
					'yah2fb': $('#yah2fb').attr('checked'),
					'json': $("#f").serializeArray(),
					
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
			*/
			
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
			$('#genre').val(obj.descr['genre']);
			$('#lang').val(obj.descr['lang'])
			
			authors = obj.descr['authors']
			$("#authors").empty()
			
			for(i=0; i< authors.length; i++)
				add_author(authors[i]['first'], authors[i]['middle'], authors[i]['last']);
			
			autodetect_change()
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