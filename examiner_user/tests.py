from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

# Create your tests here.

# settings for testing
home_adress = "https://examiner-mp.herokuapp.com"
test_login = "Test"
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
        self.browser.get(home_adress)
        click_id(self.browser, "login")
        type_id(self.browser, "username", test_login)
        type_id(self.browser, "password", test_password)
        click_id(self.browser, "submit")

    @classmethod
    def tearDownClass(self):
        self.browser.get(home_adress + "/examiner/test")
        click_id(self.browser, "logout")
        self.browser.close()
        super().tearDownClass()
    
    def setUp(self):
        self.create_student()
        self.create_course()
    
    def tearDown(self):
        self.browser.get(home_adress + "/examiner/test")

    def create_course(self):
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "add")
        type_id(self.browser, "id_name", "Testowa nazwa kursu")
        type_id(self.browser, "id_category", "Testowa kategoria")
        click_id(self.browser, "submit")

    def create_student(self):
        click_id(self.browser, "users")
        click_id(self.browser, "create_student")
        type_id(self.browser, "id_username", "testowyStudent")
        type_id(self.browser, "id_password1", test_password)
        type_id(self.browser, "id_password2", test_password)
        click_id(self.browser, "submit")

    def test_logging_in(self):
        # user loggs in and sees his username on the sidebar
        self.assertEquals(self.browser.find_element(By.ID, "current_username").text, test_login)
    
    def test_create_course(self):
        # there is a course with corresponding name and all the apropriate values are set to 0
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Testowa nazwa kursu"))
        self.assertEquals(self.browser.find_element(By.ID, "category_Testowa nazwa kursu").text, "Testowa kategoria")
        self.assertEquals(self.browser.find_element(By.ID, "time_Testowa nazwa kursu").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "question_amount_Testowa nazwa kursu").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "lesson_amount_Testowa nazwa kursu").text, "0")
        self.assertEquals(self.browser.find_element(By.ID, "student_amount_Testowa nazwa kursu").text, "0")
    
    def test_edit_course(self):
        # users edits name, category, time and attempt amount of course
        click_id(self.browser, "name_Testowa nazwa kursu")
        click_id(self.browser, "edit")
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", "Edytowana nazwa kursu")
        clear_id(self.browser, "id_category")
        type_id(self.browser, "id_category", "Edytowana kategoria kursu")
        clear_id(self.browser, "id_attempt_amount")
        type_id(self.browser, "id_attempt_amount", "12")
        clear_id(self.browser, "id_time")
        type_id(self.browser, "id_time", "34")
        click_id(self.browser, "submit")
        # user sees the changes in course detail view
        self.assertEquals(self.browser.find_element(By.ID, "name").text, "Nazwa kursu: Edytowana nazwa kursu")
        self.assertEquals(self.browser.find_element(By.ID, "category").text, "Kategoria: Edytowana kategoria kursu")
        self.assertEquals(self.browser.find_element(By.ID, "attempt_amount").text, "Ilość podejść: 12")
        self.assertEquals(self.browser.find_element(By.ID, "time").text, "Czas trwania testu: 34 minut")
        # user sees the changes in course general view
        click_id(self.browser, "nav_courses")
        self.assertEquals(self.browser.find_element(By.ID, "name_Edytowana nazwa kursu").text, "Edytowana nazwa kursu")
        self.assertEquals(self.browser.find_element(By.ID, "category_Edytowana nazwa kursu").text, "Edytowana kategoria kursu")
        self.assertEquals(self.browser.find_element(By.ID, "time_Edytowana nazwa kursu").text, "34")

    def test_create_student(self):
        # user creates new student
        click_id(self.browser, "users")
        # user checks if user is created
        self.assertIsNotNone(self.browser.find_element(By.ID, "testowyStudent"))

    def test_append_student(self):
        click_id(self.browser, "users")
        click_id(self.browser, "nav_courses")
        # user appends student to test
        click_id(self.browser, "name_Testowa nazwa kursu")
        click_id(self.browser, "edit")
        click_id(self.browser, "student_nav")
        type_id(self.browser, "id_student", "testowyStudent")
        # I need to use execute_script becouse otherwise exception is rised due to button being obscured by div
        student_submit = self.browser.find_element(By.ID, "submit_student")
        self.browser.execute_script("arguments[0].click();", student_submit)
        # user checks if student is appeneded
        # student_nav must be double clicked due to unscrolling aimation
        click_id(self.browser, "student_nav")
        time.sleep(1)
        click_id(self.browser, "student_nav")
        self.assertIsNotNone(self.browser.find_element(By.ID, "testowyStudent_table"))
        # user removes student from course
        click_id(self.browser, "testowyStudent_delete")
        click_id(self.browser, "student_nav")
        # user checks if there is no student in the course student list
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "testowyStudent_table"))

    def test_search(self):
        click_id(self.browser, "nav_courses")
        # user looks for non_existing course
        type_id(self.browser, "id_name", "jakieś inne szkolenie")
        type_id(self.browser, "id_name", Keys.ENTER)
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "name_Testowa nazwa kursu"))
        # user clears the field and refreshes to see if the created course is visible
        clear_id(self.browser, "id_name")
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Testowa nazwa kursu"))
        # user looks for existing course
        type_id(self.browser, "id_name", "Testowa nazwa kursu")
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Testowa nazwa kursu"))
        click_id(self.browser, "users")
        self.assertIsNotNone(self.browser.find_element(By.ID, "testowyStudent"))
        # checks if user can be found when not looked for
        type_id(self.browser, "id_name", "inny uczen")
        type_id(self.browser, "id_name", Keys.ENTER)
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "testowyStudent"))
        # checks if clearing allows to see student again
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "testowyStudent"))
        # checks if student can be found when looked for
        type_id(self.browser, "id_name", "testowyStudent")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "testowyStudent"))

    def test_create_question(self):
        # user creates question
        click_id(self.browser, "nav_courses")
        click_id(self.browser, "name_Testowa nazwa kursu")
        click_id(self.browser, "edit")
        click_id(self.browser, "add_question")
        type_id(self.browser, "id_text", "Testowa treść pytania")
        type_id(self.browser, "id_answer1", "Pierwsza testowa odpowiedź")
        type_id(self.browser, "id_answer2", "Druga testowa odpowiedź")
        click_id(self.browser, "id_correct_answers_1")
        click_id(self.browser, "submit")
        click_id(self.browser, "back")
        # user checks if question was created
        self.assertIsNotNone(self.browser.find_element(By.ID, "1"))
        # users checks if data was properly acepted
        click_id(self.browser, "1")
        self.assertEquals(self.browser.find_element(By.ID, "id_text").text, "Testowa treść pytania")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer1").get_attribute('value'), "Pierwsza testowa odpowiedź")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer2").get_attribute('value'), "Druga testowa odpowiedź")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer3").get_attribute('value'), "")
        # user changes the data
        type_id(self.browser, "id_text", "1")
        type_id(self.browser, "id_answer1", "2")
        type_id(self.browser, "id_answer2", "3")
        type_id(self.browser, "id_answer3", "4")
        click_id(self.browser, "submit_change")
        click_id(self.browser, "1")
        # user checks if data got changed
        self.assertEquals(self.browser.find_element(By.ID, "id_text").text, "Testowa treść pytania1")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer1").get_attribute('value'), "Pierwsza testowa odpowiedź2")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer2").get_attribute('value'), "Druga testowa odpowiedź3")
        self.assertEquals(self.browser.find_element(By.ID, "id_answer3").get_attribute('value'), "4")