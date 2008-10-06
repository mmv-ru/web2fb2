//глобалная переменная - останавливать выполнение циклических запросов или нет
CANCEL_WORK = false;

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

//для всех URL добавить http://, если надо
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

//предварительная загрузка картинок
function preload_images()
{
	$('<img>').attr('src','/misc/done.gif');
	$('<img>').attr('src','/misc/blank.gif');
	$('<img>').attr('src','/misc/progress.gif');
	$('<img>').attr('src','/misc/progress_mid.gif');
	$('<img>').attr('src','/misc/progress_big.gif');

}


//показываем ощибку, разрешаем управлять настройками
function viz_error(msg)
{
	$(".progres").hide();
	$(".error").show();
	$(".error").html(msg);
	$(".cancel").hide()
	$(".try").hide()
	
	work_enable();
}


//показывает рабочий процесс
function viz_work(data)
{
	
	$(".error").hide();
	$(".try").hide();
	$(".result").hide();
	
	$(".cancel").show('');
	$(".progres").show();
	$(".progres").html(data);
	work_disable()
}


//показывает результат
function viz_result(data)
{
	$(".progres").hide()
	$(".cancel").hide()
	$(".try").hide()
	$(".result").show()
	$(".result").html(data)
	work_enable();
}

//возвращает все на начало
function viz_start()
{
	
	$(".error").hide()
	$(".result").hide()
	$(".progres").hide()
	$(".try").hide()
	$(".cancel").hide()
	work_enable();
}

//показывает try again
function viz_try(data)
{
	work_disable()
	$(".error").hide()
	$(".progres").hide()
	$(".result").hide()
	$(".cancel").show()
	$(".try").show()
	$(".try").html(data)
}


//делаем ajax запрос
function get_ans()
{

	if (CANCEL_WORK) //если останавливаем - то ничего не делать
	{}
	else
	{
		
		work_enable() //включаем форму, чтоб можно было получить данные
		var str = $("#f").serialize() //получаем значения из формы и сериализуем их
		work_disable() //включаем форму, чтоб можно было получить данные

		$.ajax({
			url: "?ajax=1&" +str,
			cache: false,
			dataType: 'json',
			success: onAjaxSuccess,
			error: onAjaxError
		});
	}
}

//обработчик результата ajax запроса
//получает json данные
function onAjaxSuccess(obj)
{
	
	if(CANCEL_WORK) //если останавливаем - то ничего не делать
	{
	
	}
	else if (obj.error) //если ошибка
	{
		viz_error(obj.error);
	}
	else if(obj.result) //успешный результат
	{
		
		viz_result(obj.result)
		
		//заполнить авторов и титлы
		$('#title').val(obj.descr['title'])
		$('#genre').val(obj.descr['genre']);
		$('#lang').val(obj.descr['lang'])
		
		var authors = obj.descr['authors'];
		$("#authors").empty()
		
		for(i=0; i< authors.length; i++)
			add_author(authors[i]['first'], authors[i]['middle'], authors[i]['last']);
			
		autodetect_change(); //после заполнения авторов, надо их задесайблить

	}
	else if(obj.progres) //прогресс
	{
		viz_work(obj.progres)
		window.setTimeout(get_ans, 2000);
	}
	else if(obj.tryagain) //еще раз
	{
		viz_try(obj.tryagain);
		window.setTimeout(get_ans, 20000);
	}
	else //странная ситуация - видимо передли что-то не то
	{
		viz_error('Strange internal ajax error')
	}
}

//функция срабатывающая при ошибочном ajax запросе
function onAjaxError(event, request, settings)
{
	viz_error( "Internal ajax error");
}


//когда DOM загрузился, можно продолжить
$(document).ready(function(){
	
	preload_images();
	
	viz_start();
	
	add_author('', '', '');
	
	//после заполнения авторов - надо их задисайблить
	autodetect_change();

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
	
	//если нажать кнопку отмена
	$("#cancel").click(function(){
		CANCEL_WORK = true;
		viz_start();
	});
	
	//сабмит формы
	$("form").submit(function(){
			
			extend_urls(); //добавляем к урлам http
			
			viz_work('<center><img src = "/misc/progress_big.gif" /></center>') //показыываем прогресс
			
			CANCEL_WORK = false;
			
			get_ans();
			return false
		}
	)
});

//если есть флаг, что надо сразу запускать процесс - то засабмиттить форму
if ($("form #doit").attr('value'))
{
	$("form ").submit()
}