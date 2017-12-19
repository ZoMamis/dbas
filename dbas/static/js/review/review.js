/**
 * @author Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de>
 */

function Review() {
    'use strict';

	var sec = parseInt($('#request-lock').data('lock_sec'));
	var countdown;
	var _this = this;
	var countdown_min = parseInt(sec/60);
	var countdown_sec = sec - countdown_min * 60;

	/**
	 *
	 */
	this.doOptimizationAck = function(review_uid) {
		var container = $('#optimization-container');
		var opti_ack = $('#opti_ack');
		var send_edit = $('#send_edit');

		send_edit.addClass('disabled');
		$('#close-optimization-container').click(function(){
			container.hide();
			opti_ack.removeClass('disabled');
			_this.stopCountdown();
			send_edit.addClass('disabled');
			new AjaxReviewHandler().un_lockOptimizationReview(review_uid, false, _this);
		});
		new AjaxReviewHandler().un_lockOptimizationReview(review_uid, true, _this);

		// for each input in table
		$.each(container.find('table').find('input'), function(){
			$(this).focus(function(){
				if ($(this).val().length === 0){
					$(this).val($(this).attr('placeholder'));
					$('#send_edit').removeClass('disabled');
				}
			});
		});
	};

	/**
	 *
	 */
	this.sendOptimization = function(){
		var edit_array = [];
		// getting all edited values
		$.each($('#argument-part-table').find('input'), function(){
			if ($(this).val().length > 0 && $(this).val() !== $(this).attr('placeholder')) {
				edit_array.push({
					statement: $(this).data('statement'),
					type: $(this).data('type'),
					argument: $(this).data('argument'),
					val: $(this).val()
				});
			}
		});

		if (edit_array.length > 0){
			var id = $('#send_edit').data('id');
			new AjaxReviewHandler().reviewOptimizationArgument(true, id, edit_array);
		} else {
			setGlobalInfoHandler('Ohh!', _t(noEditsInOptimization));
		}
	};

	/**
	 *
	 */
	this.doDeleteAck = function(review_uid) {
		new AjaxReviewHandler().reviewDeleteArgument(true, review_uid);
	};

	/**
	 *
	 */
	this.doDeleteNack = function(review_uid) {
		new AjaxReviewHandler().reviewDeleteArgument(false, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doEditAck = function(review_uid){
		new AjaxReviewHandler().reviewEditArgument(true, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doEditNack = function(review_uid){
		new AjaxReviewHandler().reviewEditArgument(false, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doDuplicateAck = function(review_uid){
		new AjaxReviewHandler().reviewDuplicateStatement(true, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doDuplicateNack = function(review_uid){
		new AjaxReviewHandler().reviewDuplicateStatement(false, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doMergeAck = function(review_uid){
		new AjaxReviewHandler().reviewMergeStatement(true, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doMergeNack = function(review_uid){
		new AjaxReviewHandler().reviewMergeStatement(false, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doSplitAck = function(review_uid){
		new AjaxReviewHandler().reviewSplitStatement(true, review_uid);
	};

	/**
	 *
	 * @param review_uid
	 */
	this.doSplitNack = function(review_uid){
		new AjaxReviewHandler().reviewSplitStatement(false, review_uid);
	};

	/**
	 *
	 */
	this.startCountdown = function(){
		var mm = $('#countdown_timer_min');
		var ss = $('#countdown_timer_sec');
		var point = $('#countdown_timer_point');
		mm.text(countdown_min).removeClass('text-danger').addClass('text-info');
		ss.text(countdown_sec < 10 ? '0' + countdown_sec : countdown_sec).removeClass('text-danger').addClass('text-info');
		point.removeClass('text-danger').addClass('text-info');
		$('#request-lock-text').show();
		$('#request-not-lock-text').show();

		countdown = new Countdown({
            seconds: countdown_min * 60 + countdown_sec,  // number of seconds to count down
            onUpdateStatus: function(sec){
            	var m = parseInt(sec / 60);
	            var s = sec - m * 60;
            	mm.text(m);
            	ss.text(s < 10 ? '0' + s : s);
	            if (sec <= 60){
	            	mm.addClass('text-danger').removeClass('text-info');
	            	ss.addClass('text-danger').removeClass('text-info');
		            point.addClass('text-danger').removeClass('text-info');
	            }
            }, // callback for each second
            onCounterEnd: function(){
            	setGlobalErrorHandler(_t(ohsnap), _t(countdownEnded));
	            $('#send_edit').addClass('disabled');
				$('#request-lock-text').hide();
				$('#request-not-lock-text').show();
				var button = $('#request-lock');
				button.show();
				new AjaxReviewHandler().un_lockOptimizationReview(button.data('id'), false, undefined);
            } // final action
		});
		countdown.start();
	};

	/**
	 *
	 */
	this.stopCountdown = function(){
		if (countdown){
			countdown.stop();
		}
		var button = $('#request-lock');
		button.hide();
		new AjaxReviewHandler().un_lockOptimizationReview(button.data('id'), false, undefined);
	};

	/**
	 *
	 * @param only_unlock
	 */
	this.reloadPageAndUnlockData = function (only_unlock){
		new AjaxReviewHandler().un_lockOptimizationReview($('#review-id').data('id'), false, undefined);
		if (! only_unlock) {
			location.reload(true);
		}
	};
}
