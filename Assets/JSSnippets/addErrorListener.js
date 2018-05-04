
if(document.readyState === "complete") {
	add_error_listener();
}

else {
	window.addEventListener("onload", function () {add_error_listener();}, false);
}


if (typeof selenium_error_log=== 'undefined') {
    selenium_error_log = [];
}


function add_error_listener(){


	window.onerror=function(msg, url, linenumber){
		selenium_error_log.push({msg:msg,url:url,linenumber:linenumber});
    };

	return "Now Listening";
}
