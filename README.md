1. Examiner
This aplication is a simple e-learning platofrm in polish language. It can be used to create online courses, add materials to these courses and decide which student users have acess to which course. It also features creation of exams for courses. Examiner users can write questions for exams, which are going to be shown to students in random order. It is possible to write more questions than the amount that will be given to student users (in that case students will recieve only a fraction of all questions prepered). Exams can have single choice questions (radio) or mulitple choice questions (checkboxes). Exams can be given time limits (in minutes) and limited amount of attempts that students can take before failing course (3 by default). Students can then view their results and examiners can view results of all students.

2. Technical details
This aplication was written in Python and javaScript using Django framework.

3. User guide
You can fork this repository and upload it to a hosting server.
For a preview you can visit this Heroku link: https://examiner-mp.herokuapp.com
Before deployment remember to set enviormental variable - SECRET_KEY.
It is advised that Heroku preview version should not be used for serious pourposes since all examiner users have acess to all courses and results. The idea is that every examining body would have their own hosted server. If multiple unrelated examiners were to use this application then each could view and change courses and lessons belonging to each other which is not recomended.

4. Credits:
Mateusz Pawłowski