function getApplications(action){
    let data = [];
    let table = document.getElementById('pending_applications');
    let input = table.querySelectorAll('input[type="checkbox"]');
    $.each(input, function (i, e) {
        if (e.checked) {
            data.push(e["value"]);
        }
    });
    console.log(data);
    if (data.length === 0){
        alert(`Please select applications to ${action} from the list below!`)
    } else {
        let url = `/unamhe/${action}-applications/${data.join("|")}/`;
        doAjaxProcess(url, 'GET').done(function (data) {
            location.href = '/unamhe/sponsor-applications';
        }).fail(function (e) {})
    }
}


function doAjaxProcess(url, method, json_form=null){
    let request = {
        url: url,
        type:method,
    }

    if (method === 'POST'){
        let post = {
            data: json_form,
            contentType: 'application/x-www-form-urlencoded',
        }
        Object.assign(request, post);
    }

    return $.ajax(
        request
    );
}

