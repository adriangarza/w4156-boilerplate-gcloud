function fadeIn(i, elements, duration, callback){
            if(i >= elements.length)
                $.isFunction(callback) && callback();
            else
                elements.eq(i).fadeIn(duration, function(){
                   fadeIn(i+1, elements, duration, callback);
            });
        }

fadeIn(0, $('ul li'), 250)

//called by clicking on the contracted card
function expandPost(postObject) {
    if (!$(postObject).hasClass("expanded")) {
        contractAll($("#post-container"));
        $(postObject).toggleClass('expanded');
        $(postObject).find('.post-description').slideToggle(150);
        $(postObject).find('.panel-hidden').slideToggle(150);
        $(postObject).find('.expander').fadeToggle().toggleClass('flipped');
        //a dummy class just so jquery knows which list element has been expanded
    }
}

//called by clicking the up arrow
function contractPost(contractorButton) {
    var postObject = $(contractorButton.closest(".posting"));
    if (postObject.hasClass("expanded")){
        $(postObject).find('.post-description').slideToggle(150);
        $(postObject).find('.panel-hidden').slideToggle(150);
        $(postObject).find('.expander').toggleClass('flipped').fadeToggle();
        //a dummy class just so jquery knows which list element has been expanded
        $(postObject).toggleClass('expanded');
    }
}

function contractAll(domList) {
    contractPost($(domList).find(".posting.expanded"))
}

function sendRequest(statusButton, status){
    $.ajax({
      type: "POST",
      url: "/post/update",
      data: {id: $(statusButton).attr("list_id") , stat: status}
    });
}

$(document).ready(function() {
    //a hack to let the expander also expand the parent on click
    $(".expander").click(function(e) {
        e.stopPropagation();
    });
})