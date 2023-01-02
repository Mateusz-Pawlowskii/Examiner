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
class TestPlatform(LiveServerTestCase):
    
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

    @classmethod
    def tearDownClass(self):
        self.browser.get(home_adress + "/platform/test")
        click_id(self.browser, "logout")
        self.browser.close()
        super().tearDownClass()
    
    def tearDown(self):
        self.browser.get(home_adress + "/platform/test")

    def create_group(self):
        click_id(self.browser, "nav_groups")
        click_id(self.browser, "create_group")
        type_id(self.browser, "id_name", "Test_Group")
        click_id(self.browser, "submit")

    def test_logging_in(self):
        # user loggs in and sees his username on the sidebar
        self.assertEquals(self.browser.find_element(By.ID, "current_username").text, f"Administrator: {test_login}")

    def test_group_creation(self):
        self.create_group()
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Group"))

    def test_create_group(self):
        self.create_group()
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Group"))

    def test_create_student(self):
        # user creates new student
        click_id(self.browser, "nav_students")
        # user checks if user is created
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))

    def test_rename_student(self):
        click_id(self.browser, "nav_students")
        click_id(self.browser, "link_Test_Student")
        clear_id(self.browser, "id_username")
        type_id(self.browser, "id_username", "Edited_Username")
        click_id(self.browser, "submit_name")
        click_id(self.browser, "nav_students")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Edited_Username"))
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Student"))
        click_id(self.browser, "link_Edited_Username")
        clear_id(self.browser, "id_username")
        type_id(self.browser, "id_username", "Test_Student")
        click_id(self.browser, "submit_name")

    def test_append_student(self):
        self.create_group()
        click_id(self.browser, "nav_students")
        # user appends student to test
        click_id(self.browser, "link_Test_Student")
        type_id(self.browser, "id_group", "Test_Group")
        # I need to use execute_script becouse otherwise exception is rised due to button being obscured by div
        student_submit = self.browser.find_element(By.ID, "submit_group")
        self.browser.execute_script("arguments[0].click();", student_submit)
        # user checks if student is appeneded
        # student_nav must be double clicked due to unscrolling aimation
        click_id(self.browser, "nav_groups")
        click_id(self.browser, "link_Test_Group")
        click_id(self.browser, "student_nav")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # user removes student from course
        click_id(self.browser, "Test_Student_delete")
        click_id(self.browser, "student_nav")
        # user checks if there is no student in the course student list
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Student_delete"))

    def test_search(self):
        click_id(self.browser, "nav_students")
        # user looks for non_existing student
        type_id(self.browser, "id_name", "some other person")
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Student"))
        # user clears the field and refreshes to see if student is visible
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # user looks for existing student
        type_id(self.browser, "id_name", "Test_Student")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Student"))
        # checks if group can be found when not looked for
        self.create_group()
        click_id(self.browser, "nav_groups")
        type_id(self.browser, "id_name", "other group")
        with self.assertRaises(NoSuchElementException):
            (self.browser.find_element(By.ID, "Test_Group"))
        # checks if clearing allows to see group again
        clear_id(self.browser, "id_name")
        type_id(self.browser, "id_name", Keys.ENTER)
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Group"))
        # checks if group can be found when looked for
        type_id(self.browser, "id_name", "Test_Group")
        self.assertIsNotNone(self.browser.find_element(By.ID, "Test_Group"))

    def test_platform_name_change(self):
        # user changes platforms name
        click_id(self.browser, "nav_settings")
        clear_id(self.browser, "name")
        type_id(self.browser, "name", "Edited platform name")
        submit_settings = self.browser.find_element(By.ID, "submit_settings")
        self.browser.execute_script("arguments[0].click();", submit_settings)
        # user checks if name has changed
        click_id(self.browser, "homepage")
        self.assertEquals(self.browser.find_element(By.ID, "platform_name").text, "Edited platform name")
        # user reverts change
        click_id(self.browser, "nav_settings")
        clear_id(self.browser, "name")
        type_id(self.browser, "name", "Test Platform")
        submit_settings = self.browser.find_element(By.ID, "submit_settings")
        self.browser.execute_script("arguments[0].click();", submit_settings)

    def test_default_grades(self):
        # user enacts default grades
        click_id(self.browser, "nav_settings")
        click_id(self.browser, "default_school")
        # user checks if grades were added
        for n in range (1, 7):
            self.assertIsNotNone(self.browser.find_element(By.ID, f"name_{n}"))
        # user checks if grades have poper bars
        self.assertEquals(self.browser.find_element(By.ID, "bar_1").text, "0%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_2").text, "40%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_3").text, "55%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_4").text, "70%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_5").text, "84%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_6").text, "96%")
        # user deletes grades
        for n in range (1, 7):
            click_id(self.browser, f"del_{n}")

    def test_custom_grades(self):
        # user creates custom grades
        click_id(self.browser, "nav_settings")
        type_id(self.browser, "id_name", "Test Grade 1")
        type_id(self.browser, "id_bar", "20")
        click_id(self.browser, "submit_grade")
        type_id(self.browser, "id_name", "Test Grade 2")
        type_id(self.browser, "id_bar", "40")
        click_id(self.browser, "submit_grade")
        # user checks if grades were added and if their bars are correct
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Test Grade 1"))
        self.assertIsNotNone(self.browser.find_element(By.ID, "name_Test Grade 2"))
        self.assertEquals(self.browser.find_element(By.ID, "bar_Test Grade 1").text, "20%")
        self.assertEquals(self.browser.find_element(By.ID, "bar_Test Grade 2").text, "40%")
        # user deletes custom grades
        click_id(self.browser, "del_Test Grade 1")
        click_id(self.browser, "del_Test Grade 2")