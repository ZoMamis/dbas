/**
 * @author Tobias Krauthoff
 * @email krauthoff@cs.uni-duesseldorf.de
 * @copyright Krauthoff 2015
 */

/**
 * ID's
 * @type {string}
 */
var addReasonButtonId 							= 'add-reason';
var addPositionButtonId 						= 'add-position';
var addStatementContainerId 					= 'add-statement-container';
var addStatementContainerMainInputId 			= 'add-statement-container-main-input';
var addPremiseContainerId 					    = 'add-premise-container';
var addPremiseContainerMainInputId 			    = 'add-premise-container-main-input';
var addProTextareaId 							= 'add-pro-textarea';
var addConTextareaId 							= 'add-con-textarea';
var adminsSpaceForUsersId 						= 'admins-space-users';
var adminsSpaceForAttacksId 					= 'admins-space-attacks';
var addStatementErrorContainer 					= 'add-statement-error-container';
var addStatementErrorMsg 						= 'add-statement-error-msg';
var addPremiseErrorContainer 					= 'add-premise-error-container';
var addPremiseErrorMsg 						    = 'add-premise-error-msg';
var argumentBloggingSidebarId 					= 'argument-blogging-sidebar';
var contactSubmitButtonId						= 'contact-submit';
var closeStatementContainerId 					= 'close-statement-container';
var closePremiseContainerId 					= 'close-premise-container';
var closeIslandViewContainerId 					= 'close-island-view-container';
var closeGraphViewContainerId 					= 'close-graph-view-container';
var contactLink 								= 'contact-link';
var contentLink 								= 'content-link';
var conPositionColumnId 						= 'con-position-column';
var conPositionTextareaId 						= 'con-textareas';
var conIslandId 								= 'con-island';
var conTextareaPremisegroupCheckboxId 			= 'con-textarea-premisegroup-checkbox';
var contactOnErrorId 							= 'contact_on_error';
var deleteTrackButtonId 						= 'delete-track';
var deleteHistoryButtonId 						= 'delete-history';
var discussionsDescriptionId 					= 'discussions-header';
var discussionAttackSpaceId 					= 'discussions-attack-space';
var discussionAttackDescriptionId 				= 'discussions-attack-description';
var discussionStartToggleButtonId 				= 'discussion-attack-toggle-start';
var discussionContainerId 						= 'discussion-container';
var discussionEndStepBack 						= 'discussionEndStepBack';
var discussionEndRestart 						= 'discussionEndRestart';
var discussionSpaceId 							= 'discussions-space';
var discussionFailureRowId 						= 'discussion-failure-row';
var discussionFailureMsgId 						= 'discussion-failure-msg';
var displayStyleIconGuidedId                    = 'display-style-icon-guided-img';
var displayStyleIconIslandId                    = 'display-style-icon-island-img';
var displayStyleIconExpertId                    = 'display-style-icon-expert-img';
var discussionErrorDescriptionId 				= 'discussion-error-description';
var discussionErrorDescriptionSpaceId 			= 'discussion-error-description-space';
var discussionSuccessDescriptionId 				= 'discussion-success-description';
var discussionSuccessDescriptionSpaceId			= 'discussion-success-description-space';
var editStatementButtonId 						= 'edit-statement';
var forgotPasswordText 							= 'forgot-password-text';
var popupLoginEmailInputId 						= 'email-input';
var generatePasswordBodyId 						= 'generate-password-body';
var graphViewContainerId 						= 'graph-view-container';
var graphViewContainerSpaceId 					= 'graph-view-container-space';
var headingProPositionTextId 					= 'heading-pro-positions';
var headingConPositionTextId 					= 'heading-contra-positions';
var hiddenCSRFTokenId 							= 'hidden_csrf_token';
var historyTableSuccessId 						= 'history-table-success';
var historyTableFailureId 						= 'history-table-failure';
var historyTableSpaceId 						= 'history-table-space';
var historyFailureMessageId 					= 'history-failure-msg';
var historySuccessMessageId 					= 'history-success-msg';
var insertStatementForm 						= 'insert-statement-form';
var islandViewContainerId 						= 'island-view-container';
var islandViewContainerSpaceId 					= 'island-view-container-space';
var issueDropdownButtonID						= 'issue-dropdown';
var issueDropdownTextID					    	= 'issue-dropdown-text';
var issueDropdownListID							= 'dropdown-issue-list';
var issueDateId									= 'issue-date';
var issueCountId 								= 'issue-count';
var issueInfoId                                 = 'issue_info';
var listAllUsersButtonId 						= 'list-all-users';
var listAllUsersAttacksId 						= 'list-all-attacks';
var loginLinkId 								= 'login-link';
var logoutLinkId 								= 'logout-link';
var loginUserId 								= 'login-user';
var loginPwId 									= 'login-pw';
var languageDropdownId 							= 'language-dropdown';
var moreAboutPositionButtonId 					= 'more-about-position';
var navbarLeft									= 'navbar-left';
var navigationBreadcrumbId 						= 'navigation-breadcrumb';
var newsLink 									= 'news-link';
var newsBodyId 									= 'news-body';
var opinionBarometerImageId                     = 'opinion-barometer-img';
var popupLoginNickInputId 						= 'nick-input';
var passwordGeneratorButton 					= 'password-generator-button';
var passwordGeneratorOutput 					= 'password-generator-output';
var popupGeneratePasswordId 					= 'popup-generate-password';
var popupGeneratePasswordCloseButtonId	 		= 'popup-generate-password-close-button';
var popupGeneratePasswordCloseId		 		= 'popup-generate-password-close';
var popupPasswordGeneratorOutput 				= 'popup-password-generator-output';
var popupPasswordGeneratorButton 				= 'popup-password-generator-button';
var proPositionColumnId 						= 'pro-position-column';
var proPositionTextareaId 						= 'pro-textareas';
var proIslandId 								= 'pro-island';
var proTextareaPremisegroupCheckboxId 			= 'pro-textarea-premisegroup-checkbox';
var proposalStatementListGroupId 				= 'proposal-statement-list-group';
var proposalPremiseListGroupId 				    = 'proposal-premise-list-group';
var proposalEditListGroupId 				    = 'proposal-edit-list-group';
var popupConfirmDialogId 						= 'confirm-dialog-popup';
var popupConfirmDialogAcceptBtn 				= 'confirm-dialog-accept-btn';
var popupConfirmDialogRefuseBtn 				= 'confirm-dialog-refuse-btn';
var popupConfirmChecbkoxId 						= 'confirm-dialog-checkbox';
var popupConfirmChecbkoxDialogTextId 			= 'confirm-dialog-checkbox-text';
var popupConfirmChecbkoxDialogId 				= 'confirm-dialog-checkbox-popup';
var popupConfirmChecbkoxDialogAcceptBtn 		= 'confirm-dialog-checkbox-accept-btn';
var popupConfirmChecbkoxDialogRefuseBtn 		= 'confirm-dialog-checkbox-refuse-btn';
var popupEditStatementId 						= 'popup-edit-statement';
var popupEditStatementShowLogButtonId 			= 'show_log_of_statement';
var popupEditStatementCloseButtonXId 			= 'popup-edit-statement-close';
var popupEditStatementCloseButtonId 			= 'popup-edit-statement-close-button';
var popupEditStatementTextareaId 				= 'popup-edit-statement-textarea';
var popupEditStatementContentId 				= 'popup-edit-statement-content';
var popupEditStatementLogfileHeaderId 			= 'popup-edit-statement-logfile-header';
var popupEditStatementLogfileSpaceId 			= 'popup-edit-statement-logfile';
var popupEditStatementSubmitButtonId 			= 'popup-edit-statement-submit';
var popupEditStatementDescriptionId 			= 'popup-edit-statement-description-p';
var popupEditStatementWarning					= 'popup-edit-statement-warning';
var popupEditStatementWarningMessage 			= 'popup-edit-statement-warning-message';
var popupEditStatementErrorDescriptionId 		= 'popup-edit-statement-error-description';
var popupEditStatementSuccessDescriptionId 		= 'popup-edit-statement-success-description';
var popupHowToWriteText 						= 'popup-write-text';
var popupHowToWriteTextCloseButton 				= 'popup-write-text-close-button';
var popupHowToWriteTextClose 					= 'popup-write-text-close';
var popupHowToWriteTextOkayButton 				= 'popup-write-text-okay-button';
var popupHowToSetPremiseGroups 					= 'popup-set-premisegroups';
var popupHowToSetPremiseGroupsCloseButton 		= 'popup-set-premisegroups-close-button';
var popupHowToSetPremiseGroupsClose 			= 'popup-set-premisegroups-close';
var popupHowToSetPremiseGroupsOkayButton 		= 'popup-set-premisegroups-okay-button';
var popupLogin									= 'popup-login';
var popupLoginFailed 							= 'popup-login-failed';
var popupLoginSuccess 							= 'popup-login-success';
var popupLoginForgotPasswordBody				= 'popup-login-forgot-password-body';
var popupLoginForgotPasswordText				= 'popup-login-forgot-password-text';
var popupLoginGeneratePassword					= 'popup-login-generate-password';
var popupLoginGeneratePasswordBodyId			= 'popup-login-generate-password-body';
var popupLoginPasswordMeterId 					= 'popup-login-password-meter';
var popupLoginPasswordStrengthId 				= 'popup-login-password-strength';
var popupLoginPasswordInputId 					= 'popup-login-password-input';
var popupLoginPasswordconfirmInputId 			= 'popup-login-passwordconfirm-input';
var popupLoginPasswordExtrasId					= 'popup-login-password-extras';
var popupLoginCloseButton 						= 'popup-login-close-button';
var popupLoginRegistrationSuccess 				= 'popup-login-registration-success';
var popupLoginRegistrationFailed 				= 'popup-login-registration-failed';
var popupLoginButtonRegister					= 'popup-login-button-register';
var popupLoginButtonLogin						= 'popup-login-button-login';
var popupLoginButtonRequest						= 'popup-login-button-request';
var popupLoginWarningMessage					= 'popup-login-warning-message';
var popupLoginWarningMessageText 				= 'popup-login-warning-message-text';
var popupLoginInlineRadioGenderN 				= 'inlineRadioGender1';
var popupLoginInlineRadioGenderF 				= 'inlineRadioGender2';
var popupLoginInlineRadioGenderM 				= 'inlineRadioGender3';
var popupUrlSharingLongUrlButtonID 				= 'popup-url-sharing-long-url-button';
var popupUrlSharingId 							= 'popup-url-sharing';
var popupUrlSharingCloseButtonXId 				= 'popup-url-sharing-close';
var popupUrlSharingCloseButtonId 				= 'popup-url-sharing-close-button';
var popupUrlSharingInputId 						= 'popup-url-sharing-input';
var popupUrlSharingDescriptionPId 				= 'popup-url-sharing-description-p';
var reportButtonId 								= 'report-button';
var requestTrackButtonId 						= 'request-track';
var requestHistoryButtonId 						= 'request-history';
var radioButtonGroup 							= 'radioButtonGroup';
var translationLink 							= 'link-trans-';
var translationLinkDe 							= 'link-trans-de';
var translationLinkEn 							= 'link-trans-en';
var scStyleGroupId 								= 'sc-display-style';
var scStyleDialogId 							= 'sc-style-1';
var scStyleIslandId 							= 'sc-style-2';
var scStyleCompleteId 							= 'sc-style-3';
var scStyleDialogLabelId 						= 'label-sc-style-1';
var scStyleIslandLabelId 						= 'label-sc-style-2';
var scStyleCompleteLabelId 						= 'label-sc-style-3';
var shareUrlId 									= 'share-url';
var shareUrlButtonMail 							= 'share-url-mail';
var shareUrlButtonTwitter 						= 'share-url-twitter';
var shareUrlButtonGoogle 						= 'share-url-google';
var shareUrlButtonFacebook 						= 'share-url-facebook';
var shareButtonMail 							= 'share-mail';
var shareButtonTwitter 							= 'share-twitter';
var shareButtonGoogle 							= 'share-google';
var shareButtonFacebook 						= 'share-facebook';
var shareButtonMailSmall						= 'share-mail-small';
var shareButtonTwitterSmall						= 'share-twitter-small';
var shareButtonGoogleSmall						= 'share-google-small';
var shareButtonFacebookSmall					= 'share-facebook-small';
var sendNewStatementId 							= 'send-new-statement';
var sendNewPremiseId 							= 'send-new-premise';
var sendNewsButtonId 							= 'send-news';
var settingsPasswordInfoIconId					= 'password-info-icon';
var settingsPasswordInputId 					= 'settings-password-input';
var settingsPasswordOldInputId 					= 'settings-password-old-input';
var settingsPasswordConfirmInputId 				= 'settings-passwordconfirm-input';
var settingsPasswordMeterId 					= 'settings-password-meter';
var settingsPasswordStrengthId 					= 'settings-password-strength';
var settingsPasswordExtrasId 					= 'settings-password-extras';
var settingsPasswordSubmitButtonId 				= 'settings-password-submit';
var settingsPasswordChangeDangerMessage 		= 'settings-danger-message';
var settingsPasswordChangeSuccessMessage 		= 'settings-success-message';
var switchLangIndicatorEnId						= 'switch-lang-indicator-en';
var startDiscussionButtonId 					= 'start-discussion-button';
var switchLangIndicatorDeId						= 'switch-lang-indicator-de';
var supportPositionButtonId 					= 'support-position';
var trackTableSuccessId 						= 'track-table-success';
var trackTableFailureId 						= 'track-table-failure';
var trackTableSpaceId 							= 'track-table-space';
var trackFailureMessageId 						= 'track-failure-msg';
var trackSuccessMessageId 						= 'track-success-msg';
var popupLoginUserfirstnameInputId 				= 'userfirstname-input';
var popupLoginUserlastnameInputId 				= 'userlastname-input';
var uid 										= 'uid';
var writingNewsFailedId 						= 'writing-news-failed';
var writingNewsSuccessId 						= 'writing-news-success';
var writingNewsFailedMessageId 					= 'writing-news-failed-message';
var writingNewsSuccessMessageId 				= 'writing-news-success-message';
var writingNewNewsTitleId 						= 'writing-news-title';
var writingNewNewsTextId 						= 'writing-news-text';


// classes and id's
var fuzzy_start_statement		= 0;
var fuzzy_statement_popup 		= 1;
var fuzzy_start_premise 		= 2;
var fuzzy_add_reason 			= 3;
var attr_add 					= 'add';
var attr_attack 				= 'attack';
var attr_argument_uid           = 'argument_uid';
var attr_conclusion_id 			= 'conclusion_id';
var attr_confrontation_uid 		= 'confrontation_uid';
var attr_current_attack 		= 'current_attack';
var attr_confrontation_text 	= 'confrontation_text';
var attr_id 					= 'id';
var attr_last_attack 			= 'last_attack';
var attr_last_relation 			= 'last_relation';
var attr_long_id 				= 'long_id';
var attr_no_opinion 			= 'noopinion';
var attr_more_about 			= 'more_about';
var attr_overbid 				= 'overbid';
var attr_premisegroup_uid 		= 'premisegroup_uid';
var attr_premisegroup_id 		= 'premisegroup_id';
var attr_premisegroup_con 		= 'premisegroup_con';
var attr_premisegroup_pro 		= 'premisegroup_pro';
var attr_relation 				= 'relation';
var attr_related_argument 		= 'related_argument';
var attr_rebut 					= 'rebut';
var attr_premise 				= 'premise';
var attr_start 					= 'start';
var attr_step_back 				= 'stepback';
var attr_support 				= 'support';
var attr_supportive				= 'supportive';
var attr_text 					= 'text';
var attr_undermine 				= 'undermine';
var attr_undercut 				= 'undercut';

var id_pro 						= 'pro';
var id_con 						= 'con';
var id_premisses				= '0';
var id_premisse					= '1';
