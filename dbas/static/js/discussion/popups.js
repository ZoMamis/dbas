/**
 * @author Tobias Krauthoff
 * @email krauthoff@cs.uni-duesseldorf.de
 */

function PopupHandler() {
	
	/**
	 * Opens the edit statements popup
	 * @param statements_uids
	 */
	this.showEditStatementsPopup = function (statements_uids) {
		const input_space = $('#' + popupEditStatementInputSpaceId);
		const ajaxHandler = new AjaxDiscussionHandler();
		$('#' + popupEditStatementId).modal('show');
		input_space.empty();
		$('#' + popupEditStatementLogfileSpaceId).empty();
		$('#' + proposalEditListGroupId).empty();
		$('#' + popupEditStatementErrorDescriptionId).text('');
		$('#' + popupEditStatementSuccessDescriptionId).text('');
		$('#' + popupEditStatementInfoDescriptionId).text('');
		$('#' + popupEditStatementSubmitButtonId).addClass('disabled');
		
		// getting logfile
		ajaxHandler.getLogfileForStatements(statements_uids);
		
		// add inputs
		$.each(statements_uids, function (index, value) {
			const statement = $('#' + value).text().trim().replace(/\s+/g, ' ');
			
			const group = $('<div>').addClass('form-group');
			const outerInputGroup = $('<div>').addClass('col-md-12').addClass('input-group');
			const innerInputGroup = $('<div>').addClass('input-group-addon');
			const group_icon = $('<i>').addClass('fa').addClass('fa-2x').addClass('fa-file-text-o').attr('aria-hidden', '"true"');
			const input = $('<input>')
				.addClass('form-control')
				.attr('id', 'popup-edit-statement-input-' + index)
				.attr('name', 'popup-edit-statement-input-' + index)
				.attr('type', text)
				.attr('placeholder', statement)
				.attr('data-statement-uid', value)
				.val(statement);
			
			innerInputGroup.append(group_icon);
			outerInputGroup.append(innerInputGroup).append(input);
			group.append(outerInputGroup);
			input_space.append(group);
		});

		// gui for editing statements
		const _l = function(s1, s2){
			return levensthein(s1, s2);
		};
		input_space.find('input').each(function () {
			$(this).keyup(function () {
				const oem = $(this).attr('placeholder');
				const now = $(this).val();
				const id = $(this).attr('id');
				const statement_uid = $(this).data('statement-uid');
				
				// reduce noise
				const levensthein = _l(oem, now);
				$('#' + popupEditStatementInfoDescriptionId).text(levensthein < 5 ? _t_discussion(pleaseEditAtLeast) : '');
				
				if (now && oem && now.toLowerCase() == oem.toLowerCase() && levensthein < 5)
					$('#' + popupEditStatementSubmitButtonId).addClass('disabled');
				else
					$('#' + popupEditStatementSubmitButtonId).removeClass('disabled');
				
				
				setTimeout(function () {
					ajaxHandler.fuzzySearch(now,
						id,
						fuzzy_statement_popup,
						statement_uid);
				}, 200);
			})
		});
	};
	
	/**
	 * Clears the edit statement popup
	 */
	this.hideAndClearEditStatementsPopup = function () {
		$('#' + popupEditStatementId).modal('hide');
		$('#' + popupEditStatementLogfileSpaceId).empty();
		$('#' + popupEditStatementInputSpaceId).empty();
	};
	
	/**
	 * Display url sharing popup
	 */
	this.showUrlSharingPopup = function () {
		$('#' + popupUrlSharingId).modal('show');
		new AjaxDiscussionHandler().getShortenUrl(window.location);
		//$('#' + popupUrlSharingInputId).val(window.location);
	};
	
	/**
	 * Display url sharing popup
	 */
	this.showGeneratePasswordPopup = function () {
		$('#' + popupGeneratePasswordId).modal('show');
		$('#' + popupGeneratePasswordCloseButtonId).click(function () {
			$('#' + popupGeneratePasswordId).modal('hide');
		});
		$('#' + popupLoginCloseButton).click(function () {
			$('#' + popupGeneratePasswordId).modal('hide');
		});
	};
	
	/**
	 * Displays add topic plugin
	 *
	 * @param callbackFunctionOnDone
	 */
	this.showAddTopicPopup = function (callbackFunctionOnDone) {
		$('#popup-add-topic').modal('show');
		$('#popup-add-topic-accept-btn').click(function () {
			const info = $('#popup-add-topic-info-input').val();
			const title = $('#popup-add-topic-title-input').val();
			const lang = $('#popup-add-topic-lang-input').find('input[type="radio"]:checked').attr('id');
			new AjaxDiscussionHandler().sendNewIssue(info, title, lang, callbackFunctionOnDone);
		});
		$('#popup-add-topic-refuse-btn').click(function () {
			$('#popup-add-topic').modal('hide');
		});
	};
	
	/**
	 * Display popup for flagging statements
	 *
	 * @param uid of the argument
	 * @param is_argument is true if the statement is a complete argument
	 */
	this.showFlagStatementPopup = function (uid, is_argument) {
		const popup = $('#popup-flag-statement');
		if (is_argument) {
			popup.find('.statement_text').hide();
			popup.find('.argument_text').show();
		} else {
			popup.find('.statement_text').show();
			popup.find('.argument_text').hide();
		}
		popup.modal('show');
		popup.on('hide.bs.modal', function () {
			popup.find('input').off('click').unbind('click');
		});
		popup.find('input').click(function () {
			const reason = $(this).attr('value');
			new AjaxMainHandler().ajaxFlagArgumentOrStatement(uid, reason, is_argument);
			popup.find('input').prop('checked', false);
			popup.modal('hide');
		});
	};
	
	/**
	 * Display popup for flagging arguments
	 *
	 * @param uid of the argument
	 */
	this.showFlagArgumentPopup = function (uid) {
		const popup = $('#popup-flag-argument');
		// var text = $('.triangle-l:last-child .triangle-content').text();
		
		// clean text
		// cut the part after <br><br>
		let text = $('.triangle-l:last-child .triangle-content').html();
		text = text.substr(0, text.indexOf('<br>'));
		
		// cut the author
		const tmp = text.indexOf('</a>');
		if (tmp != -1) {
			const a = $('.triangle-l:last-child .triangle-content a').attr('title');
			text = a + ' ' + text.substr(tmp + '</a>'.length);
		}
			
		// cut all spans
		while (text.indexOf('</span>') != -1)
			text = text.replace('</span>', '');
		while (text.indexOf('<span') != -1)
			text = text.substr(0, text.indexOf('<span')) + text.substr(text.indexOf('>') + 1);
		
		$('#popup-flag-argument-text').text(text);
		popup.modal('show');
		popup.on('hide.bs.modal', function () {
			popup.find('input').off('click').unbind('click');
		});
		popup.find('input').click(function () {
			if ($(this).data('special') === 'undercut') {
				$('#item_undercut').click();
				
			} else if ($(this).data('special') === 'argument') {
				$('#popup-flag-statement-text').text(text);
				new PopupHandler().showFlagStatementPopup(uid, true);
				
			} else {
				new PopupHandler().showFlagStatementPopup($(this).attr('id'), false);
				$('#popup-flag-statement-text').text($(this).next().find('em').text());
			}
			popup.find('input').prop('checked', false);
			popup.modal('hide');
		});
		
		// pretty stuff on hovering
		popup.find('input').each(function () {
			if ($(this).data('special') === '') {
				const current = $(this).next().find('em').text().trim();
				$(this).hover(function () {
					const modded_text = text.replace(new RegExp("(" + (current + '').replace(/([\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:])/g, "\\$1") + ")", 'gi'), "<span class='text-primary'>$1</span>");
					$('#popup-flag-argument-text').html(modded_text);
					$(this).next().find('em').html("<span class='text-primary'>" + current + "</span>");
				}, function () {
					$('#popup-flag-argument-text').text(text);
					$(this).next().find('em').html(current);
				});
			}
		});
		popup.find('label').each(function () {
			if ($(this).prev().data('special') === '') {
				const current = $(this).find('em').text().trim();
				$(this).hover(function () {
					const modded_text = text.replace(new RegExp("(" + (current + '').replace(/([\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:])/g, "\\$1") + ")", 'gi'), "<span class='text-primary'>$1</span>");
					$('#popup-flag-argument-text').html(modded_text);
					$(this).find('em').html("<span class='text-primary'>" + current + "</span>");
				}, function () {
					$('#popup-flag-argument-text').text(text);
					$(this).find('em').text(current);
				});
			}
		});
	};
	
	/**
	 * Popup for revoking content
	 *
	 * @param uid of the element
	 * @param is_argument boolean
	 */
	this.showDeleteContentPopup = function (uid, is_argument) {
		const popup = $('#popup-delete-content');
		popup.modal('show');
		
		$('#popup-delete-content-submit').click(function () {
			new AjaxDiscussionHandler().revokeContent(uid, is_argument);
			popup.modal('hide');
		});
		
		$('#popup-delete-content-close').click(function () {
			popup.modal('hide');
		});
	};
	
	/**
	 * Popup for managing the references
	 *
	 * @param data in json-format
	 */
	this.showReferencesPopup = function (data) {
		const popup = $('#' + popupReferences);
		const references_body = $('#popup-references-body');
		const references_body_add = $('#popup-references-body-add').hide();
		const add_button = $('#popup-reference-add-btn');
		const send_button = $('#popup-reference-send-btn');
		const dropdown = $('#popup-references-cite-dropdown');
		const dropdown_list = $('#popup-references-cite-dropdown-list');
		const reference_text = $('#popup-references-add-text');
		const reference_source = $('#popup-references-add-source');
		const info_text = $('#choose_reference_text');
		
		dropdown.hide();
		info_text.hide();
		popup.modal('show');
		dropdown_list.empty();
		references_body.empty();
		add_button.show();
		send_button.prop('disabled', true);
		reference_text.val('');
		reference_source.val('');
		
		add_button.off('click').click(function () {
			add_button.hide();
			references_body_add.fadeIn();
			//send_button.prop('disabled', false);
			if (dropdown_list.find('li').length < 2) {
				dropdown.hide();
				info_text.hide();
			} else {
				dropdown.show();
				info_text.show();
			}
			send_button.prop('disabled', false);
		});
		
		send_button.off('click').click(function () {
			const uid = $(this).data('id');
			const reference = reference_text.val();
			const ref_source = reference_source.val();
			new AjaxReferenceHandler().setReference(uid, reference, ref_source);
		});
		
		this.createReferencesPopupBody(data);
		
		if (references_body.children().length == 0) {
			references_body.append($('<p>').addClass('lead').text(_t_discussion(noReferencesButYouCanAdd)));
			add_button.hide();
			send_button.prop('disabled', false);
			references_body_add.fadeIn();
			if (dropdown_list.find('li').length < 2) {
				dropdown.hide();
				info_text.hide();
			} else {
				dropdown.show();
				info_text.show();
			}
		}
	};
	
	/**
	 * Creates the body of the reference popup
	 *
	 * @param data in json-format
	 */
	this.createReferencesPopupBody = function (data) {
		const popup = $('#' + popupReferences);
		const references_body = $('#popup-references-body');
		const send_button = $('#popup-reference-send-btn');
		const dropdown = $('#popup-references-cite-dropdown');
		const dropdown_list = $('#popup-references-cite-dropdown-list');
		const dropdown_title = $('#popup-references-cite-dropdown-title');
		
		// data is an dictionary with all statement uid's as key
		// the value of every key is an array with dictionaries for every reference
		$.each(data.data, function (statement_uid, array) {
			const statements_div = $('<div>');
			let text = '';
			// build a callout for every reference
			array.forEach(function (dict) {
				text = dict.statement_text;
				const author = $('<a>').attr({'href': dict.author.link, 'target': '_blank'}).addClass('pull-right')
					.append($('<span>').text(dict.author.name).css('padding-right', '0.5em'))
					.append($('<img>').addClass('img-circle').attr('src', dict.author.img));
				
				const link = $('<a>').attr({
					'href': dict.host + dict.path,
					'target': '_blank'
				}).text('(' + dict.host + dict.path + ')');
				const span = $('<span>').text(dict.reference + ' ');
				
				const label = $('<label>').addClass('bs-callout').addClass('bs-callout-primary');
				const body = $('<p>').append(span).append(link).append(author);
				label.append(body);
				
				statements_div.append(label);
			});
			// add the statemet itself
			const glqq = $.parseHTML('<i class="fa fa-quote-left" aria-hidden="true" style="padding: 0.5em; font-size: 12px;"></i>');
			const grqq = $.parseHTML('<i class="fa fa-quote-right" aria-hidden="true" style="padding: 0.5em; font-size: 12px;"></i>');
			const statement = $('<span>').addClass('lead').text(text);
			const wrapper = $('<p>').append(glqq).append(statement).append(grqq);
			
			// add elements for the dropdown
			if (text.length > 0) {
				references_body.append(wrapper.append(statements_div));
			} else {
				text = data.text[statement_uid];
			}
			console.log(text);
			const tmp = $('<a>').attr('href', '#').attr('data-id', statement_uid).text(text).click(function () {
				// set text, remove popup
				dropdown_title.text($(this).text()).parent().attr('aria-expanded', false);
				dropdown.removeClass('open');
				send_button.attr('data-id', statement_uid);
			});
			dropdown_list.append($('<li>').append(tmp));
			
			// default id
			send_button.attr('data-id', statement_uid);
		});
	};
	
	/**
	 * Closes the popup and deletes all of its content
	 */
	this.hideAndClearUrlSharingPopup = function () {
		$('#' + popupUrlSharingId).modal('hide');
		$('#' + popupUrlSharingInputId).val('');
	};
}