import json
import requests
import sys
from bs4 import BeautifulSoup as bS
from datetime import datetime


def json_format(success, message_or_grades):
  """
  Args:
      success: boolean if scraping was successful
      message_or_grades: a message for errors or grade data in JSON format

  Returns:
      A JSON formatted response
  """

  if success:
    return json.dumps({'success': True, 'new_grades': message_or_grades})

  return json.dumps({'success': False, 'message': message_or_grades})


def status(progress, message):
  return json.dumps({'progress': progress, 'message': message})


def clean_string(s):
  """Cleans the string"""
  s = s.strip()
  if s == "":
    return False
  return s


def clean_number(n):
  """Cleans the number"""
  n = n.strip()
  try:
    n = float(n)
    return n
  except:
    return False


def clean(_soup):
  to_delete = _soup.find_all('span', class_='visually-hidden')
  [t.decompose() for t in to_delete]


class BasisClass:
  def __init__(self, class_name, assignments, tests, assesments):
    self.class_name = class_name
    self.assignments = assignments
    self.tests = tests
    self.assesments = assesments

  @property
  def as_dict(self):
    return {
      "class_name": self.class_name,
      "overall_percent": self.overall_percent,
      "grades": self.grades
    }


class BasisWeights:
  def __init__(self):
    self._weights = {}

  @property
  def as_dict(self):
    return self._weights

  def add_class(self, class_name):
    if class_name not in self._weights:
      self._weights[class_name] = {}

  def add_weight(self, class_name, weight_name, weight_value):
    self.add_class(class_name)

    if weight_name not in self._weights[class_name]:
      self._weights[class_name][weight_name] = weight_value


class Scraper:
    def __init__(self):
        """Inits with a session"""
        self.session = requests.Session()
        self._progress = 0
        self._message = ""
        print(status(self._progress, self._message))

    @property
    def progress(self):
        return self._progress

    @property
    def message(self):
        return self._message

    @progress.setter
    def progress(self, value):
        self._progress = value
        print(status(self._progress, self._message))

    @message.setter
    def message(self, value):
        self._message = value
        print(status(self._progress, self._message))


class BasisScraper(Scraper):
  def login(self, email, _password):
    url = "https://app.schoology.com/login?destination=grades/grades"

    payload = {'mail': email,
               'pass': _password,
               'form_id': 's_user_login_form'}

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'origin': 'https://app.schoology.com',
      'referer': 'https://app.schoology.com/login?destination=grades/grades',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
    }

    resp = self.session.post(url, headers=headers, data=payload, allow_redirects=False)
    self.progress = 5
    self.message = "Logged in!"
    if len(resp.cookies) == 0:
      self.progress = 0
      print(json_format(False, "Incorrect login details."))
      sys.exit()

    return True

  def get_present(self):
    url = "https://app.schoology.com/grades/grades"

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'referer': 'https://app.schoology.com/login?destination=grades/grades',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
    }

    resp = self.session.post(url, headers=headers)
    self.progress = 20
    self.message = 'Searching for courses...'

    soup = bS(resp.text, 'html.parser')

    classes = soup.find_all('div', class_="gradebook-course")

    all_classes = []
    weights = BasisWeights()
    term = None

    total_course_count = len(classes)
    scraped_course_count = 0
    initial_progress = self.progress
    max_progress = 100
    self.message = 'Synced ' + str(scraped_course_count) + ' of ' + str(total_course_count) + ' courses...'
    self.progress = initial_progress + (max_progress - initial_progress) * scraped_course_count / total_course_count
    with open('classes.txt','w') as out:
        print('',file=out)
    for class_ in classes:
      class_name_soup = class_.find('div', class_='gradebook-course-title')
      clean(class_name_soup)
      class_name = class_name_soup.text
      
      with open('classes.txt','a') as out:
        print(class_name,file=out)
      class_name = clean_string(class_name)

      weights.add_class(class_name)

      if 'lunch' in class_name.lower() or 'office' in class_name.lower():
        total_course_count -= 1
        self.message = 'Synced ' + str(scraped_course_count) + ' of ' + str(total_course_count) + ' courses...'
        self.progress = initial_progress + (max_progress - initial_progress) * scraped_course_count / total_course_count
        continue

      grades_soup = class_.find('div', class_='gradebook-course-grades')
      overall_grade_soup = grades_soup.find('span', class_='numeric-grade primary-grade')
      if overall_grade_soup is None:
        overall_grade = None
      else:
        overall_grade_soup = overall_grade_soup.find('span', class_='rounded-grade')
        overall_grade = overall_grade_soup['title']

      grades_soup = grades_soup.find('table', role='presentation')
      term_soup = grades_soup.find('tr', class_='period-row').find('span', class_='title')
      clean(term_soup)
      if term is None:
        term = '-'.join(list(map(lambda t: t[-2:], term_soup.text.split(' - '))))
        term = clean_string(term)

      categories_soup = grades_soup.find_all('tr', class_='category-row')
      grades = []
      for category_soup in categories_soup:
        clean(category_soup)
        category_name = category_soup.find('span', class_='title')
        if category_name is None:
          continue

        category_name = clean_string(category_name.text)

        category_value = category_soup.find('span', class_='percentage-contrib')
        if category_value is None:
          continue

        category_value = clean_number(category_value.text[1:-2])
        category_id = category_soup['data-id']

        if category_name is not False and category_value is not False:
          weights.add_weight(class_name, category_name, category_value)
          assignments_soup = grades_soup.find_all('tr', {'data-parent-id': category_id})
          for assignment_soup in assignments_soup:
            assignment_id = assignment_soup['data-id']

            assignment_name_soup = assignment_soup.find('span', class_='title')
            clean(assignment_name_soup)
            assignment_name = assignment_name_soup.text

            assignment_date_time_soup = assignment_soup.find('span', class_='due-date')
            if assignment_date_time_soup is not None:
              clean(assignment_date_time_soup)
              date_time = assignment_date_time_soup.text
              date, time = date_time.split(' ')
              sort_date = datetime.strptime(date_time, "%m/%d/%y %I:%M%p").timestamp()
            else:
              date = None
              time = None
              sort_date = None

            assignment_grade_soup = assignment_soup.find('td', class_='grade-column')

            points_gotten_soup = assignment_grade_soup.find('span', class_='rounded-grade')
            if points_gotten_soup is not None:
              points_gotten = clean_number(points_gotten_soup['title'])
            else:
              points_gotten = None

            points_possible_soup = assignment_grade_soup.find('span', class_='max-grade')
            if points_possible_soup is not None:
              points_possible = clean_number(points_possible_soup.text[3:])
            else:
              points_possible = None

            assignment = {"date": date, "time": time, "category": category_name, "assignment_name": assignment_name, "points_possible": points_possible, "points_gotten": points_gotten,
                          "id": assignment_id, 'sort_date': sort_date}

            grades.append(assignment)

      no_due_date = list(filter(lambda j: j['sort_date'] is None, grades))
      no_due_date.reverse()
      due_date = list(filter(lambda j: j['sort_date'] is not None, grades))
      grades = sorted(due_date, key=lambda j: j['sort_date'], reverse=True)
      [grades.insert(0, item) for item in no_due_date]
      grades = [{key: value for key, value in assignment.items() if key != 'sort_date'} for assignment in grades]
      all_classes.append(BasisClassGrade(class_name, overall_grade, grades).as_dict)
      scraped_course_count += 1
      self.message = 'Synced ' + str(scraped_course_count) + ' of ' + str(total_course_count) + ' courses...'
      self.progress = initial_progress + (max_progress - initial_progress) * scraped_course_count / total_course_count

    if term is not None:
      result = {"grades": {term: {"_": all_classes}}, "weights": {term: {"_": weights.as_dict}}}
      print(json_format(True, result))
    #else:
      print(json_format(False, "No class data."))


if __name__ == "__main__":
  school = "basis"
  if school == "basis":
    user = sys.argv[1]
    print(user)
    password = sys.argv[2]
    bs = BasisScraper()
    try:
      if bs.login(user, password):
        bs.get_present()
    except requests.Timeout:
      print(json_format(False, "Could not connect to Schoology."))
    except Exception as e:
      # Error when something in PowerSchool breaks scraper
      print(json_format(False, "An Unknown Error occurred. Contact support."))
      # Uncomment below to print error
      # print(e)