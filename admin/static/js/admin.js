/**
 * @author Tobias Krauthoff
 * @email krauthoff@cs.uni-duesseldorf.de
 */

function AdminIndex(){
	
	/**
	 *
	 */
	this.login = function () {
		var csrfToken = $('#' + hiddenCSRFTokenId).val();
		$('#admin-login-failed').hide();
		$('#admin-login-failed-message').html('');
		
		var user = $('#admin-login-user').val();
		var password = $('#admin-login-pw').val();
		var url = window.location.href;
		var keep_login = $('#admin-keep-login-box').prop('checked') ? 'true' : 'false';
		$.ajax({
			url: mainpage + 'ajax_user_login',
			type: 'GET',
			data: {
				user: user,
				password: password,
				url: url,
				keep_login: keep_login
			},
			dataType: 'json',
			async: true,
			headers: {'X-CSRF-Token': csrfToken}
		}).done(function (data) { // display fetched data
			try {
				var jsonData = $.parseJSON(data);
				if (jsonData.error.length != 0) {
					$('#admin-login-failed').show();
					$('#admin-login-failed-message').html(jsonData.error);
				} else {
					location.reload(true);
				}
			} catch(err){
				//var htmlData = $.parseHTML(data);
				var url = location.href;
				if (url.indexOf('?session_expired=true') != -1)
					url = url.substr(0, url.length - '?session_expired=true'.length);
				location.href = url;
			}
		}).fail(function () { // display error message
			setGlobalErrorHandler('Ohh', _t(requestFailed));
			location.reload();
		});
	};
}

/**
 *
 * @param _this
 * @param elements_class
 * @param text_class
 */
function activateElement(_this, elements_class, text_class){
	var element = $(_this).parents('td:first').find('.' + elements_class);
	element.removeClass('text-muted').addClass(text_class);
	element.parent().css('pointer-events', '');
}

/**
 *
 * @param _this
 * @param elements_class
 * @param text_class
 */
function deactivateElement(_this, elements_class, text_class){
	var element = $(_this).parents('td:first').find('.' + elements_class);
	element.addClass('text-muted').removeClass(text_class);
	element.parent().css('pointer-events', 'none');
}

/**
 *
 * @param parent
 */
function setAddClickEvent(parent){
	parent.find('.add').each(function(){
		$(this).click(function(){
			console.log('todo create');
		})
	});
}
/**
 *
 * @param parent
 */
function setEditClickEvent(parent){
	parent.find('.pencil').each(function(){
		$(this).click(function(){
			var uid = $(this).parents('tr:first').find('td:first').text();
			activateElement(this, 'floppy', 'text-success');
			activateElement(this, 'square', 'text-danger');
			console.log('todo edit ' + uid);
		})
	});
}
/**
 *
 * @param parent
 */
function setDeleteClickEvent(parent){
	parent.find('.trash').each(function(){
		$(this).click(function(){
			var uid = $(this).parents('tr:first').find('td:first').text();
			console.log('todo delete ' + uid);
		})
	});
}
/**
 *
 * @param parent
 */
function setSaveClickEvent(parent){
	parent.find('.floppy').each(function(){
		$(this).click(function(){
			var uid = $(this).parents('tr:first').find('td:first').text();
			deactivateElement(this, 'floppy', 'text-success');
			deactivateElement(this, 'square', 'text-danger');
			console.log('todo save ' + uid);
		})
	});
}
/**
 *
 * @param parent
 */
function setCancelClickEvent(parent){
	parent.find('.square').each(function(){
		$(this).click(function(){
			var uid = $(this).parents('tr:first').find('td:first').text();
			deactivateElement(this, 'floppy', 'text-success');
			deactivateElement(this, 'square', 'text-danger');
			console.log('todo cancel ' + uid);
		})
	});
}

// main function
$(document).ready(function () {
	$('#admin-login-button').click(function(){
		new AdminIndex().login();
	});
	
	var data = $('#data');
	
	// events for edit
	setEditClickEvent(data);
	
	// events for delete
	setCancelClickEvent(data);
	
	// events for save
	setSaveClickEvent(data);
	
	// events for cancel
	setCancelClickEvent(data);
	
	// events for add
	setAddClickEvent(data);
});
