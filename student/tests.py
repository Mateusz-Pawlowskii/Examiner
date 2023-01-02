from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

# Create your tests here.

# settings for testing
home_adress = "http://127.0.0.1:8000"
test_login_examiner = "Test_Examiner"
test_login = "Test_Student"
# both test accounts are assumed to use same password
test_password = "JBfP64Zbk3mKBYAt"
geko_driver_directory = ""

# functions used in testing
# functions to make using selenium easier in general
def select_id(driver, id, value):
    shortcut = Select(driver.find_element(By.ID, id))
    shortcut.select_by_value(value)

def select_text(driver, id, text):
    shortcut = Select(driver.find_element(By.ID, id))
    shortcut.select_by_visible_text(text)

def type_id(driver, id, text):
    shortcut = driver.find_element(By.ID, id)
    shortcut.send_keys(text)

def click_id(driver, id):
    shortcut = driver.find_element(By.ID, id)
    shortcut.click()

def clear_id(driver, id):
    shortcut = driver.find_element(By.ID, id)
    shortcut.clear()

# tests
class TestStudent(LiveServerTestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.browser = webdriver.Firefox(geko_driver_directory)
        self.browser.maximize_window()
        self.browser.get(home_adress)
        self.create_group(self)
        self.create_test(self, "Test course name")
        self.create_test(self, "Failed")
        self.create_test(self, "Out of time")
        self.login_student(self)

    @classmethod
    def tearDownClass(self):
        click_id(self.browser, "logout")
        self.login_examiner(self)
        self.browser.get(home_adress + "/examiner/test")
        click_id(self.browser, "logout")
        self.browser.close()
        super().tearDownClass()
    
    def login_student(self):
        click_id(self.browser, "login")
        type_id(self.browser, "username", test_login)
        type_id(self.browser, "password", test_password)
        click_id(self.browser, "submit")
        click_id(self.browser, "English")

    def login_examiner(self):
        click_id(self.browser, "login")
        type_id(self.browser, "username", test_login_examiner)
        type_id(self.browser, "password", test_password)
        click_id(self.browser, "submit")
        click_id(self.browser, "English")

    def create_group(self):
        self.login_examiner(self)
        click_id(self.browser, "nav_groups")
        click_id(self.browser, "create_group")
        type_id(self.browser, "id_name", "Test_Group")
        click_id(self.browser, "submit")
        click_id(self.browser, "link_Test_Group")
        click_id(self.browser, "student_nav")
        type_id(self.browser, "id_student", test_login)
        student_submit = self.browser.find_element(By.ID, "submit_student")
        self.browser.execute_script("arguments[0].click();", student_submit)
        click_id(self.browser, "logout")

    def create_test(self, name):
        self.login_examiner(self)
        self.create_course(self, name)
        click_id(self.browser, "nav_courses")
        self.browser.find_element(By.XPATH, f'/html/body/div/table/tbody/tr[@id="{name}"]/td[1]/a').click()
        click_id(self.browser, "edit")
        clear_id(self.browser, "id_time")
        type_id(self.browser, "id_time", "1")
        clear_id(self.browser, "id_attempt_amount")
        type_id(self.browser, "id_attempt_amount", "1")
        clear_id(self.browser, "id_question_amount")
        type_id(self.browser, "id_question_amount", "1")
        clear_id(self.browser, "id_passing_score")
        type_id(self.browser, "id_passing_score", "1")
        click_id(self.browser, "id_test_ready")
        click_id(self.browser, "submit")
        click_id(self.browser, "edit")
        click_id(self.browser, "student_nav")
        type_id(self.browser, "id_group", "Test_Group")
        type_id(self.browser, "id_deadline", "2030-11-11")
        # I need to use execute_script becouse otherwise exception is rised due to button being obscured by div
        student_submit = self.browser.find_element(By.ID, "submit_student")
        self.browser.execute_script("arguments[0].click();", student_submit)
        click_id(self.browser, "add_question")
        type_id(self.browser, "id_text", "Test question text")
        type_id(self.browser, "id_answer1", "First test answer")
        type_id(self.browser, "id_answer2", "Secound test answer")
        click_id(self.browser, "id_correct_answers_1")
        click_id(self.browser, "submit")
        click_id(self.browser, "logout")

    def create_course(self, name):
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "add")
        type_id(self.browser, "id_name", name)
        type_id(self.browser, "id_category", "Test category")
        click_id(self.browser, "submit")
    
    def test_logging_in(self):
        # user checks if their username is properly shown
        self.assertEquals(self.browser.find_element(By.ID, "current_username").text, f"Student: {test_login}")
    
    def test_exam(self):
        # user checks if course that they were assigned to shows up
        click_id(self.browser, "nav_courses")
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_stu_Test course name"))
        # for some reason standard click didn't work
        self.browser.find_element(By.XPATH, '/html/body/div/table/tbody/tr[@id="Test course name"]/td[1]/a').click()
        click_id(self.browser, "exam")
        self.assertEquals(self.browser.find_element(By.ID, "course_name").text, "Test course name")
        # user finishes exam sucessfully
        click_id(self.browser, "submit")
        click_id(self.browser, "id_correct_answers_1")
        click_id(self.browser, "submit")
        # checks if sucess message shows up
        self.assertIsNotNone(self.browser.find_element(By.ID, "success"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "failure"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "timeout"))
        # user finishes exam unsucessfully
        click_id(self.browser, "nav_courses")
        self.browser.find_element(By.XPATH, '/html/body/div/table/tbody/tr[@id="Failed"]/td[1]/a').click()
        click_id(self.browser, "exam")
        click_id(self.browser, "submit")
        click_id(self.browser, "id_correct_answers_2")
        click_id(self.browser, "submit")
        # checks if failure message show up
        self.assertIsNotNone(self.browser.find_element(By.ID, "failure"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "success"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "timeout"))
        # user runs out of time
        click_id(self.browser, "nav_courses")
        self.browser.find_element(By.XPATH, '/html/body/div/table/tbody/tr[@id="Out of time"]/td[1]/a').click()
        click_id(self.browser, "exam")
        click_id(self.browser, "submit")
        time.sleep(63)
        # checks if failure message show up
        self.assertIsNotNone(self.browser.find_element(By.ID, "timeout"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "success"))
        click_id(self.browser, "ok")
        # user checks passed result
        click_id(self.browser, "nav_results")
        self.assertEquals(self.browser.find_element(By.ID, "status_Test course name").text, "Passed")
        self.browser.find_element(By.XPATH, f'/html/body/div/table/tbody/tr[@id="Test course name"]/td[1]/a').click()
        self.assertEquals(self.browser.find_element(By.ID, "status_Test course name_1").text, "Passing")
        self.assertEquals(self.browser.find_element(By.ID, "perc_Test course name_1").text, "100")
        self.assertEquals(self.browser.find_element(By.ID, "score_Test course name_1").text, "1")
        # user checks failed result
        click_id(self.browser, "nav_results")
        self.assertEquals(self.browser.find_element(By.ID, "status_Failed").text, "Failed")
        self.browser.find_element(By.XPATH, f'/html/body/div/table/tbody/tr[@id="Failed"]/td[1]/a').click()
        self.assertEquals(self.browser.find_element(By.ID, "status_Failed_1").text, "Failing")
        self.assertEquals(self.browser.find_element(By.ID, "perc_Failed_1").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "score_Failed_1").text, "0")