function approveEvent(rowid) {
    const request = new XMLHttpRequest();
    request.open('POST', '/approve_event');
    request.onload = function() {
        window.location.reload(true);
    }
    const form = new FormData();
    form.append('rowid', rowid);
    request.send(form);
    return false;
}

function refresh() {
    const request = new XMLHttpRequest();
    request.open('POST', '/refresh');
    request.onload = function() {
        window.location.reload(true);
    }
    request.send()
    return false;
}

function declineEvent(rowid) {
    const request = new XMLHttpRequest();
    request.open('POST', '/decline_event');
    request.onload = function() {
        window.location.reload(true);
    }
    const form = new FormData();
    form.append('rowid', rowid);
    request.send(form);
    return false;
}

$(document).ready(function() {
    // Configure/customize these variables.
    var showChar = 200;  // How many characters are shown by default
    var ellipsestext = "...";
    var moretext = "Раскрыть +";
    var lesstext = "Спрятать -";


    $('.more').each(function() {
        var content = $(this).html();

        if(content.length > showChar) {

            var c = content.substr(0, showChar);
            var h = content.substr(showChar, content.length - showChar);

            var html = c + '<span class="moreellipses">' + ellipsestext+ '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';

            $(this).html(html);
        }

    });

    $(".morelink").click(function(){
        if($(this).hasClass("less")) {
            $(this).removeClass("less");
            $(this).html(moretext);
        } else {
            $(this).addClass("less");
            $(this).html(lesstext);
        }
        $(this).parent().prev().toggle();
        $(this).prev().toggle();
        return false;
    });
});