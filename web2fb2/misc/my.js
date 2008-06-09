$(document).ready(function(){
    
    
	a1 = $('<img>').attr('src','/misc/done.gif');
	a2 = $('<img>').attr('src','/misc/blank.gif');
	a3 = $('<img>').attr('src','/misc/progress.gif');
	a4 = $('<img>').attr('src','/misc/progress_big.gif');
	
	$("#descr_div").hide();
    $(".descr").attr({disabled: true});
    $(".error").hide()
    $(".result").hide()
    $(".progres").hide()
    
    

    $("#descr_tab").click(function(){
        $("#descr_div").slideToggle("fast")
    });
    
    $("#descr_div #autodetect").change(
        function(){
            if( $(this).attr('checked') )
                $(".descr").attr({disabled: true})
            else
                $(".descr").attr({disabled: false})
        }
    );
    
    $("form").submit(
        function(){
            $(".error").html('')
            $(".error").hide()
            $(".result").html('')
            $(".result").hide('')
            $(".progres").show('')
			$(".progres").html('<center><img src = "/misc/progress_big.gif" /></center>')
			
			$(".error").ajaxError(function(event, request, settings){
				$(this).html("<li>Ajax error requesting page " + settings.url + "</li>");
				$(".progres").hide('');
				$(".error").show();
			});
			get_ans()
			
            return false
        }
    )
    
	function get_ans()
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
	
	function onAjaxSuccess(obj)
    {
        if (obj.error)
        {
            $(".progres").hide()
			$(".error").show()
            $(".error").html(obj.error)
        }
        else if(obj.result)
        {
            $(".progres").hide()
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
			$(".progres").show()
            $(".progres").html(obj.progres)
			window.setTimeout(get_ans, 1000);
		}
		else
		{
			$(".progres").hide()
			$(".error").show()
            $(".error").html('Ajax error')
		}
    }
});