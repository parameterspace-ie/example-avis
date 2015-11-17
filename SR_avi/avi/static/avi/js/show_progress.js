/////////////////////////////////////////////
// CSRF management via cookies
/////////////////////////////////////////////
// Get the jquery.cookie library!
function csrfSafeMethod(method){
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
	beforeSend: function(xhr, settings){
		var csrftoken = $.cookie('csrftoken');
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	}
});

/////////////////////////////////////////////
// Utility functionality
/////////////////////////////////////////////
function showSection(sectionID){
    $('#start_form').collapse("hide");
    $('#processing').collapse("hide");
    $('#finished').collapse("hide");
    setTimeout(function () {
        $(sectionID).collapse("show");
    }, 500);
}

/////////////////////////////////////////////
// Entrypoint for hooking in behavior
/////////////////////////////////////////////

function badButton(btn){
    btn.addClass("btn-danger");
    btn.attr('disabled','disabled');
}

/////////////////////////////////////////////
// Clientside functionality
/////////////////////////////////////////////

function monitorProgress(){
    var interval = null;
    requestId = window.jobID;
    interval = setInterval(function() { 
        queryProgressAndUpdate(requestId); 
    }, 500);

    function queryProgressAndUpdate(requestId){
        statusUrl = '/avi/status/' + requestId;
        $.ajax({
            type: "GET",
            url: statusUrl,
            dataType: "json",
            success: function(statusObj){
                manageProgressBar(statusObj);
                state = statusObj['state'];
                finished = statusObj['finished'];
                progressPercent = statusObj['progress'];

                $('#statusField').text(state);
                if (finished == true){
                    clearInterval(interval); 
                    
                    if (state == "FAILURE"){
                        current_task = statusObj['current_task'];
                        exception = statusObj['exception'];
                        showError(current_task, exception);
                    }

                    if (state == "SUCCESS"){
                        showJobSummary();
                    }
                }
            },
            error: function(err){
                console.log(err);
            }
        });
    }
}

function manageProgressBar(statusObj){
    state = statusObj['state'];
    finished = statusObj['finished'];
    progressPercent = statusObj['progress'];

    // Gonna be stylish
    // Set the progress bar width
    if (finished == true){
        $('#process_progress').
            width("100%").
            removeClass('progress-bar-striped').
            removeClass('active').
            removeClass('progress-bar-info');
        // States: http://celery.readthedocs.org/en/latest/reference/celery.states.html
        if (state == "FAILURE"){
            $('#process_progress').addClass('progress-bar-danger');
            $('#statusField').addClass('label-danger');
        }
        else if (state == "SUCCESS"){
            $('#process_progress').addClass('progress-bar-success');
            $('#statusField').addClass('label-success');
        }
    } else {
        $('#process_progress').width(progressPercent + "%");
        if (progressPercent > 0){
            $('#process_progress').
                addClass('progress-bar-striped').
                addClass('active');
        }
    }
}

function showError(job_id, exception){
    $('#errorInfo_error').text(exception);
    $("#errorInfo").find("div").fadeIn();
}

function showJobSummary(){
    var resultUrl = '/avi/job_summary/' + requestId;
    $.ajax({
        type: "GET",
        url: resultUrl,
        success: function(html){
            $('#result').html(html).fadeIn();
        },
        error: function(err){
            console.log(err);
        }
    });
}

monitorProgress();