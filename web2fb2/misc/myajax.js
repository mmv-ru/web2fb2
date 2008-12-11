
CANCEL_WORK = false; //глобалная переменная - останавливать выполнение циклических запросов или нет
IN_WORK = false; //глобалная переменная

//хнедлер события добавки автора
function add_aut(source)
{
	if( ! IN_WORK)
		if( ! $("#autodetect").attr('checked') )
			if( $("#authors > #author").length < 10)
				add_author(
					source.children('#author_first').val(),
					source.children('#author_middle').val(), 
					source.children('#author_last').val(),
					source
				);
}
	
//удалить автора
function rem_aut(target)
{
	if( ! IN_WORK)
		if( ! $("#autodetect").attr('checked') )
			if( $("#authors > #author").length > 1)
				target.remove();
}
	

//добавить автора
function add_author(first, middle, last, source)
{
	id = 0
	
	if( $("#authors > #author:last input").attr('name'))
	{
		id = 1 + parseInt($("#authors > #author:last input").attr('name').split('|')[1]);
	}
	
	
	var new_aut = $("#authors_source > #author:first").clone(true); //клонируем автора от донора
	new_aut.children('#author_first').val(first);
	new_aut.children('#author_first').attr('name', 'author_first|' + id)
	new_aut.children('#author_middle').val(middle);
	new_aut.children('#author_middle').attr('name', 'author_middle|' + id)
	new_aut.children('#author_last').val(last);
	new_aut.children('#author_last').attr('name', 'author_last|' + id)
	
	if(source)
		new_aut.insertAfter(source);
	else
		new_aut.appendTo("#authors");
}

//сделать поля ввода неаквтивными
function work_disable()
{
	IN_WORK = true;
	$("#f input,select").attr({disabled: true});
}
	
//сделать поля ввода автивными
function work_enable()
{
	IN_WORK = false;
	$("#f input, select").attr({disabled: false});
	autodetect_change();
	change_ext_features_state();
}

//енаблит, дасаблит поля в дескрипшене
function autodetect_change()
{
	if( $("#autodetect").attr('checked') )
		$("#box_descr input, select").not('#autodetect').not('#descr_applay').attr({disabled: true})
	else
		$("#box_descr input, select").not('#autodetect').not('#descr_applay').attr({disabled: false})
}


//скрыть дескрипшн
function description_hide()
{
	$("#box_descr").hide("fast", function(){
		$('#descr_off').hide();
		$('#descr_on').show();
	});
}

//показать дескрипшн
function description_show()
{
	$("#box_descr").show("fast", function(){
		$('#descr_on').hide();
		$('#descr_off').show();
	});
}

//показать расширенные параметры
function adv_params_show()
{
	$("#box_adv_params").show("fast", function(){
		$("#adv_params_on").hide();
		$("#adv_params_off").show();
	});
}

//скрыть расширенные параметры
function adv_params_hide()
{
	$("#box_adv_params").hide("fast", function(){
		$("#adv_params_off").hide();
		$("#adv_params_on").show();
	});
}

//для всех URL добавить http://, если надо
function extend_urls()
{
	$("#urls > #url_row > #url").each(function(){
		if (this.value != '')
			if(this.value.indexOf("://") == -1)
				this.value =  "http://" + this.value
	});
}

//добавить урл
function add_url(source)
{
	if( ! IN_WORK)
		if( $("#urls > #url_row").length < 10)
			source.clone(true).insertAfter(source)
}

//удалить урл
function rem_url(target)
{
	if( ! IN_WORK)
		if( $("#urls > #url_row").length > 1)
			$(target).remove();
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


//показываем ощибку, разрешаем управлять настройками
function viz_error(msg)
{
	$("#box_progres").hide();
	$("#box_error").show();
	$("#box_error").html(msg);
	$("#box_cancel").hide()
	$("#box_try").hide()
	
	work_enable();
}


//показывает рабочий процесс
function viz_work(data)
{
	
	$("#box_error").hide();
	$("#box_try").hide();
	$("#box_result").hide();
	
	$("#box_cancel").show('');
	$("#box_progres").show();
	$("#box_progres").html(data);
	work_disable()
}


//показывает результат
function viz_result(data)
{
	$("#box_progres").hide()
	$("#box_cancel").hide()
	$("#box_try").hide()
	$("#box_result").show()
	$("#box_result").html(data)
	work_enable();
}

//возвращает все на начало
function viz_start()
{
	
	$("#box_error").hide()
	$("#box_result").hide()
	$("#box_progres").hide()
	$("#box_try").hide()
	$("#box_cancel").hide()
	work_enable();
}

//показывает try again
function viz_try(data)
{
	work_disable()
	$("#box_error").hide()
	$("#box_progres").hide()
	$("#box_result").hide()
	$("#box_cancel").show()
	$("#box_try").show()
	$("#box_try").html(data)
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

	viz_start();

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
		add_url($(this).parent());
		
	});
	
	//убрать урл
	$("#remurl").click(function(){
		rem_url($(this).parent());
	});
	
	//добавить автора
	$("#addaut").click(function(){
		add_aut( $(this).parent() );
	});
	
	//добавить автора
	$("#remaut").click(function(){
		rem_aut( $(this).parent() );
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
	$("#f").submit(function(){
			
			extend_urls(); //добавляем к урлам http
			
			viz_work('<center><img src = "/misc/progress_big.gif" /></center>') //показыываем прогресс
			
			CANCEL_WORK = false;
			
			get_ans();
			return false
		}
	)
	
	//добавляем первого автора
	add_author('', '', '');
	
	//после заполнения авторов - надо их задисайблить
	autodetect_change();
});

//если есть флаг, что надо сразу запускать процесс - то засабмиттить форму
if ($("#doit").attr('value'))
{
	$("#f").submit()
}