//добавить автора
function addaut(obj)
{
	if (! $("input", $(obj).parent()).attr('disabled'))
		add_author($('input:eq(0)', $(obj).parent()).val(), $('input:eq(1)', $(obj).parent()).val(), $('input:eq(2)', $(obj).parent()).val())
}
	
//удалить автора
function remaut(obj)
{
	if (! $("input", $(obj).parent()).attr('disabled'))
		if( $("#authors tr").length > 1)
			$(obj).parent().remove();
}
	
//добавление самой первой строки автора
function add_author(first, middle, last)
{
	id = 0
	if ($("#authors tr:last input").attr('name'))
		id = 1 + parseInt($("#authors tr:last input").attr('name').split('|')[1]);
		
	$("#authors").append("<tr><td>Author:</td><td><input class='descr' type='text' name='author_first|" + id +"'  size='20' maxlength='256' value = '" + first + "'/><br /><label style='font-size:x-small'>first name</label></td><td><input class='descr' type='text' name='author_middle|" + id +"' size='20' maxlength='256' value = '" + middle + "' /><br /><label style='font-size:x-small'>middle name</label></td><td><input class='descr' type='text' name='author_last|" + id +"' size='20' maxlength='256' value = '" + last + "' /><br /><label style='font-size:x-small'>last name</label></td><td id ='addaut' onClick = 'addaut(this)'>[+]<br />&nbsp;</td><td id ='remaut' onClick = 'remaut(this)'>[-]<br />&nbsp;</td></tr>")
		
}

//сделать поля ввода неаквтивными
function work_disable()
{
	$(".descr").attr({disabled: true});
	$("form input").attr({disabled: true});
}
	
//сделать поля ввода автивными
function work_enable()
{
	$(".descr").attr({disabled: false});
	$("form input").attr({disabled: false});
	autodetect_change();
	change_ext_features_state();
}

//енаблит, дасаблит поля в дескрипшене
function autodetect_change()
{
	if( $("#descr_div #autodetect").attr('checked') )
		$(".descr").attr({disabled: true})
	else
		$(".descr").attr({disabled: false})
}


//скрыть дескрипшн
function description_hide()
{
	$("#descr_div").hide("fast", function(){
		$('#descr_off').hide();
		$('#descr_on').show();
	});
}

//показать дескрипшн
function description_show()
{
	$("#descr_div").show("fast", function(){
		$('#descr_on').hide();
		$('#descr_off').show();
	});
}

//показать расширенные параметры
function adv_params_show()
{
	$("#adv_params").show("fast", function(){
		$("#adv_params_on").hide();
		$("#adv_params_off").show();
	});
}

//скрыть расширенные параметры
function adv_params_hide()
{
	$("#adv_params").hide("fast", function(){
		$("#adv_params_off").hide();
		$("#adv_params_on").show();
	});
}

function extend_urls()
{
	var urls = $("#urls > #url_row > #url")
	for(i=0; i < urls.length; i++)
	{	
		old_url = urls[i].value;
		if (old_url != '')
			if(old_url.indexOf("://") == -1)
			{
				new_url = "http://" + old_url;
				urls[i].value = new_url;
			}
	}
}

//добавить урл
function add_url(source)
{
	if (! $("input", $(source).parent()).attr('disabled'))
	{
		if( $("#urls > #url_row").length < 10)
		{
			
			$(source).parent().clone(true).insertAfter($(source).parent())
		}
	}
}

//удалить урл
function rem_url(target)
{
	if (! $("input", $(target).parent()).attr('disabled'))
		if( $("#urls > #url_row").length > 1)
			$(target).parent().remove();
}

//подстановка примера
function do_example()
{
	$("#urls > #url_row > #url")[0].value = $("#example_url").text();
	
}

//функция, которая дисаблит, энаблит контролы, отвечающие за включение-выключение дополнительных фич нового движка
function change_ext_features_state(){
	if( $("#old_h2fb2").attr('checked') )
	{
		$("#tab").attr({disabled: true})
		$("#tab").attr({checked: false})
				
		$("#pre").attr({disabled: true})
		$("#pre").attr({checked: false})
	}
	else
	{
		$("#tab").attr({disabled: false})
				
		$("#pre").attr({disabled: false})
	}
}

var a1 = $('<img>').attr('src','/misc/done.gif');
var a2 = $('<img>').attr('src','/misc/blank.gif');
var a3 = $('<img>').attr('src','/misc/progress.gif');
var a4 = $('<img>').attr('src','/misc/progress_big.gif');


//когда DOM загрузился, можно продолжить
$(document).ready(function(){
	
	
	$("#descr_div").hide();
	$(".error").hide()
	$(".result").hide()
	$(".progres").hide()
	$(".try").hide()
	$(".cancel").hide()
	
	add_author('', '', '')
	
	autodetect_change()

	//открыть, закрыть форму с дескрипшеном
	$("#descr_off").click(function(){
		description_hide()
	});
	$("#descr_on").click(function(){
		description_show()
	});
	
	//показать/скрыть расширенные параметры
	$("#adv_params_on").click(function(){
		adv_params_show();
	});
	$("#adv_params_off").click(function(){
		adv_params_hide();
	});
	
	//добавить урл
	$("#addurl").click(function(){
		add_url(this);
	});
	
	//убрать урл
	$("#remurl").click(function(){
		rem_url(this);
	});
	
	//чек-анчек контрола старого движка
	$("#old_h2fb2").change(function(){
		change_ext_features_state()
	});
	
	//изменение контрола автодетекта дескрипшена
	$("#autodetect").change(function(){
		autodetect_change()
	});
	
	//действие при клике на пример
	$("#example_url").click(function(){
		do_example();
	});
	
	
	$("#cancel").click(
		function(){
			CANCEL = true;
			do_cancel()
		}
	);
	
	$("form").submit(function(){
			extend_urls();
			$(".error").html('');
			$(".error").hide();
			$(".try").html('');
			$(".try").hide();
			$(".result").html('');
			$(".result").hide('');
			$(".cancel").show('');
			$(".progres").show('');
			$(".progres").html('<center><img src = "/misc/progress_big.gif" /></center>');
			
			CANCEL = false;
			
			$(".error").ajaxError(function(event, request, settings){
				$(this).html("<li>Ajax error requesting page " + settings.url + "</li>");
				$(".progres").hide('');
				$(".error").show();
			});
			get_ans();
			return false
		}
	)


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
			
			var authors = obj.descr['authors'];
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