$(".delete-button").click(function() {
    delete_posting(this)
});

$("#register-button").click(function() {
    window.location.href = "settings/index.html"
});

// takes the delete button for a post element as an argument and gets the relevant info to send to the server
function delete_posting(del_button) {
    // get the first parent of class posting
    post_obj = $(del_button).parents(".posting");
    console.log(post_obj.attr("datetime"));
    console.log(post_obj.attr("uni"));
    to_send = {
        datetime: post_obj.attr("datetime"),
        uni: post_obj.attr("uni")
    };
    var del_request = $.ajax({
        url:"/profile/delete",
        type:"POST",
        data: JSON.stringify(to_send),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });

    del_request.done(function(result) {
            console.log("post deleted successfully!");
            hide_post(post_obj);
            window.reload();
    });

}

// removes the actual posting from the DOM
function hide_post(post_obj) {
    $(post_obj).fadeOut();
}