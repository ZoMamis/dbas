"""
Class for front end tests with Splinter and Selenium

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

import time
from splinter import Browser, exceptions
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException

main_page = 'http://localhost:4284/'
test_counter = 0
wait_time = 0.3
nickname_test_user1 = 'Pascal'
nickname_test_user2 = 'Kurt'
nickname_real_user1 = 'Tobias'
nickname_real_user2 = 'Martin'
nickname_real_user3 = 'Christian'
password = 'iamatestuser2016'


class Helper:
    """
    Todo
    """

    @staticmethod
    def print_info(message=''):
        """

        :param message:
        :return:
        """
        print('    ' + 'Info: ' + message)

    @staticmethod
    def print_success(has_success, message=''):
        """

        :param has_success:
        :param message:
        :return:
        """
        print('    ' + ('✓' if has_success else '✗') + ' ' + message)

    @staticmethod
    def login(browser, user, pw, url):
        """

        :param browser:
        :param user:
        :param pw:
        :param url:
        :return:
        """
        browser.visit(main_page + 'ajax_user_login?user=' + user + '&password=' + pw + '&keep_login=false&url=' + url)
        return browser

    @staticmethod
    def logout(browser):
        """

        :param browser:
        :return:
        """
        browser.visit(main_page + 'ajax_user_logout')
        return browser

    @staticmethod
    def print_error(error_name, test_name, error):
        """

        :param error_name:
        :param test_name:
        :param error:
        :return:
        """
        print('    -> ' + error_name + ' occurred in ' + test_name)
        print('       ' + str(error))

    @staticmethod
    def test_wrapper(name, test_function, *args):
        """
        Wrapper method
        :param name: of the test
        :param test_function: the function itself
        :return: value of the test_function on success, 0 otherwise
        """
        ret_val = 0
        try:
            global test_counter
            test_counter += 1
            ret_val = test_function(*args)
            print('    SUCCESS' if ret_val == 1 else '    FAIL')
            print('')
        except AttributeError as e:
            Helper.print_error('AttributeError', name, e)
        except exceptions.ElementDoesNotExist as e:
            Helper.print_error('ElementDoesNotExist', name, e)
        except IndexError as e:
            Helper.print_error('IndexError', name, e)
        except ElementNotVisibleException as e:
            Helper.print_error('ElementNotVisibleException', name, e)
        except WebDriverException as e:
            Helper.print_error('WebDriverException', name, e)
        except ConnectionResetError as e:
            Helper.print_error('ConnectionResetError', name, e)
        except ConnectionRefusedError as e:
            Helper.print_error('ConnectionRefusedError', name, e)
        except Exception as e:
            Helper.print_error('Exception', name, e)
        finally:
            return ret_val if ret_val != 0 else ret_val

    @staticmethod
    def check_for_present_text(browser, text, message):
        """
        Checks whether given text is presented in the browser
        :param browser: current browser
        :param text: text for the check
        :param message: for pint on console
        :return: true if text is present else false
        """
        if browser.is_text_present(text):
            Helper.print_success(True, message)
            return True
        else:
            Helper.print_success(False, message)
            return False

    @staticmethod
    def check_for_non_present_text(browser, text, message, print_message=True):
        """
        Checks whether given text is not presented in the browser
        :param browser: current browser
        :param text: text for the check
        :param message: for pint on console
        :param print_message: boolean for printing
        :return: true if text is present else false
        """
        if not browser.is_text_present(text):
            if print_message:
                Helper.print_success(True, message)
            return True
        else:
            if print_message:
                Helper.print_success(False, message)
            return False


class FrontendTests:
    """

    """

    @staticmethod
    def run_tests(browser_style, input_list):
        """
        Just runs every test

        :param browser_style: String
        :param input_list: List
        :return:
        """

        # server check
        if not Helper.test_wrapper('testing for connectivity to server', FrontendTests.check_for_server, browser_style):
            print('====================================================')
            print('Exit gracefully!')
            return

        global test_counter
        test_counter = 0
        success_counter = 0

        splitted_list = input_list.split(',')
        if len(splitted_list) == 1 and splitted_list[0] == 'a':
            splitted_list = []
            for i in range(17):
                splitted_list.append(str(i))

        start = time.time()
        while len(splitted_list) > 0:
            cid = int(splitted_list[0].strip())
            if cid in range(0, len(test_list) - 1):
                success_counter += Helper.test_wrapper(test_list[cid]['test_description'], test_list[cid]['test_call'], browser_style)
            else:
                print('Malicious list entry: ' + splitted_list[0])
            splitted_list.remove(splitted_list[0])
        end = time.time()

        diff = str(end - start)
        diff = diff[0:diff.index('.') + 3]

        print('====================================================')
        print('Failed ' + str(test_counter - success_counter) + ' out of ' + str(test_counter) + ' in ' + str(diff) + 's')

    @staticmethod
    def check_for_server(browser):
        """
        Checks whether the server if online
        :param browser: current browser
        :return: true when the server is on, false otherwise
        """
        print('Is server online? ')
        b = Browser(browser)
        b.visit(main_page)
        success = Helper.check_for_present_text(b, 'part of the graduate school', 'check main page')
        b.quit()
        return success

    @staticmethod
    def test_pages_when_not_logged_in(browser):
        """
        Checks pages
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for pages_not_logged_in:')
        success = True
        b = Browser(browser)
        b.visit(main_page)
        b.find_by_css('.dropdown-toggle[href="#language"]').click()
        b.find_by_id('link-trans-en').click()

        pages = [main_page,
                 main_page + 'contact',
                 main_page + 'news',
                 main_page + 'imprint',
                 main_page + 'discuss',
                 main_page + 'settings',
                 main_page + 'notifications',
                 main_page + 'admin/main',
                 main_page + 'user/Tobias']
        tests = ['main',
                 'contact',
                 'news',
                 'imprint',
                 'discuss',
                 'settings',
                 'notifications',
                 'admin',
                 'user']
        texts = ['part of the graduate school',
                 'Feel free to drop us a',
                 'COMMA16',
                 'Liability for content',
                 'Current discussion is about:',
                 'part of the graduate school',
                 'part of the graduate school',
                 'Dashboard',
                 'Tobias']
        for index, p in enumerate(pages):
            b.visit(p)
            t = 'testing ' + tests[index] + ' page'
            success = success and Helper.check_for_present_text(b, texts[index], t)

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_login_logout(browser):
        """

        :param browser:
        :return:
        """
        success = True
        print('Starting tests for login_logout:')
        b = Browser(browser)

        b = Helper.login(b, nickname_test_user1, 'wrong_password', main_page)
        t = 'testing wrong login'
        success = success and Helper.check_for_present_text(b, 'do not match', t)

        time.sleep(wait_time)
        b = Helper.login(b, nickname_test_user1, password, main_page)
        t = 'testing right login'
        success = success and Helper.check_for_present_text(b, nickname_test_user1, t)
        time.sleep(wait_time)

        b = Helper.logout(b)
        t = 'testing logout'
        success = success and Helper.check_for_non_present_text(b, 'tobias', t)

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_pages_when_logged_in(browser):
        """

        :param browser:
        :return:
        """
        success = True
        print('Starting tests for pages_logged_in:')
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page)

        pages = [main_page + 'settings',
                 main_page + 'notifications',
                 main_page + 'admin/main']
        tests = ['settings',
                 'notifications',
                 'admin']
        texts = ['Personal Information',
                 'Notification Board',
                 '401']
        for index, p in enumerate(pages):
            b.visit(p)
            t = 'testing ' + tests[index] + ' page'
            success = success and Helper.check_for_present_text(b, texts[index], t)
            time.sleep(wait_time * 2)

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_popups(browser):
        """
        Checks UI popups
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for popups:')
        b = Browser(browser)
        b.visit(main_page)

        # open author popup
        b.find_by_id('link_popup_author').click()
        success = Helper.check_for_present_text(b, 'About me', 'check for author text')
        close = b.find_by_name('popup_author_icon_close')
        close.click()

        time.sleep(wait_time)

        # open licence popup
        b.find_by_id('link_popup_license').click()
        success = success and Helper.check_for_present_text(b, 'MIT', 'check for license text')
        close = b.find_by_name('popup_license_icon_close')
        close.click()

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_contact_form(browser):
        """
        Checks every form on the contact page
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for contact_form:')
        b = Browser(browser)
        b.visit('http://localhost:4284/contact')

        form = ['',
                'name',
                'mail',
                'content',
                'spam']
        content = ['',
                   'some_name',
                   'some_mail@gmx.de',
                   'some_content',
                   'some_spam']
        txt = ['name is empty',
               'mail is',
               'content is empty',
               'anti-spam message is empty or wrong',
               'anti-spam message is empty or wrong']
        prefix = 'testing contact form for '
        msg = [prefix + 'empty name',
               prefix + 'empty e-mail',
               prefix + 'empty content',
               prefix + 'empty anti-spam',
               prefix + 'wrong anti-spam']

        success = True
        for i in range(0, len(txt)):
            # special cases
            if i > 0:
                b.fill(form[i], content[i])
            if i == 4:
                b.fill(form[3], content[3])
            b.find_by_name('form.contact.submitted').click()
            success = success and Helper.check_for_present_text(b, txt[i], msg[i])

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_language_switch(browser):
        """
        Testing language switch
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for language_switch:')
        b = Browser(browser)

        b.visit(main_page)
        success = Helper.check_for_present_text(b, 'part of the graduate', 'check english language')

        b.find_by_css('.dropdown-toggle[href="#language"]').click()
        b.find_by_id('link-trans-de').click()
        success = success and Helper.check_for_present_text(b, 'Teil des Graduierten-Kollegs', 'check switch to german language')

        time.sleep(wait_time * 5)
        b.find_by_css('.dropdown-toggle[href="#language"]').click()
        b.find_by_id('link-trans-de').click()
        success = success and Helper.check_for_present_text(b, 'part of the graduate', 'check switch back to english language')

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_discussion_buttons(browser):
        """
        Checks the discussions buttons
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for discussion_buttons:')
        b = Browser(browser)
        success = True
        b = Helper.login(b, nickname_test_user1, password, main_page + 'discussion')

        # check url popup
        if not b.find_by_id('share-url').visible:
            b.find_by_css('.hamburger span:first-child')[0].click()
            time.sleep(wait_time * 2)
            b.find_by_css('.tack-wrapper i')[0].click()

        # long url
        b.find_by_id('share-url').click()
        success = success and Helper.check_for_present_text(b, 'Share your URL', 'check for share url popup')
        b.find_by_id('popup-url-sharing-long-url-button').click()
        success = success and Helper.check_for_present_text(b, 'discussion', 'check for long url')
        b.find_by_id('popup-url-sharing-close').click()
        time.sleep(wait_time)

        # check issue dropdown and switch issue
        b.find_by_id('issue-dropdown').click()
        success = success and Helper.check_for_present_text(b, 'Cat or Dog', 'check for issue dropdown')
        b.find_by_css('.dropdown-menu li.enabled a').click()
        time.sleep(wait_time)
        if b.is_text_present('Change of discussion'):
            success = success and Helper.check_for_present_text(b, 'Change of discussion', 'check for change topic popup')
            b.find_by_id('confirm-dialog-checkbox-accept-btn').click()
            time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, 'Your family argues', 'check for switched issue')

        # check finish
        b.find_by_id('finish-button').click()
        success = success and Helper.check_for_present_text(b, 'Thank you!', 'check for finish button')

        # go back
        b.find_by_id('back-to-discuss-button').click()

        # click position
        success = success and Helper.check_for_present_text(b, 'What is the initial position', 'check for first step in discussion')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        success = success and Helper.check_for_present_text(b, 'What do you think', 'check for second step in discussion')

        # restart
        b.find_by_id('discussion-restart-btn').click()
        success = success and Helper.check_for_present_text(b, 'What is the initial position', 'check for restart')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_demo_discussion(browser):
        """
        Checks the demo of the discussion. Simple walk through Helper.
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for demo_discussion:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'discussion')

        # position
        success = success and Helper.check_for_present_text(b, 'initial ', 'check for position')
        b.find_by_id('item_36').click()
        time.sleep(wait_time)

        # attitude
        success = success and Helper.check_for_present_text(b, 'What do you think', 'check for attitude')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # premise
        success = success and Helper.check_for_present_text(b, 'most important reason', 'check for premise')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # confrontation
        success = success and Helper.check_for_present_text(b, 'Other participants', 'check for confrontation')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # justification
        tmp1 = Helper.check_for_present_text(b, 'most important reason', 'check for justification 1')
        tmp2 = Helper.check_for_present_text(b, 'Let me state my ', 'check for justification 2')
        success = success and (tmp1 or tmp2)
        time.sleep(wait_time)

        # go back
        b.find_by_id('discussion-restart-btn').click()
        success = success and Helper.check_for_present_text(b, 'initial ', 'check for position again')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_functions_while_discussion(browser):
        """
        Checks different functions in the discussion like adding one premise, premise groups and so one
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for functions_while_discussion:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'discussion')

        # new position
        b.find_by_css('#discussions-space-list li:last-child input').click()
        success = success and Helper.check_for_present_text(b, 'What is your idea', 'check for new position field')
        position = 'some new position ' + str(time.time())
        b.find_by_id('add-statement-container-main-input').fill(position)
        b.find_by_id('send-new-statement').click()
        time.sleep(wait_time)

        # dont know attitude
        success = success and Helper.check_for_present_text(b, 'What do you think about ' + position, 'check for attitude')
        b.find_by_css('#item_dontknow').click()
        time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, 'do not have any opinion', 'check for dont know attitude 1')
        success = success and Helper.check_for_present_text(b, 'ends here', 'check for dont know attitude 2')
        b.back()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # new premise
        success = success and Helper.check_for_present_text(b, 'Let me enter my reason', 'check for new window premise')
        reason1 = 'some new reason'
        b.find_by_id('add-premise-container-main-input').fill(reason1)
        b.find_by_id('send-new-premise').click()
        time.sleep(wait_time)

        # confrontation
        success = success and Helper.check_for_present_text(b, position[1:] + ' because some new reason', 'check for new argument')
        success = success and Helper.check_for_present_text(b, 'Other participants do not have any counter-argument for that.', 'check that no confrontation exists')
        success = success and Helper.check_for_present_text(b, 'The discussion ends here.', 'check for end text')

        # go back to first premise
        # b.find_by_css('div.line-wrapper-r:first-child a').click()
        b.find_by_css('#discussion-restart-btn').click()
        b.find_by_text(position)[0].click()
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        b.find_by_css('#item_start_premise').click()
        time.sleep(wait_time)
        # add new premise
        success = success and Helper.check_for_present_text(b, 'me enter my reason', 'check for new premise window again')
        reason2 = 'some new reason 1 and some new reason 2'
        b.find_by_id('add-premise-container-main-input').fill(reason2)
        # add another input field
        b.find_by_css('.icon-add-premise').click()
        time.sleep(wait_time)
        b.find_by_id('send-new-premise').click()
        time.sleep(wait_time)

        # check for premisegroups popup
        success = success and Helper.check_for_present_text(b, 'We need your help', 'check for pgroup popup')
        b.find_by_id('insert_more_arguments_0').click()
        time.sleep(wait_time)
        b.find_by_id('popup-set-premisegroups-send-button').click()
        time.sleep(wait_time)

        # check choosing
        success = success and Helper.check_for_present_text(b, 'multiple reasons', 'check options for choosing ')
        success = success and Helper.check_for_present_text(b, 'some new reason 1', 'check options for choosing answer 1')
        success = success and Helper.check_for_present_text(b, 'some new reason 2', 'check options for choosing answer 2')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_content(browser):
        """
        Checks the formulation of arguments
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for test_content:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'discussion')

        # start
        b.visit(main_page + 'discuss/town-has-to-cut-spending')
        success = success and Helper.check_for_present_text(b, 'initial position you are interested', 'check for question of inital position')
        b.find_by_text('The city should reduce the number of street festivals').click()
        time.sleep(wait_time)

        # attitude
        success = success and Helper.check_for_present_text(b, 'think about', 'check for question of attitude')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # justify position
        success = success and Helper.check_for_present_text(b, 'most important', 'check for question of reason')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # confrontation - give feedback
        success = success and Helper.check_for_present_text(b, 'Other participants', 'check for confronting question')
        success = success and Helper.check_for_present_text(b, 'stronger argument for accepting', 'check for accepting formulation of rebut')

        # earlier used argument
        b.find_by_css('#discussions-space-list li:nth-child(4) input').click()
        success = success and Helper.check_for_present_text(b, 'You used this earlier', 'check for earlier used formulation')
        b.back()
        time.sleep(wait_time)

        while Helper.check_for_non_present_text(b, 'every street festival is funded by large companies', 'sanity check', print_message=False):
            b.back()
            b.reload()
            time.sleep(wait_time)
            b.find_by_css('#discussions-space-list li:first-child input').click()
        b.find_by_css('#discussions-space-list li:nth-child(2) input').click()
        time.sleep(wait_time)

        # support of confrontation
        success = success and Helper.check_for_present_text(b, 'Earlier you argued', 'check for formulation on \'supports\' 1')
        success = success and Helper.check_for_present_text(b, 'convinced you that', 'check for formulation on \'supports\' 2')
        b.find_by_css('#discussion-restart-btn').click()
        time.sleep(wait_time)
        b.find_by_text('The city should reduce the number of street festivals').click()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # confrontation - give feedback again
        success = success and Helper.check_for_present_text(b, 'Other participants', 'check for confronting question again')
        # b.find_by_css('#item_rebut label').click()
        b.find_by_css('#discussions-space-list li:nth-child(4) input').click()
        time.sleep(wait_time)

        # rebut of confrontation
        success = success and Helper.check_for_present_text(b, 'You have a much stronger argument for accepting', 'check for formulation on rebut')
        b.find_by_css('#discussion-restart-btn').click()
        time.sleep(wait_time)

        # restart
        b.find_by_text('The city should reduce the number of street festivals').click()
        time.sleep(wait_time)

        # attitude
        b.find_by_css('#discussions-space-list li:nth-child(2) input').click()
        time.sleep(wait_time)

        # confrontation - give feedback again
        success = success and Helper.check_for_present_text(b, 'You disagree with', 'check for question of rejection')
        b.find_by_css('#discussions-space-list li:first-child input').click()
        time.sleep(wait_time)

        # confrontation - give feedback
        success = success and Helper.check_for_present_text(b, 'does not hold', 'check for rejecting opinion')
        tmp_success1 = b.is_text_present('stronger statement for accepting')
        tmp_success2 = b.is_text_present('good counter-argument for')
        Helper.print_success(tmp_success1 or tmp_success2, 'check for rejecting formulation of rebut')
        success = success and (tmp_success1 or tmp_success2)
        # b.find_by_css('#item_rebut label').click()
        b.find_by_css('#discussions-space-list li:nth-child(4) input').click()

        # rebut of confrontation
        success = success and Helper.check_for_present_text(b, 'You have a much stronger argument for rejecting', 'check for formulation on rebut again')
        success = success and Helper.check_for_present_text(b, 'is not a good idea', 'check for question again')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_user_page(browser):
        """
        Testing language switch
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for user_page:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'user/' + nickname_test_user1)

        success = success and Helper.check_for_present_text(b, 'Public Information', 'check for public page')
        success = success and Helper.check_for_present_text(b, nickname_test_user1, 'check for real nickname')

        b.visit(main_page + 'settings')
        b.find_by_css('#settings-table tr:nth-child(3) .toggle').click()
        time.sleep(wait_time)

        fake_name = b.find_by_css('#info-table tr:nth-child(3) td:nth-child(2)').text
        b.visit(main_page + 'user/' + fake_name)
        success = success and Helper.check_for_present_text(b, fake_name, 'check for fake nickname')

        b.visit(main_page + 'settings')
        b.find_by_css('#settings-table tr:nth-child(3) .toggle').click()
        time.sleep(wait_time)

        b.visit(main_page + 'user/' + nickname_test_user1)
        success = success and Helper.check_for_present_text(b, nickname_test_user1, 'check for real nickname again')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_notification_system(browser):
        """
        Testing notification system
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for notification_system:')
        success = True
        b = Browser(browser)

        b = Helper.login(b, nickname_test_user1, password, main_page + 'notifications')

        txt = 'You have got 0 unread notifications and 0 total in the inbox. There are 0 in the outbox.'
        success = success and Helper.check_for_present_text(b, txt, 'check for zero notifications')

        b.find_by_id('new-notification').click()
        time.sleep(wait_time)

        # write message
        b.find_by_id('popup-writing-notification-recipient').fill(nickname_test_user2)
        b.find_by_id('popup-writing-notification-title').fill('Test notification for Kurt')
        b.find_by_id('popup-writing-notification-text').fill('This is a test notification for splinter tests')
        b.find_by_id('popup-writing-notification-send').click()
        time.sleep(wait_time)

        success = success and Helper.check_for_present_text(b, 'was send', 'check for send notifications')

        b.visit(main_page + 'notifications')
        time.sleep(wait_time)
        txt = 'There are 1 in the outbox.'
        success = success and Helper.check_for_present_text(b, txt, 'check for one outbox notifications')

        b.find_by_id('outbox-link').click()
        time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, 'Test notification', 'check for the notification in the outbox')

        # delete message
        b.find_by_css('.glyphicon-trash').click()
        time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, 'deleted', 'check for deleted message')
        success = success and Helper.check_for_present_text(b, 'There are 0 in the outbox.', 'check for zero outbox notifications')

        b = Helper.logout(b)
        b = Helper.login(b, nickname_test_user2, password, main_page + 'notifications')
        success = success and Helper.check_for_present_text(b, 'Test notification', 'check for one new notifications 1')
        txt = 'You have got 1 unread notifications and 1 total in the inbox. There are 0 in the outbox.'
        success = success and Helper.check_for_present_text(b, txt, 'check for one new notifications 2')

        # delete message
        b.find_by_css('.glyphicon-trash').click()
        time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, 'deleted', 'check for deleted message')
        txt = 'You have got 0 unread notifications and 0 total in the inbox. There are 0 in the outbox.'
        success = success and Helper.check_for_present_text(b, txt, 'check for zero notifications')

        b = Helper.logout(b)

        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_review_page(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for review page:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_real_user1, nickname_real_user1.lower(), main_page)

        b.visit(main_page + 'review')
        success = success and Helper.check_for_present_text(b, 'Help improve the dialog', 'check for review header')
        old_count = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        b.visit(main_page + 'review/deletes')
        b.find_by_css('#del_ack').click()
        time.sleep(wait_time)

        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        success = success and (int(old_count) < int(new_count))

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_flag_statement(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for flag statement:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'review')
        b.visit(main_page + 'review')
        time.sleep(wait_time)
        old_count_for_users = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        b.visit(main_page + 'discuss')
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:nth-child(2)').mouse_over()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:nth-child(2) .item-flag').click()
        time.sleep(wait_time)
        b.find_by_css('#popup-flag-argument input[value=offtopic]').click()
        success = success and Helper.check_for_present_text(b, 'Thanks for reporting', 'Success text for flagging')

        b.find_by_css('#discussions-space-list li:nth-child(2)').mouse_over()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:nth-child(2) .item-flag').click()
        time.sleep(wait_time)
        b.find_by_css('#popup-flag-argument input[value=offtopic]').click()
        success = success and Helper.check_for_present_text(b, 'You have already reported this argument', 'Info text for flagging')

        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count_for_user1 = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text
        b = Helper.logout(b)

        b = Helper.login(b, nickname_test_user2, password, main_page + 'review')
        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count_for_user2 = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        success = success and (int(new_count_for_user1) == int(old_count_for_users))
        Helper.print_success(success, 'Check review queue length for user, who has flagged (' + str(old_count_for_users) + '/' + str(new_count_for_user1) + ')')
        success = success and (int(new_count_for_user2) > int(old_count_for_users))
        Helper.print_success(success, 'Check review queue length for different user (' + str(old_count_for_users) + '/' + str(new_count_for_user2) + ')')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_flag_argument(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for flag argument:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user2, password, main_page + 'review')
        time.sleep(wait_time)
        old_count = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        b.visit(main_page + 'discuss/town-has-to-cut-spending/reaction/32/rebut/36')
        time.sleep(wait_time)
        b.find_by_css('.pull-right .fa-flag').click()
        time.sleep(wait_time)
        b.find_by_css('#popup-flag-argument input[value=offtopic]').click()
        success = success and Helper.check_for_present_text(b, 'Thanks for reporting', 'Success text for flagging')

        b.find_by_css('.pull-right .fa-flag').click()
        time.sleep(wait_time)
        b.find_by_css('#popup-flag-argument input[value=offtopic]').click()
        success = success and Helper.check_for_present_text(b, 'You have already reported this argument', 'Info text for flagging')

        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count = b.find_by_css('#review-table tbody tr:nth-child(1) strong').text

        Helper.print_info('Old/new review count ' + str(old_count) + '/' + str(new_count))

        success = success and (int(new_count) < int(old_count))

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_review_queue(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for review queue:')
        success = True
        b = Browser(browser)

        # login ang get points of the first test user
        b = Helper.login(b, nickname_test_user1, password, main_page + 'review')
        old_points  = b.find_by_css('#queues h6 a').text
        b = Helper.logout(b)

        # login, have a look at the deletes, search for the text of pascal and vote for delete
        b = Helper.login(b, nickname_real_user1, nickname_real_user1.lower(), main_page + 'review/deletes')
        while not b.is_text_present(nickname_test_user1):
            b.reload()
            time.sleep(wait_time)
        text = b.find_by_css('#reviewed-argument-text').text
        b.find_by_css('#del_ack').click()
        time.sleep(wait_time)
        b = Helper.logout(b)

        # login, have a look at the deletes, search for saved text and vote for delete
        b = Helper.login(b, nickname_real_user2, nickname_real_user2.lower(), main_page + 'review/deletes')
        while not b.is_text_present(text):
            b.reload()
            time.sleep(wait_time)
        b.find_by_css('#del_ack').click()
        time.sleep(wait_time)
        b = Helper.logout(b)

        # login, have a look at the deletes, search for saved text an d vote for delete
        b = Helper.login(b, nickname_real_user3, nickname_real_user3.lower(), main_page + 'review/ongoing')
        time.sleep(wait_time)
        success = success and Helper.check_for_present_text(b, text[0:15], 'Check for the text of revised statement in ongoing queue (must be there)')

        b.visit(main_page + 'review/deletes')
        while not b.is_text_present(text):
            b.reload()
            time.sleep(wait_time)
        b.find_by_css('#del_ack').click()
        time.sleep(wait_time)

        b.visit(main_page + 'review/ongoing')
        success = success and Helper.check_for_non_present_text(b, text[0:15], 'Check for the text of revised statement in ongoing queue (must be gone)')
        b.visit(main_page + 'review/history')
        success = success and Helper.check_for_present_text(b, text[0:15], 'Check for the text of revised statement in history queue (must be there)')
        b = Helper.logout(b)

        # have a look at the discussion page and check, whether the text ist not visible!
        b.visit(main_page + 'discuss')
        time.sleep(wait_time)
        success = success and Helper.check_for_non_present_text(b, text, 'Check for the forbidden text "' + text + '"')
        b = Helper.logout(b)

        # login ang get points of the first test user
        b = Helper.login(b, nickname_test_user1, password, main_page + 'review')
        new_points  = b.find_by_css('#queues h6 a').text
        Helper.print_info('Old/new reputation count ' + str(old_points) + '/' + str(new_points))
        success = success and (int(old_points) < int(new_points))

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_undo_review_in_queue(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for undo review in queue:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page)

        Helper.print_info('TODO')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_cancel_review_in_queue(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for cancel review in queue:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page)

        Helper.print_info('TODO')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_edit_statement(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for edit statement:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page + 'review')
        time.sleep(wait_time)
        old_count_for_users = b.find_by_css('#review-table tbody tr:nth-child(3) strong').text

        # hover edit flag
        b.visit(main_page + 'discuss')
        time.sleep(wait_time)
        text = b.find_by_css('#discussions-space-list li:nth-child(2) label').text
        b.find_by_css('#discussions-space-list li:nth-child(2)').mouse_over()
        time.sleep(wait_time)
        b.find_by_css('#discussions-space-list li:nth-child(2) .item-edit').click()
        time.sleep(wait_time)

        b.fill('popup-edit-statement-input-0', text + '#42')
        time.sleep(wait_time)

        b.find_by_css('#popup-edit-statement-submit').click()
        success = success and Helper.check_for_present_text(b, 'Your proposals', 'Check for general success popup after edit')

        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count_for_user1 = b.find_by_css('#review-table tbody tr:nth-child(3) strong').text
        b = Helper.logout(b)

        b = Helper.login(b, nickname_test_user2, password, main_page + 'review')
        b.visit(main_page + 'review')
        time.sleep(wait_time)
        new_count_for_user2 = b.find_by_css('#review-table tbody tr:nth-child(3) strong').text

        success = success and (int(new_count_for_user1) == int(old_count_for_users))
        Helper.print_success(success, 'Check review queue length for user, who has flagged (' + str(old_count_for_users) + '/' + str(new_count_for_user1) + ')')
        success = success and (int(new_count_for_user2) > int(old_count_for_users))
        Helper.print_success(success, 'Check review queue length for different user (' + str(old_count_for_users) + '/' + str(new_count_for_user2) + ')')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0

    @staticmethod
    def test_edit_as_optimization(browser):
        """
        Testing some review mechanism
        :param browser: current browser
        :return: 1 if success else 0
        """
        print('Starting tests for cancel review in queue:')
        success = True
        b = Browser(browser)
        b = Helper.login(b, nickname_test_user1, password, main_page)

        Helper.print_info('TODO')

        b = Helper.logout(b)
        b.quit()
        return 1 if success else 0


test_list = [
    {'console_description': 'tests for normal/not logged in pages',
     'test_description': 'tests for normal/not logged in pages',
     'test_call': FrontendTests.test_pages_when_not_logged_in,
     'test_id': 0},
    {'console_description': 'tests for login logout',
     'test_description': 'tests for login logout',
     'test_call': FrontendTests.test_login_logout,
     'test_id': 1},
    {'console_description': 'tests for logged in pages',
     'test_description': 'tests for logged in pages',
     'test_call': FrontendTests.test_pages_when_logged_in,
     'test_id': 2},
    {'console_description': 'tests for popups',
     'test_description': 'tests for popups',
     'test_call': FrontendTests.test_popups,
     'test_id': 3},
    {'console_description': 'tests for contact form',
     'test_description': 'tests for contact form',
     'test_call': FrontendTests.test_contact_form,
     'test_id': 4},
    {'console_description': 'tests for language switch',
     'test_description': 'tests for language switch',
     'test_call': FrontendTests.test_language_switch,
     'test_id': 5},
    {'console_description': 'tests for discussion buttons',
     'test_description': 'tests for discussion buttons',
     'test_call': FrontendTests.test_discussion_buttons,
     'test_id': 6},
    {'console_description': 'tests for demo discussion',
     'test_description': 'tests for demo discussion',
     'test_call': FrontendTests.test_demo_discussion,
     'test_id': 7},
    {'console_description': 'tests for demo discussion with all functions',
     'test_description': 'tests for demo discussion with all functions',
     'test_call': FrontendTests.test_functions_while_discussion,
     'test_id': 8},
    {'console_description': 'tests for content',
     'test_description': 'tests for content',
     'test_call': FrontendTests.test_content,
     'test_id': 9},
    {'console_description': 'tests for public user page',
     'test_description': 'tests for public user page',
     'test_call': FrontendTests.test_user_page,
     'test_id': 10},
    {'console_description': 'tests for notification system',
     'test_description': 'tests for notification system',
     'test_call': FrontendTests.test_notification_system,
     'test_id': 11},
    {'console_description': 'tests for review page',
     'test_description': 'test for review_page',
     'test_call': FrontendTests.test_review_page,
     'test_id': 12},
    {'console_description': 'tests for flag statement',
     'test_description': 'test for flag statement',
     'test_call': FrontendTests.test_flag_statement,
     'test_id': 13},
    {'console_description': 'tests for flag argument',
     'test_description': 'test for flag argument',
     'test_call': FrontendTests.test_flag_argument,
     'test_id': 14},
    {'console_description': 'tests for review queue (only with 13!)',
     'test_description': 'test for review queue',
     'test_call': FrontendTests.test_review_queue,
     'test_id': 15},
    {'console_description': 'tests for undo review in queue',
     'test_description': 'test for undo review in queue',
     'test_call': FrontendTests.test_undo_review_in_queue,
     'test_id': 16},
    {'console_description': 'tests for cancel review in queue',
     'test_description': 'test for cancel review in queue',
     'test_call': FrontendTests.test_cancel_review_in_queue,
     'test_id': 17},
    {'console_description': 'tests for edit statement',
     'test_description': 'test for edit statement',
     'test_call': FrontendTests.test_edit_statement,
     'test_id': 18},
    {'console_description': 'tests for edit as optimization',
     'test_description': 'test for edit as optimization',
     'test_call': FrontendTests.test_edit_as_optimization,
     'test_id': 19}
]

if __name__ == "__main__":
    print('  /---------------------------------------/')
    print(' / PLEASE USE A FRESH DB WITH DUMMY DATA /')
    print('/---------------------------------------/')
    print('')
    print('Please choose a web browser:')
    print('  [b]reak')
    print('  [c]hrome  (default)')
    print('  [f]irefox')
    input_browser = input('Enter: ')
    print('')
    print('Please choose a testing style:')
    print('  [ a]ll (default)')
    for test in test_list:
        id = (' ' + str(test['test_id'])) if test['test_id'] < 10 else str(test['test_id'])
        print('  [' + id + '] ' + test['console_description'])
    input_list = input('You can enter a number, like 3, or a list, like 5,2,9: ')

    if str(input_browser) != 'b':
        web_driver = 'firefox' if str(input_browser) == 'f' else 'chrome'
        if len(input_list) == 0:
            input_list = 'a'

        print('')
        print('-> Tests will be done with ' + web_driver)
        print('')

        try:
            FrontendTests.run_tests(web_driver, input_list)
        except ConnectionResetError as e1:
            print('  Server is offline found: ' + str(e1))
        except FileNotFoundError as e2:
            print('FileNotFoundError found: ' + str(e2))
        except AttributeError as e3:
            print('AttributeError found: ' + str(e3))
        except WebDriverException as e4:
            print('WebDriverException found: ' + str(e4))
        except KeyboardInterrupt as e5:
            print('Exit through KeyboardInterrupt')
