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
test_login = "Test_Examiner"
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
class TestExaminer(LiveServerTestCase):
    
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.browser = webdriver.Firefox(geko_driver_directory)
        self.browser.maximize_window()
        self.browser.get(home_adress)
        click_id(self.browser, "login")
        type_id(self.browser, "username", test_login)
        type_id(self.browser, "password", test_password)
        click_id(self.browser, "submit")
        click_id(self.browser, "English")

    @classmethod
    def tearDownClass(self):
        click_id(self.browser, "logout")
        self.browser.close()
        super().tearDownClass()
    
    def setUp(self):
        self.browser.get(home_adress)
        click_id(self.browser, "English")
        self.create_course()
        self.create_group()

    def tearDown(self):
        self.browser.get(home_adress + "/examiner/test")

    def create_group(self):
        click_id(self.browser, "nav_groups")
        click_id(self.browser, "create_group")
        type_id(self.browser, "id_name", "Test_Group")
        click_id(self.browser, "submit")

    def create_course(self):
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "add")
        type_id(self.browser, "id_name", "Test course name")
        type_id(self.browser, "id_category", "Test category")
        click_id(self.browser, "submit")

    def test_logging_in(self):
        # user loggs in and sees his username on the sidebar
        self.assertEquals(self.browser.find_element(By.ID, "current_username").text,(f"Examiner: {test_login}"))
    
    def test_create_course(self):
        click_id(self.browser, "nav_courses")
        # there is a course with corresponding name and all the apropriate values are set to 0
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Test course name"))
        self.assertEquals(self.browser.find_element(By.ID, "category_Test course name").text, "Test category")
        self.assertEquals(self.browser.find_element(By.ID, "time_Test course name").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "question_amount_Test course name").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "lesson_amount_Test course name").text, "0")
    
    def test_edit_course(self):
        # users edits name, category, time and attempt amount of course
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "link_Test course name")
        click_id(self.browser, "edit")
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", "Edited course name")
        clear_id(self.browser, "id_category")
        type_id(self.browser, "id_category", "Edited course category")
        clear_id(self.browser, "id_attempt_amount")
        type_id(self.browser, "id_attempt_amount", "12")
        clear_id(self.browser, "id_time")
        type_id(self.browser, "id_time", "34")
        click_id(self.browser, "submit")
        # user sees the changes in course detail view
        self.assertEquals(self.browser.find_element(By.ID, "name").text, "Course name: Edited course name")
        self.assertEquals(self.browser.find_element(By.ID, "category").text, "Category: Edited course category")
        self.assertEquals(self.browser.find_element(By.ID, "attempt_amount").text, "Attempt amount: 12")
        self.assertEquals(self.browser.find_element(By.ID, "time").text, "Exam duration: 34 minutes")
        # user sees the changes in course general view
        click_id(self.browser, "nav_courses")
        self.assertEquals(self.browser.find_element(By.ID, "name_Edited course name").text, "Edited course name")
        self.assertEquals(self.browser.find_element(By.ID, "category_Edited course name").text, "Edited course category")
        self.assertEquals(self.browser.find_element(By.ID, "time_Edited course name").text, "34")

    def test_create_group(self):
        # user checks if group was created with proper name
        click_id(self.browser, "nav_groups")
        self.assertEquals(self.browser.find_element(By.ID, "Test_Group").text, "Test_Group")

    def test_append_student(self):
        click_id(self.browser, "nav_users")
        # user appends student to test
        click_id(self.browser, "link_Test_Student")
        type_id(self.browser, "id_group", "Test_Group")
        # I need to use execute_script becouse otherwise exception is rised due to button being obscured by div
        student_submit = self.browser.find_element(By.ID, "submit")
        self.browser.execute_script("arguments[0].click();", student_submit)
        # user checks if student is appeneded
        # student_nav must be double clicked due to unscrolling aimation
        click_id(self.browser, "nav_groups")
        click_id(self.browser, "link_Test_Group")
        click_id(self.browser, "student_nav")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # user removes student from course
        student_remove = self.browser.find_element(By.ID, "Test_Student_delete")
        self.browser.execute_script("arguments[0].click();", student_remove)
        click_id(self.browser, "student_nav")
        # user checks if there is no student in the course student list
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Student_table"))

    def test_append_course(self):
        # user appends course to student group
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "link_Test course name")
        click_id(self.browser, "edit")
        click_id(self.browser, "student_nav")
        type_id(self.browser, "id_group", "Test_Group")
        type_id(self.browser, "id_deadline", "2030-11-11")
        click_id(self.browser, "submit_student")
        # user checks if course is appended
        click_id(self.browser, "student_nav")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Group_table"))

    def test_search(self):
        click_id(self.browser, "nav_courses")
        # user looks for non_existing course
        type_id(self.browser, "id_name", "some other training")
        type_id(self.browser, "id_name", Keys.ENTER)
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "name_Test course name"))
        # user clears the field and refreshes to see if the created course is visible
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Test course name"))
        # user looks for existing course
        type_id(self.browser, "id_name", "Test course name")
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Test course name"))
        click_id(self.browser, "nav_users")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # checks if user can be found when not looked for
        type_id(self.browser, "id_name", "other student")
        type_id(self.browser, "id_name", Keys.ENTER)
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Student"))
        # checks if clearing allows to see student again
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # checks if student can be found when looked for
        type_id(self.browser, "id_name", "Test_Student")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))

    def test_create_question(self):
        # user creates question
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "link_Test course name")
        click_id(self.browser, "edit")
        click_id(self.browser, "add_question")
        type_id(self.browser, "id_text", "Test question text")
        type_id(self.browser, "id_answer1", "First test answer")
        type_id(self.browser, "id_answer2", "Secound test answer")
        click_id(self.browser, "id_correct_answers_1")
        click_id(self.browser, "submit")
        click_id(self.browser, "back")
        # user checks if question was created
        self.assertIsNotNone(self.browser.find_element(By.ID, "1"))
        # users checks if data was properly acepted
        click_id(self.browser, "1")
        self.assertEquals(self.browser.find_element(By.ID, "id_text").text, "Test question text")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer1").get_attribute('value'), "First test answer")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer2").get_attribute('value'), "Secound test answer")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer3").get_attribute('value'), "")
        # user changes the data
        type_id(self.browser, "id_text", "1")
        type_id(self.browser, "id_answer1", "2")
        type_id(self.browser, "id_answer2", "3")
        type_id(self.browser, "id_answer3", "4")
        click_id(self.browser, "submit_change")
        click_id(self.browser, "1")
        # user checks if data got changed
        self.assertEquals(self.browser.find_element(By.ID, "id_text").text, "Test question text1")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer1").get_attribute('value'), "First test answer2")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer2").get_attribute('value'), "Secound test answer3")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer3").get_attribute('value'), "4")