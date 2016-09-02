/**
 * @author Tobias Krauthoff
 * @email krauthoff@cs.uni-duesseldorf.de
 */

var socket = undefined;
const port = 5001;

$(document).ready(function() {
	
	// try to connect
	try {
		doConnect();
	} catch (e) {
		console.log('Error on connect: ' + e.message);
	}
	
	// delete subscription on page unload events
	$(window).bind('beforeunload',function(){
		if (socket)
			socket.emit('remove_name', $('#' + headerNicknameId).text());
	});
	
});

/**
 * Connects the sockets and enables publishing
 */
function doConnect(){
	// switch between a local (http) and a global (https) mode
	var dict = {query: 'nickname=' + $('#' + headerNicknameId).text(), secure: true};
	var address =  'http://localhost:';
	if (mainpage.indexOf('localhost') == -1) {
		address = 'https://dbas.cs.uni-duesseldorf.de:';
		dict['secure'] = true;
	}
	socket = io.connect(address + port, dict);
	
	socket.on('publish', function(data){
		doPublish(data);
	});
	
	socket.on('recent_review', function(data){
		doRecentReview(data);
	});
	
	console.log('Socket.io connected.');
	enableTesting();
}

/**
 * Differentiate between the differen publication types
 * @param data dict
 */
function doPublish(data){
	if (data.type == 'success') {	        handleMessage(data, 'Huray!', doSuccess);
	} else if (data.type == 'warning') {	handleMessage(data, 'Uhh!', doWarning);
	} else if (data.type == 'info') {	    handleMessage(data, 'Ooh!', doInfo);
	} else {                                setGlobalInfoHandler('Mhhh!', data.msg);
	}
	console.log('publish ' + data.type + ' ' + data.msg);
}

/**
 *
 * @param data
 * @param intro
 * @param func
 */
function handleMessage(data, intro, func){
	var msg = 'url' in data ? '<a target="_blank" href="' + data.url + '">' + data.msg + '</a>' : data.msg;
	func(intro, msg);
	if ('increase_counter' in data) {
		incrementCounter($('#' + headerBadgeCountNotificationsId));
		incrementCounter($('#' + menuBadgeCountNotificationsId));
	}
}

/**
 * Calls setGlobalSuccessHandler with given params
 * @param intro String
 * @param msg String
 */
function doSuccess(intro, msg){
	setGlobalSuccessHandler(intro, msg);
}

/**
 * Calls setGlobalErrorHandler with given params
 * @param intro String
 * @param msg String
 */
function doWarning(intro, msg){
	setGlobalErrorHandler(intro, msg);
}

/**
 * Calls setGlobalInfoHandler with given params
 * @param intro String
 * @param msg String
 */
function doInfo(intro, msg){
	setGlobalInfoHandler(intro, msg);
}

/**
 *
 * @param data
 */
function doRecentReview(data){
	if (window.location.href.indexOf('review') == -1)
		return;
	
	var queue = $('#' + data.queue);
	if (queue.length != 0){
		// just push, if given user is not the last reviwer
		var last_reviewer = $('#' + data.queue + ' a:first-child');
		var last_reviewer_name = last_reviewer.attr('title');
		var last_reviewer_gravatar = last_reviewer.find('img').attr('src');
		if (last_reviewer_name != data.reviewer_name && last_reviewer_gravatar != data.img_url + '?d=wavatar&s=40') {
			console.log(data.reviewer_name + ' is a new reviewer');
			$('#' + data.queue + ' a:last-child').remove();
			var link = $('<a>').attr('target', '_blank').attr('title', data.reviewer_name).attr('href', '/user/' + data.reviewer_name);
			var img = $('<img>').attr('src', data.img_url + '?d=wavatar&s=40').css('width', '40px').css('margin', '2px');
			link.append(img);
			queue.prepend(link);
		} else {
			console.log(data.reviewer_name + ' is already in the list');
		}
	}
}

/**
 * Increments the text counter in given element
 * @param element DOM-Element
 */
function incrementCounter(element){
	element.text(parseInt(element.text()) + 1);
}

/**
 * Enables testing for the main page
 */
function enableTesting(){
	socket.on('connect', function() {
		var field = $('#socketStatus');
		if (field)
			field.text('Connected!');
	});

    socket.on('disconnect', function() {
		var field = $('#socketStatus');
		if (field)
			field.text('Disconnected!');
    });

    socket.on('pong', function(ms){
    	var testCount = $('#testCount');
		var latency = $('#latency');
		if (latency)
			latency.text(ms + 'ms');
	    if (testCount)
			testCount.text(parseInt(testCount.text()) + 1);
    });
	
	setInterval(function(){
        socket.emit('ping', {});
	}, 100);
	
	socket.on('push_test', function(data) {
		if (data.type == 'success') {	        handleMessage(data, 'TEST!', doSuccess);
		} else if (data.type == 'warning') {	handleMessage(data, 'TEST!', doWarning);
		} else if (data.type == 'info') {	    handleMessage(data, 'TEST!', doInfo);
		} else {                                console.log('unknown test type');
		}
	});
	
	// getting socket id from server
	socket.on('push_socketid', function(id){
		var field = $('#socketioId');
		
		if (field)
			field.text(id);
	});
	
	$('#test_success_btn,#test_danger_btn,#test_info_btn').click(function(){
		socket.emit('push_test', $(this).attr('data-type'), $('#test-input').val());
	});
}
